"""
ExpressQL Utilities - Helper functions and constants for SQL generation.

This module provides utility functions and constants used throughout ExpressQL
for SQL string manipulation, validation, and parameter handling.

Key Functions:
    parse_number: Parse a string into int or float if possible
    format_sql_value: Format Python values for SQL representation
    normalize_args: Decorator to normalize function arguments
    merge_placeholders: Merge parameter lists together
    ensure_bracketed: Ensure a string is wrapped in parentheses
    bracket_string_sandwich: Wrap a string in parentheses

Key Constants:
    forbidden_chars: Set of characters not allowed in column names
    forbidden_words: Set of SQL keywords that should not be used as column names

Classes:
    TwoWayDict: A bidirectional dictionary for key-value lookups

Example:
    >>> from expressql.utils import parse_number, format_sql_value
    >>> parse_number("42")
    42
    >>> format_sql_value("test")
    "'test'"
"""

from typing import Any, Callable, List
from collections.abc import Iterable
from functools import wraps
# Constants
forbidden_chars = {
    " ", ".", ",", ";", ":", "'", '"', "\\", "/", "|", "?", "!", "@",
    "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", "="
}
forbidden_words = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "FROM", "WHERE", "JOIN",
    "INNER", "LEFT", "RIGHT", "FULL", "OUTER", "CROSS", "GROUP",
    "BY", "ORDER", "HAVING", "LIMIT", "OFFSET", "DISTINCT",
    "UNION", "INTERSECT", "EXCEPT", "AS", "INTO"
}




def normalize_args(skip: int = 0, decompose_string=False, decompose_bytes=False, convert=True, ignore_dict=True):
    """
    Decorator to normalize *args into a list, skipping the first `skip` arguments.
    If a single iterable (not a string) is passed as *args, it will be unpacked.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            skipped_args = args[:skip]
            target_args = args[skip:] if len(args) > skip else ()

            normalized_args = _normalize_args(
                *target_args,
                decompose_string=decompose_string,
                decompose_bytes=decompose_bytes,
                convert=convert,
                ignore_dict=ignore_dict
            )

            return func(*skipped_args, *normalized_args, **kwargs)
        return wrapper
    return decorator


def _normalize_args(*args, decompose_string=False, decompose_bytes=False, convert=True, ignore_dict=True):

    if not args:
        return []
    elif len(args) > 1:
        return list(args)
    if isinstance(args[0], str):
        if decompose_string:
            return list(args[0])
        return [args[0]]
    elif isinstance(args[0], bytes):
        if decompose_bytes:
            return list(args[0])
        return [args[0]] 
    elif isinstance(args[0], dict):
        if ignore_dict:
            return [args[0]]
        return list(args[0].values())
    elif isinstance(args[0], Iterable) and not isinstance(args[0], (str, bytes)):
        #Second check should never happen, but just in case someone alters the function
        if convert:
            return list(args[0])
        return args[0]
    else:

        return list(args)
def merge_placeholders(parameters: List[Any], new_params: Any) -> None:
    """Merge a new parameter or list of parameters o the current parameters list."""
    if isinstance(new_params, list):
        parameters.extend(new_params)
    else:
        parameters.append(new_params)

class TwoWayDict:
    """
    A dictionary that allows two-way lookup.
    Keys and values are the same thing.
    """

    def __init__(self):
        self._dict = {}

    def __setitem__(self, key, value):
        if key in self._dict:
            old_value = self._dict.pop(key)
            self._dict.pop(old_value, None)
        if value in self._dict:
            old_key = self._dict.pop(value)
            self._dict.pop(old_key, None)
        self._dict[key] = value
        self._dict[value] = key

    def __getitem__(self, key):
        return self._dict[key]

    def __delitem__(self, key):
        if key not in self._dict:
            raise KeyError(key)
        value = self._dict.pop(key)
        self._dict.pop(value, None)

    def pop(self, key, default=None):
        if key in self._dict:
            value = self._dict.pop(key)
            self._dict.pop(value, None)
            return value
        if default is not None:
            return default
        raise KeyError(key)

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def _elements(self):
        """Return a set of all unique elements (both keys and values)."""
        seen = set()
        elements = []
        for k, v in self._dict.items():
            if k not in seen and v not in seen:
                elements.append(k)
                elements.append(v)
                seen.add(k)
                seen.add(v)
        return elements

    def keys(self):
        """Same as values: returns all unique elements."""
        return iter(self._elements())

    def values(self):
        """Same as keys: returns all unique elements."""
        return iter(self._elements())

    def items(self):
        """Return unique (key, value) pairs."""
        seen = set()
        for k, v in self._dict.items():
            if k not in seen and v not in seen:
                yield (k, v)
                seen.add(k)
                seen.add(v)

    def elements(self):
        """Return all unique elements (both keys and values)."""
        return self._elements()
    
    def __contains__(self, key):
        return key in self._dict

    def __len__(self):
        return len(self._elements())

    def __iter__(self):
        return self.keys()

    def __repr__(self):
        pairs = [f"{k}: {v}" for k, v in self.items()]
        return "{" + ", ".join(pairs) + "}"

    def load(self, pairs):
        """Load from an iterable of (key, value) pairs."""
        for key, value in pairs:
            self[key] = value

    def update(self, mapping):
        """Update from a dict-like object."""
        for key, value in mapping.items():
            self[key] = value

Twd = TwoWayDict


def is_outer_bracketed(s: str) -> bool:

    return s.startswith("(") and s.endswith(")") and s.count("(") == 1 and s.count(")") == 1

def bracket_string_sandwich(string: str) -> str:
    """
    Do I really need to explain this?
    Wraps a string in parentheses.
    """
    return f"({string})"

def ensure_bracketed(string: str) -> str:
    """
    Ensures that a string is wrapped in parentheses.
    If the string is already bracketed, it is returned unchanged.
    """
    if string.startswith("(") and string.endswith(")"):
        return string
    return bracket_string_sandwich(string)

def parse_number(s: str) -> Any:
    """
    Try converting string to int or float; return original if both fail.
    
    Preserves numeric precision by:
    - Converting to int only if the value is a whole number
    - Converting to float if the value has decimal places
    - Returns original value if not a number
    
    Args:
        s: Value to parse (can be string, int, or float)
        
    Returns:
        int, float, or original value
    """
    # Handle None explicitly
    if s is None:
        return None
    
    # If already a number, preserve its type
    if isinstance(s, (int, float)):
        return s
    
    # Try to parse as string
    if not isinstance(s, str):
        return s
        
    try:
        # Try float first to preserve decimal precision
        float_val = float(s)
        # Convert to int only if it's a whole number
        if float_val.is_integer():
            return int(float_val)
        return float_val
    except (ValueError, AttributeError):
        return s

def is_between(s:str, start: str, end: str) -> bool:
    """
    Check if a string starts with `start` and ends with `end`.
    Returns True if it does, False otherwise.
    """
    return s.startswith(start) and s.endswith(end)

def is_quoted(s: str) -> bool:
    """
    Check if a string is wrapped in single or double quotes.
    Returns True if it is quoted, False otherwise.
    """
    return is_between(s, "'", "'") or is_between(s, '"', '"')

# Formatting
def format_sql_value(val: Any, convert_numbers:bool = True) -> str:

    """
    Formats a Python value into a SQL-compatible string representation.
    Args:
        val (Any): The value to be formatted. Supported types include:
            - str: Escapes single quotes and wraps the string in single quotes.
            - bool: Converts to "1" for True and "0" for False.
            - int, float: Converts to a string representation of the number.
            - None: Converts to "NULL".
        convert_numbers (bool, optional): If True, converts numeric values (int, float)
            to their string representation. If False, returns the numeric value as-is.
            Defaults to True.
    Returns:
        str: The SQL-compatible string representation of the input value.
    Raises:
        TypeError: If the input value is of an unsupported type.
    """
    
    single_quote = "'"
    if isinstance(val, str):

        return f"""'{val.replace(f"{single_quote}", f"{single_quote}{single_quote}")}'"""  # escape single quotes
    elif isinstance(val, bool):

        return "1" if val else "0"
    elif isinstance(val, (int, float)):
        if convert_numbers:
            return str(val)
        else:
            return val

    elif val is None:
        return "NULL"
    else:
        raise TypeError(f"Unsupported SQL value type: {type(val)}")

