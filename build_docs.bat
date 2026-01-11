@echo off
REM Build ExpressQL documentation
REM This script builds the Sphinx documentation for ExpressQL

echo Building ExpressQL Documentation...
echo ====================================
echo.

REM Check if we're in the project root
if not exist "pyproject.toml" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

REM Check if Sphinx is installed
sphinx-build --version >nul 2>&1
if errorlevel 1 (
    echo Sphinx is not installed. Installing documentation dependencies...
    pip install -e .[docs]
)

echo Cleaning previous build...
cd docs
call make clean

echo.
echo Building HTML documentation...
call make html

echo.
echo ====================================
echo Documentation built successfully!
echo Open docs\build\html\index.html in your browser to view the documentation.
echo.
