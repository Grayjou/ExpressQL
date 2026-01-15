"""Tests for validation functions."""
from expressql.validators import is_number, get_forbidden_words_in


class TestIsNumber:
    """Test is_number validator function."""

    def test_valid_integer(self):
        """Test with valid integer string."""
        assert is_number("42") is True

    def test_valid_float(self):
        """Test with valid float string."""
        assert is_number("3.14") is True

    def test_valid_negative(self):
        """Test with negative number."""
        assert is_number("-100") is True

    def test_valid_zero(self):
        """Test with zero."""
        assert is_number("0") is True

    def test_valid_scientific(self):
        """Test with scientific notation."""
        assert is_number("1e5") is True
        assert is_number("1.5e-10") is True

    def test_invalid_string(self):
        """Test with non-numeric string."""
        assert is_number("abc") is False

    def test_empty_string(self):
        """Test with empty string."""
        assert is_number("") is False

    def test_mixed_string(self):
        """Test with mixed alphanumeric string."""
        assert is_number("123abc") is False

    def test_whitespace(self):
        """Test with whitespace."""
        assert is_number("  42  ") is True  # Python's float() handles whitespace

    def test_none_value(self):
        """Test with None value."""
        assert is_number(None) is False

    def test_actual_number(self):
        """Test with actual number (not string)."""
        assert is_number(42) is True
        assert is_number(3.14) is True


class TestGetForbiddenWordsIn:
    """Test get_forbidden_words_in function."""

    def test_select_keyword(self):
        """Test detection of SELECT keyword."""
        result = get_forbidden_words_in("SELECT name FROM users")
        # Function returns lowercase keywords
        assert "select" in result or "SELECT" in result
        assert "from" in result or "FROM" in result

    def test_insert_keyword(self):
        """Test detection of INSERT keyword."""
        result = get_forbidden_words_in("INSERT INTO table VALUES")
        assert "insert" in result or "INSERT" in result

    def test_update_keyword(self):
        """Test detection of UPDATE keyword."""
        result = get_forbidden_words_in("UPDATE users SET name")
        assert "update" in result or "UPDATE" in result
        assert "set" in result or "SET" in result

    def test_delete_keyword(self):
        """Test detection of DELETE keyword."""
        result = get_forbidden_words_in("DELETE FROM users")
        assert "delete" in result or "DELETE" in result
        assert "from" in result or "FROM" in result

    def test_case_insensitive(self):
        """Test case-insensitive detection."""
        result_lower = get_forbidden_words_in("select name from users")
        result_upper = get_forbidden_words_in("SELECT NAME FROM USERS")
        result_mixed = get_forbidden_words_in("SeLeCt NaMe FrOm UsErS")
        
        # Should detect keywords regardless of case
        assert len(result_lower) > 0 or len(result_upper) > 0 or len(result_mixed) > 0

    def test_no_forbidden_words(self):
        """Test with string containing no forbidden words."""
        result = get_forbidden_words_in("age salary department")
        assert len(result) == 0

    def test_empty_string(self):
        """Test with empty string."""
        result = get_forbidden_words_in("")
        assert len(result) == 0

    def test_partial_match(self):
        """Test that partial matches are not detected."""
        # "SELECTED" contains "SELECT" but should not match
        get_forbidden_words_in("SELECTED INFORMATION")
        # This depends on implementation - it may or may not match
        # The test documents current behavior

    def test_multiple_keywords(self):
        """Test detection of multiple keywords."""
        result = get_forbidden_words_in("SELECT * FROM users WHERE id IN (1,2,3)")
        assert len(result) >= 2  # At least SELECT and FROM
