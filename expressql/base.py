"""
ExpressQL Base Module - Core SQL expression and condition classes.

This module provides the fundamental building blocks for constructing SQL expressions
and conditions in a Pythonic way. It includes classes for representing SQL values,
columns, arithmetic operations, comparisons, and logical operations.

Key Classes:
    SQLExpression: Represents any SQL expression (column, value, arithmetic, etc.)
    SQLCondition: Represents a SQL condition (comparison or logical operation)
    SQLComparison: Base class for comparison operations (=, <, >, etc.)
    AndCondition, OrCondition, NotCondition: Logical operations on conditions
    Func: Represents SQL function calls

Key Functions:
    col: Create a column expression
    cols: Create multiple column expressions
    num: Create a numeric value expression
    text: Create a text value expression
    where_string: Convert a condition to a WHERE clause string
    get_comparison: Create a comparison from a string operator

Example:
    >>> from expressql.base import col, Func
    >>> age = col("age")
    >>> salary = col("salary")
    >>> condition = (age > 25) & (salary > 40000)
    >>> sql, params = condition.placeholder_pair()
"""

from __future__ import annotations
from typing import Any, Union, List, Iterable, Tuple, Set

from .utils import (parse_number, format_sql_value,Twd, bracket_string_sandwich, ensure_bracketed,
        normalize_args, merge_placeholders
                     )

from .validators import is_number, validate_name, validate_subquery_safe

# Comparison key aliases
less_than_keys = { "lt", "<", "lessthan"}
greater_than_keys = { "gt", ">", "greaterthan"}
equal_to_keys = { "eq", "=", "equals"}
greater_or_equal_keys = { "gte", "ge", ">=", "greaterorequal", "get"}
less_or_equal_keys = { "lte", "le", "<=", "lessorequal", "let"}
not_equal_keys = { "ne", "!=", "notequal"}
between_keys = {"between", "btw", "bet", "within"}
in_keys = {"in", "within", "includes", "among"}
is_null_keys = {"isnull", "null"}
is_not_null_keys = {"isnotnull", "notnull"}
like_keys = {"like", "~"}
not_like_keys = {"notlike", "not like", "!~"}


def apply_signs_and_inverts(s: str, positive: bool, include_sign: bool, include_sign_only_if_negative: bool, invert: bool) -> str:
    """Apply signs and inverts to a string."""
    if invert:
        s = f"1/{s}"
    if include_sign:
        if not positive:
            return f"-{s}"
        elif not include_sign_only_if_negative:
            return f"+{s}"
    return s

def ensure_sql_expression(value: SQLInput) -> SQLExpression:
    """Ensure a value is an SQLExpression, or wrap it as one."""
    if isinstance(value, SQLExpression):
        return value

    return SQLExpression(value, "value", auto_parse_numbers=False)

def ensure_col(column_name: str) -> SQLExpression:
    """Ensure a value is a column name, or wrap it as one."""
    if isinstance(column_name, SQLExpression) and column_name.expression_type == "column":
        return column_name
    return SQLExpression(column_name, "column", auto_parse_numbers=False)

def extract_value(item: SQLInput) -> Any:
    """Extract the value from an SQLExpression or return the item itself."""
    if isinstance(item, SQLExpression):
        return item.true_value()
    return item

def _alias_str(expr: SQLExpression) -> str:
    """Return the alias string for an SQLExpression."""
    if not isinstance(expr, SQLExpression):
        raise TypeError("Expression must be an SQLExpression to get alias.")
    if expr.alias:
        return f" AS {expr.alias.sql_string()}"
    return ""

def _apply_alias(wrapped:str, expr: SQLExpression, *, apply_brackets = True) -> str:
    """Apply an alias to a wrapped string."""
    if not isinstance(expr, SQLExpression):
        raise TypeError("Expression must be an SQLExpression to apply alias.")
    alias_str = expr.alias_str()
    if alias_str:
        if apply_brackets:
            wrapped = ensure_bracketed(wrapped)
        wrapped += alias_str
    return wrapped


VALID_TYPES = {"value", "column", "sum", "mul", "set", "pow", "func", "concat", "query"} 

@normalize_args(skip=0, decompose_string=False)
def add_validtypes(*args):
    VALID_TYPES.update(args)

@normalize_args(skip=0, decompose_string=False)
def remove_validtypes(*args):
    for arg in args:
        if arg in VALID_TYPES:
            VALID_TYPES.remove(arg)

class SQLExpression:
    """Represents an SQL expression, either a literal value, column name, or a more complex structure like sum or product."""
    def __init__(
        self,
        expression_value: Union[str, int, float, bool],
        expression_type: str = "value",
        auto_parse_numbers: bool = True,
        positive: bool = True, *, inverted: bool = False,
        alias: SQLExpression = None,
        skip_validation: bool = False
    ):
        """
        Initialize an SQLExpression instance.

        Args:
            expression_value (Union[str, int, float, bool]): The value of the expression.
            expression_type (str): The type of the expression. Must be one of VALID_TYPES.
            auto_parse_numbers (bool): Whether to automatically parse numbers from strings.
            positive (bool): Whether the expression is positive or negative.
            inverted (bool): Whether the expression is inverted.
        """

        if expression_type not in VALID_TYPES:
            raise ValueError(f"Invalid expression type: {expression_type}. Must be one of ({', '.join(VALID_TYPES)}).")
        #determine expression value
        if expression_type == "value" and auto_parse_numbers:
            expression_value = parse_number(expression_value)
        self.skip_validation = skip_validation
        self.expression_type = expression_type
        self.expression_value = expression_value
        self.positive = positive
        self.inverted = inverted
        self.alias = alias

        
    # --- Properties ---
    @property
    def positive(self) -> bool:
        return self._positive
    @positive.setter
    def positive(self, value: bool) -> None:
        try:
            new_value = bool(value)
            self._positive = new_value
        except ValueError:
            raise ValueError(f"Invalid value for positive: {value}. Must be a boolean.")
    @property
    def negative(self) -> bool:
        return not self._positive
    @negative.setter
    def negative(self, value: bool) -> None:
        try:
            new_value = not bool(value)
            self._positive = new_value
        except ValueError:
            raise ValueError(f"Invalid value for negative: {value}. Must be a boolean.")
    @property
    def expression_value(self) -> Union[str, int, float, bool]:
        return self._expression_value
    @expression_value.setter
    def expression_value(self, value: Union[str, int, float, bool]) -> None:
        if self.expression_type == "column" and not self.skip_validation:
            validate_name(value, allow_dot=True, allow_digit=True)
        self._expression_value = value

    @property
    def alias(self) -> SQLExpression:
        return self._alias
    @alias.setter
    def alias(self, value: SQLExpression) -> None:
        convert_to_expression = False
        if isinstance(value, SQLExpression):
            if value.expression_type != "column":
                raise ValueError("Alias must be a column name.")
            name_to_validate = value.expression_value
        elif isinstance(value, str):
            name_to_validate = value
            convert_to_expression = True
        elif value is None:
            self._alias = None
            return
        else:
            raise TypeError("Alias must be a string or SQLExpression.")    
        #No digit or dot allowed in alias
        if not self.skip_validation:
            validate_name(name_to_validate, allow_dot=False, allow_digit=False)
        if convert_to_expression:
            value = SQLExpression(name_to_validate, "column", auto_parse_numbers=False)
        self._alias = value
    # --- End Properties ---

    # --- Simple Methods ---
    def is_numeric(self) -> bool:
        return is_number(self.expression_value) and self.expression_type == "value"

    def is_text(self) -> bool:
        return isinstance(self.expression_value, str) and self.expression_type == "value"

    def true_value(self) -> Union[str, int, float, bool, Set]:
        if self.expression_type == "column":
            return self.expression_value
        elif self.expression_type == "set":
            if isinstance(self.expression_value, Iterable):
                output_set = {extract_value(x) for x in self.expression_value}
                return output_set
            else:
                raise TypeError("Set expression value must be an iterable.")
        elif self.expression_type == "value":

            if isinstance(self.expression_value, str):
                return self.expression_value
            elif is_number(self.expression_value):
                myvalue = self.expression_value
                mymult = 1 if self.positive else -1
                myvalue *= mymult
                if self.inverted:
                    try:
                        myvalue = 1 / myvalue
                    except ZeroDivisionError:
                        raise ValueError("Cannot invert zero value.")
                return myvalue

            
        self._assert_not_sum_mul("true value")
    
    def sign(self) -> str:
        if self.expression_type == "column":
            return ""
        elif self.expression_type == "value":
            true_value = self.true_value()
            if true_value > 0:
                return "+"
            elif true_value < 0:
                return "-"
            else:
                return ""
        self._assert_not_sum_mul("sign")

    
    def _assert_not_sum_mul(self, context: str = "operation") -> None:
        if self.expression_type in {"sum", "mul"}:
            raise NotImplementedError(f"{self.expression_type.capitalize()} type not implemented yet for {context}.")
    
    #--- End Simple Methods ---


    #-- SQL String Methods ---
    def sql_string(
        self, 
        include_sign: bool = True, 
        include_sign_only_if_negative: bool = True, invert: bool = True,
        include_alias: bool = True):
        if self.expression_type == "column":

            col_name = self.expression_value
            col_name = apply_signs_and_inverts(col_name, self.positive, include_sign, include_sign_only_if_negative, invert and self.inverted)
            output_str = col_name

        elif self.expression_type == "value":
            if self.is_text():
                return f"'{self.expression_value}'"
            true_value = self.true_value()
            true_value_str = format_sql_value(abs(true_value))
            true_value_str = apply_signs_and_inverts(true_value_str, self.positive, include_sign, include_sign_only_if_negative, invert and self.inverted)
            output_str = true_value_str
        elif self.expression_type == "set":
            output_str = f"({', '.join(map(str, self.expression_value))})"
        self._assert_not_sum_mul("SQL string")
        if include_alias:
            output_str += self.alias_str()
        return output_str

    def placeholder_str(self, include_sign = True, include_sign_only_if_negative: bool = True,
                         invert: bool = True, include_alias = True) -> str:
        if self.expression_type == "column":
            return self.sql_string(include_sign=include_sign,
                                      include_sign_only_if_negative=include_sign_only_if_negative,
                                        invert=invert, include_alias=include_alias)
        elif self.expression_type == "value":
            return "?"
        elif self.expression_type == "set":
            return f"({', '.join(['?' for _ in self.expression_value])})"
        self._assert_not_sum_mul("placeholder string")
    def placeholder_pair(self, include_sign = True, include_sign_only_if_negative: bool = True,
                          invert: bool = True, include_alias = True) -> Tuple[str, Any]:

        if self.expression_type == "column":
            return self.placeholder_str(include_sign=include_sign,
                                        include_sign_only_if_negative=include_sign_only_if_negative,
                                        invert=invert, include_alias= include_alias), []
        if self.expression_type == "set":
            pair = self.placeholder_str(), list(self.true_value())
        else:
            pair = self.placeholder_str(), [self.true_value()]
        return pair
    def _placeholder_pair(self, include_sign = True, include_sign_only_if_negative: bool = True,
                          invert: bool = True, include_alias = True) -> Tuple[str, Any]:

        if self.expression_type == "column":
            return self.placeholder_str(include_sign=include_sign,
                                        include_sign_only_if_negative=include_sign_only_if_negative,
                                        invert=invert, include_alias= include_alias), []
        if self.expression_type == "set":
            pair = self.placeholder_str(), list(self.true_value())
        else:
            pair = self.placeholder_str(), [self.true_value()]
        return pair
    #-- End SQL String Methods ---

    #--- Expression Methods ---

    def flatten(self, *args, **kwargs) -> List[SQLExpression]:
        return [self]
    def flattened_expression(self, *args, **kwargs) -> SQLExpression:
        return self
    
    @staticmethod
    def ensure_expression(value: SQLInput) -> SQLExpression:
        return ensure_sql_expression(value)
    def copy(self) -> SQLExpression:
        """Create a copy of the SQLExpression."""

        return SQLExpression(
            expression_value=self.expression_value,
            expression_type=self.expression_type,
            auto_parse_numbers=False,
            positive=self.positive,
            inverted=self.inverted,
            alias=self.alias,
        )
    def copy_with(self, **kwargs) -> SQLExpression:
        """Copy with optional changes."""
        return SQLExpression(
            expression_value=kwargs.get("expression_value", self.expression_value),
            expression_type=kwargs.get("expression_type", self.expression_type),
            auto_parse_numbers=kwargs.get("auto_parse_numbers", False),
            positive=kwargs.get("positive", self.positive),
            inverted=kwargs.get("inverted", self.inverted),
            alias=kwargs.get("alias", self.alias),
            skip_validation=kwargs.get("skip_validation", self.skip_validation),
        )
    @staticmethod
    def ensure_expressions(values: Iterable[SQLInput]) -> List[SQLExpression]:
        """Ensure all values are SQLExpressions."""
        return [SQLExpression.ensure_expression(value) for value in values]

    def change_sign(self) -> None:
        self.positive = not self.positive

    def additive_opposite(self) -> SQLExpression:
        """Return the additive opposite of the expression."""
        return self.copy_with(positive=not self.positive)

    def multiplicative_opposite(self) -> SQLExpression:
        """Return the multiplicative opposite of the expression."""
        return self.copy_with(inverted=not self.inverted)

    def is_column_expression(self) -> bool:
        return self.expression_type == "column"

    #--- End Expression Methods ---

    # --- Comparison Operators ---

    def _compare(self, comparator_class, other: SQLInput) -> SQLCondition:
        return SQLCondition(self, comparator_class(SQLExpression.ensure_expression(other)))

    def __eq__(self, other: SQLInput) -> SQLCondition:
        # Handle None comparison by converting to IS NULL
        if other is None:
            return self._is_null()
        return self._compare(EqualTo, other)

    def __ne__(self, other: SQLInput) -> SQLCondition:
        # Handle None comparison by converting to IS NOT NULL
        if other is None:
            return self._is_not_null()
        return self._compare(NotEqualTo, other)

    def __lt__(self, other: SQLInput) -> SQLCondition:
        return self._compare(LessThan, other)

    def __le__(self, other: SQLInput) -> SQLCondition:
        return self._compare(LessOrEqualThan, other)

    def __gt__(self, other: SQLInput) -> SQLCondition:
        return self._compare(GreaterThan, other)

    def __ge__(self, other: SQLInput) -> SQLCondition:
        return self._compare(GreaterOrEqualThan, other)
    
    # --- End Comparison Operators ---

    # --- Arithmetic Operators ---

    def __add__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionSum([self, SQLExpression.ensure_expression(other)])

    def __radd__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionSum([SQLExpression.ensure_expression(other), self])

    def __neg__(self) -> SQLExpression:
        return self.copy_with(positive=not self.positive)

    def __sub__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionSum([self, -SQLExpression.ensure_expression(other)])

    def __rsub__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionSum([SQLExpression.ensure_expression(other), -self])

    def __mul__(self, other: SQLInput) -> SQLExpression:

        return SQLExpressionProduct([self, SQLExpression.ensure_expression(other)])

    def __rmul__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionProduct([SQLExpression.ensure_expression(other), self])

    def __truediv__(self, other: SQLInput) -> SQLExpression:
        other_expr = SQLExpression.ensure_expression(other)
        inverted_other = other_expr.copy()
        inverted_other.inverted = not inverted_other.inverted
        return SQLExpressionProduct([self, inverted_other])

    def __rtruediv__(self, other: SQLInput) -> SQLExpression:
        inverted_self = self.copy()
        inverted_self.inverted = not inverted_self.inverted
        return SQLExpressionProduct([SQLExpression.ensure_expression(other), inverted_self])
    
    def __pow__(self, exponent: SQLInput) -> SQLExpression:
        return SQLExpressionPower(self, SQLExpression.ensure_expression(exponent))
    
    def __abs__(self) -> SQLExpression:
        return Func("ABS", self)
    # --- End Arithmetic Operators ---

    # --- SQL Condition Methods ---

    def between(self, left: SQLInput, right: SQLInput) -> SQLCondition:
        left_expr = SQLExpression.ensure_expression(left)
        right_expr = SQLExpression.ensure_expression(right)
        return SQLCondition(self, Between(left_expr, right_expr))

    def _is_null(self) -> SQLCondition:
        return SQLCondition(self, IsNull())

    def _is_not_null(self) -> SQLCondition:
        return SQLCondition(self, IsNotNull())

    # Both property and callable alias
    is_null = property(_is_null)
    is_not_null = property(_is_not_null)

    # Method alias to support calling
    is_null = _is_null
    is_not_null = _is_not_null
    
    def is_in(self, values: Iterable) -> SQLCondition:
        if isinstance(values, SQLExpression):
            if values.expression_type in {"set", "query"}:
                set_expr_ = values
                #handle query in In.__new__
            return SQLCondition(self, In(set_expr_))
        elif isinstance(values, Iterable) and not isinstance(values, str):
            set_expr_ = set_expr(values)
            return SQLCondition(self, In(set_expr_))
        else:
            raise TypeError("In operator only accepts SQLExpression or iterable.")
    IN = is_in
    
    def is_in_subquery(self, subquery: str, params:List = None) -> SQLCondition:
        params = params or []
        return SQLCondition(self, InSubquery(subquery, params))
    IN_subquery = is_in_subquery
    def not_in_subquery(self, subquery: str, params:List = None) -> SQLCondition:
        params = params or []
        return SQLCondition(self, NotInSubquery(subquery, params))
    NOT_IN_subquery = not_in_subquery
    NOTIN_subquery = not_in_subquery
    def is_not_in(self, values: Iterable) -> SQLCondition:
        if isinstance(values, SQLExpression):
            if values.expression_type in {"set", "query"}:
                set_expr_ = values
                #handle query in In.__new__
            return SQLCondition(self, NotIn(set_expr_))
        elif isinstance(values, Iterable) and not isinstance(values, str):
            set_expr_ = set_expr(values)
            return SQLCondition(self, NotIn(set_expr_))
        else:
            raise TypeError("NotIn operator only accepts SQLExpression or iterable.")
    NOTIN = is_not_in
    NOT_IN = is_not_in

    
    def __or__(self, other: SQLInput) -> SQLExpression:
        return SQLExpressionConcat([self, SQLExpression.ensure_expression(other)])

    def like(self, pattern: SQLInput) -> SQLCondition:
        return SQLCondition(self, Like(SQLExpression.ensure_expression(pattern)))

    def not_like(self, pattern: SQLInput) -> SQLCondition:
        return SQLCondition(self, NotLike(SQLExpression.ensure_expression(pattern)))


    
    def startswith(self, pattern: SQLInput) -> SQLCondition:
        return SQLCondition(self, Like(SQLExpression.ensure_expression(pattern) + "%"))

    def AS(self, alias: Union[SQLExpression, str] = None):
        """Set an alias for the expression."""
        if isinstance(alias, str):
            alias = SQLExpression(alias, "column")
        elif isinstance(alias, SQLExpression):
            if alias.expression_type != "column":
                raise ValueError("Alias must be a column name.")
        elif alias is None:
            pass
        else:
            raise TypeError("Alias must be a string or SQLExpression.")
        copied = self.copy_with(alias=alias)
        return copied
        
    set_alias = AS
    aliased = AS
    As = AS

    def alias_str(self) -> str:
        """Return the alias string for the expression."""
        return _alias_str(self)
    
    #--- End SQL Condition Methods ---

    # --- Python Methods ---

    def __getattr__(self, name):
        if name.isupper():
            def dynamic_func(*args, **kwargs):
                return Func(name, self, *args, **kwargs)
            return dynamic_func
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def __str__(self) -> str:
        if self.expression_type == "column":
            return f"Col({self.expression_value})"
        elif self.expression_type == "value":
            if isinstance(self.expression_value, str):
                return f"Text('{self.expression_value}')"
            else:
                return f'Num({str(self.true_value())})'
        elif self.expression_type == "set":
            return f"Set({', '.join(map(str, self.expression_value))})"
        self._assert_not_sum_mul("string representation")
    def __repr__(self) -> str:
        return f"SQLExpression({self.expression_value!r}, {self.expression_type!r}, positive={self.positive}), inverted={self.inverted})"
    



SQLExpression.isin = SQLExpression.is_in
SQLExpression.notin = SQLExpression.is_not_in    

SQLInput = Union[SQLExpression, str, int, float]

class SubQuery(SQLExpression):
    """Represents a subquery in SQL."""
    def __init__(self, placeholder_str_: str, parameters: List[Any], alias = None, skip_validation: bool = False):
        self.placeholder_str_ = placeholder_str_
        self.parameters = parameters
        if not skip_validation:
            validate_subquery_safe(placeholder_str_)
            if alias is not None:
                validate_name(alias, allow_dot=False, allow_digit=False)
        super().__init__(None, expression_type="query", auto_parse_numbers=False, skip_validation=True, alias=alias)

        self.skip_validation = skip_validation
        
    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        return self.placeholder_str_, self.parameters
    def sql_string(self, include_sign = True, include_sign_only_if_negative = True,
                    invert = True, include_alias = True) -> str:

        if not self.placeholder_str_:
            raise ValueError("Subquery placeholder string is empty.")
        fragments = self.placeholder_str_.split("?")
        first = fragments[0]

        for i in range(len(fragments) - 1):

            value = self.parameters[i]
            true_value = extract_value(value)
            formatted_value = format_sql_value(true_value)
            first += formatted_value + fragments[i + 1]

        if include_alias:
            first = _apply_alias(first, self, apply_brackets=True) 
        return first
    def placeholder_str(self, *args, include_alias = True, **kwargs) -> str:
        if not self.placeholder_str_:
            raise ValueError("Subquery placeholder string is empty.")
        output_str = self.placeholder_str_
        if include_alias:
            output_str = _apply_alias(output_str, self, apply_brackets=True)
        return output_str

    def __str__(self) -> str:
        return f"SubQuery({self.placeholder_str_}, {self.parameters})"
    def __repr__(self) -> str:
        return f"SubQuery({self.placeholder_str_!r}, {self.parameters!r})"    
    

class SQLZero(SQLExpression):
    def __init__(self, expression_type: str = "value", *args, **kwargs):
        super().__init__(0, expression_type=expression_type)




class SQLArithmeticOperation(SQLExpression):
    symbol_to_type = {"*": "mul", "+": "sum", "||": "concat"}
    symbol : str = None
    neutral : SQLExpression = None
    operation_name = None
    def __new__(cls, expressions: List[SQLExpression], positive: bool = True, inverted: bool = False, *, alias=None, bruteforce = False):

        if not isinstance(expressions, list):
            expressions = [SQLExpression.ensure_expression(expressions)]

        symbol = cls.symbol
        expression_type = cls.symbol_to_type.get(symbol, "sum")
        neutral = cls.neutral
        if not expressions:
            return cls.neutral
        if len(expressions) == 1:
            if isinstance(expressions[0], List):
                expressions = expressions[0]
            elif isinstance(expressions[0], SQLExpression):
                return SQLExpression.ensure_expression(expressions[0])
            
        expressions = SQLExpression.ensure_expressions(expressions)
        expressions = cls._flatten_expressions(expressions, expression_type)
        if bruteforce or cls.operation_name == "Concat":
            instance = super().__new__(cls)
            instance._precomputed_expressions = expressions
            return instance
        # --- START folding constants early ---
        value_expressions = []
        set_expressions = []
        others = []

        for expr in expressions:
            if expr.expression_type == "value":
                value_expressions.append(expr)
            elif expr.expression_type == "set":
                set_expressions.append(expr)
            else:
                others.append(expr)

        # Merge sets if applicable (only for +)
        if symbol == "+" and set_expressions:
            total_set = set()
            for s_expr in set_expressions:
                total_set.update(s_expr.true_value())
            set_expressions = [set_expr(total_set)] if total_set else []

 # Merge numeric constants
        datatypes = {type(x.expression_value) for x in value_expressions}
        value_type = None
        if datatypes:
            if str in datatypes:
                if symbol == "*":
                    raise TypeError("Cannot multiply strings.")
                if int in datatypes or float in datatypes:
                    raise TypeError("Cannot mix strings and numbers in a sum.")
                value_type = "text"
            else:
                value_type = "number"

        if value_type == "text":
            total_value = ""
        elif value_type == "number":
            total_value = 1 if symbol == "*" else 0
        else:
            total_value = neutral.true_value()

        op_dict = {"+": lambda x, y: x + y, "*": lambda x, y: x * y, "||": lambda x, y: str(x) + str(y)}
        if value_type:
            for v_expr in value_expressions:
                total_value = op_dict[symbol](total_value, v_expr.true_value())

            if total_value != (1 if symbol == "*" else 0):
                folded_value = SQLExpression(total_value, expression_type="value", auto_parse_numbers=False)
                value_expressions = [folded_value]
            else:
                value_expressions = []

        folded_expressions = value_expressions + set_expressions + others
        # --- END folding constants early ---

        # Special return cases
        if not folded_expressions:
            return neutral
        if len(folded_expressions) == 1:
            return folded_expressions[0]

        # Real object construction

        instance = super().__new__(cls)
        instance._precomputed_expressions = folded_expressions
        return instance

    def __init__(self, expressions: List[SQLExpression], positive: bool = True, inverted: bool = False, *, alias = None, bruteforce=False):
        symbol = self.__class__.symbol
        # Expressions were folded in __new__
        flattened = getattr(self, '_precomputed_expressions', expressions)
        self.symbol = symbol
        if bruteforce:
            self.expressions = flattened
            super().__init__(None, expression_type=self.symbol_to_type[symbol], auto_parse_numbers=False, positive=positive, inverted=inverted, alias=alias)
            return

        self.expressions = flattened
        super().__init__(None, expression_type=self.symbol_to_type[symbol], auto_parse_numbers=False, positive=positive, inverted=inverted, alias=alias)
    @staticmethod
    def _flatten_expressions(expressions: List[SQLExpression], expression_type = "sum") -> List[SQLExpression]:
        flattened = []
        for expr in expressions:
            if expr.expression_type == expression_type:
                flattened.extend(expr.flatten())
            else:
                flattened.append(expr)
        return flattened
    def flatten(self, *, update_self = False) -> List[SQLExpression]:
        flattened = self._flatten_expressions(self.expressions)
        if update_self:
            self.expressions = flattened
        return flattened
    def flattened_expression(self) -> SQLExpression:
        raise NotImplementedError("Flattened expression not implemented for SQLArithmeticOperation.")
    
    def is_numeric(self) -> bool:
        if self.expression_value is None:
            return False
        if is_number(self.expression_value):
            return True
        return False 
    
    def sql_string(self, *args, **kwargs) -> None:
        raise NotImplementedError("SQL string not implemented for SQLArithmeticOperation.")

    def placeholder_str(self, include_sign = True, include_sign_only_if_negative: bool = True,
                         invert: bool = True, include_alias = True) -> str:
        if not self.expressions:
            return "0"
        first_expr = self.expressions[0]
        fragments = [first_expr.placeholder_str(include_sign=not first_expr.positive,
                                                include_alias = False)]
        fragments += [expr.placeholder_str(include_alias=False) for expr in self.expressions[1:]]
        joined = self.symbol.join(fragments)
        wrapped = bracket_string_sandwich(joined) if len(self.expressions) > 1 else joined
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert)
        if include_alias:
            wrapped = _apply_alias(wrapped, self, apply_brackets=True)
        return wrapped

    def placeholder_pair(self, include_sign = True, include_sign_only_if_negative: bool = True, invert: bool = True,
                         include_alias = True) -> Tuple[str, List[Any]]:
        if not self.expressions:
            return "0", []
        first_expr = self.expressions[0]


        first, parameters = first_expr.placeholder_pair(include_alias=False)
        fragments = [first]

        for expr in self.expressions[1:]:
            placeholder, params = expr.placeholder_pair(include_alias=False)
            fragments.append(placeholder)
            merge_placeholders(parameters, params)

        joined = self.symbol.join(fragments)
        wrapped = bracket_string_sandwich(joined) if len(self.expressions) > 1 else joined
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert)
        if include_alias:
            wrapped = _apply_alias(wrapped, self, apply_brackets=True)
        return wrapped, parameters
    def __str__(self):
        name = self.__class__.operation_name
        return f"{name}({self.expressions})"

    def is_column_expression(self):
        return all(expr.is_column_expression() for expr in self.expressions)

class SQLExpressionSum(SQLArithmeticOperation):
    symbol = "+"
    neutral = SQLZero()
    operation_name = "Sum"
    def sql_string(self, include_sign: bool = True, include_sign_only_if_negative: bool = True,
                   *, invert:bool = False, include_alias = True) -> str:
        if not self.expressions:
            return "0"
        fragments = []
        first = self.expressions[0]
        fragments.append(first.sql_string(include_sign=not first.positive,
                                          include_alias=False))
        for expr in self.expressions[1:]:
            fragments.append(expr.sql_string(include_sign=True,
                                              include_sign_only_if_negative=False,
                                              include_alias=False))
        joined = "".join(fragments)

        wrapped = bracket_string_sandwich(joined) if len(self.expressions) > 1 else joined
        if self.inverted and invert:
            wrapped = '1/' + wrapped
        if not include_sign:
            pass
        elif self.positive:
            if not include_sign_only_if_negative:
                wrapped = f"+{wrapped}"
        else:
            wrapped = f"-{wrapped}"
        if include_alias:
            wrapped = _apply_alias(wrapped, self, apply_brackets=True)
        return wrapped
        
    def placeholder_pair(self, include_sign = True, include_sign_only_if_negative: bool = True,
                          invert: bool = True, include_alias = True) -> Tuple[str, List[Any]]:
        if not self.expressions:
            return "0", []
        first_expr = self.expressions[0]
        first, collected_inserts = first_expr.placeholder_pair(include_sign=not first_expr.positive,
                                                                invert = True,
                                                                include_alias=False)
        fragments = [first]
        for expr in self.expressions[1:]:
            placeholder, params = expr.placeholder_pair(include_sign=True,
                                                         include_sign_only_if_negative=False, invert = True,
                                                         include_alias=False)
            fragments.append(placeholder)
            merge_placeholders(collected_inserts, params)
        joined = "".join(fragments)
        wrapped = bracket_string_sandwich(joined) if len(self.expressions) > 1 else joined
        if self.inverted and invert:
            wrapped = '1/' + wrapped
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert and self.inverted)
        if include_alias:
            wrapped = _apply_alias(wrapped, self, apply_brackets=True)
        return wrapped, collected_inserts
    def flattened_expression(self) -> SQLExpression:
        flat = self.flatten(update_self=False)
        if len(flat) == 1:
            return flat[0]
        # Bruteforce: do not simplify further after flattening
        return SQLExpressionSum(flat, positive=self.positive, inverted=self.inverted, bruteforce=True)
    @classmethod
    @normalize_args(skip = 1)
    def gather_vals(cls, *args: SQLInput) -> SQLExpression:
        expressions = [SQLExpression.ensure_expression(arg) for arg in args]
        return cls(expressions)

    @classmethod
    @normalize_args(skip = 1)
    def gather_cols(cls, *args: str) -> SQLExpression:
        expressions = [SQLExpression(arg, "column") for arg in args]
        return cls(expressions)
    
    @classmethod
    @normalize_args(skip = 1)
    def gobble(cls, *args: SQLInput) -> SQLExpression:
        """Gathers values into a SQLExpressionSum."""
        return cls.gather_vals(*args)
    

    def copy(self) -> SQLExpression:
        """Create a copy of the SQLExpression."""
        return SQLExpressionSum(
            [expr.copy() for expr in self.expressions],
            positive=self.positive,
            inverted=self.inverted,
            bruteforce=True
        )
    def copy_with(self, **kwargs) -> SQLExpression:
        """Copy with optional changes."""
        return SQLExpressionSum(
            [expr.copy() for expr in self.expressions],
            positive=kwargs.get("positive", self.positive),
            inverted=kwargs.get("inverted", self.inverted),
            bruteforce=True,
            alias = kwargs.get("alias", self.alias)
        )

def ensure_brackets(s:str):
    """Ensure the string is wrapped in brackets."""
    if not s.startswith("(") or not s.endswith(")"):
        return bracket_string_sandwich(s)
    return s    

class SQLExpressionProduct(SQLArithmeticOperation):
    symbol = "*"
    neutral = SQLExpression(1, expression_type="value")
    operation_name = "Product"
    def sql_string(self, include_sign: bool = True, include_sign_only_if_negative: bool = True,
                   *, invert:bool = False, include_alias = True) -> str:
        if not self.expressions:
            return "0"
        pos = self.positive
        first = self.expressions[0]
        numerator = []
        denominator = []
        first_str = first.sql_string(include_sign=not first.positive, include_alias=False)
        if first.inverted:
            denominator.append(first_str)
        else:
            numerator.append(first_str)
        pos = pos == first.positive

        for expr in self.expressions[1:]:
            if expr.inverted:
                denominator.append(expr.sql_string(include_sign=False,
                                                    invert = False,
                                                    include_alias=False))
            else:
                numerator.append(expr.sql_string(include_sign=False,
                                                  invert = False,
                                                  include_alias=False))
            if expr.expression_type == "column":
                pos = pos == expr.positive
            elif expr.expression_type == "value":
                if expr.true_value() < 0:
                    pos = not pos
        if self.inverted:
            numerator, denominator = denominator, numerator
        numerator_str = "*".join(numerator)
        denominator_str = "*".join(denominator)
        if not numerator:
            wrapped_numerator = "1"
        elif len(numerator) > 1:
            wrapped_numerator = ensure_brackets(numerator_str)
        else:
            wrapped_numerator = numerator_str
        
        if not denominator:
            wrapped_denominator = ""
        else:
            wrapped_denominator = bracket_string_sandwich(denominator_str) if len(denominator) > 1 else denominator_str
            wrapped_denominator = "/" + wrapped_denominator

        wrapped = wrapped_numerator + wrapped_denominator
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert = False)
        if include_alias:
            wrapped += self.alias_str()
        return wrapped
    def placeholder_pair(self, include_sign = True, include_sign_only_if_negative: bool = True,
                          invert: bool = True, include_alias = True
                          ) -> Tuple[str, List[Any]]:

        if not self.expressions:
            return "0", []
        first_expr = self.expressions[0]
        first, collected_inserts = first_expr.placeholder_pair(include_sign=not first_expr.positive,
                                                                invert = False,
                                                                include_alias=False)
        numerator = []
        denominator = []
        if first_expr.inverted:
            denominator.append(first)
        else:
            numerator.append(first)

        pos = self.positive == first_expr.positive
        for expr in self.expressions[1:]:
            placeholder, params = expr.placeholder_pair(include_sign=False,
                                                        invert = False,
                                                        include_alias=False)
            if expr.inverted:
                denominator.append(placeholder)
            else:
                numerator.append(placeholder)
            merge_placeholders(collected_inserts, params)
            if expr.expression_type == "column":
                pos = pos == expr.positive
            elif expr.expression_type == "value":
                if expr.true_value() < 0:
                    pos = not pos
        if self.inverted:
            numerator, denominator = denominator, numerator
        numerator_str = "*".join(numerator)
        denominator_str = "*".join(denominator)
        if not numerator:
            wrapped_numerator = "1"
        elif len(numerator) > 1:
            wrapped_numerator = ensure_brackets(numerator_str)
        else:
            wrapped_numerator = numerator_str
        
        if not denominator:
            wrapped_denominator = ""
        else:
            wrapped_denominator = bracket_string_sandwich(denominator_str) if len(denominator) > 1 else denominator_str
            wrapped_denominator = "/" + wrapped_denominator

        wrapped = wrapped_numerator + wrapped_denominator
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert = False)
        if include_alias:   
            wrapped += self.alias_str()
        return wrapped, collected_inserts
    def flattened_expression(self) -> SQLExpression:
        flat = self.flatten(update_self=False)
        if len(flat) == 1:
            return flat[0]
        # Bruteforce: do not simplify further after flattening
        return SQLExpressionProduct(flat, positive=self.positive, inverted=self.inverted, bruteforce=True)
    @classmethod
    @normalize_args(skip = 1)
    def gather_vals(cls, *args: SQLInput) -> SQLExpression:
        expressions = [SQLExpression.ensure_expression(arg) for arg in args]
        return SQLExpressionProduct(expressions)
    @classmethod
    @normalize_args(skip = 1)
    def gather_cols(cls, *args: str) -> SQLExpression:
        expressions = [SQLExpression(arg, "column") for arg in args]
        return SQLExpressionProduct(expressions)
    @classmethod
    @normalize_args(skip = 1)
    def gobble(cls, *args: SQLInput) -> SQLExpression:
        """Gathers values into a SQLExpressionSum."""
        return SQLExpressionProduct.gather_vals(*args)
    def copy(self) -> SQLExpression:
        """Create a copy of the SQLExpression."""
        return SQLExpressionProduct(
            [expr.copy() for expr in self.expressions],
            positive=self.positive,
            inverted=self.inverted,
            bruteforce=True
        )
    def copy_with(self, **kwargs) -> SQLExpression:
        """Copy with optional changes."""
        return SQLExpressionProduct(
            [expr.copy() for expr in self.expressions],
            positive=kwargs.get("positive", self.positive),
            inverted=kwargs.get("inverted", self.inverted),
            bruteforce=True,
            alias = kwargs.get("alias", self.alias)
        )

class SQLExpressionConcat(SQLArithmeticOperation):
    symbol = "||"
    neutral = SQLExpression("", expression_type="value")  # Neutral for string concatenation
    operation_name = "Concat"

    def sql_string(self, include_sign: bool = False, include_sign_only_if_negative: bool = False,
                   *, invert: bool = False, include_alias = True) -> str:
        if not self.expressions:
            return "''"

        fragments = [expr.sql_string(include_sign=False, include_alias=False) for expr in self.expressions]
        joined = " || ".join(fragments)
        joined = f"({joined})" if len(self.expressions) > 1 else joined
        if include_alias:
            joined = _apply_alias(joined, self, apply_brackets=True)
        return joined

    def placeholder_str(self, *args, include_alias = True, **kwatgs) -> str:
        if not self.expressions:
            return "''"
        fragments = [expr.placeholder_str(include_alias=False) for expr in self.expressions]
        joined = " || ".join(fragments)
        if len(self.expressions) > 1:
            joined = bracket_string_sandwich(joined)
        if include_alias:
            joined = _apply_alias(joined, self, apply_brackets=True)
        return joined

    def placeholder_pair(self, *args, include_alias = True, **kwargs) -> Tuple[str, List[Any]]:
        fragments, params = [], []
        WHITELIST_INLINE = {" ", "", "-", "/", ":"}  # You can expand as needed
        for expr in self.expressions:
            if expr.expression_type == "value" and isinstance(expr.expression_value, str):
                val = expr.expression_value
                if val in WHITELIST_INLINE:
                    fragments.append(f"'{val}'")  # inline directly
                    continue
            ph, vals = expr.placeholder_pair(include_alias=False)
            fragments.append(ph)
            merge_placeholders(params, vals)
        joined = " || ".join(fragments)
        if len(self.expressions) > 1:
            joined = bracket_string_sandwich(joined)
        if include_alias:
            joined = _apply_alias(joined, self, apply_brackets=True)
        return joined, params

    def copy(self) -> SQLExpression:
        return SQLExpressionConcat(
            [expr.copy() for expr in self.expressions],
            positive=self.positive,
            inverted=self.inverted,
            bruteforce=True,
            alias=self.alias
        )

    def copy_with(self, **kwargs) -> SQLExpression:
        return SQLExpressionConcat(
            [expr.copy() for expr in self.expressions],
            positive=kwargs.get("positive", self.positive),
            inverted=kwargs.get("inverted", self.inverted),
            bruteforce=True,
            alias=kwargs.get("alias", self.alias)
        )
    @normalize_args(skip = 1)
    def add_items(self, *args: SQLInput) -> None:
        """Add items to the concatenation."""

        args = SQLExpression.ensure_expressions(args)
        self.expressions.extend(args)


class SQLExpressionPower(SQLExpression):
    def __new__(cls, base: SQLExpression, exponent: SQLInput, *, positive: bool = True, inverted: bool = False, alias=None):
        base = SQLExpression.ensure_expression(base)
        exponent = SQLExpression.ensure_expression(exponent)

        if base.is_numeric() and base.true_value() == 0 and exponent.is_numeric() and exponent.true_value() > 0:
            return num(0)
        if exponent.is_numeric():
            exp_val = exponent.true_value()
            if exp_val == 0:
                return num(1)
            if exp_val == 1:
                return base
        return super().__new__(cls)
    def __init__(self, base: SQLExpression, exponent: SQLInput, *, positive: bool = True, inverted: bool = False, alias=None):
        self.base = SQLExpression.ensure_expression(base)
        self.exponent = SQLExpression.ensure_expression(exponent)
        super().__init__(None, expression_type="pow", auto_parse_numbers=False, positive=positive, inverted=inverted, alias=alias)

    def sql_string(self, include_sign: bool = True, include_sign_only_if_negative: bool = True,
                    invert=True, include_alias = True) -> str:
        base_str = self.base.sql_string(include_sign=True, include_sign_only_if_negative=True,
                                         invert=True, include_alias=False)
        if self.inverted and invert:
            new_exp = self.exponent.copy()
            new_exp.positive = not new_exp.positive
            exp_str = new_exp.sql_string(include_sign=True, include_sign_only_if_negative=True, invert=True, include_alias=False)
        else:
            exp_str = self.exponent.sql_string(include_sign=True, include_sign_only_if_negative=True, invert=True, include_alias=False)
        
        full_str = f"POWER({base_str}, {exp_str})"
        full_str = apply_signs_and_inverts(full_str, self.positive, include_sign, include_sign_only_if_negative, invert = False)
        
        if include_alias:
            full_str += self.alias_str()
        return full_str

    def placeholder_str(self, include_sign = True, include_sign_only_if_negative = True,
                         invert = True, include_alias = True) -> str:
        if self.inverted and invert:
            new_exp = self.exponent.copy()
            new_exp.inverted = not new_exp.inverted
            exp_str = new_exp.placeholder_str(include_alias=False)
        else:
            exp_str = self.exponent.placeholder_str(include_alias=False)
        base_str = self.base.placeholder_str(include_alias=False)
        wrapped = f"POWER({base_str}, {exp_str})"
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert = False)
        if include_alias:
            wrapped += self.alias_str()
        return wrapped

    def placeholder_pair(self, include_sign = True, include_sign_only_if_negative = True,
                          invert = True, include_alias = True) -> Tuple[str, List[Any]]:
        base_placeholder, base_params = self.base.placeholder_pair()
        exp_placeholder, exp_params = self.exponent.placeholder_pair()
        wrapped =  f"POWER({base_placeholder}, {exp_placeholder})"
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert = self.inverted and invert)
        if include_alias:
            wrapped += self.alias_str()
        return wrapped, [*base_params, *exp_params]

    def flatten(self, *args, **kwargs) -> List[SQLExpression]:
        return [self]

    def flattened_expression(self) -> SQLExpression:
        return self

    def copy(self) -> SQLExpression:
        return SQLExpressionPower(self.base.copy(), self.exponent.copy(),
                                 positive=self.positive, inverted=self.inverted)

    def __repr__(self) -> str:
        return f"SQLExpressionPower({self.base}, {self.exponent})"
    
    def __str__(self):
        return f"POWER({self.base}, {self.exponent})"
    
    def is_column_expression(self):
        return self.base.is_column_expression() and self.exponent.is_column_expression()



class Func(SQLExpression):
    def __init__(self, func_name: str, *args: SQLInput, tag: str = None, positive: bool = True, inverted: bool = False, alias=None):
        if not isinstance(func_name, str) or not func_name.strip():
            raise ValueError("Function name must be a non-empty string.")
        if " " in func_name:
            raise ValueError("Function name must not contain spaces.")
        if ";" in func_name or "--" in func_name:
            raise ValueError("Function name contains potentially unsafe characters.")
        self.func_name = func_name.upper()
        self.args = SQLExpression.ensure_expressions(args) if args else []
        self.tag = tag
        super().__init__(None, expression_type="func", auto_parse_numbers=False, positive=positive, inverted=inverted, alias=alias)

    def sql_string(self, include_sign: bool = True, include_sign_only_if_negative: bool = True,
                    invert = True, include_alias = True) -> str:
        args_sql = ", ".join(arg.sql_string(include_sign=True,
                                            include_sign_only_if_negative=True,
                                            include_alias= False) for arg in self.args) if self.args else ""
        if self.tag:
            args_sql = f"{self.tag} {args_sql}"
        wrapped = f"{self.func_name}({args_sql})"
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign=include_sign, include_sign_only_if_negative=include_sign_only_if_negative, invert= invert and self.inverted)
        if include_alias:
            wrapped += self.alias_str()
        return wrapped

    def placeholder_str(self, include_sign: bool = True,
                         include_sign_only_if_negative: bool = True, invert = True,
                         include_alias = True
                         ) -> str:
        args_placeholder = ", ".join(arg.placeholder_str(include_sign=True,
                                                        include_sign_only_if_negative=True,
                                                        include_alias=False) for arg in self.args)
        if self.tag:
            args_placeholder = f"{self.tag} {args_placeholder}"
        s = f"{self.func_name}({args_placeholder})"
        s = apply_signs_and_inverts(s, self.positive, include_sign, include_sign_only_if_negative, invert= invert and self.inverted)
        if include_alias:
            s += self.alias_str()
        return s

    def placeholder_pair(self, include_sign=True,
                          include_sign_only_if_negative=True, invert=True,
                          include_alias=True
                          ) -> Tuple[str, List[Any]]:
        fragments = []
        params = []
        for arg in self.args:
            placeholder, param = arg.placeholder_pair(include_alias=False)
            fragments.append(placeholder)
            param = merge_placeholders(params, param)
        args_sql = ", ".join(fragments)
        if self.tag:
            args_sql = f"{self.tag} {args_sql}"
        wrapped = f"{self.func_name}({args_sql})"
        wrapped = apply_signs_and_inverts(wrapped, self.positive, include_sign, include_sign_only_if_negative, invert=invert and self.inverted)
        if include_alias:
            wrapped += self.alias_str()
        return wrapped, params

    def flatten(self, *args, **kwargs) -> List[SQLExpression]:
        return [self]

    def flattened_expression(self) -> SQLExpression:
        return self

    def copy(self) -> SQLExpression:
        return Func(self.func_name, *[arg.copy() for arg in self.args], tag=self.tag,
                    positive=self.positive, inverted=self.inverted, alias=self.alias)
    
    def copy_with(self, func_name: str = None, args: List[SQLExpression] = None,
                   tag: str = None, positive: bool = None,
                     inverted: bool = None, alias: str = None, arguments : List = None) -> SQLExpression:
        return Func(
            func_name or self.func_name,
            *[arg.copy() for arg in args] if args else [arg.copy() for arg in self.args] if arguments is None else list(arguments),
            tag=tag or self.tag,
            positive=positive if positive is not None else self.positive,
            inverted=inverted if inverted is not None else self.inverted,
            alias=alias or self.alias
        )
    
    def is_column_expression(self):
        return all(arg.is_column_expression() for arg in self.args)
    @normalize_args(skip = 1)
    def add_args(self, *args: SQLInput) -> None:
        """Add arguments to the function."""

        for arg in args:
            self.args.append(SQLExpression.ensure_expression(arg))

    def clear(self):
        """Clear all arguments."""
        self.args.clear()

    


class SQLComparison:
    def __init__(self, comparator: str, expressions: List[SQLExpression]):
        self.expressions = expressions
        self.comparator = comparator
        self.attatchable = False
    def sql_string(self) -> str:

        if not self.expressions:
            raise ValueError("No expressions provided for SQL comparison.")
        return f"{self.comparator} {self.expressions[0].sql_string(include_sign=True, include_sign_only_if_negative=True)}"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        if not self.expressions:
            raise ValueError("No expressions provided for SQL comparison.")
        
        expr_placeholder, expr_params = self.expressions[0].placeholder_pair()

        sql = f"{self.comparator} {expr_placeholder}"

        parameters = []
        if isinstance(expr_params, list):
            parameters.extend(expr_params)
        else:
            parameters.append(expr_params)

        return sql, parameters

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(map(str, self.expressions))})"
    
    def __neg__(self) -> SQLComparison:
        negation_class = negation_dict.get(type(self), None)
        if negation_class:
            return negation_class(*self.expressions)
        raise NotImplementedError(f"Negation not implemented for {self.__class__.__name__}.")
    def copy(self) -> SQLComparison:
        return SQLComparison(self.comparator, [expr.copy() for expr in self.expressions])


class LessThan(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('<', [expression])
        self.attatchable = True
    


class GreaterThan(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('>', [expression])
        self.attatchable = True

class EqualTo(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('=', [expression])
        self.attatchable = True

class GreaterOrEqualThan(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('>=', [expression])
        self.attatchable = True

class LessOrEqualThan(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('<=', [expression])
        self.attatchable = True

class NotEqualTo(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('!=', [expression])
        self.attatchable = True

class Between(SQLComparison):
    def __init__(self, left: SQLExpression, right: SQLExpression):
        left, right = SQLExpression.ensure_expressions([left, right])
        super().__init__('BETWEEN', [left, right])
        self.left, self.right = self.expressions
    def sql_string(self) -> str:
        return f"{self.comparator} {self.left.sql_string(include_sign=False, include_sign_only_if_negative=True)} AND {self.right.sql_string(include_sign=True, include_sign_only_if_negative=True)}"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        left_placeholder, left_params = self.left.placeholder_pair()
        right_placeholder, right_params = self.right.placeholder_pair()
        sql = f"{self.comparator} {left_placeholder} AND {right_placeholder}"
        params = []
        if isinstance(left_params, list):
            params.extend(left_params)
        else:
            params.append(left_params)
        if isinstance(right_params, list):
            params.extend(right_params)
        else:
            params.append(right_params)
        return sql, params

    def __neg__(self):
        return NotBetween(self.left, self.right)
    def copy(self) -> SQLComparison:
        return Between(self.left.copy(), self.right.copy())
class NotBetween(Between):
    def __init__(self, left: SQLExpression, right: SQLExpression):
        super().__init__(left, right)
        self.comparator = 'NOT BETWEEN'

    def __neg__(self):
        return Between(self.left, self.right)
    def copy(self) -> SQLComparison:
        return NotBetween(self.left.copy(), self.right.copy())
class In(SQLComparison):
    def __new__(cls, set_expression: SQLExpression):
        set_expression = SQLExpression.ensure_expression(set_expression)
        if set_expression.expression_type == "query":
            return InSubquery(set_expression)
        if set_expression.expression_type != "set":
            raise TypeError("In comparison expects a 'set' SQLExpression.")
        return super().__new__(cls)
    def __init__(self, set_expression: SQLExpression):
        super().__init__('IN', [set_expression])
        self.set_expression = set_expression
    def sql_string(self) -> str:
        return f"{self.comparator} {self.set_expression.sql_string(include_sign=False)}"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        placeholder, params = self.set_expression.placeholder_pair()
        return f"{self.comparator} {placeholder}", list(params if isinstance(params, list) else [params])
    def copy(self) -> SQLComparison:
        return In(self.set_expression.copy())

class NotIn(In):
    def __new__(cls, set_expression: SQLExpression):
        set_expression = SQLExpression.ensure_expression(set_expression)
        if set_expression.expression_type == "query":
            return NotInSubquery(set_expression)
        if set_expression.expression_type != "set":
            raise TypeError("NotIn comparison expects a 'set' SQLExpression.")
        return object.__new__(cls)
    def __init__(self, set_expression: SQLExpression):
        super().__init__(set_expression)
        self.comparator = 'NOT IN'
    def copy(self) -> SQLComparison:
        return NotIn(self.set_expression.copy())

class InSubquery(SQLComparison):
    def __init__(self, subquery: str, placeholders: List[str] = None):
        if isinstance(subquery, SubQuery) or isinstance(subquery, SQLExpression) and subquery.expression_type == "query":
            _ , placeholders = subquery.placeholder_pair() 
        elif isinstance(subquery, (tuple, list)) and len(subquery) == 2:
            subquery = SubQuery(subquery[0], subquery[1])
        else:
            subquery = SubQuery(subquery, parameters=placeholders)
        
        self.subquery:SubQuery = subquery
        self._validate_subquery_safe(subquery.sql_string())
        super().__init__('IN', [])
        self.placeholders = placeholders if placeholders else []

    @staticmethod
    def _validate_subquery_safe(subquery: str) -> None:
        try:
            import sqlparse
            from sqlparse.tokens import DML
        except ImportError:
            import logging
            logging.warning("sqlparse is not installed. Subquery validation is skipped.")
            return
        subquery = subquery.strip("()")
        parsed = sqlparse.parse(subquery)
        if not parsed:
            raise ValueError("Empty subquery is not allowed.")
        stmt = parsed[0]
        first_token = stmt.token_first(skip_cm=True)

        if not first_token or first_token.ttype != DML or first_token.value.upper() != 'SELECT':
            raise ValueError("Only SELECT subqueries are allowed.")

        if len(parsed) > 1:
            raise ValueError("Multiple statements are not allowed in subquery.")

        if ";" in subquery[:-1]:
            raise ValueError("Semicolons are not allowed inside the subquery.")

    def sql_string(self) -> str:
        return f"IN ({self.subquery.sql_string()})"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        text, placeholders = self.subquery.placeholder_pair()
        return f"IN ({text})", placeholders 
    
class NotInSubquery(InSubquery):
    def __init__(self, subquery: str, placeholders: List[str] = None):
        super().__init__(subquery, placeholders)
        self.comparator = 'NOT IN'
    def sql_string(self) -> str:
        return f"NOT IN ({self.subquery.sql_string()})"
    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        text, self.placeholders = self.subquery.placeholder_pair()
        return f"NOT IN ({text})", self.placeholders

class Like(SQLComparison):
    def __init__(self, expression: SQLExpression):
        super().__init__('LIKE', [expression])

    def sql_string(self) -> str:
        return f"{self.comparator} {self.expressions[0].sql_string(include_sign=False)}"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        expr_placeholder, expr_params = self.expressions[0].placeholder_pair()
        return f"{self.comparator} {expr_placeholder}", expr_params if isinstance(expr_params, list) else [expr_params]

class NotLike(Like):
    def __init__(self, expression: SQLExpression):
        super().__init__(expression)
        self.comparator = 'NOT LIKE'
    

class IsNull(SQLComparison):
    def __init__(self):
        super().__init__('IS NULL', [])

    def sql_string(self) -> str:
        return "IS NULL"
    
    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        return "IS NULL", []

    def __neg__(self):
        return IsNotNull()

class IsNotNull(SQLComparison):
    def __init__(self):
        super().__init__('IS NOT NULL', [])

    def sql_string(self) -> str:
        return "IS NOT NULL"
    
    def placeholder_pair(self):
        return "IS NOT NULL", []

    def __neg__(self):
        return IsNull()


    


negation_dict_ = {
    LessThan: GreaterOrEqualThan,
    GreaterThan: LessOrEqualThan,
    EqualTo: NotEqualTo,
    Like: NotLike,
    In: NotIn,
}
negation_dict = Twd()
negation_dict.update(negation_dict_)


def get_comparison(statement: str, value1: SQLInput = None, value2: SQLInput = None) -> SQLComparison:
    if value1 is None and statement.strip().lower() not in (is_null_keys | is_not_null_keys):
        raise ValueError("Value1 cannot be None for this comparison.")

    stmt = statement.strip().lower().replace("_", "").replace(" ", "")

    # Normalize input to SQLExpressions
    if value1 is not None:
        value1 = SQLExpression.ensure_expression(value1)
    if value2 is not None:
        value2 = SQLExpression.ensure_expression(value2)

    if stmt in less_than_keys:
        return LessThan(value1)
    if stmt in greater_than_keys:
        return GreaterThan(value1)
    if stmt in equal_to_keys:
        return EqualTo(value1)
    if stmt in greater_or_equal_keys:
        return GreaterOrEqualThan(value1)
    if stmt in less_or_equal_keys:
        return LessOrEqualThan(value1)
    if stmt in not_equal_keys:
        return NotEqualTo(value1)
    if stmt in between_keys:
        if value2 is None:
            raise ValueError("BETWEEN requires two values.")
        return Between(value1, value2)
    if stmt in in_keys:
        if not isinstance(value1, SQLExpression) or value1.expression_type != "set":
            raise ValueError("IN condition requires a 'set' SQLExpression.")
        return In(value1)
    if stmt in is_null_keys:
        return IsNull()
    if stmt in is_not_null_keys:
        return IsNotNull()
    if stmt in like_keys:
        return Like(value1)

    if stmt in not_like_keys:
        return NotLike(value1)
    raise ValueError(f"Unknown SQL comparison keyword: {statement}")

class SQLCondition:
    def __init__(self, expression: SQLExpression, comparison: SQLComparison):
        self.expression = expression
        self.comparison = comparison

    def sql_string(self) -> str:
        return f"{self.expression.sql_string(include_sign=True, include_sign_only_if_negative=True)} {self.comparison.sql_string()}"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:

        expr_placeholder, expr_params = self.expression.placeholder_pair()
        comp_placeholder, comp_params = self.comparison.placeholder_pair()

        sql = f"{expr_placeholder} {comp_placeholder}"
        return sql, list(expr_params) + list(comp_params)

    def flatten(self) -> List[SQLCondition]:
        return [self]

    def flatten_condition(self) -> SQLCondition:
        return self

    def __repr__(self):
        return f"{self.__class__.__name__}({self.expression}, {self.comparison})"

    def __str__(self):
        return self.sql_string()

    def __neg__(self) -> SQLCondition:
        return SQLCondition(self.expression, -self.comparison)

    @staticmethod
    def simple(col_name: str, comparator: str, value: Any, value2: Any = None) -> SQLCondition:
        expression = col(col_name)
        comparison = get_comparison(comparator, num(value)) if value2 is None else get_comparison(comparator, num(value), num(value2))
        return SQLCondition(expression, comparison)

    def copy(self) -> SQLCondition:
        return SQLCondition(self.expression.copy(), self.comparison.copy())

    def copy_with(self, *, expression: SQLExpression = None, comparison: SQLComparison = None) -> SQLCondition:
        return SQLCondition(
            expression if expression is not None else self.expression.copy(),
            comparison if comparison is not None else self.comparison.copy()
        )

    def _binary_logic(self, other, logic_cls, invert_other=False):
        """Helper for logical operations."""
        if not isinstance(other, SQLCondition):
            raise TypeError(f"Expected SQLCondition, got {type(other).__name__}")
        other = ~other if invert_other else other
        return logic_cls(self, other).flatten_condition()

    def __add__(self, other):
        return self._binary_logic(other, OrCondition)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        return self._binary_logic(other, AndCondition)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __and__(self, other):
        return self.__mul__(other)

    def __or__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self._binary_logic(other, AndCondition, invert_other=True)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __invert__(self):
        return NotCondition(self)

    def _relational_operator(self, other: Union[SQLInput, SQLChainCondition], op: str) -> SQLChainCondition:

        if not self.comparison.attatchable:
            raise ValueError(f"Cannot use {op} operator on non-attachable comparison.")
        if not isinstance(other, (SQLExpression, str, int, float)):
            raise TypeError(f"Right operand must be SQLInput, got {type(other).__name__}.")
        new_chain = SQLChainCondition.from_condition(self, copy_items=True)
        if op not in new_chain._valid_comparators(new_chain.behaviour):
            new_chain = new_chain.flipped()
        
        new_chain.attatch_items(other, first_comparator=op)
        return new_chain
    # Relational operators
    def __lt__(self, other):
        return self._relational_operator(other, "<")
    
    def __le__(self, other):
        return self._relational_operator(other, "<=")
    
    def __gt__(self, other):
        return self._relational_operator(other, ">")
    
    def __ge__(self, other):
        return self._relational_operator(other, ">=")
    
    def __eq__(self, other):
        return self._relational_operator(other, "=")
    def flipped(self) -> SQLCondition:
        """Flip the condition's comparison."""
        if not self.comparison.attatchable:
            raise ValueError("Cannot flip non-attachable comparison.")
        comparison_expression = self.comparison.expressions[0]
        opposite_comparator = inverted_inequalities.get(self.comparison.comparator, None)
        if not opposite_comparator:
            raise ValueError(f"Cannot flip comparison {self.comparison.comparator}.")
        new_comparison = get_comparison(opposite_comparator, self.expression)
        new_condition = SQLCondition(comparison_expression, new_comparison)
        return new_condition
        
increasing = {"<", "<="}
decreasing = {">", ">="}
equal = {"="}
inverted_inequalities = {"<": ">", ">": "<", "<=": ">=", ">=": "<=", "=":"="}

simple_inequalities = {EqualTo, LessThan, GreaterThan, LessOrEqualThan, GreaterOrEqualThan}

def copy_expressions_and_strings(exprs: List[Union[SQLExpression, str]]) -> List[Union[SQLExpression, str]]:
    """Copy expressions to ensure they are not modified."""
    return [expr.copy() if isinstance(expr, SQLExpression) else expr for expr in exprs]


class SQLChainCondition(SQLCondition):
    def __init__(self, *items: Union[SQLInput, str], copy_items: bool = True):
        if len(items) == 1 and isinstance(items[0], list):
            items = items[0]
        
        if len(items) % 2 == 0:
            raise ValueError("ChainCondition expects [expr, comp, expr, comp, expr, ...]")

        new_items = []
        for i, item in enumerate(items):
            if i % 2 == 0:
                if copy_items:
                    new_items.append(SQLExpression.ensure_expression(item).copy())
                else:
                    new_items.append(SQLExpression.ensure_expression(item))
            else:
                if not isinstance(item, str):
                    raise ValueError(f"Expected string comparator at index {i}, got {type(item).__name__}.")
                new_items.append(item)
            

        self.items = new_items
        self._rebuild_internal()

    @property
    def behaviour(self) -> str:
        return self._determine_behaviour()

    @classmethod
    def from_condition(cls, condition: SQLCondition, copy_items = True) -> "SQLChainCondition":
        expr = condition.expression
        comp = condition.comparison
        if not comp.attatchable:
            raise ValueError("Cannot create SQLChainCondition from non-attachable comparison.")
        return cls(expr, comp.comparator, comp.expressions[0], copy_items=copy_items)

    @staticmethod
    def _comparators_behaviours(comparators: Set[str]) -> str:
        comparators = set(comparators)
        if comparators == equal:
            return "equal"
        comps = comparators - equal
        if increasing.issuperset(comps):
            return "increasing"
        if decreasing.issuperset(comps):
            return "decreasing"
        raise ValueError("Chain comparators must be all increasing or all decreasing.")

    def _determine_behaviour(self) -> str:
        return self._comparators_behaviours(set(self.items[1::2]))

    def _rebuild_internal(self) -> None:
        pairs = list(zip(self.items[::2], self.items[1::2], self.items[2::2]))
        conditions = [ SQLCondition(left,get_comparison(op, right)) for left, op, right in pairs]
        if len(conditions) == 1:
            final = conditions[0]
        else:
            final = AndCondition(*conditions)
        self.inner_condition = final
        super().__init__(None, None)

    @staticmethod
    def _valid_comparators(behaviour: str) -> Set[str]:
        if behaviour == "equal":
            return equal | increasing | decreasing
        elif behaviour == "increasing":
            return increasing | equal
        elif behaviour == "decreasing":
            return decreasing | equal
        else:
            raise ValueError("Unknown chain behaviour.")

    def _validate_comparator(self, comp: str) -> None:
        behaviour = self._determine_behaviour()
        valid_comparators = self._valid_comparators(behaviour)
        if comp not in valid_comparators:
            raise ValueError(f"Invalid comparator '{comp}' for {behaviour} chain.")


    def sql_string(self) -> str:
        return self.inner_condition.sql_string()

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        return self.inner_condition.placeholder_pair()

    def flatten(self) -> List[SQLCondition]:
        return self.inner_condition.flatten()

    def flattened_condition(self) -> SQLCondition:
        return self.inner_condition.flattened_condition()

    def __repr__(self):
        return f"SQLChainCondition({self.items})"

    def __str__(self):
        return self.sql_string()

    def attatch_comparisons(self, *comparisons: SQLComparison) -> None:
        if not all(comparison.attatchable for comparison in comparisons):
            raise ValueError("All comparisons must be attachable.")
        comparators = [comparison.comparator for comparison in comparisons]
        expressions = [comparison.expressions[0] for comparison in comparisons]
        valid_comparators = self._valid_comparators(self.behaviour)
        if not set(comparators).issubset(valid_comparators):
            raise ValueError(f"Invalid comparators {set(comparators)} for {self.behaviour} chain.")
        last_part = []
        for comparator, expr in zip(comparators, expressions):
            last_part.append(comparator)
            last_part.append(expr)
        self.items = self.items + last_part
        self._rebuild_internal()

    def attatch_pairs(self, *pairs: Tuple[str, SQLInput]) -> None:
        comparisons = [get_comparison(pair[0], pair[1]) for pair in pairs]
        self.attatch_comparisons(*comparisons)

    def attatch_items(self, *items: Any, first_comparator: str = None,  ignore_fails: bool = False) -> None:
        items = list(items)
        if isinstance(items[0], List):
            items = items[0]
        if first_comparator is not None:
            items = [first_comparator] + items  # copy-safe addition

        if all(isinstance(item, SQLComparison) for item in items):
            self.attatch_comparisons(*items)
            return


        pairs = []
        fails = []

        i = 0
        while i < len(items):
            comparator = items[i]
            if i + 1 >= len(items):
                fails.append((comparator, None))
                break
            target = items[i + 1]
            if isinstance(target, (SQLExpression, str, int, float)):
                pairs.append((comparator, target))
            elif isinstance(target, SQLChainCondition):
                pairs.extend(self._pairs_from_comparator_and_chain(comparator, target))
            else:

                fails.append((comparator, target))
            i += 2

        if fails and not ignore_fails:
            raise ValueError(f"Failed to attach: {', '.join(f'{comp} {tgt}' for comp, tgt in fails)}")

        if pairs:
            self.attatch_pairs(*pairs)

    def _pairs_from_comparator_and_chain(self, comparator: str, chain: SQLChainCondition) -> List[Tuple[str, SQLInput]]:
        extended_items = [comparator] + chain.items
        return list(zip(extended_items[::2], extended_items[1::2]))

    def flipped(self) -> SQLCondition:
        new = []
        for i, item in enumerate(self.items[::-1]):
            if i % 2 == 0:
                new.append(item.copy())
            else:
                new.append(inverted_inequalities[item])
        return SQLChainCondition(*new, copy_items=False)
    
    def inverted(self) -> SQLCondition:
        new = []
        for i, item in enumerate(self.items):
            if i % 2 == 0:
                new.append(item.copy())
            else:
                new.append(inverted_inequalities[item])
        return SQLChainCondition(*new, copy_items=False)
    def math_inequality(self) -> str:
        output = ""
        for i, item in enumerate(self.items):
            if i % 2 == 0:
                output += item.sql_string(include_sign=True, include_sign_only_if_negative=True)
            else:
                output += f" {item} "
        return output
    def _binary_operator(self, other: Union[SQLInput, SQLChainCondition], operator: str) -> SQLChainCondition:
        behaviour = self.behaviour
        if operator in ("<", "<=") and behaviour == "decreasing":
            raise ValueError(f"Cannot use {operator} operator on decreasing chain.")
        if operator in (">", ">=") and behaviour == "increasing":
            raise ValueError(f"Cannot use {operator} operator on increasing chain.")
        
        copy_self = self.copy()
        
        if isinstance(other, (SQLExpression, str, int, float)):
            comparison = get_comparison(operator, other)
            copy_self.attatch_comparisons(comparison)
        elif isinstance(other, SQLChainCondition):
            if other.behaviour != behaviour and other.behaviour != "equal":
                raise ValueError("Cannot chain with incompatible behaviour.")
            copy_self.attatch_items(other, first_comparator=operator)
        else:
            raise TypeError(f"Invalid type for binary operation: {type(other).__name__}")
        
        return copy_self

    def __lt__(self, other: Union[SQLInput, SQLChainCondition]) -> SQLChainCondition:
        return self._binary_operator(other, "<")

    def __le__(self, other: Union[SQLInput, SQLChainCondition]) -> SQLChainCondition:
        return self._binary_operator(other, "<=")

    def __gt__(self, other: Union[SQLInput, SQLChainCondition]) -> SQLChainCondition:
        return self._binary_operator(other, ">")

    def __ge__(self, other: Union[SQLInput, SQLChainCondition]) -> SQLChainCondition:
        return self._binary_operator(other, ">=")

    def __eq__(self, other: Union[SQLInput, SQLChainCondition]) -> SQLChainCondition:
        return self._binary_operator(other, "=")

    def copy(self) -> SQLChainCondition:
        return SQLChainCondition(*self.items, copy_items=True)



class AndCondition(SQLCondition):
    def __init__(self, *conditions: SQLCondition):
        self.conditions = conditions
        self.flatten(update_self=True)

    def sql_string(self) -> str:
        sandwiched_conditions = [bracket_string_sandwich(condition.sql_string()) for condition in self.conditions]
        return " AND ".join(sandwiched_conditions)

    def __repr__(self):
        return f"AndCondition({', '.join(map(str, self.conditions))})"

    def __str__(self):
        return f"AndCondition({', '.join(map(str, self.conditions))})"

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, index: int) -> SQLCondition:
        return self.conditions[index]

    def flatten(self, update_self=True) -> List[SQLCondition]:
        flattened = []
        for cond in self.conditions:
            if isinstance(cond, AndCondition):
                flattened.extend(cond.flatten())
            elif isinstance(cond, OrCondition):
                flattened.append(OrCondition(*cond.flatten()))
            elif isinstance(cond, TrueCondition):
                continue  # True disappears
            elif isinstance(cond, FalseCondition):
                flattened = [FalseCondition()]  # False annihilates
                break
            else:
                flattened.append(cond)
        # Unwrap if unnecessary nesting
        while len(flattened) == 1 and isinstance(flattened[0], (AndCondition, OrCondition)):
            flattened = flattened[0].flatten(update_self=False)
        if update_self:
            self.conditions = flattened
        return flattened

    def flattened_condition(self) -> SQLCondition:
        flattened_list = self.flatten(update_self=False)
        if len(flattened_list) == 1:
            return flattened_list[0]
        return AndCondition(*flattened_list)

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        fragments = []
        params = []
        
        for cond in self.conditions:
            placeholder, cond_params = cond.placeholder_pair()
            fragments.append(bracket_string_sandwich(placeholder))
            if isinstance(cond_params, list):
                params.extend(cond_params)
            else:
                params.append(cond_params)
        joined = " AND ".join(fragments)
        return joined, params

    @classmethod
    def gather(cls, *param_lists: List[Union[str, int]]) -> AndCondition:
        return cls(*[SQLCondition.simple(*params) for params in param_lists])

class OrCondition(SQLCondition):
    def __init__(self, *conditions: SQLCondition):
        self.conditions = conditions
        self.flatten(update_self=True)

    def sql_string(self) -> str:
        sandwiched_conditions = [bracket_string_sandwich(cond.sql_string()) for cond in self.conditions]
        return " OR ".join(sandwiched_conditions)

    def __repr__(self):
        return f"OrCondition({', '.join(map(str, self.conditions))})"

    def __str__(self):
        return f"OrCondition({', '.join(map(str, self.conditions))})"

    def __len__(self):
        return len(self.conditions)

    def __getitem__(self, index: int) -> SQLCondition:
        return self.conditions[index]

    def flatten(self, update_self=True) -> List[SQLCondition]:
        flattened = []
        for cond in self.conditions:
            if isinstance(cond, OrCondition):
                flattened.extend(cond.flatten())
            elif isinstance(cond, AndCondition):
                flattened.append(AndCondition(*cond.flatten()))
            elif isinstance(cond, TrueCondition):
                return [TrueCondition()]  # True dominates
            elif isinstance(cond, FalseCondition):
                continue  # False disappears
            else:
                flattened.append(cond)
        # Avoid nested single Or/And
        while len(flattened) == 1 and isinstance(flattened[0], (OrCondition, AndCondition)):
            flattened = flattened[0].flatten(update_self=False)
        if update_self:
            self.conditions = flattened
        return flattened

    def flattened_condition(self) -> SQLCondition:
        flattened_list = self.flatten(update_self=False)
        if len(flattened_list) == 1:
            return flattened_list[0]
        return OrCondition(*flattened_list)

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        fragments = []
        params = []
        for cond in self.conditions:
            placeholder, cond_params = cond.placeholder_pair()
            fragments.append(bracket_string_sandwich(placeholder))
            if isinstance(cond_params, list):
                params.extend(cond_params)
            else:
                params.append(cond_params)
        joined = " OR ".join(fragments)
        return joined, params

    @classmethod
    def gather(cls, *param_lists: List[Union[str, int]]) -> OrCondition:
        return cls(*[SQLCondition.simple(*params) for params in param_lists])

    @classmethod
    def SOP(cls, *products: List[AndCondition]) -> OrCondition:
        return cls(*products)

    @classmethod
    def quick(cls, column_name: str, comparison_str: str, value1: Any, value2: Any = None) -> OrCondition:
        return cls(AndCondition(SQLCondition.simple(column_name, comparison_str, value1, value2)))

    def __list__(self) -> List[SQLCondition]:
        return list(self.conditions)

    def __iter__(self):
        return iter(self.conditions)

    def __eq__(self, other):
        return isinstance(other, OrCondition) and self.conditions == other.conditions

class NotCondition(SQLCondition):
    def __new__(cls, condition: SQLCondition):
        if isinstance(condition, NotCondition):
            return condition.condition.flattened_condition()
        return super().__new__(cls)

    def __init__(self, condition: SQLCondition):
        self.condition = condition

    def sql_string(self) -> str:
        return f"NOT ({self.condition.sql_string()})"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        placeholder, params = self.condition.placeholder_pair()
        return f"NOT ({placeholder})", params if isinstance(params, list) else [params]

    def flatten(self, *args, **kwargs) -> List[SQLCondition]:
        return [self]

    def flattened_condition(self) -> SQLCondition:
        current = self
        flip = False
        while isinstance(current, NotCondition):
            flip = not flip
            current = current.condition

        if flip:
            return NotCondition(current)
        else:
            return current

    def __invert__(self) -> SQLCondition:
        return self.condition.flattened_condition()

    def __repr__(self):
        return f"NotCondition({repr(self.condition)})"

    def __str__(self):
        return f"NotCondition({str(self.condition)})"


class NoCondition(SQLCondition):
    def __init__(self):
        super().__init__(SQLExpression(1, "value"), None)

    def sql_string(self) -> str:
        return ""

    def __repr__(self):
        return "NoCondition()"

    def __str__(self):
        return "NoCondition()"

    def __bool__(self):
        return False

    def flatten(self) -> List[SQLCondition]:
        return []

    def flatten_condition(self) -> SQLCondition:
        return self

    def copy(self) -> SQLCondition:
        return NoCondition()

    def __or__(self, other: SQLCondition) -> SQLCondition:
        return self if isinstance(other, NoCondition) else other

    def __and__(self, other: SQLCondition) -> SQLCondition:
        if not isinstance(other, SQLCondition):
            raise TypeError("Other must be an SQLCondition.")
        return other




class TrueCondition(SQLCondition):
    def __init__(self):
        super().__init__("", None)

    def sql_string(self) -> str:
        return "1=1"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        return "1=1", []

    def __repr__(self):
        return "TrueCondition()"

    def __str__(self):
        return "TrueCondition()"

    def __bool__(self):
        return True

    def __eq__(self, other):
        return isinstance(other, TrueCondition) or other in (True, 1)

class FalseCondition(SQLCondition):
    def __init__(self):
        super().__init__("", None)


    def sql_string(self) -> str:
        return "0=1"

    def placeholder_pair(self) -> Tuple[str, List[Any]]:
        return "0=1", []

    def __repr__(self):
        return "FalseCondition()"

    def __str__(self):
        return "FalseCondition()"

    def __bool__(self):
        return False

    def __eq__(self, other):
        return isinstance(other, FalseCondition) or other in (False, 0)

def num(value: Union[str, int, float]) -> SQLExpression:
    """
    Create a numeric SQL expression.
    
    Converts a numeric value to an SQLExpression suitable for use in SQL operations.
    The function preserves numeric precision:
    - Integer values remain as integers
    - Float values preserve their decimal precision
    - String representations of numbers are parsed accordingly
    
    Args:
        value: A numeric value (int, float) or string representation of a number
    
    Returns:
        SQLExpression: A value-type expression containing the numeric value
    
    Raises:
        TypeError: If the value is not a number or cannot be parsed as one
    
    Examples:
        >>> # Integer values
        >>> age = num(25)
        >>> sql, params = age.placeholder_pair()
        >>> # sql = "?", params = [25]
        
        >>> # Float values (precision preserved)
        >>> price = num(19.99)
        >>> sql, params = price.placeholder_pair()
        >>> # sql = "?", params = [19.99]
        
        >>> # String representations
        >>> value = num("3.14159")
        >>> sql, params = value.placeholder_pair()
        >>> # sql = "?", params = [3.14159]
    
    Note:
        As of version 0.3.6, float precision is properly preserved.
        Previously, floats were rounded to integers, which has been fixed.
    """
    if not is_number(value):
        raise TypeError("Numeric value must be a number. For other types, use text() or col().")
    return SQLExpression(value, "value", auto_parse_numbers=True)

def col(name: str, *, skip_validation:bool = False) -> SQLExpression:
    """Create a column SQL expression."""
    return SQLExpression(name, "column", auto_parse_numbers=False, skip_validation=skip_validation)

def set_expr(values: Iterable, *, skip_validation:bool = False) -> SQLExpression:
    """
    Create a set SQL expression for use in IN/NOT IN clauses.
    
    This function creates a set expression that can be used with the IN operator
    in SQL conditions. It's designed for filtering queries, not for UPDATE SET clauses.
    
    For UPDATE SET clauses with expressions (e.g., `stock = stock + ?`), use regular
    SQLExpression arithmetic operations instead.
    
    Args:
        values: An iterable of values to include in the set
        skip_validation: If True, skip validation of the values
    
    Returns:
        SQLExpression: A set-type expression suitable for IN/NOT IN clauses
    
    Examples:
        >>> # For WHERE ... IN clauses
        >>> region = col("region")
        >>> cond = region.is_in(["North", "South", "East"])
        >>> # Or using set_expr directly
        >>> regions = set_expr(["North", "South", "East"])
        >>> cond = region.is_in(regions)
        
        >>> # For UPDATE with expressions, use arithmetic operations:
        >>> stock = col("stock")
        >>> new_value = stock + 10  # Creates an expression for `stock = stock + 10`
    
    Note:
        This function is specifically for IN/NOT IN operations. For UPDATE SET clauses
        that involve expressions (e.g., `stock = stock + ?`), construct the expression
        using normal arithmetic operations on column objects.
    """
    return SQLExpression(values, "set", auto_parse_numbers=False, skip_validation=skip_validation)

def text(value: str) -> SQLExpression:
    """Create a text SQL expression."""
    if not isinstance(value, str):
        raise TypeError("Text value must be a string. For other types, use num() or col().")
    return SQLExpression(value, "value", auto_parse_numbers=False)


@normalize_args()
def cols(*names: str, skip_validation:bool = False) -> List[SQLExpression]:
    """
    Create a list of column SQL expressions.
    
    This function creates multiple column expressions at once, which is useful for
    SELECT clauses or GROUP BY operations in external query builders like recordsql.
    
    Note: ExpressQL focuses on expressions and conditions, not full query building.
    For SELECT and GROUP BY operations, use a query builder like recordsql that can
    extract column names from SQLExpression objects.
    
    Args:
        *names: Column names as separate arguments or comma-separated in a single string
        skip_validation: If True, skip validation of column names
    
    Returns:
        list[SQLExpression]: A list of column expressions
    
    Examples:
        >>> # Multiple arguments
        >>> age, name, email = cols("age", "name", "email")
        
        >>> # Comma-separated string
        >>> columns = cols("age, name, email")
        
        >>> # For use with query builders (pseudocode):
        >>> columns = cols("id", "name", "email")
        >>> # Query builder should extract: [col.expression_value for col in columns]
        >>> # Result: ["id", "name", "email"]
    
    Integration with Query Builders:
        Query builders using ExpressQL should:
        1. Check if argument is an SQLExpression with expression_type == "column"
        2. Extract the column name using: expression.expression_value
        3. Handle lists of expressions by extracting each column name
    """
    
    if isinstance(names[0], str) and len(names) == 1:
        words = names[0].split(",")
        names = [word.strip() for word in words if word.strip()]
    return [col(name, skip_validation=skip_validation) for name in names]

@normalize_args()
def nums(*values: Union[str, int, float]) -> List[SQLExpression]:
    """Create a list of numeric SQL expressions."""
    return [num(value) for value in values]

@normalize_args()
def text_exprs(*values: str) -> List[SQLExpression]:
    """Create a list of text SQL expressions."""
    return [text(value) for value in values]

no_condition = NoCondition()
#aliases for convenience
ExprSum = SQLExpressionSum
ExprMul = SQLExpressionProduct
ExprPow = SQLExpressionPower
Chain = SQLChainCondition


def where_string(condition: SQLCondition = no_condition) -> str:
    """Return the SQL WHERE clause string for a given condition."""
    if isinstance(condition, NoCondition):
        return ""
    return f"WHERE {condition.sql_string()}"

def where_placeholder_pair(condition: SQLCondition = no_condition) -> Tuple[str, List[Any]]:
    """Return the SQL WHERE clause placeholder and parameters for a given condition."""
    if isinstance(condition, NoCondition):
        return "", []
    placeholder_str, params = condition.placeholder_pair()
    if placeholder_str:
        placeholder_str = f"WHERE {placeholder_str}"
    return placeholder_str, params

