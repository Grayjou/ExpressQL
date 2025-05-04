from .base import Func

AGGREGATE_FUNCTIONS = {"AVG", "COUNT", "GROUP_CONCAT", "MAX", "MIN", "SUM", "TOTAL"}
NUMERIC_FUNCTIONS = {"ABS", "ROUND", "CEIL", "CEILING", "FLOOR", "POWER", "EXP", "LN", "LOG", "LOG10", "MOD", "RANDOM"}
STRING_FUNCTIONS = {"LENGTH", "LOWER", "UPPER", "TRIM", "LTRIM", "RTRIM", "SUBSTR", "REPLACE", "INSTR", "HEX", "QUOTE"}
DATETIME_FUNCTIONS = {"DATE", "TIME", "DATETIME", "JULIANDAY", "STRFTIME"}
CONDITIONAL_FUNCTIONS = {"IFNULL", "COALESCE", "NULLIF"}
ALL_DEFAULT_FUNCTIONS = AGGREGATE_FUNCTIONS | NUMERIC_FUNCTIONS | STRING_FUNCTIONS | DATETIME_FUNCTIONS | CONDITIONAL_FUNCTIONS


def make_factory(name):
    return lambda *args: Func(name, *args)

globals().update({
    name: make_factory(name) 
    for name in ALL_DEFAULT_FUNCTIONS
})

__all__ = list(ALL_DEFAULT_FUNCTIONS)  # so `import *` knows what to import
