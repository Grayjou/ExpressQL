Functions
=========

ExpressQL supports SQL functions through the :class:`~expressql.Func` class and provides convenient shortcuts for common functions.

Basic Function Usage
--------------------

Using Func
~~~~~~~~~~

The :class:`~expressql.Func` class creates SQL function calls:

.. code-block:: python

   from expressql import col, Func
   
   salary = col("salary")
   age = col("age")
   
   # Simple function with one argument
   avg_salary = Func("AVG", salary)
   print(avg_salary.placeholder_pair())
   # Output: ('AVG(salary)', [])
   
   # Function with multiple arguments
   power_result = Func("POWER", age, 2)
   print(power_result.placeholder_pair())
   # Output: ('POWER(age, ?)', [2])
   
   # Function with literal values
   custom_calc = Func("CALCULATE", 100, 200, salary)
   print(custom_calc.placeholder_pair())
   # Output: ('CALCULATE(?, ?, salary)', [100, 200])

Uppercase Method Shortcuts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any uppercase method on an expression becomes a function call:

.. code-block:: python

   from expressql import col
   
   value = col("value")
   
   # These are equivalent:
   result1 = Func("ABS", value)
   result2 = value.ABS()
   
   print(result1.placeholder_pair())
   # Output: ('ABS(value)', [])
   
   print(result2.placeholder_pair())
   # Output: ('ABS(value)', [])

Common SQL Functions
--------------------

Aggregate Functions
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   salary = col("salary")
   employee_id = col("employee_id")
   
   # COUNT
   count_employees = Func("COUNT", employee_id)
   
   # SUM
   total_salary = Func("SUM", salary)
   
   # AVG
   average_salary = Func("AVG", salary)
   
   # MAX
   max_salary = Func("MAX", salary)
   
   # MIN
   min_salary = Func("MIN", salary)
   
   # COUNT DISTINCT
   unique_departments = Func("COUNT", Func("DISTINCT", col("department")))

Mathematical Functions
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   value = col("value")
   angle = col("angle")
   
   # ABS - Absolute value
   abs_value = Func("ABS", value)
   
   # ROUND - Round to specified decimals
   rounded = Func("ROUND", value, 2)
   
   # CEIL - Ceiling
   ceiling = Func("CEIL", value)
   
   # FLOOR - Floor
   floor_value = Func("FLOOR", value)
   
   # SQRT - Square root
   sqrt_value = Func("SQRT", value)
   
   # POWER - Exponentiation
   powered = Func("POWER", value, 3)
   
   # LOG - Logarithm
   log_value = Func("LOG", value, 10)  # base 10
   
   # EXP - Exponential
   exp_value = Func("EXP", value)
   
   # Trigonometric functions
   sin_value = Func("SIN", angle)
   cos_value = Func("COS", angle)
   tan_value = Func("TAN", angle)

String Functions
~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   name = col("name")
   text = col("text")
   
   # UPPER - Convert to uppercase
   upper_name = Func("UPPER", name)
   
   # LOWER - Convert to lowercase
   lower_name = Func("LOWER", name)
   
   # LENGTH - String length
   name_length = Func("LENGTH", name)
   
   # SUBSTRING - Extract substring
   first_three = Func("SUBSTRING", name, 1, 3)
   
   # CONCAT - Concatenate strings
   full_name = Func("CONCAT", col("first_name"), " ", col("last_name"))
   
   # TRIM - Remove whitespace
   trimmed = Func("TRIM", text)
   
   # REPLACE - Replace substring
   cleaned = Func("REPLACE", text, "old", "new")

Date and Time Functions
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   created_at = col("created_at")
   date_field = col("date_field")
   
   # CURRENT_TIMESTAMP
   now = Func("CURRENT_TIMESTAMP")
   
   # DATE - Extract date part
   date_only = Func("DATE", created_at)
   
   # YEAR, MONTH, DAY - Extract components
   year = Func("YEAR", created_at)
   month = Func("MONTH", created_at)
   day = Func("DAY", created_at)
   
   # DATE_ADD - Add interval
   future_date = Func("DATE_ADD", date_field, Func("INTERVAL", 7, "DAY"))
   
   # DATE_DIFF - Difference between dates
   days_diff = Func("DATEDIFF", col("end_date"), col("start_date"))
   
   # EXTRACT - Extract date part
   hour = Func("EXTRACT", "HOUR", "FROM", created_at)

Conditional Functions
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   status = col("status")
   amount = col("amount")
   
   # CASE - Conditional expression
   status_label = Func("CASE",
       Func("WHEN", status == 1, Func("THEN", "Active")),
       Func("WHEN", status == 0, Func("THEN", "Inactive")),
       Func("ELSE", "Unknown")
   )
   
   # COALESCE - Return first non-null value
   fallback_value = Func("COALESCE", col("optional_field"), "default")
   
   # NULLIF - Return NULL if values are equal
   safe_division = amount / Func("NULLIF", col("divisor"), 0)
   
   # IFNULL / ISNULL - Handle NULL values
   with_default = Func("IFNULL", col("nullable_field"), 0)

Functions in Expressions
-------------------------

Combine functions with arithmetic:

.. code-block:: python

   from expressql import col, Func
   
   weight = col("weight")
   height = col("height")
   age = col("age")
   
   # Calculate BMI with age adjustment
   bmi = weight / Func("POWER", height, 2)
   adjusted_bmi = bmi * (1 + age / 100)
   
   print(adjusted_bmi.placeholder_pair())
   
   # Use functions in conditions
   condition = Func("ABS", col("balance")) > 1000
   print(condition.placeholder_pair())
   # Output: ('ABS(balance) > ?', [1000])

Nested Functions
----------------

Functions can be nested:

.. code-block:: python

   from expressql import col, Func
   
   value = col("value")
   
   # Round the absolute value
   result = Func("ROUND", Func("ABS", value), 2)
   print(result.placeholder_pair())
   # Output: ('ROUND(ABS(value), ?)', [2])
   
   # Complex nested calculation
   salary = col("salary")
   normalized = Func("LOG", salary, 10) / Func("LOG", Func("MAX", salary), 10)

Custom Functions
----------------

Define your own database functions:

.. code-block:: python

   from expressql import col, Func
   
   # Custom function for your database
   result = Func("MY_CUSTOM_FUNCTION", col("input_col"), 42, "parameter")
   print(result.placeholder_pair())
   # Output: ('MY_CUSTOM_FUNCTION(input_col, ?, ?)', [42, 'parameter'])
   
   # Custom aggregate function
   custom_agg = Func("CUSTOM_AGGREGATE", col("value"))

Window Functions
----------------

Use window functions for analytics:

.. code-block:: python

   from expressql import col, Func
   
   salary = col("salary")
   department = col("department")
   
   # ROW_NUMBER
   row_num = Func("ROW_NUMBER")
   
   # RANK
   salary_rank = Func("RANK")
   
   # DENSE_RANK
   dense_rank = Func("DENSE_RANK")
   
   # LEAD / LAG
   next_value = Func("LEAD", salary, 1)
   prev_value = Func("LAG", salary, 1)
   
   # Note: OVER clause would need to be added separately in your query builder

Inverted Functions
------------------

Create inverted function results (1/result):

.. code-block:: python

   from expressql import col, Func
   
   value = col("value")
   
   # Normal function
   normal = Func("CUSTOM_CALC", value)
   print(normal.placeholder_pair())
   # Output: ('CUSTOM_CALC(value)', [])
   
   # Inverted function (1/result)
   inverted = Func("CUSTOM_CALC", value, inverted=True)
   print(inverted.placeholder_pair())
   # Output: ('1/CUSTOM_CALC(value)', [])

Using the functions Module
---------------------------

ExpressQL provides a functions module with pre-defined common functions:

.. code-block:: python

   from expressql import col
   from expressql import functions as f
   
   salary = col("salary")
   bonus = col("bonus")
   
   # Use pre-defined functions
   total = f.SUM(salary + bonus)
   average = f.AVG(salary)
   count = f.COUNT(col("employee_id"))
   
   # Mathematical functions
   abs_value = f.ABS(col("balance"))
   rounded = f.ROUND(salary, 2)
   
   # String functions
   upper_name = f.UPPER(col("name"))
   length = f.LENGTH(col("description"))

Best Practices
--------------

1. **Use appropriate function names**: Match your database's function names

   .. code-block:: python
   
      # Good - standard SQL
      result = Func("UPPER", col("name"))
      
      # Check your database docs for proprietary functions
      # MySQL: Func("SUBSTRING", col, start, length)
      # PostgreSQL: Func("SUBSTR", col, start, length)

2. **Type safety with arguments**: Be aware of expected types

   .. code-block:: python
   
      # Numeric functions expect numbers
      power = Func("POWER", col("value"), 2)  # OK
      
      # String functions expect strings
      upper = Func("UPPER", col("name"))  # OK

3. **Test complex functions**: Verify the SQL output

   .. code-block:: python
   
      complex_calc = Func("COMPLEX", arg1, arg2, arg3)
      sql, params = complex_calc.placeholder_pair()
      print(f"Generated: {sql}")
      print(f"Parameters: {params}")

4. **Consider NULL handling**: Many functions have special NULL behavior

   .. code-block:: python
   
      # Use COALESCE for NULL safety
      safe_value = Func("COALESCE", col("nullable_field"), 0)

5. **Aggregate functions in conditions**: Use with HAVING, not WHERE

   .. code-block:: python
   
      # Typically used with GROUP BY in your query builder
      avg_salary = Func("AVG", col("salary"))
      
      # Use in HAVING clause: avg_salary > 50000
      condition = avg_salary > 50000

Common Patterns
---------------

Calculate Percentages
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   value = col("value")
   total = col("total")
   
   # Percentage calculation
   percentage = (value * 100.0) / Func("NULLIF", total, 0)

Safe Division
~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   numerator = col("numerator")
   denominator = col("denominator")
   
   # Avoid division by zero
   safe_result = numerator / Func("NULLIF", denominator, 0)

Date Ranges
~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   created_at = col("created_at")
   
   # Records from last 30 days
   recent = created_at > Func("DATE_SUB",
       Func("CURRENT_DATE"),
       Func("INTERVAL", 30, "DAY")
   )

String Matching
~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   email = col("email")
   
   # Case-insensitive search
   condition = Func("LOWER", email).like("%@example.com")
