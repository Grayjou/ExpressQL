"""
ExpressQL Functions Module - SQL function wrappers and utilities.

This module provides convenient access to common SQL functions and allows
dynamic creation of custom function calls. All standard SQL functions are
available as Python functions that return Func objects.

Function Categories:
    - AGGREGATE_FUNCTIONS: SUM, AVG, COUNT, MAX, MIN, etc.
    - NUMERIC_FUNCTIONS: ABS, ROUND, POWER, SQRT, etc.
    - STRING_FUNCTIONS: UPPER, LOWER, LENGTH, TRIM, etc.
    - DATETIME_FUNCTIONS: DATE, TIME, DATETIME, etc.
    - CONDITIONAL_FUNCTIONS: COALESCE, IFNULL, NULLIF, etc.

Dynamic Function Creation:
    Any uppercase name can be used as a function name via __getattr__.

Example:
    >>> import expressql.functions as f
    >>> from expressql import col
    >>> 
    >>> # Use built-in function
    >>> result = f.SUM(col("salary"))
    >>> 
    >>> # Use custom function
    >>> custom = f.MY_CUSTOM_FUNC(col("value"), 10)
"""

from .base import Func

AGGREGATE_FUNCTIONS = {"AVG", "COUNT", "GROUP_CONCAT", "MAX", "MIN", "SUM", "TOTAL"}
NUMERIC_FUNCTIONS = {"ABS", "ROUND", "CEIL", "CEILING", "FLOOR", "POWER", "EXP", "LN", "LOG", "LOG10", "MOD", "RANDOM"}
STRING_FUNCTIONS = {"LENGTH", "LOWER", "UPPER", "TRIM", "LTRIM", "RTRIM", "SUBSTR", "REPLACE", "INSTR", "HEX", "QUOTE"}
DATETIME_FUNCTIONS = {"DATE", "TIME", "DATETIME", "JULIANDAY", "STRFTIME"}
CONDITIONAL_FUNCTIONS = {"IFNULL", "COALESCE", "NULLIF"}
ALL_DEFAULT_FUNCTIONS = AGGREGATE_FUNCTIONS | NUMERIC_FUNCTIONS | STRING_FUNCTIONS | DATETIME_FUNCTIONS | CONDITIONAL_FUNCTIONS


def make_factory(name):
    return lambda *args, **kwargs: Func(name, *args, **kwargs)


globals().update({
    name: make_factory(name) 
    for name in ALL_DEFAULT_FUNCTIONS
})

def __getattr__(name):
    """
    Allow dynamic SQL function creation:
    f.MYFUNC(...) → Func('MYFUNC', ...)
    """
    if name.isupper():
        def dynamic_func(*args, **kwargs):
            return Func(name, *args, **kwargs)
        return dynamic_func
    raise AttributeError(f"No such function: {name}")

__all__ = list(ALL_DEFAULT_FUNCTIONS)  # so `import *` knows what to import
