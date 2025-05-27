from .conditions_parser import parse_condition
from .expressions_parser import parse_expression
from ..base import SQLExpression, SQLCondition
from .parsing_utils import remove_outer_brackets
condition_items = set("=<>") | {"and", "or", "not", "is", "like", "in", "between", "exists"}
def parse_expr_or_cond(s:str) -> SQLExpression | SQLCondition:
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
    
