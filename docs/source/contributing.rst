Contributing
============

We welcome contributions to ExpressQL! This guide will help you get started.

Getting Started
---------------

1. **Fork the repository** on GitHub
2. **Clone your fork** locally::

       git clone https://github.com/YOUR-USERNAME/ExpressQL.git
       cd ExpressQL

3. **Install in development mode**::

       pip install -e ".[dev]"

This installs ExpressQL with all development dependencies including pytest and sqlparse.

Development Setup
-----------------

Install Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install with development extras
   pip install -e ".[dev]"
   
   # Or install dependencies separately
   pip install pytest pytest-cov sqlparse

Running Tests
~~~~~~~~~~~~~

Run the test suite to ensure everything works:

.. code-block:: bash

   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=expressql
   
   # Run specific test file
   pytest tests/test_base.py
   
   # Run specific test
   pytest tests/test_base.py::test_column_creation

Code Style
----------

ExpressQL follows Python best practices:

- Use **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes
- Keep functions focused and single-purpose

Example of good style:

.. code-block:: python

   def create_condition(column: str, value: Any) -> SQLCondition:
       """
       Create a condition comparing a column to a value.
       
       Args:
           column: Column name to compare
           value: Value to compare against
           
       Returns:
           SQLCondition object representing the comparison
           
       Example:
           >>> cond = create_condition("age", 30)
           >>> sql, params = cond.placeholder_pair()
       """
       col_expr = col(column)
       return col_expr == value

Making Changes
--------------

1. **Create a new branch** for your changes::

       git checkout -b feature/your-feature-name

2. **Make your changes** in the code

3. **Add tests** for new functionality

4. **Run the tests** to ensure nothing broke::

       pytest

5. **Update documentation** if needed

6. **Commit your changes**::

       git add .
       git commit -m "Add feature: description of your changes"

7. **Push to your fork**::

       git push origin feature/your-feature-name

8. **Open a Pull Request** on GitHub

Pull Request Guidelines
------------------------

When submitting a pull request:

- **Describe your changes** clearly in the PR description
- **Reference any related issues** using #issue-number
- **Include tests** for new features or bug fixes
- **Update documentation** if you change the API
- **Ensure all tests pass** before submitting
- **Keep PRs focused** - one feature or fix per PR

Example PR description::

   ## Description
   Add support for CASE WHEN conditions
   
   ## Changes
   - Added CaseWhen class to handle CASE expressions
   - Added tests for CASE WHEN functionality
   - Updated documentation with examples
   
   ## Related Issues
   Fixes #42

Reporting Issues
----------------

Found a bug or have a feature request?

1. **Check existing issues** to avoid duplicates
2. **Create a new issue** with a clear title
3. **Provide details**:
   - For bugs: steps to reproduce, expected vs actual behavior
   - For features: use case, proposed API, examples

Bug Report Template::

   **Bug Description**
   Clear description of the bug
   
   **To Reproduce**
   ```python
   from expressql import col
   age = col("age")
   # Steps that cause the bug
   ```
   
   **Expected Behavior**
   What should happen
   
   **Actual Behavior**
   What actually happens
   
   **Environment**
   - Python version: 3.10
   - ExpressQL version: 0.3.7
   - OS: Ubuntu 22.04

Feature Request Template::

   **Feature Description**
   Clear description of the feature
   
   **Use Case**
   Why is this feature needed?
   
   **Proposed API**
   ```python
   # Example of how it would be used
   ```
   
   **Alternatives Considered**
   Other ways to achieve the same goal

Areas for Contribution
----------------------

We're especially interested in contributions in these areas:

Core Functionality
~~~~~~~~~~~~~~~~~~

- Additional SQL functions
- Performance improvements
- Better error messages
- Edge case handling

Parsing
~~~~~~~

- Support for more SQL syntax
- Better error handling in parsers
- Performance optimizations

Documentation
~~~~~~~~~~~~~

- More examples
- Tutorial improvements
- API documentation enhancements
- Translation to other languages

Testing
~~~~~~~

- Additional test cases
- Integration tests with real databases
- Performance benchmarks

Integrations
~~~~~~~~~~~~

- Example integrations with popular ORMs
- Query builder integrations
- Database-specific optimizations

Code Review Process
-------------------

All contributions go through code review:

1. **Automated checks** run on your PR (tests, linting)
2. **Manual review** by maintainers
3. **Feedback and discussion** may be requested
4. **Approval and merge** once everything looks good

Don't be discouraged by feedback - it helps improve the code!

Development Tips
----------------

Writing Tests
~~~~~~~~~~~~~

Place tests in the ``tests/`` directory:

.. code-block:: python

   # tests/test_my_feature.py
   import pytest
   from expressql import col
   
   def test_my_feature():
       """Test description."""
       age = col("age")
       condition = age > 30
       
       sql, params = condition.placeholder_pair()
       assert sql == "age > ?"
       assert params == [30]

Documentation
~~~~~~~~~~~~~

Update relevant documentation in ``docs/source/``:

- Add examples to ``examples.rst``
- Update API docs if you change function signatures
- Add user guide sections for major features

Local Documentation Build
~~~~~~~~~~~~~~~~~~~~~~~~~

Build and view documentation locally:

.. code-block:: bash

   cd docs
   make html
   
   # Open docs/build/html/index.html in your browser

Getting Help
------------

Need help with your contribution?

- **Ask in the issue**: Comment on the relevant issue
- **GitHub Discussions**: For general questions
- **Pull Request**: Ask for guidance in your PR

Communication
-------------

- Be respectful and constructive
- Focus on the code, not the person
- Accept feedback gracefully
- Help others when you can

Code of Conduct
---------------

We expect all contributors to:

- Be welcoming and inclusive
- Respect different viewpoints
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

Recognition
-----------

All contributors are recognized in:

- Git history
- Release notes
- Contributors list (if we add one)

Thank you for contributing to ExpressQL!

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.
