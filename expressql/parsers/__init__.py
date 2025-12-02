"""
ExpressQL Parsers - Parse SQL-like strings into ExpressQL objects.

This module provides parsers that can convert SQL-like string syntax into
ExpressQL expressions and conditions. This allows for flexible input handling
while maintaining the safety and benefits of the ExpressQL DSL.

Functions:
    parse_expr_or_cond: Auto-detect and parse either an expression or condition
    parse_expression: Parse a SQL expression string into an SQLExpression
    parse_condition: Parse a SQL condition string into an SQLCondition

Example:
    >>> from expressql.parsers import parse_expression, parse_condition
    >>> expr = parse_expression("LOG(age, 10) + 15")
    >>> cond = parse_condition("age BETWEEN 30 AND 50")
"""

from .main import parse_expr_or_cond
from .expressions_parser import parse_expression
from .conditions_parser import parse_condition

__all__ = [
    "parse_expr_or_cond",
    "parse_expression",
    "parse_condition"
]
