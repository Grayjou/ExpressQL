Functions Module
================

The functions module provides convenient access to common SQL functions.

.. automodule:: expressql.functions
   :members:
   :undoc-members:
   :show-inheritance:

Common Functions
----------------

This module contains pre-defined wrappers for common SQL functions such as:

- Aggregate functions (SUM, AVG, COUNT, MAX, MIN)
- Mathematical functions (ABS, ROUND, POWER, SQRT, LOG)
- String functions (UPPER, LOWER, LENGTH, CONCAT, TRIM)
- Date/time functions (CURRENT_TIMESTAMP, DATE, YEAR, MONTH, DAY)

Example Usage
-------------

.. code-block:: python

   from expressql import col
   from expressql import functions as f
   
   salary = col("salary")
   name = col("name")
   
   # Aggregate functions
   total = f.SUM(salary)
   average = f.AVG(salary)
   count = f.COUNT(col("id"))
   
   # Mathematical functions
   abs_value = f.ABS(col("balance"))
   rounded = f.ROUND(salary, 2)
   
   # String functions
   upper_name = f.UPPER(name)
   length = f.LENGTH(name)
