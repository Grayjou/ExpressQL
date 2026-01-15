"""
ExpressQL Expression Parser - Parse SQL-like expression strings.

This module provides functionality to parse SQL expression strings into
SQLExpression objects. It handles arithmetic operations, function calls,
column references, literals, and complex nested expressions.

Key Features:
    - Parses arithmetic operations (+, -, *, /)
    - Parses function calls (e.g., SUM(column))
    - Handles nested expressions with proper precedence
    - Supports string concatenation (||)
    - Handles subqueries

Functions:
    parse_expression: Main entry point for parsing expression strings

Example:
    >>> from expressql.parsers.expressions_parser import parse_expression
    >>> expr = parse_expression("LOG(age, 10) + salary * 2")
    >>> sql, params = expr.placeholder_pair()
"""

from ..base import SQLExpression, SQLExpressionSum, SQLExpressionConcat, SQLExpressionProduct, Func, \
SubQuery
from typing import List, Union, Tuple, Dict
from ..utils import is_quoted, ensure_bracketed
from .parsing_utils import extract_word_before, remove_outer_brackets, ensure_outer_bracketed, is_outer_bracketed
from .subquery_placeholder import parametrize_subquery
import re


double_quote = '"'
letters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

class _Token:
    pass 
class Token(_Token):
    def __init__(self, content, inverted=False, positive=True):
        self.content:str = content
        self.inverted:bool = inverted
        self.positive:bool = positive


    def __repr__(self):
        return f"Token(content={self.content!r}, inverted={self.inverted}, positive={self.positive})"

    def __str__(self):
        flags = []
        if self.inverted:
            flags.append("inverted")
        if not self.positive:
            flags.append("negative")
        return f"Token({self.content}" + (f" [{', '.join(flags)}]" if flags else "") + ")"

    def can_simple_resolve(self) -> bool:
        return set("+-*/%&^!<>=~|").isdisjoint(set(self.content))

    def _simple_resolve(self) -> SQLExpression:
        content:str = self.content.strip()
        if is_quoted(content):
            return SQLExpression(expression_value=content.strip(double_quote))
        elif is_outer_bracketed(content):
            content = content[1:-1].strip()
            if "," in content:
                values = [v.strip() for v in content.split(",")]
                return SQLExpression(expression_type="set", expression_value=values)
            else:
                return SQLExpression(value=content)
        
        try:
            float(content)
            positive = self.positive
            while content.startswith("-"):
                positive = not positive
                content = content[1:].strip()
            return self.export_expression(expression_type="value", positive=positive)
        except ValueError:
            pass
        if " " not in content:
            positive = self.positive
            while content.startswith("-"):
                positive = not positive
                content = content[1:].strip()
            return self.export_expression(expression_type="column", positive=positive)
        raise ValueError(f"Cannot resolve token: {self.content}")

    def resolve(self) -> SQLExpression:
        if isinstance(self.content, SQLExpression):
            return self.content
        if is_function_call(self.content):
            return tokenize_function(self.content, inverted=self.inverted, positive=self.positive).resolve()
        if self.can_simple_resolve():
            expr = self._simple_resolve()
        else:
            expr = outermost_operation_tokenize(
                self.content,
                inverted=self.inverted,
                positive=self.positive
            ).resolve()

        expr.inverted = self.inverted
        expr.positive = self.positive
        return expr

    def export_expression(self, expression_type: str = "value", positive = None) -> SQLExpression:
        return SQLExpression(
            expression_value=self.content,
            expression_type=expression_type,
            inverted=self.inverted,
            positive=self.positive if positive is None else positive
        )

class TokenSum(_Token):
    def __init__(self, items: List[Union[Token, SQLExpression]] = None,
                 inverted: bool = False, positive: bool = True):
        self.items = items or []
        self.inverted = inverted
        self.positive = positive

    def resolve(self) -> SQLExpressionSum:
        expressions: List[SQLExpression] = []
        for item in self.items:
            if isinstance(item, _Token):
                expressions.append(item.resolve())
            elif isinstance(item, SQLExpression):
                expressions.append(item)
            else:
                raise TypeError(f"Expected Token or SQLExpression, got {type(item)}")
        return SQLExpressionSum(expressions, positive=self.positive, inverted=self.inverted)

    def __repr__(self):
            return f"TokenSum(items={self.items!r})"

class TokenMul(_Token):
    def __init__(self, items: List[Union[Token, SQLExpression]] = None,
                 inverted: bool = False, positive: bool = True):
        self.items = items or []
        self.inverted = inverted
        self.positive = positive

    def resolve(self) -> SQLExpressionSum:
        expressions: List[SQLExpression] = []
        for item in self.items:
            if isinstance(item, _Token):
                expressions.append(item.resolve())
            elif isinstance(item, SQLExpression):
                expressions.append(item)
            else:
                raise TypeError(f"Expected Token or SQLExpression, got {type(item)}")
        return SQLExpressionProduct(expressions, positive=self.positive, inverted=self.inverted)

    def __repr__(self):
            return f"TokenMul(items={self.items!r})"

class TokenConcat(_Token):
    def __init__(self, items: List[Union[Token, SQLExpression]] = None, 
                 inverted: bool = False, positive: bool = True):
        self.items = items or []
        self.inverted = inverted
        self.positive = positive

    def resolve(self) -> SQLExpressionConcat:
        expressions: List[SQLExpression] = []
        for item in self.items:
            if isinstance(item, _Token):
                expressions.append(item.resolve())
            elif isinstance(item, SQLExpression):
                expressions.append(item)
            else:
                raise TypeError(f"Expected Token or SQLExpression, got {type(item)}")
        return SQLExpressionConcat(expressions)

    def __repr__(self):
            return f"TokenConcat(items={self.items!r})"
    
class TokenFunc:
    def __init__(self, function_name: str, arguments: List[Token], 
                 inverted: bool = False, positive: bool = True):
        self.function_name = function_name
        self.arguments = arguments
        self.inverted = inverted
        self.positive = positive
    def resolve(self) -> SQLExpression:
        resolved_args = [arg.resolve() for arg in self.arguments]

        return Func(self.function_name, *resolved_args, positive=self.positive, inverted=self.inverted)

    def __repr__(self):
        return f"TokenFunc(function_name={self.function_name!r}, arguments={self.arguments!r})"

class TokenSubQuery(_Token):
    def __init__(self, query:SubQuery):
        self.query = query
    def resolve(self) -> SQLExpression:
        return self.query

def is_function_call(string: str) -> bool:
    string = string.strip()
    if not string:
        return False
    if "(" not in string or ")" not in string:
        return False
    if string.startswith("(") or not string.endswith(")"):
        return False
    if string.count("(") != string.count(")"):
        return False
    first_paren = string.find("(")
    if set(string[:first_paren]) & set("0123456789+-|*/%&^!<>=~"):
        return False
    return True

def extract_replace_outermost_bracketed_withfunc(string: str, replacement:str) -> Tuple[str, str]:
    """
    Extracts and replaces the outermost bracketed expression in a given string.
    This function identifies the outermost pair of parentheses in the input string,
    extracts the content within them, and replaces the entire bracketed expression
    with the specified replacement string. If a function call is detected immediately
    before the opening parenthesis, it is included in the returned tuple.
    Args:
        string (str): The input string containing the bracketed expression.
        replacement (str): The string to replace the outermost bracketed expression.
    Returns:
        tuple[str, str]: A tuple containing:
            - The modified string with the outermost bracketed expression replaced.
            - The extracted content of the bracketed expression, including any
                associated function call if present.
    """
    
    depth = 0
    start = None
    for i, char in enumerate(string):
        if char == '(':
            if depth == 0:
                start = i
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0 and start is not None:
                #Backtrack from the left bracket to find a function call
                start_, word = extract_word_before(string, set("+-*/%&^!<>=~|"), start)
                if word.replace(" ", ""):
                    return string[:start_] + replacement + string[i+1:], word + ensure_outer_bracketed(string[start+1:i])
                return string[:start] + replacement + string[i+1:], ensure_bracketed(string[start+1:i])

    return string, ""

def tokenize_function(string, inverted: bool = False, positive: bool = True) -> TokenFunc:

    func_name = string.split("(", 1)[0]
    args_str = string[len(func_name)+1:-1]  # strip function name and parentheses
    string, outermost_tokens = collect_outhermost_placeholders(args_str)
    args = string.split(",") if string else []
    args = replace_placeholders(args, outermost_tokens)
    tokenized_args = []
    for arg in args:
        arg = arg.strip()
        if is_function_call(arg):
            tokenized_args.append(tokenize_function(arg))
        else:
            tokenized_args.append(Token(arg))


    return TokenFunc(function_name=func_name, arguments=tokenized_args, inverted=inverted, positive=positive)

def collect_outhermost_placeholders(string: str) -> Tuple[str, Dict[str, str]]:
    outermost_tokens: Dict[str, str] = {}
    i = 0
    repeated = False
    while "(" in string and ")" in string:
        placeholder = f'{{X{i}}}'
        string_, extracted = extract_replace_outermost_bracketed_withfunc(string, placeholder)
        if string_ == string:
            if repeated:
                #This will happen if there are mismatched parentheses
                # or if the string is malformed in some way
                raise ValueError(f"Cannot extract outermost placeholder from: {string}")
            repeated = True
        string = string_
        # Store the raw extracted text (without wrapping in Token)
        outermost_tokens[placeholder] = extracted
        i += 1
    return string, outermost_tokens

def replace_placeholders(parts: List[str], outermost_tokens: Dict[str, str]) -> List[str]:
    for p, part in enumerate(parts):
        found = None
        for key, value in outermost_tokens.items():
            if key in part:
                parts[p] = part.replace(key, value)
                found = key
                part = parts[p]
        if found is not None:
            outermost_tokens.pop(found, None)
    return parts

def remove_starting_nonsense(string: str) -> str:
    while string.startswith("--") or string.startswith("++"):
        string = string[2:].strip()
    return string

def replace_sign_nonsense(string: str) -> str:
    while "--" in string:
        string = string.replace("--","").strip()
    while "+-" in string:
        string = string.replace("+-","-").strip()
    while "-+" in string:
        string = string.replace("-+","+").strip()
    while "++" in string:
        string = string.replace("++","").strip()
    while "-+-" in string:
        string = string.replace("-+-", "+").strip()
    while "+-+" in string:
        string = string.replace("+-+", "-").strip()
    return string

def prepare_string(string: str, inverted: bool = False, positive: bool = True, *,
                    outer_brackets_removed: bool = False
                    ) -> str:
    if not string:
        raise ValueError("Input string cannot be empty")

    string = remove_starting_nonsense(string)
    if not outer_brackets_removed:
        string = remove_outer_brackets(string)
    if string.upper().startswith("SELECT"):
        return string, inverted, positive
    string = string.replace(" ", "")
    if string.startswith("-"):
        if is_outer_bracketed(string[1:]):
            positive = not positive
            string = remove_outer_brackets(string[1:])
            string = remove_starting_nonsense(string)
    elif is_outer_bracketed(string):
        string = remove_outer_brackets(string)
        string = remove_starting_nonsense(string)
    return string, inverted, positive


def outermost_operation_tokenize(string: str, inverted: bool = False, positive: bool = True, *,
                                 outer_brackets_removed: bool = False
                                 ) -> Token:
    
    string, inverted, positive = prepare_string(string, inverted=inverted, positive=positive,
                                                 outer_brackets_removed=outer_brackets_removed)
    

    if is_function_call(string):
        return tokenize_function(string, inverted=inverted, positive=positive)
    if string.upper().startswith("SELECT"):

        subquery, params = parametrize_subquery(string, style = "?")
        subquery_obj = SubQuery(subquery, params)

        return TokenSubQuery(subquery_obj)
    string, outermost_tokens = collect_outhermost_placeholders(string) 

    # Determine top‐level operation
    if "||" in string:
        op = "concat"
    elif "+" in string or "-" in string:
        op = "sum"
    elif "*" in string or "/" in string:
        op = "mul"
    else:
        # No operator: plain token
        return Token(string, inverted=inverted, positive=positive)




    if op == "concat":
        parts = string.split("||")
        parts = replace_placeholders(parts, outermost_tokens)
        tokens = [Token(part) for part in parts if part]
        return TokenConcat(items=tokens, inverted=inverted, positive=positive)

    if op == "sum":
        # Normalize unary minus => "+ -"
        string = string.replace("-", "+-")
        parts = string.split("+")
        parts = replace_placeholders(parts, outermost_tokens)
        tokens = []
        for part in parts:
            txt = part.strip()

            is_pos = not txt.startswith("-")
            txt = txt.lstrip("-")
            if not txt:
                continue
            tokens.append(Token(txt, positive=is_pos))
        return TokenSum(items=tokens, inverted=inverted, positive=positive)

    if op == "mul":
        parts = re.split(r'([*/])', string)
        parts = replace_placeholders(parts, outermost_tokens)
        tokens = []
        next_inverted = False
        for part in parts:
            txt = part
            if txt == "*":
                continue
            if txt == "/":
                next_inverted = True
                continue
            if not txt:
                continue
            tokens.append(Token(txt, inverted=next_inverted))
            next_inverted = False
        return TokenMul(items=tokens, inverted=inverted, positive=positive)

def parse_expression(string: str, inverted: bool = False, positive: bool = True,
                     outer_brackets_removed: bool = False
                     ) -> SQLExpression:
    """
    Parses a string expression into a SQLExpression object.
    Handles basic arithmetic operations, function calls, and nested expressions.
    """

    token = outermost_operation_tokenize(string, inverted=inverted, positive=positive,
                                          outer_brackets_removed=outer_brackets_removed)
    return token.resolve()


