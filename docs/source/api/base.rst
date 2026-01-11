Base Module
===========

The base module contains the core classes for building SQL expressions and conditions.

.. automodule:: expressql.base
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __add__, __sub__, __mul__, __truediv__, __mod__, __pow__, __eq__, __ne__, __lt__, __le__, __gt__, __ge__, __and__, __or__, __invert__

Key Classes
-----------

SQLExpression
~~~~~~~~~~~~~

.. autoclass:: expressql.base.SQLExpression
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

SQLCondition
~~~~~~~~~~~~

.. autoclass:: expressql.base.SQLCondition
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

SQLComparison
~~~~~~~~~~~~~

.. autoclass:: expressql.base.SQLComparison
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Comparison Classes
------------------

.. autoclass:: expressql.base.EqualTo
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.NotEqualTo
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.LessThan
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.LessOrEqualThan
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.GreaterThan
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.GreaterOrEqualThan
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.Between
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.In
   :members:
   :show-inheritance:

Logical Operators
-----------------

.. autoclass:: expressql.base.AndCondition
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.OrCondition
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.NotCondition
   :members:
   :show-inheritance:

Special Conditions
------------------

.. autoclass:: expressql.base.TrueCondition
   :members:
   :show-inheritance:

.. autoclass:: expressql.base.FalseCondition
   :members:
   :show-inheritance:

Helper Functions
----------------

.. autofunction:: expressql.base.col

.. autofunction:: expressql.base.cols

.. autofunction:: expressql.base.num

.. autofunction:: expressql.base.text

.. autofunction:: expressql.base.set_expr

.. autofunction:: expressql.base.where_string

.. autofunction:: expressql.base.get_comparison

.. autofunction:: expressql.base.no_condition

.. autofunction:: expressql.base.ensure_sql_expression

Function Class
--------------

.. autoclass:: expressql.base.Func
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
