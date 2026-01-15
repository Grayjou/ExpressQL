"""Tests for utility functions."""
from expressql.utils import (
    parse_number, format_sql_value, forbidden_chars, forbidden_words,
    _normalize_args, bracket_string_sandwich,
    ensure_bracketed, merge_placeholders
)


class TestParseNumber:
    """Test parse_number function."""

    def test_parse_integer(self):
        """Test parsing integer string."""
        result = parse_number("42")
        assert result == 42
        assert isinstance(result, int)

    def test_parse_float(self):
        """Test parsing float string."""
        result = parse_number("3.14")
        assert result == 3.14
        assert isinstance(result, float)

    def test_parse_negative(self):
        """Test parsing negative number."""
        result = parse_number("-100")
        assert result == -100

    def test_parse_zero(self):
        """Test parsing zero."""
        result = parse_number("0")
        assert result == 0

    def test_parse_scientific_notation(self):
        """Test parsing scientific notation."""
        result = parse_number("1e5")
        assert result == 100000.0

    def test_invalid_string(self):
        """Test with invalid string."""
        result = parse_number("abc")
        # Returns original string if not parseable
        assert result == "abc"

    def test_empty_string(self):
        """Test with empty string."""
        result = parse_number("")
        # Returns empty string if not parseable
        assert result == ""
    
    def test_parse_float_preserves_precision(self):
        """Test that float values preserve their precision."""
        # Test float input (not string)
        result = parse_number(3.14159)
        assert result == 3.14159
        assert isinstance(result, float)
    
    def test_parse_int_preserves_type(self):
        """Test that int values preserve their type."""
        # Test int input (not string)
        result = parse_number(42)
        assert result == 42
        assert isinstance(result, int)
    
    def test_parse_whole_number_float_string(self):
        """Test that whole number strings become ints."""
        result = parse_number("3.0")
        assert result == 3
        assert isinstance(result, int)
    
    def test_parse_decimal_float_string(self):
        """Test that decimal strings become floats."""
        result = parse_number("3.14")
        assert result == 3.14
        assert isinstance(result, float)
    
    def test_parse_none_returns_none(self):
        """Test that None is returned as-is."""
        result = parse_number(None)
        assert result is None


class TestFormatSqlValue:
    """Test format_sql_value function."""

    def test_format_string(self):
        """Test formatting string value."""
        result = format_sql_value("test")
        assert isinstance(result, str)
        assert "test" in result

    def test_format_number(self):
        """Test formatting number value."""
        result = format_sql_value(42)
        assert result == "42"

    def test_format_float(self):
        """Test formatting float value."""
        result = format_sql_value(3.14)
        assert "3.14" in result

    def test_format_boolean(self):
        """Test formatting boolean value."""
        result_true = format_sql_value(True)
        result_false = format_sql_value(False)
        assert result_true in ["1", "TRUE"]
        assert result_false in ["0", "FALSE"]

    def test_format_none(self):
        """Test formatting None value."""
        result = format_sql_value(None)
        assert result == "NULL"


class TestNormalizeArgs:
    """Test normalize_args decorator and helper."""

    def test_normalize_single_arg(self):
        """Test normalizing single argument."""
        result = _normalize_args("test")
        assert result == ["test"]

    def test_normalize_multiple_args(self):
        """Test normalizing multiple arguments."""
        result = _normalize_args("a", "b", "c")
        assert result == ["a", "b", "c"]

    def test_normalize_list_arg(self):
        """Test normalizing list argument."""
        result = _normalize_args(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_normalize_tuple_arg(self):
        """Test normalizing tuple argument."""
        result = _normalize_args(("x", "y", "z"))
        assert result == ["x", "y", "z"]

    def test_normalize_empty(self):
        """Test normalizing with no arguments."""
        result = _normalize_args()
        assert result == []


class TestBracketHelpers:
    """Test bracket-related helper functions."""

    def test_ensure_bracketed_already_bracketed(self):
        """Test ensure_bracketed with already bracketed string."""
        result = ensure_bracketed("(test)")
        assert result == "(test)"

    def test_ensure_bracketed_not_bracketed(self):
        """Test ensure_bracketed with non-bracketed string."""
        result = ensure_bracketed("test")
        assert result == "(test)"

    def test_ensure_bracketed_empty(self):
        """Test ensure_bracketed with empty string."""
        result = ensure_bracketed("")
        assert result == "()"

    def test_bracket_string_sandwich(self):
        """Test bracket_string_sandwich function."""
        result = bracket_string_sandwich("test")
        assert result == "(test)"


class TestMergePlaceholders:
    """Test merge_placeholders function."""

    def test_merge_list(self):
        """Test merging list of parameters."""
        params = [1, 2, 3]
        merge_placeholders(params, [4, 5])
        assert params == [1, 2, 3, 4, 5]

    def test_merge_single(self):
        """Test merging single parameter."""
        params = [1, 2]
        merge_placeholders(params, 3)
        assert params == [1, 2, 3]

    def test_merge_empty_list(self):
        """Test merging empty list."""
        params = [1, 2]
        merge_placeholders(params, [])
        assert params == [1, 2]


class TestForbiddenCharsAndWords:
    """Test forbidden characters and words constants."""

    def test_forbidden_chars_exist(self):
        """Test that forbidden_chars is defined."""
        assert isinstance(forbidden_chars, set)
        assert len(forbidden_chars) > 0
        assert " " in forbidden_chars
        assert ";" in forbidden_chars

    def test_forbidden_words_exist(self):
        """Test that forbidden_words is defined."""
        assert isinstance(forbidden_words, set)
        assert len(forbidden_words) > 0
        assert "SELECT" in forbidden_words
        assert "DELETE" in forbidden_words
