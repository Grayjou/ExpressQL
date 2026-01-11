Exceptions Module
=================

The exceptions module defines custom exceptions used throughout ExpressQL.

.. automodule:: expressql.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Exception Classes
-----------------

.. autoexception:: expressql.exceptions.ForbiddenCharacterError
   :members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from expressql.exceptions import ForbiddenCharacterError
   from expressql import col
   
   try:
       # This might raise ForbiddenCharacterError for invalid characters
       invalid_col = col("user;id")  # Semicolon is not allowed
   except ForbiddenCharacterError as e:
       print(f"Error: {e}")
       print(f"Forbidden characters: {e.forbidden_chars}")

Error Handling Best Practices
------------------------------

1. **Catch specific exceptions**: Handle different error types appropriately

   .. code-block:: python
   
      from expressql.exceptions import ForbiddenCharacterError
      
      try:
          # Your ExpressQL code
          result = build_complex_condition()
      except ForbiddenCharacterError as e:
          # Handle validation errors (user input issues)
          log.warning(f"Invalid input: {e}")
          return default_condition()
      except Exception as e:
          # Handle other errors
          log.error(f"Error: {e}")
          raise

2. **Validate user input early**: Catch errors before building complex queries

   .. code-block:: python
   
      from expressql.validators import validate_name
      
      def safe_column(name):
          try:
              validate_name(name)
              return col(name)
          except ValueError:
              raise ValueError(f"Invalid column name: {name}")

3. **Provide helpful error messages**: Include context in error handling

   .. code-block:: python
   
      from expressql.parsers import parse_condition
      
      try:
          condition = parse_condition(user_input)
      except Exception as e:
          raise ValueError(
              f"Failed to parse condition '{user_input}': {e}"
          ) from e
