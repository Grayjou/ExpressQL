#!/bin/bash

# Build ExpressQL documentation
# This script builds the Sphinx documentation for ExpressQL

set -e

echo "Building ExpressQL Documentation..."
echo "===================================="
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Sphinx is installed
if ! command -v sphinx-build &> /dev/null; then
    echo "Sphinx is not installed. Installing documentation dependencies..."
    pip install -e ".[docs]"
fi

echo "Cleaning previous build..."
cd docs
make clean

echo ""
echo "Building HTML documentation..."
make html

echo ""
echo "===================================="
echo "Documentation built successfully!"
echo "Open docs/build/html/index.html in your browser to view the documentation."
echo ""
