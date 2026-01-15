"""Tests for functions module."""
import pytest
from expressql import col
import expressql.functions as f


class TestBuiltInFunctions:
    """Test built-in SQL functions."""

    def test_sum_function(self):
        """Test SUM function."""
        salary = col("salary")
        func = f.SUM(salary)
        sql, params = func.placeholder_pair()
        assert "SUM" in sql
        assert "salary" in sql

    def test_avg_function(self):
        """Test AVG function."""
        score = col("score")
        func = f.AVG(score)
        sql, params = func.placeholder_pair()
        assert "AVG" in sql
        assert "score" in sql

    def test_count_function(self):
        """Test COUNT function."""
        func = f.COUNT(col("id"))
        sql, params = func.placeholder_pair()
        assert "COUNT" in sql

    def test_max_function(self):
        """Test MAX function."""
        age = col("age")
        func = f.MAX(age)
        sql, params = func.placeholder_pair()
        assert "MAX" in sql
        assert "age" in sql

    def test_min_function(self):
        """Test MIN function."""
        price = col("price")
        func = f.MIN(price)
        sql, params = func.placeholder_pair()
        assert "MIN" in sql
        assert "price" in sql

    def test_abs_function(self):
        """Test ABS function."""
        balance = col("balance")
        func = f.ABS(balance)
        sql, params = func.placeholder_pair()
        assert "ABS" in sql
        assert "balance" in sql

    def test_round_function(self):
        """Test ROUND function."""
        price = col("price")
        func = f.ROUND(price, 2)
        sql, params = func.placeholder_pair()
        assert "ROUND" in sql
        assert "price" in sql

    def test_power_function(self):
        """Test POWER function."""
        base = col("base")
        func = f.POWER(base, 2)
        sql, params = func.placeholder_pair()
        assert "POWER" in sql
        assert params == [2]

    def test_upper_function(self):
        """Test UPPER function."""
        name = col("name")
        func = f.UPPER(name)
        sql, params = func.placeholder_pair()
        assert "UPPER" in sql
        assert "name" in sql

    def test_lower_function(self):
        """Test LOWER function."""
        email = col("email")
        func = f.LOWER(email)
        sql, params = func.placeholder_pair()
        assert "LOWER" in sql
        assert "email" in sql

    def test_length_function(self):
        """Test LENGTH function."""
        text = col("text")
        func = f.LENGTH(text)
        sql, params = func.placeholder_pair()
        assert "LENGTH" in sql
        assert "text" in sql

    def test_coalesce_function(self):
        """Test COALESCE function."""
        email = col("email")
        phone = col("phone")
        func = f.COALESCE(email, phone, "N/A")
        sql, params = func.placeholder_pair()
        assert "COALESCE" in sql
        assert "email" in sql
        assert "phone" in sql


class TestDynamicFunctions:
    """Test dynamic function creation."""

    def test_custom_uppercase_function(self):
        """Test creating custom function with uppercase name."""
        value = col("value")
        func = f.CUSTOM_FUNC(value, 10)
        sql, params = func.placeholder_pair()
        assert "CUSTOM_FUNC" in sql
        assert "value" in sql

    def test_dynamic_function_via_getattr(self):
        """Test that uppercase names create functions dynamically."""
        result = col("test")
        func = f.MY_CUSTOM_FUNCTION(result)
        sql, params = func.placeholder_pair()
        assert "MY_CUSTOM_FUNCTION" in sql

    def test_invalid_function_name(self):
        """Test that lowercase names raise AttributeError."""
        with pytest.raises(AttributeError):
            f.invalid_function_name()


class TestFunctionInExpressions:
    """Test functions used in expressions and conditions."""

    def test_function_in_arithmetic(self):
        """Test function in arithmetic expression."""
        salary = col("salary")
        bonus = col("bonus")
        total = f.SUM(salary) + bonus
        sql, params = total.placeholder_pair()
        assert "SUM" in sql
        assert "+" in sql

    def test_function_in_condition(self):
        """Test function in comparison condition."""
        age = col("age")
        cond = f.ABS(age) > 18
        sql, params = cond.placeholder_pair()
        assert "ABS" in sql
        assert ">" in sql
        assert params == [18]

    def test_nested_functions(self):
        """Test nested function calls."""
        value = col("value")
        func = f.ABS(f.ROUND(value, 2))
        sql, params = func.placeholder_pair()
        assert "ABS" in sql
        assert "ROUND" in sql

    def test_function_with_expression(self):
        """Test function with complex expression as argument."""
        a = col("a")
        b = col("b")
        func = f.SQRT(a ** 2 + b ** 2)
        sql, params = func.placeholder_pair()
        assert "SQRT" in sql
        assert "POWER" in sql


class TestFunctionCategories:
    """Test function category constants."""

    def test_aggregate_functions_exist(self):
        """Test that aggregate functions are defined."""
        assert hasattr(f, "AGGREGATE_FUNCTIONS")
        assert "SUM" in f.AGGREGATE_FUNCTIONS
        assert "AVG" in f.AGGREGATE_FUNCTIONS
        assert "COUNT" in f.AGGREGATE_FUNCTIONS

    def test_numeric_functions_exist(self):
        """Test that numeric functions are defined."""
        assert hasattr(f, "NUMERIC_FUNCTIONS")
        assert "ABS" in f.NUMERIC_FUNCTIONS
        assert "ROUND" in f.NUMERIC_FUNCTIONS
        assert "POWER" in f.NUMERIC_FUNCTIONS

    def test_string_functions_exist(self):
        """Test that string functions are defined."""
        assert hasattr(f, "STRING_FUNCTIONS")
        assert "UPPER" in f.STRING_FUNCTIONS
        assert "LOWER" in f.STRING_FUNCTIONS
        assert "LENGTH" in f.STRING_FUNCTIONS

    def test_datetime_functions_exist(self):
        """Test that datetime functions are defined."""
        assert hasattr(f, "DATETIME_FUNCTIONS")
        assert "DATE" in f.DATETIME_FUNCTIONS
        assert "TIME" in f.DATETIME_FUNCTIONS

    def test_conditional_functions_exist(self):
        """Test that conditional functions are defined."""
        assert hasattr(f, "CONDITIONAL_FUNCTIONS")
        assert "COALESCE" in f.CONDITIONAL_FUNCTIONS
        assert "IFNULL" in f.CONDITIONAL_FUNCTIONS
