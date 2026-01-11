Conditions
==========

Conditions represent SQL WHERE clauses and boolean logic. They are created by comparing expressions and can be combined using logical operators.

Creating Conditions
-------------------

Comparison Operators
~~~~~~~~~~~~~~~~~~~~

Create conditions using Python's comparison operators:

.. code-block:: python

   from expressql import col
   
   age = col("age")
   salary = col("salary")
   department = col("department")
   
   # Equal to
   cond1 = age == 30
   print(cond1.placeholder_pair())
   # Output: ('age = ?', [30])
   
   # Not equal to
   cond2 = department != "HR"
   print(cond2.placeholder_pair())
   # Output: ('department != ?', ['HR'])
   
   # Greater than
   cond3 = salary > 50000
   
   # Less than
   cond4 = age < 65
   
   # Greater than or equal
   cond5 = salary >= 40000
   
   # Less than or equal
   cond6 = age <= 50

Chained Comparisons
~~~~~~~~~~~~~~~~~~~

ExpressQL supports Python-style chained comparisons:

.. code-block:: python

   from expressql import col
   
   age = col("age")
   score = col("score")
   
   # Age between 25 and 65
   condition = 25 <= age <= 65
   print(condition.placeholder_pair())
   # Output: ('(age >= ?) AND (age <= ?)', [25, 65])
   
   # Score in range (exclusive)
   condition = 50 < score < 100
   print(condition.placeholder_pair())
   # Output: ('(score > ?) AND (score < ?)', [50, 100])
   
   # Mixed comparisons
   condition = 0 <= score < 100
   print(condition.placeholder_pair())
   # Output: ('(score >= ?) AND (score < ?)', [0, 100])

Logical Operators
-----------------

AND Conditions
~~~~~~~~~~~~~~

Use ``*`` or ``&`` for AND logic:

.. code-block:: python

   from expressql import cols
   
   age, department, salary = cols("age", "department", "salary")
   
   # Using * operator (recommended)
   condition = (age > 30) * (department == "IT") * (salary > 50000)
   print(condition.placeholder_pair())
   # Output: ('(age > ?) AND (department = ?) AND (salary > ?)', [30, 'IT', 50000])
   
   # Using & operator (alternative)
   condition = (age > 30) & (department == "IT")

OR Conditions
~~~~~~~~~~~~~

Use ``+`` or ``|`` for OR logic:

.. code-block:: python

   from expressql import cols
   
   age, salary = cols("age", "salary")
   
   # Using + operator (recommended)
   condition = (age > 50) + (salary > 100000)
   print(condition.placeholder_pair())
   # Output: ('(age > ?) OR (salary > ?)', [50, 100000])
   
   # Using | operator (alternative)
   condition = (age < 25) | (age > 65)

NOT Conditions
~~~~~~~~~~~~~~

Use ``~`` for NOT logic:

.. code-block:: python

   from expressql import col
   
   department = col("department")
   active = col("active")
   
   # Negate a condition
   condition = ~(department == "IT")
   print(condition.placeholder_pair())
   # Output: ('NOT (department = ?)', ['IT'])
   
   # Negate complex conditions
   condition = ~((age > 50) * (active == True))
   print(condition.placeholder_pair())
   # Output: ('NOT ((age > ?) AND (active = ?))', [50, True])

Complex Logical Combinations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine multiple logical operators:

.. code-block:: python

   from expressql import cols
   
   age, dept, salary, active = cols("age", "department", "salary", "active")
   
   # (age > 30 AND dept = IT) OR (salary > 100000 AND active = true)
   condition = ((age > 30) * (dept == "IT")) + ((salary > 100000) * active.is_not_null)
   
   print(condition.placeholder_pair())

NULL Operations
---------------

Check for NULL values:

is_null
~~~~~~~

.. code-block:: python

   from expressql import col
   
   email = col("email")
   phone = col("phone")
   
   # Single NULL check
   condition = email.is_null
   print(condition.placeholder_pair())
   # Output: ('email IS NULL', [])
   
   # Combined with other conditions
   condition = email.is_null + phone.is_null
   print(condition.placeholder_pair())
   # Output: ('(email IS NULL) OR (phone IS NULL)', [])

not_null / is_not_null
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col
   
   email = col("email")
   
   # Check NOT NULL
   condition = email.not_null
   print(condition.placeholder_pair())
   # Output: ('email IS NOT NULL', [])
   
   # Alternative syntax
   condition = email.is_not_null

Set Operations
--------------

IN Conditions
~~~~~~~~~~~~~

Check if a column value is in a set:

.. code-block:: python

   from expressql import col
   
   department = col("department")
   status = col("status")
   
   # IN with list
   condition = department.isin(["HR", "IT", "Sales"])
   print(condition.placeholder_pair())
   # Output: ('department IN (?, ?, ?)', ['HR', 'IT', 'Sales'])
   
   # IN with tuple
   condition = status.isin(("active", "pending"))
   print(condition.placeholder_pair())
   # Output: ('status IN (?, ?)', ['active', 'pending'])

NOT IN Conditions
~~~~~~~~~~~~~~~~~

Check if a column value is NOT in a set:

.. code-block:: python

   from expressql import col
   
   department = col("department")
   
   # NOT IN
   condition = department.not_in(["Legal", "Compliance"])
   print(condition.placeholder_pair())
   # Output: ('department NOT IN (?, ?)', ['Legal', 'Compliance'])

String Operations
-----------------

LIKE Conditions
~~~~~~~~~~~~~~~

Pattern matching with LIKE:

.. code-block:: python

   from expressql import col
   
   name = col("name")
   email = col("email")
   
   # LIKE pattern
   condition = name.like("John%")
   print(condition.placeholder_pair())
   # Output: ('name LIKE ?', ['John%'])
   
   # Contains pattern
   condition = email.like("%@gmail.com")

NOT LIKE Conditions
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col
   
   email = col("email")
   
   # NOT LIKE pattern
   condition = email.not_like("%@spam.com")
   print(condition.placeholder_pair())
   # Output: ('email NOT LIKE ?', ['%@spam.com'])

BETWEEN Operations
------------------

Check if a value is within a range:

.. code-block:: python

   from expressql import col
   
   age = col("age")
   salary = col("salary")
   
   # BETWEEN (inclusive)
   condition = age.between(25, 65)
   print(condition.placeholder_pair())
   # Output: ('age BETWEEN ? AND ?', [25, 65])
   
   # NOT BETWEEN
   condition = salary.not_between(0, 30000)
   print(condition.placeholder_pair())
   # Output: ('salary NOT BETWEEN ? AND ?', [0, 30000])

Special Conditions
------------------

Always True
~~~~~~~~~~~

.. code-block:: python

   from expressql import TrueCondition
   
   # Condition that's always true
   always_true = TrueCondition()
   print(always_true.placeholder_pair())
   # Output: ('1 = 1', [])

Always False
~~~~~~~~~~~~

.. code-block:: python

   from expressql import FalseCondition
   
   # Condition that's always false
   always_false = FalseCondition()
   print(always_false.placeholder_pair())
   # Output: ('1 = 0', [])

No Condition
~~~~~~~~~~~~

.. code-block:: python

   from expressql import no_condition
   
   # Empty condition (useful for building dynamic queries)
   condition = no_condition()
   print(condition.placeholder_pair())
   # Output: ('', [])

Working with WHERE Clauses
---------------------------

Convert conditions to WHERE clause strings:

.. code-block:: python

   from expressql import cols, where_string
   
   age, department = cols("age", "department")
   
   condition = (age > 30) * (department == "IT")
   
   # Get WHERE clause
   where_clause = where_string(condition)
   print(where_clause)
   # Output: WHERE (age > ?) AND (department = ?)

Primary Key Conditions
~~~~~~~~~~~~~~~~~~~~~~

Create conditions for primary keys:

.. code-block:: python

   from expressql.dsl import pk_condition
   
   # Single primary key
   pk_cond = pk_condition({"id": 123})
   print(pk_cond.placeholder_pair())
   # Output: ('id = ?', [123])
   
   # Composite primary key
   pk_cond = pk_condition({"user_id": 123, "account_id": 456})
   print(pk_cond.placeholder_pair())
   # Output: ('(user_id = ?) AND (account_id = ?)', [123, 456])

Best Practices
--------------

1. **Always use placeholders**: Never concatenate values directly

   .. code-block:: python
   
      # GOOD: Uses placeholders
      age = col("age")
      condition = age > 30
      
      # BAD: SQL injection risk (don't do this manually)
      # sql = f"age > {user_input}"  # NEVER DO THIS

2. **Use parentheses for complex logic**: Make precedence explicit

   .. code-block:: python
   
      # Clear precedence
      condition = ((a > 10) * (b < 20)) + ((c == 5) * (d != 0))

3. **Test generated SQL**: Always check the output

   .. code-block:: python
   
      condition = complex_condition_here
      sql, params = condition.placeholder_pair()
      print(f"SQL: {sql}")
      print(f"Params: {params}")

4. **Reuse conditions**: Build conditions incrementally

   .. code-block:: python
   
      base_condition = active == True
      
      if user_filter:
          condition = base_condition * (user_id == user_filter)
      else:
          condition = base_condition

5. **Handle NULL carefully**: Remember SQL NULL semantics

   .. code-block:: python
   
      # NULL comparisons require special operators
      email = col("email")
      
      # GOOD
      is_missing = email.is_null
      
      # BAD (won't work as expected in SQL)
      # is_missing = email == None
