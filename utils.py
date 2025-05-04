from typing import Any, Dict, Set, Union , Callable, Iterable
from collections.abc import Iterable
from .exceptions import ForbiddenCharacterError
from functools import wraps
import re
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




def normalize_args(skip: int = 0):
    """
    Decorator to normalize *args into a list, skipping the first `skip` arguments.
    If a single iterable (not a string) is passed as *args, it will be unpacked.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Split into skipped and target args
            skipped_args = args[:skip]
            target_args = args[skip:]

            if len(target_args) == 1 and isinstance(target_args[0], Iterable) and not isinstance(target_args[0], str):
                normalized_args = list(target_args[0])
            else:
                normalized_args = list(target_args)

            return func(*skipped_args, *normalized_args, **kwargs)
        return wrapper
    return decorator


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
    """Try converting string to int or float; return original if both fail."""
    for cast in (int, float):
        try:
            return cast(s)
        except ValueError:
            continue
    return s

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

