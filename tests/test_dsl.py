"""Tests for DSL module."""
import pytest
from expressql.dsl import pk_condition, primary_key_condition, expressions_guide, conditions_guide
from expressql import cols


class TestPrimaryKeyCondition:
    """Test primary_key_condition function."""

    def test_single_key(self):
        """Test with single primary key."""
        pk = {"id": 123}
        cond = pk_condition(pk)
        sql, params = cond.placeholder_pair()
        assert "id" in sql
        assert "=" in sql
        assert params == [123]

    def test_composite_key(self):
        """Test with composite primary key."""
        pk = {"user_id": 1, "post_id": 42}
        cond = pk_condition(pk)
        sql, params = cond.placeholder_pair()
        assert "user_id" in sql
        assert "post_id" in sql
        assert "AND" in sql
        assert 1 in params
        assert 42 in params

    def test_string_key(self):
        """Test with string primary key."""
        pk = {"uuid": "abc-123-def"}
        cond = pk_condition(pk)
        sql, params = cond.placeholder_pair()
        assert "uuid" in sql
        assert params == ["abc-123-def"]

    def test_multiple_keys_order(self):
        """Test that multiple keys are properly combined."""
        pk = {"a": 1, "b": 2, "c": 3}
        cond = pk_condition(pk)
        sql, params = cond.placeholder_pair()
        # Should have AND operators
        assert sql.count("AND") == 2
        # Should have all values
        assert set(params) == {1, 2, 3}

    def test_alias_function(self):
        """Test that primary_key_condition is same as pk_condition."""
        pk = {"id": 1}
        cond1 = pk_condition(pk)
        cond2 = primary_key_condition(pk)
        
        sql1, params1 = cond1.placeholder_pair()
        sql2, params2 = cond2.placeholder_pair()
        
        assert sql1 == sql2
        assert params1 == params2


class TestGuides:
    """Test guide functions."""

    def test_expressions_guide_runs(self):
        """Test that expressions_guide runs without error."""
        # This function prints examples, just ensure it doesn't crash
        try:
            expressions_guide()
        except Exception as e:
            pytest.fail(f"expressions_guide raised {type(e).__name__}: {e}")

    def test_conditions_guide_runs(self):
        """Test that conditions_guide runs without error."""
        # This function prints examples, just ensure it doesn't crash
        try:
            conditions_guide()
        except Exception as e:
            pytest.fail(f"conditions_guide raised {type(e).__name__}: {e}")


class TestDSLIntegration:
    """Test DSL integration scenarios."""

    def test_cols_helper(self):
        """Test cols helper from DSL."""
        age, name, dept = cols("age", "name", "department")
        
        # Build a condition using these
        cond = (age > 25) & (dept == "IT")
        sql, params = cond.placeholder_pair()
        
        assert "age" in sql
        assert "department" in sql
        assert "AND" in sql
        assert params == [25, "IT"]

    def test_complex_dsl_expression(self):
        """Test complex DSL expression."""
        weight, height = cols("weight", "height")
        bmi = weight / (height ** 2)
        
        # Create condition
        cond = (bmi >= 18.5) & (bmi <= 24.9)
        sql, params = cond.placeholder_pair()
        
        assert "weight" in sql
        assert "height" in sql
        assert "POWER" in sql
        assert "AND" in sql
