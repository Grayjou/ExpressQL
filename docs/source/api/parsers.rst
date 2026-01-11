Parsers Module
==============

The parsers module provides functions to parse SQL-like strings into ExpressQL objects.

.. automodule:: expressql.parsers
   :members:
   :undoc-members:
   :show-inheritance:

Main Parser Functions
---------------------

.. autofunction:: expressql.parsers.parse_expression

.. autofunction:: expressql.parsers.parse_condition

.. autofunction:: expressql.parsers.parse_expr_or_cond

Sub-modules
-----------

Main Parser
~~~~~~~~~~~

.. automodule:: expressql.parsers.main
   :members:
   :undoc-members:
   :show-inheritance:

Conditions Parser
~~~~~~~~~~~~~~~~~

.. automodule:: expressql.parsers.conditions_parser
   :members:
   :undoc-members:
   :show-inheritance:

Expressions Parser
~~~~~~~~~~~~~~~~~~

.. automodule:: expressql.parsers.expressions_parser
   :members:
   :undoc-members:
   :show-inheritance:

Parsing Utilities
~~~~~~~~~~~~~~~~~

.. automodule:: expressql.parsers.parsing_utils
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

   from expressql.parsers import parse_expression, parse_condition
   
   # Parse an expression
   expr = parse_expression("LOG(age, 10) + salary * 1.5")
   sql, params = expr.placeholder_pair()
   
   # Parse a condition
   cond = parse_condition("age BETWEEN 30 AND 50 AND department = 'IT'")
   sql, params = cond.placeholder_pair()
