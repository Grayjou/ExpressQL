"""
ExpressQL Main Parser - Auto-detect expression or condition parsing.

This module provides the main entry point for parsing SQL-like strings
into either SQLExpression or SQLCondition objects, automatically detecting
which type is appropriate based on the content.

Functions:
    parse_expr_or_cond: Automatically parse a string as expression or condition

Example:
    >>> from expressql.parsers.main import parse_expr_or_cond
    >>> result = parse_expr_or_cond("age > 25 AND salary > 40000")
    >>> type(result)
    <class 'expressql.base.SQLCondition'>
"""

from .conditions_parser import parse_condition
from .expressions_parser import parse_expression
from ..base import SQLExpression, SQLCondition
from typing import Union
from .parsing_utils import remove_outer_brackets
condition_items = set("=<>") | {"and", "or", "not", "is", "like", "in", "between", "exists"}
def parse_expr_or_cond(s:str) -> Union[SQLExpression, SQLCondition]:
    """
    Parse a string into an SQL expression or condition.

    Args:
        s (str): The string to parse.

    Returns:
        SQLExpression | SQLCondition: The parsed SQL expression or condition.
    """
    s = remove_outer_brackets(s.strip())
    if not s.upper().startswith("SELECT") and any(item in s.lower() for item in condition_items):
        return parse_condition(s, outer_brackets_removed=True)
    else:
        print("Parsing as expression:", s)
        return parse_expression(s, outer_brackets_removed=True)
    
