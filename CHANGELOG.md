# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-01-17

### 🎉 First Stable Release

expressql is now production-ready! This release marks API stability and commitment to backward compatibility.

### Added
- **Python 3.8 - 3.14 support** with full CI/CD testing across all versions
- Ecosystem documentation linking to recordsQL and tablesQLite

### Changed
- Updated development status from Beta to Production/Stable
- Comprehensive documentation updates with ecosystem links
- Clarified package scope and integration patterns

### Notes
- All core features from 0.3.x are stable and tested
- Comprehensive test coverage with pytest
- Full Sphinx documentation available
- Zero open issues

## [0.3.9] - 2026-01-15

### Changed
- Fix negation features
- Modernize project structure with tests and docstrings
- Fix NotIn.__new__ recursion bug
- Fix NULL comparison, float precision, and API documentation
- Improve condition parsing for IN, LIKE, and BETWEEN
- Add comprehensive Sphinx documentation

**Full Changelog**: https://github.com/Grayjou/expressql/commits/0.3.9

## [0.1.0] - 2025-05-04
### Added
- Initial release of `expressql`.
- Arithmetic expressions and SQL-safe translation.
- Logical operators (AND, OR, NOT).
- Chained conditions and comparisons.
- Function integration (`Func`).
- Null-safe checks and set operations.
- Examples and full DSL usage guides.

## [0.1.1] - 2025-05-05
-Bugfixes
-Cleanup of leftover comments

# [0.2.0] - 2025-05-08
- Added easy custom function support in SQLExpression
- Fixed bugs regarding inversion of complex expressions

# [0.2.1] - 2025-05-10
- Fixed bugs around subquery in select

# [0.2.2] - 2025-05-10
- Fixed typo and expression_type checks

# [0.2.3] - 2025-05-11
- Added Alias support and the possibility to skip validation in SQLExpression

# [0.2.4] - 2025-05-11
- Attempt to fix an upload bug where base.py wasn't updating properly
- It worked

## [0.3.0] - 2025-05-27
### Added
- New parsing utilities: `parse_condition`, `parse_expression`, and `transform_betweens`.
- Support for direct parsing of strings into SQLExpression and SQLCondition objects.
- Extended test coverage and usage examples for DSL interpretation.
### Example
```python
log = parse_expression("LOG(col1, 10) + CUSTOM_FUNC(col2, col3*col5/col4) + 15")
print(log)
print(*log.placeholder_pair())
# Output:
# Sum([...])
# (?+LOG(col1, ?)+CUSTOM_FUNC(col2, (col3*col5)/col4)) [15, 10]
```
##[0.3.3] - 2025-06-13
- Now table_name validation accepts accented characters

## [0.3.6] - 2025-12-02
### Fixed
- **NULL Handling**: Fixed `SQLExpression.__eq__()` and `SQLExpression.__ne__()` to properly detect `None` values and generate `IS NULL` / `IS NOT NULL` SQL instead of `= ?` with `[None]` parameter
- **Float Precision**: Fixed `num()` function to preserve decimal precision - floats are no longer silently rounded to integers. Updated `parse_number()` to preserve numeric types properly
- **Type Safety**: Improved `is_number()` to handle `None` values gracefully (returns `False` without raising errors)

### Improved
- Enhanced documentation in `parse_number()` to clarify precision handling behavior
- **Enhanced `num()` documentation**: Added comprehensive documentation explaining precision preservation behavior with examples
- **Enhanced `set_expr()` documentation**: Added detailed documentation clarifying its use for IN/NOT IN clauses, with guidance on UPDATE SET expressions
- **Enhanced `cols()` documentation**: Added documentation explaining integration with query builders like recordsql, including how to extract column names from SQLExpression objects for SELECT and GROUP BY operations

### Documentation
- Clarified that `set_expr()` is for IN/NOT IN operations, not UPDATE SET clauses with expressions
- Added guidance for query builder integration: how to extract column names from SQLExpression objects
- Documented that ExpressQL focuses on expressions/conditions; full query building should use recordsql or similar


## [0.3.7] - 2025-12-15
### Fixed
- Improved condition parsing to handle `IN` lists, `LIKE` clauses, and `BETWEEN` keywords case-insensitively.
- Added support for quoted `LIKE` patterns and literal `IN` value lists during placeholder generation.
- Re-enabled parser tests for condition handling to cover the updated behavior.




