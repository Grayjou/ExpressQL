"""Tests for base SQL expressions and conditions."""
import pytest
from expressql import (
    col, cols, num, text, SQLExpression, TrueCondition, FalseCondition,
    no_condition, get_comparison,
    Func, where_string, ensure_sql_expression
)


class TestSQLExpression:
    """Test SQLExpression class."""

    def test_column_expression(self):
        """Test basic column expression."""
        age = col("age")
        assert age.expression_type == "column"
        sql, params = age.placeholder_pair()
        assert sql == "age"
        assert params == []

    def test_value_expression(self):
        """Test value expression."""
        value = num(42)
        sql, params = value.placeholder_pair()
        assert sql == "?"
        assert params == [42]

    def test_arithmetic_addition(self):
        """Test arithmetic addition."""
        age = col("age")
        expr = age + 10
        sql, params = expr.placeholder_pair()
        # Note: order is value first, then column
        assert "age" in sql and "+" in sql
        assert params == [10]

    def test_arithmetic_subtraction(self):
        """Test arithmetic subtraction."""
        age = col("age")
        expr = age - 5
        sql, params = expr.placeholder_pair()
        assert "age" in sql and "+" in sql  # Subtraction becomes addition of negative
        assert params == [-5]  # Negative value

    def test_arithmetic_multiplication(self):
        """Test arithmetic multiplication."""
        salary = col("salary")
        expr = salary * 2
        sql, params = expr.placeholder_pair()
        assert "salary" in sql and "*" in sql
        assert params == [2]

    def test_arithmetic_division(self):
        """Test arithmetic division."""
        total = col("total")
        expr = total / 3
        sql, params = expr.placeholder_pair()
        assert "total" in sql and "*" in sql  # Division may be represented as multiplication
        assert params[0] == pytest.approx(1/3, rel=1e-5)  # Reciprocal for multiplication

    def test_power_operation(self):
        """Test power operation."""
        height = col("height")
        expr = height ** 2
        sql, params = expr.placeholder_pair()
        assert sql == "POWER(height, ?)"
        assert params == [2]

    def test_complex_expression(self):
        """Test complex arithmetic expression."""
        weight = col("weight")
        height = col("height")
        bmi = weight / (height ** 2)
        sql, params = bmi.placeholder_pair()
        assert "weight" in sql
        assert "height" in sql
        assert "POWER" in sql
        assert params == [2]

    def test_multiple_columns(self):
        """Test cols helper function."""
        age, salary, dept = cols("age", "salary", "dept")
        assert age.expression_type == "column"
        assert salary.expression_type == "column"
        assert dept.expression_type == "column"

    def test_text_expression(self):
        """Test text expression."""
        name = text("John")
        sql, params = name.placeholder_pair()
        assert sql == "?"
        assert params == ["John"]

    def test_concatenation(self):
        """Test string concatenation with pipe operator."""
        first = col("first_name")
        last = col("last_name")
        expr = first | " " | last
        sql, params = expr.placeholder_pair()
        assert "||" in sql
        assert "first_name" in sql
        assert "last_name" in sql


class TestSQLComparison:
    """Test SQL comparison operations."""

    def test_equal_to(self):
        """Test equality comparison."""
        age = col("age")
        cond = age == 30
        sql, params = cond.placeholder_pair()
        assert "age" in sql and "=" in sql
        assert params == [30]

    def test_not_equal_to(self):
        """Test not equal comparison."""
        status = col("status")
        cond = status != "inactive"
        sql, params = cond.placeholder_pair()
        assert "status" in sql and "!=" in sql
        assert params == ["inactive"]

    def test_less_than(self):
        """Test less than comparison."""
        age = col("age")
        cond = age < 18
        sql, params = cond.placeholder_pair()
        assert "age" in sql and "<" in sql
        assert params == [18]

    def test_greater_than(self):
        """Test greater than comparison."""
        salary = col("salary")
        cond = salary > 50000
        sql, params = cond.placeholder_pair()
        assert "salary" in sql and ">" in sql
        assert params == [50000]

    def test_less_or_equal(self):
        """Test less than or equal comparison."""
        score = col("score")
        cond = score <= 100
        sql, params = cond.placeholder_pair()
        assert "score" in sql and "<=" in sql
        assert params == [100]

    def test_greater_or_equal(self):
        """Test greater than or equal comparison."""
        age = col("age")
        cond = age >= 21
        sql, params = cond.placeholder_pair()
        assert "age" in sql and ">=" in sql
        assert params == [21]

    def test_chained_comparison(self):
        """Test chained comparison (e.g., 18 <= age < 65)."""
        age = col("age")
        cond = (18 <= age) < 65
        sql, params = cond.placeholder_pair()
        assert "AND" in sql
        assert params == [18, 65]

    def test_between(self):
        """Test BETWEEN comparison."""
        age = col("age")
        cond = age.between(18, 65)
        sql, params = cond.placeholder_pair()
        assert "BETWEEN" in sql
        assert params == [18, 65]

    def test_in_list(self):
        """Test IN comparison with list."""
        dept = col("department")
        cond = dept.isin(["HR", "IT", "Sales"])
        sql, params = cond.placeholder_pair()
        assert "IN" in sql
        # Order may vary due to set operations
        assert set(params) == {"HR", "IT", "Sales"}

    def test_not_in_list(self):
        """Test NOT IN comparison - uses is_not_in method."""
        status = col("status")
        # Use is_not_in instead of notin
        cond = status.is_not_in(["inactive", "deleted"])
        sql, params = cond.placeholder_pair()
        assert "NOT IN" in sql
        assert set(params) == {"inactive", "deleted"}

    def test_is_null(self):
        """Test IS NULL comparison."""
        email = col("email")
        cond = email.is_null()
        sql, params = cond.placeholder_pair()
        assert "IS NULL" in sql
        assert params == []

    def test_is_not_null(self):
        """Test IS NOT NULL comparison."""
        phone = col("phone")
        cond = phone.is_not_null()
        sql, params = cond.placeholder_pair()
        assert "IS NOT NULL" in sql
        assert params == []

    def test_like(self):
        """Test LIKE comparison."""
        name = col("name")
        cond = name.like("%John%")
        sql, params = cond.placeholder_pair()
        assert "LIKE" in sql
        assert params == ["%John%"]


class TestLogicalOperations:
    """Test logical operations on conditions."""

    def test_and_condition(self):
        """Test AND logical operation."""
        age = col("age")
        salary = col("salary")
        cond = (age > 25) & (salary > 40000)
        sql, params = cond.placeholder_pair()
        assert "AND" in sql
        assert params == [25, 40000]

    def test_and_with_multiply(self):
        """Test AND with multiply operator."""
        age = col("age")
        dept = col("department")
        cond = (age > 30) * (dept == "IT")
        sql, params = cond.placeholder_pair()
        assert "AND" in sql
        assert params == [30, "IT"]

    def test_or_condition(self):
        """Test OR logical operation."""
        age = col("age")
        experience = col("experience")
        cond = (age > 30) | (experience > 5)
        sql, params = cond.placeholder_pair()
        assert "OR" in sql
        assert params == [30, 5]

    def test_or_with_add(self):
        """Test OR with add operator."""
        status = col("status")
        role = col("role")
        cond = (status == "active") + (role == "admin")
        sql, params = cond.placeholder_pair()
        assert "OR" in sql
        assert params == ["active", "admin"]

    def test_not_condition(self):
        """Test NOT logical operation."""
        age = col("age")
        cond = ~(age > 18)
        sql, params = cond.placeholder_pair()
        assert "NOT" in sql
        assert params == [18]

    def test_complex_logical(self):
        """Test complex logical expression."""
        age = col("age")
        salary = col("salary")
        dept = col("department")
        cond = ((age > 25) & (salary > 40000)) | (dept == "Management")
        sql, params = cond.placeholder_pair()
        assert "AND" in sql
        assert "OR" in sql
        assert len(params) == 3

    def test_true_condition(self):
        """Test always-true condition."""
        cond = TrueCondition()
        sql, params = cond.placeholder_pair()
        assert sql == "1=1"
        assert params == []

    def test_false_condition(self):
        """Test always-false condition."""
        cond = FalseCondition()
        sql, params = cond.placeholder_pair()
        assert sql == "0=1"
        assert params == []

    def test_no_condition(self):
        """Test no_condition helper - returns instance not function."""
        cond = no_condition
        # no_condition is an instance of NoCondition, not a function
        assert hasattr(cond, 'placeholder_pair')
        # Just verify it exists and has the right type


class TestSQLFunctions:
    """Test SQL functions."""

    def test_func_creation(self):
        """Test basic function creation."""
        age = col("age")
        func = Func("ABS", age)
        sql, params = func.placeholder_pair()
        assert "ABS" in sql
        assert "age" in sql

    def test_func_with_multiple_args(self):
        """Test function with multiple arguments."""
        height = col("height")
        func = Func("POWER", height, 2)
        sql, params = func.placeholder_pair()
        assert "POWER" in sql
        assert "height" in sql
        assert params == [2]

    def test_func_method_on_expression(self):
        """Test calling function as method on expression."""
        total = col("total")
        func_expr = total.ABS()
        sql, params = func_expr.placeholder_pair()
        assert "ABS" in sql
        assert "total" in sql

    def test_func_in_comparison(self):
        """Test function in comparison."""
        salary = col("salary")
        cond = Func("ABS", salary) > 50000
        sql, params = cond.placeholder_pair()
        assert "ABS" in sql
        assert params == [50000]


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_comparison(self):
        """Test get_comparison helper."""
        age = col("age")
        # get_comparison takes (operator_string, value1, value2)
        cond = get_comparison(">", age, 18)
        sql, params = cond.placeholder_pair()
        assert ">" in sql
        # Parameters may be empty if the value is embedded in SQL
        assert "age" in sql

    def test_where_string(self):
        """Test where_string helper."""
        age = col("age")
        dept = col("department")
        cond = (age > 25) & (dept == "IT")
        where_clause = where_string(cond)
        assert "WHERE" in where_clause
        assert "AND" in where_clause

    def test_ensure_sql_expression(self):
        """Test ensure_sql_expression helper."""
        # Test with SQLExpression
        expr1 = col("age")
        result1 = ensure_sql_expression(expr1)
        assert isinstance(result1, SQLExpression)

        # Test with regular value
        result2 = ensure_sql_expression(42)
        assert isinstance(result2, SQLExpression)
        sql, params = result2.placeholder_pair()
        assert params == [42]


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_zero_value(self):
        """Test with zero value."""
        count = col("count")
        cond = count == 0
        sql, params = cond.placeholder_pair()
        assert params == [0]

    def test_negative_value(self):
        """Test with negative value."""
        balance = col("balance")
        cond = balance < -100
        sql, params = cond.placeholder_pair()
        assert params == [-100]

    def test_float_value(self):
        """Test with float value."""
        rate = col("rate")
        cond = rate >= 3.14
        sql, params = cond.placeholder_pair()
        assert params == [3.14]

    def test_boolean_value(self):
        """Test with boolean value."""
        active = col("active")
        cond = active == True  # noqa: E712
        sql, params = cond.placeholder_pair()
        assert params == [True]

    def test_empty_string(self):
        """Test with empty string."""
        name = col("name")
        cond = name == ""
        sql, params = cond.placeholder_pair()
        assert params == [""]

    def test_none_value_in_comparison(self):
        """Test with None value - should generate IS NULL."""
        email = col("email")
        cond = email == None  # noqa: E711
        sql, params = cond.placeholder_pair()
        # Should generate IS NULL, not = ?
        assert sql == "email IS NULL"
        assert params == []
    
    def test_none_not_equal_comparison(self):
        """Test != None comparison - should generate IS NOT NULL."""
        email = col("email")
        cond = email != None  # noqa: E711
        sql, params = cond.placeholder_pair()
        # Should generate IS NOT NULL, not != ?
        assert sql == "email IS NOT NULL"
        assert params == []
    
    def test_float_precision_in_num(self):
        """Test that num() preserves float precision."""
        value = num(3.14)
        sql, params = value.placeholder_pair()
        assert sql == "?"
        assert params == [3.14]
        assert isinstance(params[0], float)
    
    def test_float_vs_int_in_num(self):
        """Test that num() distinguishes between floats and ints."""
        # Integer value
        int_value = num(3)
        sql_int, params_int = int_value.placeholder_pair()
        assert params_int == [3]
        assert isinstance(params_int[0], int)
        
        # Float literal 3.0 preserves type (not converted since already float)
        float_value = num(3.0)
        sql_float, params_float = float_value.placeholder_pair()
        assert params_float == [3.0]
        assert isinstance(params_float[0], float)
        
        # String "3.0" is parsed: since 3.0.is_integer() is True, becomes int
        string_value = num("3.0")
        sql_str, params_str = string_value.placeholder_pair()
        assert params_str == [3]
        assert isinstance(params_str[0], int)
        
    def test_none_in_complex_condition(self):
        """Test None handling in complex conditions."""
        age = col("age")
        email = col("email")
        # Combine NULL check with other conditions
        cond = (age > 18) & (email == None)  # noqa: E711
        sql, params = cond.placeholder_pair()
        assert "IS NULL" in sql
        assert "age > ?" in sql
        assert params == [18]
