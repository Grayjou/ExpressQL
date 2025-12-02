"""
ExpressQL Subquery Placeholder - Utilities for parameterizing subqueries.

This module provides functions to safely parameterize SQL subqueries by replacing
literal values with placeholders and extracting the values into a separate list.
This helps prevent SQL injection and supports different placeholder styles.

Functions:
    parametrize_subquery: Replace literals in a subquery with placeholders

Example:
    >>> from expressql.parsers.subquery_placeholder import parametrize_subquery
    >>> sql, params = parametrize_subquery("age > 30 AND name = 'Alice'")
    >>> print(sql)
    age > %s AND name = %s
    >>> print(params)
    [30, 'Alice']
"""

import re
from typing import Tuple, List, Any

def parametrize_subquery(
    subquery: str,
    style: str = "%s"
) -> Tuple[str, List[Any]]:
    """
    Scan `subquery` for integer, float or single-quoted string literals,
    replace each with a placeholder, and collect their Python values.

    Args:
      subquery: SQL fragment, e.g. "age > 30 AND name = 'Alice'"
      style:    placeholder style
                - "%s" for psycopg2 / MySQLdb
                - "?"  for SQLite
                - "$"  for PostgreSQL numbered placeholders

    Returns:
      (new_subquery, values)
    """
    # match either single-quoted strings or numbers
    pattern = re.compile(r"""
        (                               # group 1: a string literal
          '(?:\\'|[^'])*'               #   '…' with escaped quotes
        )
        |                               # OR
        (                               # group 2: a number
          \b\d+(?:\.\d+)?\b             #   integer or decimal
        )
    """, re.VERBOSE)

    values: List[Any] = []
    counter = 0

    def _repl(m: re.Match) -> str:
        nonlocal counter
        counter += 1

        # which group matched?
        if m.group(1) is not None:
            # strip the surrounding quotes and un-escape
            raw = m.group(1)[1:-1]
            val = raw.replace("\\'", "'")
        else:
            num = m.group(2)
            val = float(num) if '.' in num else int(num)

        values.append(val)

        # choose placeholder format
        if style == "$":
            return f"${counter}"
        else:
            # treat style as a literal token ("%s" or "?")
            return style

    new_query = pattern.sub(_repl, subquery)
    return new_query, values
