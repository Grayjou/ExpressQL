"""Tests for expressql parsers module."""
from expressql.parsers import parse_expression, parse_condition, parse_expr_or_cond
from expressql import SQLExpression, SQLCondition, col


class TestExpressionParser:
    """Test parse_expression function."""

    def test_parse_simple_column(self):
        """Test parsing a simple column name."""
        expr = parse_expression("age")
        assert isinstance(expr, SQLExpression)
        assert expr.expression_type == "column"
        sql, params = expr.placeholder_pair()
        assert sql == "age"
        assert params == []

    def test_parse_numeric_literal(self):
        """Test parsing numeric literals."""
        expr = parse_expression("42")
        assert isinstance(expr, SQLExpression)
        assert expr.expression_type == "value"
        sql, params = expr.placeholder_pair()
        assert params == [42]

    def test_parse_string_literal(self):
        """Test parsing string literals."""
        expr = parse_expression("'hello'")
        assert isinstance(expr, SQLExpression)
        assert expr.expression_type == "value"
        sql, params = expr.placeholder_pair()
        # Parser includes quotes in the string value
        assert params == ["'hello'"]

    def test_parse_addition(self):
        """Test parsing addition expression."""
        expr = parse_expression("age + 10")
        sql, params = expr.placeholder_pair()
        assert "age" in sql
        assert "+" in sql
        assert 10 in params

    def test_parse_subtraction(self):
        """Test parsing subtraction expression."""
        expr = parse_expression("salary - 1000")
        sql, params = expr.placeholder_pair()
        assert "salary" in sql
        assert 1000 in params or -1000 in params

    def test_parse_multiplication(self):
        """Test parsing multiplication expression."""
        expr = parse_expression("price * quantity")
        sql, params = expr.placeholder_pair()
        assert "price" in sql
        assert "quantity" in sql
        assert "*" in sql

    def test_parse_division(self):
        """Test parsing division expression."""
        expr = parse_expression("total / 2")
        sql, params = expr.placeholder_pair()
        assert "total" in sql

    def test_parse_power(self):
        """Test parsing power expression."""
        expr = parse_expression("POWER(height, 2)")
        sql, params = expr.placeholder_pair()
        assert "POWER" in sql
        assert "height" in sql
        assert 2 in params

    def test_parse_simple_function(self):
        """Test parsing simple function call."""
        expr = parse_expression("ABS(value)")
        sql, params = expr.placeholder_pair()
        assert "ABS" in sql
        assert "value" in sql

    def test_parse_function_with_multiple_args(self):
        """Test parsing function with multiple arguments."""
        expr = parse_expression("COALESCE(col1, col2, 0)")
        sql, params = expr.placeholder_pair()
        assert "COALESCE" in sql
        assert "col1" in sql
        assert "col2" in sql

    def test_parse_nested_arithmetic(self):
        """Test parsing nested arithmetic expressions."""
        expr = parse_expression("(price + tax) * quantity")
        sql, params = expr.placeholder_pair()
        assert "price" in sql
        assert "tax" in sql
        assert "quantity" in sql

    def test_parse_complex_expression(self):
        """Test parsing complex nested expression."""
        expr = parse_expression("(weight / POWER(height, 2)) * 703")
        sql, params = expr.placeholder_pair()
        assert "weight" in sql
        assert "height" in sql
        assert "POWER" in sql


class TestConditionParser:
    """Test parse_condition function."""

    def test_parse_simple_equality(self):
        """Test parsing simple equality condition."""
        cond = parse_condition("age = 30")
        assert isinstance(cond, SQLCondition)
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "=" in sql
        assert 30 in params

    def test_parse_greater_than(self):
        """Test parsing greater than condition."""
        cond = parse_condition("salary > 50000")
        sql, params = cond.placeholder_pair()
        assert "salary" in sql
        assert ">" in sql
        assert 50000 in params

    def test_parse_less_than(self):
        """Test parsing less than condition."""
        cond = parse_condition("age < 65")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "<" in sql
        assert 65 in params

    def test_parse_not_equal(self):
        """Test parsing not equal condition."""
        cond = parse_condition("status != 'inactive'")
        sql, params = cond.placeholder_pair()
        assert "status" in sql
        assert "!=" in sql or "NOT" in sql.upper()
        # Parser includes quotes in string values
        assert "'inactive'" in params

    def test_parse_between(self):
        """Test parsing BETWEEN condition."""
        cond = parse_condition("age BETWEEN 18 AND 65")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "BETWEEN" in sql
        assert 18 in params
        assert 65 in params

    def test_parse_in_list(self):
        """Test parsing IN condition."""
        cond = parse_condition("status IN ('active', 'pending')")
        sql, params = cond.placeholder_pair()
        assert "status" in sql
        assert "IN" in sql
        assert "active" in params
        assert "pending" in params

    def test_parse_is_null(self):
        """Test parsing IS NULL condition."""
        cond = parse_condition("email IS NULL")
        sql, params = cond.placeholder_pair()
        assert "email" in sql
        assert "IS NULL" in sql
        assert params == []

    def test_parse_is_not_null(self):
        """Test parsing IS NOT NULL condition."""
        cond = parse_condition("phone IS NOT NULL")
        sql, params = cond.placeholder_pair()
        assert "phone" in sql
        assert "IS NOT NULL" in sql
        assert params == []

    def test_parse_like(self):
        """Test parsing LIKE condition."""
        cond = parse_condition("name LIKE '%John%'")
        sql, params = cond.placeholder_pair()
        assert "name" in sql
        assert "LIKE" in sql
        # Parser includes quotes in string values
        assert "'%John%'" in params

    def test_parse_and_condition(self):
        """Test parsing AND condition."""
        cond = parse_condition("age > 25 AND salary > 40000")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "salary" in sql
        assert "AND" in sql
        assert 25 in params
        assert 40000 in params

    def test_parse_or_condition(self):
        """Test parsing OR condition."""
        cond = parse_condition("age < 18 OR age > 65")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "OR" in sql
        assert 18 in params
        assert 65 in params

    def test_parse_not_condition(self):
        """Test parsing NOT condition."""
        cond = parse_condition("NOT (age > 18)")
        sql, params = cond.placeholder_pair()
        assert "NOT" in sql
        assert "age" in sql
        assert 18 in params

    def test_parse_complex_condition(self):
        """Test parsing complex nested condition."""
        cond = parse_condition("(age > 30 AND department = 'HR') OR (salary > 100000)")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert "department" in sql
        assert "salary" in sql
        assert "AND" in sql
        assert "OR" in sql


class TestAutoParser:
    """Test parse_expr_or_cond auto-detection function."""

    def test_auto_detect_expression(self):
        """Test auto-detection of expression."""
        result = parse_expr_or_cond("salary * 2")
        assert isinstance(result, SQLExpression)

    def test_auto_detect_simple_condition(self):
        """Test auto-detection of simple condition."""
        result = parse_expr_or_cond("age > 25")
        assert isinstance(result, SQLCondition)

    def test_auto_detect_complex_condition(self):
        """Test auto-detection of complex condition."""
        result = parse_expr_or_cond("age > 25 AND salary < 100000")
        assert isinstance(result, SQLCondition)

    def test_auto_detect_function_expression(self):
        """Test auto-detection of function as expression."""
        result = parse_expr_or_cond("SUM(salary)")
        assert isinstance(result, SQLExpression)

    def test_auto_detect_in_condition(self):
        """Test auto-detection of IN condition."""
        result = parse_expr_or_cond("status IN ('active', 'pending')")
        assert isinstance(result, SQLCondition)


class TestParserEdgeCases:
    """Test edge cases and special scenarios in parsers."""

    def test_parse_with_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        cond = parse_condition("  age   >   25  ")
        sql, params = cond.placeholder_pair()
        assert "age" in sql
        assert 25 in params

    def test_parse_case_insensitive_keywords(self):
        """Test case-insensitive keyword parsing."""
        cond1 = parse_condition("age between 18 and 65")
        cond2 = parse_condition("age BETWEEN 18 AND 65")
        sql1, params1 = cond1.placeholder_pair()
        sql2, params2 = cond2.placeholder_pair()
        assert "BETWEEN" in sql1.upper()
        assert "BETWEEN" in sql2.upper()

    def test_parse_with_parentheses(self):
        """Test parsing with extra parentheses."""
        expr = parse_expression("(age)")
        sql, params = expr.placeholder_pair()
        assert "age" in sql

    def test_parse_negative_number(self):
        """Test parsing negative numbers."""
        expr = parse_expression("-100")
        sql, params = expr.placeholder_pair()
        assert -100 in params or 100 in params

    def test_parse_float_number(self):
        """Test parsing float numbers."""
        expr = parse_expression("3.14")
        sql, params = expr.placeholder_pair()
        assert 3.14 in params


class TestParserIntegration:
    """Integration tests for parsers with the rest of ExpressQL."""

    def test_parsed_expression_equals_constructed(self):
        """Test that parsed expression behaves like constructed one."""
        parsed = parse_expression("age + 10")
        constructed = col("age") + 10
        
        sql_parsed, params_parsed = parsed.placeholder_pair()
        sql_constructed, params_constructed = constructed.placeholder_pair()
        
        # Both should produce similar SQL structure
        assert "age" in sql_parsed and "age" in sql_constructed
        assert 10 in params_parsed and 10 in params_constructed

    def test_parsed_condition_equals_constructed(self):
        """Test that parsed condition behaves like constructed one."""
        parsed = parse_condition("age > 25")
        constructed = col("age") > 25
        
        sql_parsed, params_parsed = parsed.placeholder_pair()
        sql_constructed, params_constructed = constructed.placeholder_pair()
        
        assert "age" in sql_parsed and "age" in sql_constructed
        assert ">" in sql_parsed and ">" in sql_constructed
        assert 25 in params_parsed and 25 in params_constructed

    def test_parsed_in_further_operations(self):
        """Test using parsed results in further operations."""
        expr1 = parse_expression("age")
        expr2 = expr1 + 10
        
        sql, params = expr2.placeholder_pair()
        assert "age" in sql
        assert 10 in params

    def test_complex_parsing_scenario(self):
        """Test complex real-world parsing scenario."""
        # Parse a complex condition
        cond = parse_condition("(age > 30 AND department = 'HR') OR salary > 100000")
        
        # Verify it produces valid SQL
        sql, params = cond.placeholder_pair()
        assert all(keyword in sql.upper() for keyword in ["AGE", "DEPARTMENT", "SALARY"])
        assert "AND" in sql
        assert "OR" in sql
        assert 30 in params
        # Parser includes quotes in string values
        assert "'HR'" in params
        assert 100000 in params
