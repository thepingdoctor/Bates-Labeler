# Bates-Labeler Poetry Packaging Guide

This document explains the Poetry packaging structure created for the Bates-Labeler project.

## What Was Done

The project has been successfully converted from a single-script application to a properly packaged Python project using Poetry. Here's what changed:

### New Project Structure

```
bates-labeler/
├── pyproject.toml              # Poetry configuration file
├── README.md                   # Project documentation (renamed from bates-readme.md)
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore patterns
├── PACKAGING.md               # This file
├── bates-numbering-script.py  # Original script (kept for reference)
├── bates_labeler/             # Main package directory
│   ├── __init__.py            # Package initialization
│   ├── __version__.py         # Version information
│   ├── core.py                # BatesNumberer class and core functionality
│   └── cli.py                 # Command-line interface
└── tests/                     # Test directory
    ├── __init__.py
    └── test_bates_numberer.py # Unit tests
```

## Installation

### For Development

```bash
# Install Poetry (if not already installed)
pip install poetry

# Install the project and its dependencies
poetry install

# This creates a virtual environment and installs:
# - Main dependencies: pypdf, reportlab, tqdm
# - Dev dependencies: pytest, pytest-cov, black, flake8, mypy
```

### For End Users

Once published to PyPI, users can install with:

```bash
pip install bates-labeler
```

## Usage

### Command-Line Interface

The package provides a `bates` command:

```bash
# Using Poetry (during development)
poetry run bates --input evidence.pdf --bates-prefix "CASE123-"

# After installation (for end users)
bates --input evidence.pdf --bates-prefix "CASE123-"
```

### As a Python Module

```python
from bates_labeler import BatesNumberer

# Create a numberer instance
numberer = BatesNumberer(
    prefix="CASE2023-",
    start_number=1,
    padding=6,
    position="top-right",
    font_size=12,
    font_color="blue",
    bold=True
)

# Process a PDF
numberer.process_pdf("input.pdf", "output.pdf")
```

## Development Commands

### Run Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_bates_numberer.py
```

### Code Quality

```bash
# Format code with Black
poetry run black bates_labeler tests

# Lint with Flake8
poetry run flake8 bates_labeler tests

# Type checking with mypy
poetry run mypy bates_labeler
```

### Build Distribution

```bash
# Build wheel and source distribution
poetry build

# This creates files in dist/:
# - bates_labeler-1.1.0-py3-none-any.whl
# - bates-labeler-1.1.0.tar.gz
```

## Publishing to PyPI

### Test PyPI (Recommended First)

```bash
# Configure test PyPI
poetry config repositories.test-pypi https://test.pypi.org/legacy/

# Publish to test PyPI
poetry publish -r test-pypi

# Test installation from test PyPI
pip install --index-url https://test.pypi.org/simple/ bates-labeler
```

### Production PyPI

```bash
# Publish to PyPI (requires PyPI account and API token)
poetry publish --build

# Or build first, then publish
poetry build
poetry publish
```

## Package Metadata

The package is configured with the following metadata for PyPI:

- **Name:** bates-labeler
- **Version:** 1.1.0
- **Python:** >=3.8.1
- **License:** MIT
- **Keywords:** bates, bates-numbering, legal, lawyers, paralegal, litigation, discovery, pdf-processing, legal-documents, etc.
- **Classifiers:** Production/Stable, Legal Industry, Office/Business, Console application

## Dependencies

### Main Dependencies
- pypdf ^4.0.0 - PDF manipulation
- reportlab ^4.0.7 - PDF generation
- tqdm ^4.66.1 - Progress bars

### Development Dependencies
- pytest ^7.4.0 - Testing framework
- pytest-cov ^4.1.0 - Code coverage
- black ^23.7.0 - Code formatter
- flake8 ^6.1.0 - Linter
- mypy ^1.5.0 - Type checker

## Test Results

All 11 tests pass successfully:
- ✅ Initialization with defaults
- ✅ Initialization with custom values
- ✅ Bates number generation
- ✅ Bates number with suffix
- ✅ Various padding widths
- ✅ Font styling (bold, italic, bold+italic)
- ✅ Color parsing
- ✅ Version check
- ✅ Module imports

## CLI Command

The package registers the `bates` command which provides the same functionality as the original script:

```bash
bates --input file.pdf --bates-prefix "PREFIX-"
bates --batch file1.pdf file2.pdf --bates-prefix "BATCH-"
bates --version
```

## Notes

- The original `bates-numbering-script.py` has been kept for reference but is no longer the primary entry point
- The package follows Python best practices with proper module structure
- All functionality from the original script is preserved
- The CLI command is now simply `bates` instead of `python bates-numbering-script.py`
- Tests provide 22% code coverage (primarily testing the BatesNumberer class initialization and number generation)

## Next Steps

1. **Update email in pyproject.toml** - Replace `adam@example.com` with your actual email
2. **Create PyPI account** - Sign up at https://pypi.org if you want to publish
3. **Generate API token** - For secure publishing to PyPI
4. **Test locally** - Ensure everything works as expected
5. **Publish to Test PyPI first** - Verify the package before production release
6. **Publish to PyPI** - Make it available to the world!

## Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Python Packaging User Guide](https://packaging.python.org/)
