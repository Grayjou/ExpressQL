Quick Start
===========

Installation
------------

Install ExpressQL using pip:

.. code-block:: bash

   pip install expressql

For parsing features, install with the parsing extra:

.. code-block:: bash

   pip install expressql[parsing]

Basic Usage
-----------

Creating Columns
~~~~~~~~~~~~~~~~

Use the :func:`~expressql.col` or :func:`~expressql.cols` functions to create column expressions:

.. code-block:: python

   from expressql import col, cols
   
   # Create a single column
   age = col("age")
   
   # Create multiple columns at once
   name, email, status = cols("name", "email", "status")

Simple Comparisons
~~~~~~~~~~~~~~~~~~

Create SQL conditions using Python comparison operators:

.. code-block:: python

   from expressql import col
   
   age = col("age")
   salary = col("salary")
   
   # Greater than
   condition1 = age > 30
   print(condition1.placeholder_pair())
   # Output: ('age > ?', [30])
   
   # Equality
   condition2 = salary == 50000
   print(condition2.placeholder_pair())
   # Output: ('salary = ?', [50000])

Logical Operations
~~~~~~~~~~~~~~~~~~

Combine conditions using ``*`` for AND and ``+`` for OR:

.. code-block:: python

   from expressql import cols
   
   age, department, salary = cols("age", "department", "salary")
   
   # AND condition using *
   condition = (age > 30) * (department == "HR")
   print(condition.placeholder_pair())
   # Output: ('(age > ?) AND (department = ?)', [30, 'HR'])
   
   # OR condition using +
   condition = (age > 50) + (salary > 100000)
   print(condition.placeholder_pair())
   # Output: ('(age > ?) OR (salary > ?)', [50, 100000])
   
   # NOT condition using ~
   condition = ~(department == "IT")
   print(condition.placeholder_pair())
   # Output: ('NOT (department = ?)', ['IT'])

Chained Comparisons
~~~~~~~~~~~~~~~~~~~

ExpressQL supports chained comparisons just like Python:

.. code-block:: python

   from expressql import col
   
   score = col("score")
   
   # Chain comparisons naturally
   condition = 50 < score < 80
   print(condition.placeholder_pair())
   # Output: ('(score > ?) AND (score < ?)', [50, 80])

Arithmetic Expressions
~~~~~~~~~~~~~~~~~~~~~~

Perform arithmetic operations on columns:

.. code-block:: python

   from expressql import cols
   
   price, tax, discount = cols("price", "tax", "discount")
   
   # Calculate total with tax and discount
   total = (price * (1 + tax)) - discount
   
   condition = total > 100
   print(condition.placeholder_pair())
   # Output: ('((price * (? + tax)) - discount) > ?', [1, 100])

Using Functions
~~~~~~~~~~~~~~~

Call SQL functions on expressions:

.. code-block:: python

   from expressql import col, Func
   
   salary = col("salary")
   
   # Built-in function
   avg_salary = Func("AVG", salary)
   
   # Custom function
   custom_calc = Func("CUSTOM_CALC", salary, 1.5)
   print(custom_calc.placeholder_pair())
   # Output: ('CUSTOM_CALC(salary, ?)', [1.5])

NULL Operations
~~~~~~~~~~~~~~~

Check for NULL values:

.. code-block:: python

   from expressql import col
   
   email = col("email")
   
   # Check if NULL
   condition = email.is_null
   print(condition.placeholder_pair())
   # Output: ('email IS NULL', [])
   
   # Check if NOT NULL
   condition = email.not_null
   print(condition.placeholder_pair())
   # Output: ('email IS NOT NULL', [])

Set Operations
~~~~~~~~~~~~~~

Check membership in sets:

.. code-block:: python

   from expressql import col
   
   department = col("department")
   
   # IN condition
   condition = department.isin(["HR", "IT", "Sales"])
   print(condition.placeholder_pair())
   # Output: ('department IN (?, ?, ?)', ['HR', 'IT', 'Sales'])
   
   # NOT IN condition
   condition = department.not_in(["Marketing", "Legal"])
   print(condition.placeholder_pair())
   # Output: ('department NOT IN (?, ?)', ['Marketing', 'Legal'])

Parsing SQL Strings
~~~~~~~~~~~~~~~~~~~~

Parse SQL-like strings into expressions:

.. code-block:: python

   from expressql.parsers import parse_expression, parse_condition
   
   # Parse an expression
   expr = parse_expression("LOG(age, 10) + salary * 1.5")
   print(expr.placeholder_pair())
   
   # Parse a condition
   cond = parse_condition("age BETWEEN 30 AND 50 AND department = 'IT'")
   print(cond.placeholder_pair())
   # Output: ('(age >= ? AND age <= ?) AND (department = ?)', [30, 50, 'IT'])

Next Steps
----------

- Learn more about :doc:`user_guide/expressions`
- Explore :doc:`user_guide/conditions` in detail
- Check out :doc:`user_guide/functions` for SQL functions
- See :doc:`examples` for more complex use cases
