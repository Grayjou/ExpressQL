Validators Module
=================

The validators module provides validation functions for SQL identifiers and values.

.. automodule:: expressql.validators
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: expressql.validators.is_number

.. autofunction:: expressql.validators.validate_name

.. autofunction:: expressql.validators.validate_subquery_safe

Example Usage
-------------

.. code-block:: python

   from expressql.validators import is_number, validate_name
   
   # Check if a value is a number
   is_number("42")      # True
   is_number("42.5")    # True
   is_number("abc")     # False
   
   # Validate a column name
   validate_name("user_id")     # OK
   validate_name("name")        # OK
   
   try:
       validate_name("user-id")  # Raises ValueError (invalid character)
   except ValueError as e:
       print(f"Validation error: {e}")
   
   try:
       validate_name("SELECT")   # Raises ValueError (forbidden keyword)
   except ValueError as e:
       print(f"Validation error: {e}")

Validation Rules
----------------

Column Name Rules
~~~~~~~~~~~~~~~~~

Valid column names must:

- Contain only alphanumeric characters and underscores
- Not start with a digit
- Not be a SQL reserved keyword
- Not contain forbidden characters

The validator checks against:

- ``forbidden_chars``: Special characters that could cause SQL injection
- ``forbidden_words``: SQL keywords that could cause parsing issues

Safety Features
---------------

These validators help prevent:

1. **SQL Injection**: By restricting allowed characters in identifiers
2. **Syntax Errors**: By preventing use of reserved keywords
3. **Parsing Issues**: By ensuring valid SQL identifier format

The validators are used internally by ExpressQL to ensure all generated SQL is safe.
