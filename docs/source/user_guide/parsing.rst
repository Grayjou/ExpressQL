Parsing
=======

ExpressQL includes powerful parsing capabilities that allow you to convert SQL-like strings into safe, parameterized expressions and conditions.

Overview
--------

The parsing module provides three main functions:

- :func:`~expressql.parsers.parse_expression` - Parse arithmetic and function expressions
- :func:`~expressql.parsers.parse_condition` - Parse WHERE clause conditions
- :func:`~expressql.parsers.parse_expr_or_cond` - Automatically detect and parse either type

Installation
------------

Parsing features require the ``sqlparse`` library:

.. code-block:: bash

   pip install expressql[parsing]

Or install ``sqlparse`` separately:

.. code-block:: bash

   pip install sqlparse

Parsing Expressions
-------------------

Basic Expression Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~

Parse arithmetic expressions and function calls:

.. code-block:: python

   from expressql.parsers import parse_expression
   
   # Simple arithmetic
   expr = parse_expression("age + 10")
   print(expr.placeholder_pair())
   # Output: ('(age + ?)', [10])
   
   # Multiple operations
   expr = parse_expression("salary * 1.1 - tax")
   print(expr.placeholder_pair())
   # Output: ('((salary * ?) - tax)', [1.1])
   
   # Complex expression
   expr = parse_expression("(price * quantity) * (1 + tax_rate)")
   print(expr.placeholder_pair())
   # Output: ('((price * quantity) * (? + tax_rate))', [1])

Function Parsing
~~~~~~~~~~~~~~~~

Parse SQL functions within expressions:

.. code-block:: python

   from expressql.parsers import parse_expression
   
   # Simple function
   expr = parse_expression("LOG(age, 10)")
   print(expr.placeholder_pair())
   # Output: ('LOG(age, ?)', [10])
   
   # Nested functions
   expr = parse_expression("ROUND(ABS(balance), 2)")
   print(expr.placeholder_pair())
   # Output: ('ROUND(ABS(balance), ?)', [2])
   
   # Functions with expressions
   expr = parse_expression("POWER(height, 2) + weight")
   print(expr.placeholder_pair())
   # Output: ('(POWER(height, ?) + weight)', [2])

Complex Expression Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql.parsers import parse_expression
   
   # BMI calculation
   expr = parse_expression("weight / POWER(height, 2)")
   print(expr.placeholder_pair())
   # Output: ('(weight / POWER(height, ?))', [2])
   
   # Financial calculation
   expr = parse_expression("LOG(salary, 10) + CUSTOM_FUNC(bonus + 100, 1.5)")
   print(expr.placeholder_pair())
   # Output: ('(LOG(salary, ?) + CUSTOM_FUNC((bonus + ?), ?))', [10, 100, 1.5])
   
   # String concatenation
   expr = parse_expression("first_name || ' ' || last_name")
   print(expr.placeholder_pair())
   # Output: ('(first_name || ? || last_name)', [' '])

Parsing Conditions
------------------

Basic Condition Parsing
~~~~~~~~~~~~~~~~~~~~~~~~

Parse comparison conditions:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # Simple comparison
   cond = parse_condition("age > 30")
   print(cond.placeholder_pair())
   # Output: ('age > ?', [30])
   
   # Equality
   cond = parse_condition("department = 'IT'")
   print(cond.placeholder_pair())
   # Output: ('department = ?', ['IT'])
   
   # Not equal
   cond = parse_condition("status != 'inactive'")
   print(cond.placeholder_pair())
   # Output: ('status != ?', ['inactive'])

Logical Operators
~~~~~~~~~~~~~~~~~

Parse AND, OR, and NOT conditions:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # AND condition
   cond = parse_condition("age > 30 AND department = 'IT'")
   print(cond.placeholder_pair())
   # Output: ('(age > ?) AND (department = ?)', [30, 'IT'])
   
   # OR condition
   cond = parse_condition("age < 25 OR age > 65")
   print(cond.placeholder_pair())
   # Output: ('(age < ?) OR (age > ?)', [25, 65])
   
   # Complex logic
   cond = parse_condition("(age > 30 AND dept = 'IT') OR salary > 100000")
   print(cond.placeholder_pair())
   # Output: ('((age > ?) AND (dept = ?)) OR (salary > ?)', [30, 'IT', 100000])
   
   # NOT condition
   cond = parse_condition("NOT (department = 'HR')")
   print(cond.placeholder_pair())
   # Output: ('NOT (department = ?)', ['HR'])

BETWEEN Clauses
~~~~~~~~~~~~~~~

BETWEEN is automatically converted to composite comparisons:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # BETWEEN (inclusive)
   cond = parse_condition("age BETWEEN 30 AND 50")
   print(cond.placeholder_pair())
   # Output: ('(age >= ?) AND (age <= ?)', [30, 50])
   
   # BETWEEN with expressions
   cond = parse_condition("salary * 1.1 BETWEEN 40000 AND 80000")
   print(cond.placeholder_pair())
   # Output: ('((salary * ?) >= ?) AND ((salary * ?) <= ?)', [1.1, 40000, 1.1, 80000])
   
   # Combined with other conditions
   cond = parse_condition("age BETWEEN 25 AND 65 AND department = 'IT'")
   print(cond.placeholder_pair())
   # Output: ('((age >= ?) AND (age <= ?)) AND (department = ?)', [25, 65, 'IT'])

IN Clauses
~~~~~~~~~~

Parse IN and NOT IN conditions:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # IN condition
   cond = parse_condition("department IN ('IT', 'HR', 'Sales')")
   print(cond.placeholder_pair())
   # Output: ('department IN (?, ?, ?)', ['IT', 'HR', 'Sales'])
   
   # NOT IN condition
   cond = parse_condition("status NOT IN ('deleted', 'archived')")
   print(cond.placeholder_pair())
   # Output: ('status NOT IN (?, ?)', ['deleted', 'archived'])
   
   # IN with numbers
   cond = parse_condition("id IN (1, 2, 3, 4, 5)")
   print(cond.placeholder_pair())
   # Output: ('id IN (?, ?, ?, ?, ?)', [1, 2, 3, 4, 5])

NULL Conditions
~~~~~~~~~~~~~~~

Parse NULL checks:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # IS NULL
   cond = parse_condition("email IS NULL")
   print(cond.placeholder_pair())
   # Output: ('email IS NULL', [])
   
   # IS NOT NULL
   cond = parse_condition("phone IS NOT NULL")
   print(cond.placeholder_pair())
   # Output: ('phone IS NOT NULL', [])
   
   # Combined with other conditions
   cond = parse_condition("email IS NULL OR phone IS NULL")
   print(cond.placeholder_pair())
   # Output: ('(email IS NULL) OR (phone IS NULL)', [])

LIKE Patterns
~~~~~~~~~~~~~

Parse LIKE pattern matching:

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # LIKE pattern
   cond = parse_condition("name LIKE 'John%'")
   print(cond.placeholder_pair())
   # Output: ('name LIKE ?', ['John%'])
   
   # NOT LIKE pattern
   cond = parse_condition("email NOT LIKE '%@spam.com'")
   print(cond.placeholder_pair())
   # Output: ('email NOT LIKE ?', ['%@spam.com'])

Advanced Parsing
----------------

BETWEEN Transformation
~~~~~~~~~~~~~~~~~~~~~~

Transform BETWEEN clauses before parsing:

.. code-block:: python

   from expressql.parsers import transform_betweens
   
   # Transform BETWEEN to range comparisons
   sql = "age BETWEEN 18 AND 65"
   transformed = transform_betweens(sql)
   print(transformed)
   # Output: '(age >= 18 AND age <= 65)'
   
   # Complex expression with BETWEEN
   sql = "weight/POWER(height, 2) BETWEEN 18.5 AND 24.9"
   transformed = transform_betweens(sql)
   print(transformed)
   # Output: '(weight / POWER(height, 2) >= 18.5 AND weight / POWER(height, 2) <= 24.9)'
   
   # Multiple BETWEENs
   sql = "age BETWEEN 25 AND 65 AND salary BETWEEN 40000 AND 80000"
   transformed = transform_betweens(sql)
   print(transformed)
   # Output: '(age >= 25 AND age <= 65 AND salary >= 40000 AND salary <= 80000)'

Auto-Detection
~~~~~~~~~~~~~~

Automatically detect and parse expressions or conditions:

.. code-block:: python

   from expressql.parsers import parse_expr_or_cond
   
   # Detects expression
   result = parse_expr_or_cond("salary * 1.1 + bonus")
   print(result.placeholder_pair())
   # Output: ('((salary * ?) + bonus)', [1.1])
   
   # Detects condition
   result = parse_expr_or_cond("age > 30 AND department = 'IT'")
   print(result.placeholder_pair())
   # Output: ('(age > ?) AND (department = ?)', [30, 'IT'])

Combining Parsed and Manual
----------------------------

Mix parsed conditions with manual construction:

.. code-block:: python

   from expressql import col
   from expressql.parsers import parse_condition
   
   # Parse base condition
   base_cond = parse_condition("age > 30 AND department = 'IT'")
   
   # Add manual condition
   salary = col("salary")
   full_cond = base_cond * (salary > 50000)
   
   print(full_cond.placeholder_pair())
   # Output: ('((age > ?) AND (department = ?)) AND (salary > ?)', [30, 'IT', 50000])

Dynamic Query Building
----------------------

Build queries dynamically based on user input:

.. code-block:: python

   from expressql.parsers import parse_condition
   from expressql import no_condition
   
   def build_dynamic_condition(filters):
       """Build condition from dictionary of filters."""
       condition = no_condition()
       
       for field, value in filters.items():
           if value is not None:
               # Parse user filter
               filter_str = f"{field} = '{value}'"
               parsed = parse_condition(filter_str)
               
               # Combine with existing conditions
               if condition.sql_string():
                   condition = condition * parsed
               else:
                   condition = parsed
       
       return condition
   
   # Usage
   filters = {
       "department": "IT",
       "status": "active"
   }
   
   condition = build_dynamic_condition(filters)
   print(condition.placeholder_pair())

Error Handling
--------------

The parser handles various edge cases:

.. code-block:: python

   from expressql.parsers import parse_expression, parse_condition
   
   try:
       # Valid expression
       expr = parse_expression("age + 10")
       
       # Valid condition
       cond = parse_condition("age > 30")
       
   except ValueError as e:
       print(f"Parsing error: {e}")
   
   except Exception as e:
       print(f"Unexpected error: {e}")

Best Practices
--------------

1. **Validate user input**: Never trust user input directly

   .. code-block:: python
   
      def safe_parse(user_input):
          # Add validation here
          if not user_input or len(user_input) > 1000:
              raise ValueError("Invalid input")
          
          # Additional validation based on your needs
          
          return parse_condition(user_input)

2. **Use BETWEEN transformation for complex expressions**:

   .. code-block:: python
   
      from expressql.parsers import transform_betweens, parse_condition
      
      sql = "complex_expr BETWEEN 10 AND 20"
      transformed = transform_betweens(sql)
      condition = parse_condition(transformed)

3. **Test parsed SQL**: Always verify the output

   .. code-block:: python
   
      parsed = parse_condition(user_input)
      sql, params = parsed.placeholder_pair()
      print(f"Generated SQL: {sql}")
      print(f"Parameters: {params}")
      # Verify this matches expectations

4. **Combine with manual construction**: Use parsing where it helps

   .. code-block:: python
   
      # Parse complex user input
      user_condition = parse_condition(user_filter_string)
      
      # Add application-level filters manually
      app_condition = col("tenant_id") == current_tenant_id
      
      # Combine
      final_condition = user_condition * app_condition

5. **Handle parsing errors gracefully**:

   .. code-block:: python
   
      try:
          condition = parse_condition(user_input)
      except Exception as e:
          # Log error
          logger.error(f"Failed to parse condition: {e}")
          # Return safe default or error to user
          return no_condition()

Limitations
-----------

1. **Subqueries**: The parser doesn't handle subqueries
2. **Window functions**: OVER clauses are not fully supported
3. **Complex CASE statements**: Very nested CASE may not parse correctly
4. **Database-specific syntax**: Stick to standard SQL for best results

Performance Considerations
--------------------------

Parsing has overhead, so consider:

1. **Cache parsed conditions**: Don't re-parse the same string repeatedly

   .. code-block:: python
   
      from functools import lru_cache
      
      @lru_cache(maxsize=128)
      def cached_parse(condition_string):
          return parse_condition(condition_string)

2. **Parse at initialization**: Parse static conditions once at startup

   .. code-block:: python
   
      # At module level
      COMMON_FILTERS = {
          "active": parse_condition("status = 'active'"),
          "admin": parse_condition("role = 'admin'"),
      }

3. **Prefer manual construction for known conditions**: Faster than parsing

   .. code-block:: python
   
      # Faster
      condition = col("status") == "active"
      
      # Slower (but more flexible)
      condition = parse_condition("status = 'active'")
