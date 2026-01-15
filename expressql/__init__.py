"""
ExpressQL - A Pythonic DSL for SQL conditions and expressions.

This package provides a flexible, Pythonic Domain-Specific Language (DSL) for constructing
complex SQL conditions and expressions safely and expressively. It reduces boilerplate,
prevents common SQL mistakes, and allows arithmetic, logical, and chained comparisons
directly in Python syntax.

Key Features:
    - Arithmetic expressions with automatic SQL translation
    - Logical composition (AND, OR, NOT) using natural Python operators
    - Chained inequalities (e.g., 50 < col("age") < 80)
    - SQL-safe placeholder management
    - Null-safe operations (is_null, not_null)
    - Set membership (IN, NOT IN)
    - Support for custom SQL functions
    - Fluent API for advanced condition building
    - Parsing of SQL-like strings into expressions and conditions

Example:
    >>> from expressql import col, cols
    >>> age, salary, department = cols("age", "salary", "department")
    >>> condition = ((age > 30) * (department == "HR")) + (salary > 50000)
    >>> sql, params = condition.placeholder_pair()
    >>> print(sql)
    ((age > ?) AND (department = ?)) OR (salary > ?)
    >>> print(params)
    [30, 'HR', 50000]
"""

# Export core condition classes and helpers for easy external use
from .base import (SQLCondition, SQLComparison, EqualTo, LessThan, GreaterThan, LessOrEqualThan, GreaterOrEqualThan, NotEqualTo, \
Between, In, no_condition, get_comparison, AndCondition, OrCondition, NotCondition, TrueCondition, FalseCondition,
col, cols, num, text, set_expr, SQLChainCondition, SQLExpression, SQLInput, ensure_sql_expression,
where_string, Func)

from .utils import parse_number, format_sql_value, forbidden_chars, forbidden_words
from .dsl import pk_condition
from .parsers import parse_expr_or_cond, parse_expression, parse_condition
get_condition = get_comparison  # Alias for backward compatibility

__all__ = [
    "SQLCondition", "SQLComparison", "EqualTo", "LessThan", "GreaterThan", "LessOrEqualThan", "GreaterOrEqualThan", "NotEqualTo", "Between", "In",
    "AndCondition", "OrCondition", "NotCondition", "get_condition", "no_condition",
    "parse_number", "format_sql_value", "col", "IsNull", "IsNotNull", "forbidden_chars",
    "TrueCondition", "FalseCondition", "pk_condition", "forbidden_words", "set_expr",
    "num", "text", "GreaterThan", "SQLChainCondition", "SQLExpression", "SQLInput",
    "ensure_sql_expression", "where_string", "Func", "cols", "parse_expr_or_cond", "parse_expression", "parse_condition",
]

__version__ = "0.2.4"
