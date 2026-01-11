# ExpressQL Documentation

This directory contains the Sphinx documentation for ExpressQL.

## Building the Documentation

### Requirements

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

Or install Sphinx and extensions directly:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML documentation will be in `build/html/`. Open `build/html/index.html` in your browser.

### Clean Build

To clean previous builds:

```bash
make clean
```

Then rebuild:

```bash
make html
```

## Documentation Structure

- `source/` - Source files for documentation
  - `index.rst` - Main documentation index
  - `quickstart.rst` - Quick start guide
  - `user_guide/` - Detailed user guides
    - `expressions.rst` - Guide to expressions
    - `conditions.rst` - Guide to conditions
    - `functions.rst` - Guide to functions
    - `parsing.rst` - Guide to parsing
  - `api/` - API reference documentation
    - `base.rst` - Base module reference
    - `dsl.rst` - DSL module reference
    - `functions.rst` - Functions module reference
    - `parsers.rst` - Parsers module reference
    - `utils.rst` - Utils module reference
    - `validators.rst` - Validators module reference
    - `exceptions.rst` - Exceptions module reference
  - `examples.rst` - Comprehensive examples
  - `contributing.rst` - Contributing guide
  - `changelog.rst` - Changelog reference
  - `conf.py` - Sphinx configuration

- `build/` - Generated documentation (not committed to git)

## Sphinx Configuration

The documentation uses:

- **Theme**: sphinx_rtd_theme (Read the Docs theme)
- **Extensions**:
  - `sphinx.ext.autodoc` - Automatic API documentation from docstrings
  - `sphinx.ext.napoleon` - Support for Google and NumPy style docstrings
  - `sphinx.ext.viewcode` - Add links to source code
  - `sphinx.ext.intersphinx` - Link to other project documentation
  - `sphinx_autodoc_typehints` - Type hints in documentation
  - `sphinx.ext.autosummary` - Generate summary tables

## Contributing to Documentation

When contributing:

1. Keep documentation clear and concise
2. Include code examples with expected output
3. Follow the existing structure
4. Test your changes by building the docs locally
5. Check for warnings during the build

### Adding New Documentation

1. Create new `.rst` files in appropriate directories
2. Add them to the relevant `toctree` directive
3. Build and verify the documentation
4. Submit a pull request

### Writing Style

- Use clear, simple language
- Provide examples for complex concepts
- Include both simple and advanced usage
- Link to API reference where appropriate
- Use code blocks with proper syntax highlighting

## Hosting Documentation

The documentation can be hosted on:

- **Read the Docs**: Connect your GitHub repository to automatically build and host docs
- **GitHub Pages**: Build docs and push to gh-pages branch
- **Self-hosted**: Build and deploy HTML files to your web server

### Read the Docs Setup

1. Import your project at readthedocs.org
2. Configure the project settings
3. Docs will build automatically on each push

No additional configuration needed - the existing setup should work out of the box.
