Utils Module
============

The utils module provides utility functions for SQL string formatting and validation.

.. automodule:: expressql.utils
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: expressql.utils.parse_number

.. autofunction:: expressql.utils.format_sql_value

.. autofunction:: expressql.utils.bracket_string_sandwich

.. autofunction:: expressql.utils.ensure_bracketed

.. autofunction:: expressql.utils.normalize_args

.. autofunction:: expressql.utils.merge_placeholders

Constants
---------

.. autodata:: expressql.utils.forbidden_chars
   :annotation: = Set of characters forbidden in column names

.. autodata:: expressql.utils.forbidden_words
   :annotation: = Set of SQL keywords forbidden in column names

Example Usage
-------------

.. code-block:: python

   from expressql.utils import parse_number, format_sql_value
   
   # Parse a number from string
   num = parse_number("42.5")
   # Result: 42.5
   
   # Format a value for SQL
   formatted = format_sql_value("John's Test")
   # Result: properly escaped string
   
   # Check forbidden characters
   from expressql.utils import forbidden_chars, forbidden_words
   
   print(forbidden_chars)
   print(forbidden_words)
