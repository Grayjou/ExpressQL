ExpressQL Documentation
=======================

**ExpressQL** is a flexible, Pythonic Domain-Specific Language (DSL) for constructing complex SQL conditions and expressions safely and expressively.

It is designed to reduce boilerplate, prevent common SQL mistakes, and allow arithmetic, logical, and chained comparisons directly in Python syntax.

.. code-block:: python

   from expressql import col, cols
   
   age, salary, department = cols("age", "salary", "department")
   condition = ((age > 30) * (department == "HR")) + (salary > 50000)
   
   sql, params = condition.placeholder_pair()
   print(sql)
   # Output: ((age > ?) AND (department = ?)) OR (salary > ?)
   print(params)
   # Output: [30, 'HR', 50000]

Features
--------

✅ Arithmetic expressions with automatic SQL translation

✅ Logical composition (AND, OR, NOT) using natural Python operators

✅ Chained inequalities (``50 < col("age") < 80``)

✅ SQL-safe placeholder management

✅ Null-safe operations (``is_null``, ``not_null``)

✅ Set membership (``IN``, ``NOT IN``)

✅ Supports custom SQL functions (``Func(...)``)

✅ Fluent API for advanced condition building

✅ Parsing of SQL-like strings into expressions and conditions

✅ Automatic expansion of ``BETWEEN`` clauses into composite comparisons

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   quickstart
   user_guide/expressions
   user_guide/conditions
   user_guide/functions
   user_guide/parsing

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/base
   api/dsl
   api/functions
   api/parsers
   api/utils
   api/validators
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Additional Information
   
   examples
   changelog
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

