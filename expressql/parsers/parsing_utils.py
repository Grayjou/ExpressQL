"""
ExpressQL Parsing Utilities - Helper functions for parsing SQL strings.

This module provides utility functions used by the parsers to manipulate
strings, handle brackets, and extract components from SQL-like strings.

Functions:
    ensure_bracketed: Ensure a string is wrapped in parentheses
    ensure_outer_bracketed: Ensure outer parentheses are present
    bracket_string_sandwich: Wrap a string in parentheses
    is_outer_bracketed: Check if string has balanced outer brackets
    remove_outer_brackets: Remove outer brackets if present
    extract_word_before: Extract a word before a given index

Example:
    >>> from expressql.parsers.parsing_utils import ensure_bracketed
    >>> ensure_bracketed("test")
    '(test)'
"""

from typing import Set, Tuple


def ensure_bracketed(string: str) -> str:
    """
    Ensures that a string is wrapped in parentheses.
    If the string is already bracketed, it is returned unchanged.
    """
    if string.startswith("(") and string.endswith(")"):
        return string
    return bracket_string_sandwich(string)

def ensure_outer_bracketed(string: str) -> str:
    """
    Ensures that a string is wrapped in outer parentheses.
    If the string is already outer bracketed, it is returned unchanged.
    """
    if is_outer_bracketed(string):
        return string
    return bracket_string_sandwich(string)


def bracket_string_sandwich(string: str) -> str:
    """
    Do I really need to explain this?
    Wraps a string in parentheses.
    """
    return f"({string})"

def extract_word_before(string: str, undesired: Set[str], index: int) -> Tuple[int, str]:
    start = index - 1
    while start >= 0 and string[start] not in undesired:
        start -= 1
    word = string[start + 1:index].strip()
    return start + 1, word


def is_outer_bracketed(s: str) -> bool:
    # Must have at least two chars and start with '(' and end with ')'
    if len(s) < 2 or s[0] != '(' or s[-1] != ')':
        return False

    depth = 0
    for i, ch in enumerate(s):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            # As soon as depth returns to zero, we've found the match for the first '('
            if depth == 0:
                # It's only a true “outer” bracket if that happens at the very end
                return i == len(s) - 1
            # guard against unbalanced “)” anywhere
            if depth < 0:
                return False

    # If we finish the loop without ever hitting depth==0,
    # then either it was never balanced or the last ')' was missing.
    return False




def remove_outer_brackets(s: str) -> str:
    """
    Repeatedly strip a single pair of outer parentheses if and only if
    the very first '(' matches with the very last ')' of the current string.
    """
    while True:
        # quick checks: must start with '(' and end with ')'
        if len(s) < 2 or s[0] != '(' or s[-1] != ')':
            break

        # walk through to see where the first '(' closes
        depth = 0
        for i, ch in enumerate(s):
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                # once we hit depth==0, that's the match for s[0]
                if depth == 0:
                    break
                # if it ever goes negative, it's unbalanced
                if depth < 0:
                    break

        # if that matching ')' isn’t the last char, we can’t strip it
        if i != len(s) - 1 or depth != 0:
            break

        # strip that outer pair and try again
        s = s[1:-1]

    return s


def extract_replace_outermost_bracketed(string: str, replacement:str) -> Tuple[str, str]:
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
                return string[:start] + replacement + string[i+1:], ensure_bracketed(string[start+1:i])

    return string, ""