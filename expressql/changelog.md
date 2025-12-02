# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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

