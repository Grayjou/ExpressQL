Expressions
===========

Expressions are the building blocks of SQL queries in ExpressQL. They represent SQL values, columns, arithmetic operations, and function calls.

Column Expressions
------------------

Column expressions represent database columns:

.. code-block:: python

   from expressql import col, cols
   
   # Single column
   age = col("age")
   
   # Multiple columns
   name, email, salary = cols("name", "email", "salary")
   
   # From comma-separated string
   col1, col2, col3 = cols("col1, col2, col3")

Value Expressions
-----------------

ExpressQL automatically handles values:

.. code-block:: python

   from expressql import col, num, text
   
   age = col("age")
   
   # Numbers are automatically handled
   condition = age > 30  # 30 becomes a value expression
   
   # Explicit value creation (rarely needed)
   salary = col("salary")
   bonus = num(5000)
   total = salary + bonus
   
   # Text values
   dept = col("department")
   hr_dept = text("HR")
   condition = dept == hr_dept

Arithmetic Operations
---------------------

ExpressQL supports all standard arithmetic operations:

Addition and Subtraction
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   a, b = cols("a", "b")
   
   # Addition
   sum_expr = a + b + 10
   print(sum_expr.placeholder_pair())
   # Output: ('(a + b + ?)', [10])
   
   # Subtraction
   diff_expr = a - b - 5
   print(diff_expr.placeholder_pair())
   # Output: ('(a - b - ?)', [5])

Multiplication and Division
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   price, quantity, tax_rate = cols("price", "quantity", "tax_rate")
   
   # Calculate total with tax
   subtotal = price * quantity
   total = subtotal * (1 + tax_rate)
   
   print(total.placeholder_pair())
   # Output: ('((price * quantity) * (? + tax_rate))', [1])
   
   # Division
   average = (a + b) / 2
   print(average.placeholder_pair())
   # Output: ('((a + b) / ?)', [2])

Power and Modulo
~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   base, exponent = cols("base", "exponent")
   
   # Power
   power_expr = base ** exponent
   print(power_expr.placeholder_pair())
   # Output: ('POWER(base, exponent)', [])
   
   # With literal values
   squared = base ** 2
   print(squared.placeholder_pair())
   # Output: ('POWER(base, ?)', [2])
   
   # Modulo
   remainder = base % 10
   print(remainder.placeholder_pair())
   # Output: ('(base % ?)', [10])

Absolute Value
~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col
   
   balance = col("balance")
   
   # Absolute value
   abs_balance = abs(balance)
   print(abs_balance.placeholder_pair())
   # Output: ('ABS(balance)', [])

String Concatenation
--------------------

Use the ``|`` operator for SQL string concatenation:

.. code-block:: python

   from expressql import cols
   
   first_name, last_name = cols("first_name", "last_name")
   
   # Concatenate with space
   full_name = first_name | " " | last_name
   print(full_name.placeholder_pair())
   # Output: ('(first_name || ? || last_name)', [' '])

Complex Expressions
-------------------

Combine multiple operations:

.. code-block:: python

   from expressql import cols, Func
   
   weight, height, age = cols("weight", "height", "age")
   
   # Body Mass Index with age adjustment
   bmi = weight / (height ** 2)
   adjusted_bmi = bmi * (1 + age / 100)
   
   print(adjusted_bmi.placeholder_pair())
   # Output: ('((weight / POWER(height, ?)) * (? + (age / ?)))', [2, 1, 100])
   
   # Using functions in expressions
   log_salary = Func("LOG", col("salary"), 10)
   normalized = log_salary / Func("MAX", log_salary)

Expression Methods
------------------

Expressions provide several useful methods:

placeholder_pair()
~~~~~~~~~~~~~~~~~~

Returns a tuple of (SQL string, parameter list):

.. code-block:: python

   from expressql import col
   
   age = col("age")
   condition = age > 30
   
   sql, params = condition.placeholder_pair()
   print(f"SQL: {sql}")
   print(f"Parameters: {params}")

sql_string()
~~~~~~~~~~~~

Returns just the SQL string without parameters:

.. code-block:: python

   from expressql import cols
   
   a, b = cols("a", "b")
   expr = a + b * 2
   
   print(expr.sql_string())
   # Output: (a + (b * ?))

Comparison Operations
---------------------

Create conditions from expressions:

.. code-block:: python

   from expressql import col
   
   salary = col("salary")
   
   # All comparison operators
   gt = salary > 50000
   gte = salary >= 50000
   lt = salary < 100000
   lte = salary <= 100000
   eq = salary == 75000
   neq = salary != 0
   
   # Each returns a SQLCondition object
   print(gt.placeholder_pair())
   # Output: ('salary > ?', [50000])

Advanced Usage
--------------

Aliases
~~~~~~~

Add aliases to expressions:

.. code-block:: python

   from expressql import col
   
   salary = col("salary")
   
   # Create expression with alias
   avg_salary = salary.as_("average_salary")
   
   print(avg_salary.placeholder_pair())
   # Output: ('salary AS average_salary', [])

Inverted Expressions
~~~~~~~~~~~~~~~~~~~~

Create inverse expressions:

.. code-block:: python

   from expressql import Func, col
   
   value = col("value")
   
   # Normal function
   func = Func("CUSTOM", value)
   
   # Inverted (1/result)
   inverted = Func("CUSTOM", value, inverted=True)
   print(inverted.placeholder_pair())
   # Output: ('1/CUSTOM(value)', [])

Best Practices
--------------

1. **Use descriptive column names**: Make your code self-documenting

   .. code-block:: python
   
      # Good
      customer_age = col("customer_age")
      
      # Less clear
      ca = col("ca")

2. **Group complex expressions**: Use parentheses for clarity

   .. code-block:: python
   
      price, tax, discount = cols("price", "tax", "discount")
      
      # Clear grouping
      total = (price * (1 + tax)) - discount

3. **Reuse expressions**: Don't repeat complex calculations

   .. code-block:: python
   
      weight, height = cols("weight", "height")
      
      # Calculate once
      bmi = weight / (height ** 2)
      
      # Reuse in multiple conditions
      underweight = bmi < 18.5
      overweight = bmi > 25

4. **Check the generated SQL**: Always verify with ``placeholder_pair()``

   .. code-block:: python
   
      expr = (a + b) * c
      sql, params = expr.placeholder_pair()
      print(f"Generated SQL: {sql}")
