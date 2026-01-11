Examples
========

This page provides comprehensive examples of using ExpressQL in various scenarios.

Basic Examples
--------------

Simple Filtering
~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, cols
   
   # Filter users by age
   age = col("age")
   adults = age >= 18
   
   sql, params = adults.placeholder_pair()
   # Use in your query: SELECT * FROM users WHERE age >= ?
   # Parameters: [18]

Multiple Conditions
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   age, status, department = cols("age", "status", "department")
   
   # Active adult employees in IT
   condition = (age >= 18) * (status == "active") * (department == "IT")
   
   sql, params = condition.placeholder_pair()
   # SQL: (age >= ?) AND (status = ?) AND (department = ?)
   # Parameters: [18, 'active', 'IT']

Intermediate Examples
---------------------

Complex Business Logic
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   age, salary, years_experience, department = cols(
       "age", "salary", "years_experience", "department"
   )
   
   # Senior employees: high salary OR long experience, and not in training
   senior_emp = (
       ((salary > 100000) + (years_experience > 10))
       * ~(department == "Training")
   )
   
   sql, params = senior_emp.placeholder_pair()

Dynamic Filtering
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, no_condition
   
   def build_filter(age_min=None, age_max=None, departments=None):
       """Build a dynamic filter based on provided parameters."""
       condition = no_condition()
       
       age = col("age")
       if age_min is not None:
           condition = condition * (age >= age_min)
       
       if age_max is not None:
           condition = condition * (age <= age_max)
       
       if departments:
           dept = col("department")
           condition = condition * dept.isin(departments)
       
       return condition
   
   # Usage
   filter1 = build_filter(age_min=25, departments=["IT", "HR"])
   filter2 = build_filter(age_max=65)
   filter3 = build_filter(age_min=30, age_max=50, departments=["Sales"])

Arithmetic Calculations
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols, Func
   
   weight, height = cols("weight", "height")
   
   # Calculate BMI and categorize
   bmi = weight / (height ** 2)
   
   underweight = bmi < 18.5
   healthy = (18.5 <= bmi) * (bmi < 25)
   overweight = (25 <= bmi) * (bmi < 30)
   obese = bmi >= 30
   
   # Get people with healthy BMI
   sql, params = healthy.placeholder_pair()

Advanced Examples
-----------------

Financial Calculations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols, Func
   
   price, quantity, tax_rate, discount = cols(
       "price", "quantity", "tax_rate", "discount"
   )
   
   # Calculate total with tax and discount
   subtotal = price * quantity
   tax_amount = subtotal * tax_rate
   total = subtotal + tax_amount - discount
   
   # Find orders over $1000
   large_orders = total > 1000
   
   sql, params = large_orders.placeholder_pair()

Date Range Filtering
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   created_at = col("created_at")
   
   # Records from last 30 days
   recent = created_at > Func(
       "DATE_SUB",
       Func("CURRENT_DATE"),
       Func("INTERVAL", 30, "DAY")
   )
   
   # Records from specific month
   january_2024 = (
       Func("YEAR", created_at) == 2024
   ) * (
       Func("MONTH", created_at) == 1
   )

String Manipulation
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols, Func
   
   first_name, last_name, email = cols("first_name", "last_name", "email")
   
   # Full name
   full_name = first_name | " " | last_name
   
   # Email validation (contains @)
   valid_email = email.like("%@%")
   
   # Case-insensitive search
   name_search = Func("LOWER", full_name).like("%john%")

Aggregation Examples
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, Func
   
   salary = col("salary")
   department = col("department")
   
   # Average salary condition
   avg_salary = Func("AVG", salary)
   above_average = salary > avg_salary
   
   # Count by department (use in GROUP BY)
   dept_count = Func("COUNT", col("employee_id"))

Real-World Use Cases
--------------------

User Authentication Filter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   email, password_hash, is_active, email_verified = cols(
       "email", "password_hash", "is_active", "email_verified"
   )
   
   def authenticate_user(email_input, password_input):
       """Build condition for user authentication."""
       # Match email, must be active and verified
       condition = (
           (email == email_input)
           * is_active.is_not_null
           * (email_verified == True)
       )
       
       # Then check password hash separately in application
       return condition

E-commerce Product Filter
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols
   
   price, category, in_stock, rating, brand = cols(
       "price", "category", "in_stock", "rating", "brand"
   )
   
   def filter_products(min_price=None, max_price=None, categories=None,
                      only_in_stock=True, min_rating=None, brands=None):
       """Build dynamic product filter."""
       condition = True  # Start with TrueCondition
       
       if min_price is not None:
           condition = condition * (price >= min_price)
       
       if max_price is not None:
           condition = condition * (price <= max_price)
       
       if categories:
           condition = condition * category.isin(categories)
       
       if only_in_stock:
           condition = condition * (in_stock > 0)
       
       if min_rating is not None:
           condition = condition * (rating >= min_rating)
       
       if brands:
           condition = condition * brand.isin(brands)
       
       return condition

Employee Search System
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import cols, Func
   
   first_name, last_name, department, salary, hire_date = cols(
       "first_name", "last_name", "department", "salary", "hire_date"
   )
   
   def search_employees(name_query=None, dept_list=None,
                       salary_min=None, hired_after=None):
       """Search employees with multiple criteria."""
       conditions = []
       
       # Name search (case-insensitive, partial match)
       if name_query:
           full_name = first_name | " " | last_name
           name_match = Func("LOWER", full_name).like(f"%{name_query.lower()}%")
           conditions.append(name_match)
       
       # Department filter
       if dept_list:
           conditions.append(department.isin(dept_list))
       
       # Salary filter
       if salary_min:
           conditions.append(salary >= salary_min)
       
       # Hire date filter
       if hired_after:
           conditions.append(hire_date > hired_after)
       
       # Combine all conditions with AND
       if not conditions:
           return no_condition()
       
       result = conditions[0]
       for cond in conditions[1:]:
           result = result * cond
       
       return result

Multi-Tenant Application
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql import col, cols
   
   def tenant_filter(tenant_id, user_role=None, additional_condition=None):
       """Add tenant isolation to queries."""
       tenant_col = col("tenant_id")
       base_condition = tenant_col == tenant_id
       
       # Add role-based filtering
       if user_role and user_role != "admin":
           role_col = col("role")
           base_condition = base_condition * (role_col == user_role)
       
       # Add any additional conditions
       if additional_condition:
           base_condition = base_condition * additional_condition
       
       return base_condition

Parsing Examples
----------------

Parse User Input
~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql.parsers import parse_condition
   
   # User provides filter as string
   user_filter = "age > 25 AND department IN ('IT', 'HR') AND salary >= 50000"
   
   condition = parse_condition(user_filter)
   sql, params = condition.placeholder_pair()
   # Safe parameterized query

Complex Expression Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql.parsers import parse_expression
   
   # Parse a complex calculation
   formula = "(salary + bonus) * 1.1 - tax"
   expr = parse_expression(formula)
   
   # Use in a condition
   threshold = expr > 100000
   sql, params = threshold.placeholder_pair()

BETWEEN Clause Handling
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from expressql.parsers import parse_condition, transform_betweens
   
   # Original condition with BETWEEN
   condition_str = "age BETWEEN 25 AND 65 AND salary BETWEEN 40000 AND 100000"
   
   # Transform BETWEEN to range comparisons
   transformed = transform_betweens(condition_str)
   
   # Parse into condition
   condition = parse_condition(transformed)
   sql, params = condition.placeholder_pair()

Integration Examples
--------------------

With SQLite
~~~~~~~~~~~

.. code-block:: python

   import sqlite3
   from expressql import cols
   
   conn = sqlite3.connect("database.db")
   cursor = conn.cursor()
   
   # Build condition
   age, department = cols("age", "department")
   condition = (age > 30) * (department == "IT")
   
   # Generate SQL and parameters
   where_sql, params = condition.placeholder_pair()
   
   # Execute query
   query = f"SELECT * FROM employees WHERE {where_sql}"
   cursor.execute(query, params)
   
   results = cursor.fetchall()

With PostgreSQL (psycopg2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import psycopg2
   from expressql import cols
   
   conn = psycopg2.connect("dbname=mydb user=myuser")
   cursor = conn.cursor()
   
   # Build condition
   salary, years_exp = cols("salary", "years_experience")
   condition = (salary > 50000) + (years_exp > 5)
   
   # Generate SQL (PostgreSQL uses %s for placeholders)
   where_sql, params = condition.placeholder_pair()
   query = f"SELECT * FROM employees WHERE {where_sql}"
   
   # Replace ? with %s for PostgreSQL
   query = query.replace("?", "%s")
   
   cursor.execute(query, params)
   results = cursor.fetchall()

With MySQL
~~~~~~~~~~

.. code-block:: python

   import mysql.connector
   from expressql import col
   
   conn = mysql.connector.connect(
       host="localhost",
       user="myuser",
       password="mypass",
       database="mydb"
   )
   cursor = conn.cursor()
   
   # Build condition
   status = col("status")
   condition = status == "active"
   
   where_sql, params = condition.placeholder_pair()
   query = f"SELECT * FROM users WHERE {where_sql}"
   
   cursor.execute(query, params)
   results = cursor.fetchall()

Best Practices Summary
----------------------

1. **Always use placeholders**: Let ExpressQL handle parameterization
2. **Build incrementally**: Start simple and add complexity
3. **Test generated SQL**: Check output with ``placeholder_pair()``
4. **Reuse conditions**: Don't repeat complex logic
5. **Validate input**: Especially when parsing user-provided strings
6. **Handle NULL correctly**: Use ``.is_null`` and ``.not_null``
7. **Use appropriate operators**: ``*`` for AND, ``+`` for OR
8. **Consider readability**: Use parentheses for complex logic
