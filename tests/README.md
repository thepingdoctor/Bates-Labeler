# Bates-Labeler Test Suite

Comprehensive test suite for the Bates-Labeler project covering unit tests, integration tests, edge cases, performance, and CLI functionality.

## Test Organization

### `/tests/test_bates_numberer.py` (Existing)
Core unit tests for the `BatesNumberer` class:
- Initialization with default and custom values
- Bates number generation with various configurations
- Font name selection (bold, italic, bold-italic)
- Color parsing (named colors)
- Module imports and versioning

### `/tests/test_core_advanced.py` (New)
Advanced feature unit tests:
- **Logo Features**: PNG/SVG loading, placement options, size constraints
- **QR Code Features**: Initialization, generation, placement modes, color customization
- **Watermark Features**: Text rendering, opacity, rotation, positioning, scope
- **Border Features**: Styles (solid, dashed, double, asterisks), colors, widths, corners
- **Custom Font Features**: Font file registration, format validation, fallback handling
- **Callback Features**: Status callbacks, cancellation callbacks
- **Color Parsing**: Named colors, hex codes, invalid color fallback
- **Date/Time Stamping**: Enable/disable, custom formats
- **Background Padding**: Enable/disable, padding values

### `/tests/test_pdf_processing.py` (New)
PDF processing integration tests:
- **Basic PDF Processing**: Simple documents, separator pages, metadata return
- **Encrypted PDFs**: Password protection, correct/incorrect passwords
- **Continuous Numbering**: Across multiple PDFs, maintaining sequence
- **Page Sizes**: Letter, A4, Legal format handling
- **Batch Processing**: Multiple files, separator pages, continuous numbering
- **PDF Combination**: Merging documents, separator pages, index pages, metadata tracking
- **Filename Mapping**: CSV and PDF mapping file generation

### `/tests/test_edge_cases.py` (New)
Boundary conditions and error handling:
- **Edge Cases**: Empty prefix/suffix, very long prefix/suffix, max/min padding, large start numbers, number overflow, single page PDFs, very large PDFs (100+ pages), special/Unicode characters
- **Error Handling**: Nonexistent files, invalid directories, corrupted PDFs, invalid positions, invalid colors, callback exceptions
- **Cancellation**: Pre-processing cancellation, mid-processing cancellation
- **Memory Management**: Temporary file cleanup, QR code cleanup, multiple operations without leaks

### `/tests/test_performance.py` (New)
Performance benchmarks and scalability:
- **Large Documents**: 100-page, 500-page processing
- **Batch Performance**: 20 files with 10 pages each
- **PDF Combination**: 50 PDFs merged
- **Memory Usage**: Tracking with `tracemalloc`
- **Sequential Operations**: 10,000 Bates number generation
- **Overlay Creation**: 100 overlay generations
- **QR Code Generation**: 100 QR codes
- **Complex Features**: All features enabled simultaneously
- **Scalability**: Increasing page counts (10, 50, 100, 200), concurrent instances

### `/tests/test_cli.py` (New)
Command-line interface tests:
- **Basic Commands**: Version, help, basic processing
- **Options**: Separator pages, positions, fonts, date stamps, backgrounds
- **Batch Processing**: Multiple files, output directory
- **PDF Combination**: Merge, separators, index pages
- **Bates Filenames**: Output naming, mapping files
- **Custom Settings**: Padding, font sizes, special characters
- **Error Cases**: Nonexistent inputs, invalid options
- **Integration Workflows**: Complete legal document processing

### `/tests/conftest.py` (New)
Pytest configuration:
- Custom markers for slow tests
- `--runslow` option for performance tests
- Automatic slow test skipping

## Running Tests

### Run All Tests
```bash
# Standard test run
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=bates_labeler --cov-report=term-missing

# Skip slow tests (default)
pytest tests/ -v

# Include slow tests
pytest tests/ -v --runslow
```

### Run Specific Test Files
```bash
# Core functionality
pytest tests/test_bates_numberer.py -v

# Advanced features
pytest tests/test_core_advanced.py -v

# PDF processing
pytest tests/test_pdf_processing.py -v

# Edge cases
pytest tests/test_edge_cases.py -v

# Performance (slow)
pytest tests/test_performance.py -v --runslow

# CLI
pytest tests/test_cli.py -v
```

### Run Specific Test Classes or Methods
```bash
# Specific test class
pytest tests/test_core_advanced.py::TestLogoFeatures -v

# Specific test method
pytest tests/test_pdf_processing.py::TestPDFProcessing::test_process_simple_pdf -v
```

### Coverage Reports
```bash
# Terminal report
pytest tests/ --cov=bates_labeler --cov-report=term

# HTML report
pytest tests/ --cov=bates_labeler --cov-report=html

# XML report (for CI/CD)
pytest tests/ --cov=bates_labeler --cov-report=xml
```

## Test Coverage Goals

- **Statements**: >80%
- **Branches**: >75%
- **Functions**: >80%
- **Lines**: >80%

## Test Categories

### Unit Tests
- Test individual functions and methods in isolation
- Mock external dependencies
- Fast execution (<1ms per test)
- Located in: `test_bates_numberer.py`, `test_core_advanced.py`

### Integration Tests
- Test feature workflows end-to-end
- Use real PDF files and operations
- Moderate execution time
- Located in: `test_pdf_processing.py`

### Edge Case Tests
- Test boundary conditions
- Test error handling and recovery
- Test invalid inputs
- Located in: `test_edge_cases.py`

### Performance Tests
- Benchmark large operations
- Test scalability
- Memory usage tracking
- Marked with `@pytest.mark.slow`
- Located in: `test_performance.py`

### CLI Tests
- Test command-line interface
- Test argument parsing
- Test end-to-end workflows
- Located in: `test_cli.py`

## Test Fixtures

### Temporary Directories
All tests use temporary directories created in `setup_method()` and cleaned up in `teardown_method()`:
```python
def setup_method(self):
    self.temp_dir = tempfile.mkdtemp()

def teardown_method(self):
    if os.path.exists(self.temp_dir):
        shutil.rmtree(self.temp_dir)
```

### Test PDF Creation
Helper method to create test PDFs with customizable page counts:
```python
def _create_test_pdf(self, filename, num_pages=1):
    filepath = os.path.join(self.temp_dir, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    for i in range(num_pages):
        c.drawString(100, 750, f"Page {i + 1}")
        c.showPage()
    c.save()
    return filepath
```

## Continuous Integration

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    pytest tests/ -v --cov=bates_labeler --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Metrics

### Current Coverage (Target)
- **Core Module** (`core.py`): >85%
- **CLI Module** (`cli.py`): >80%
- **Streamlit App** (`app.py`): >70% (UI components harder to test)
- **Overall Project**: >80%

### Test Count by Category
- Unit Tests: ~60 tests
- Integration Tests: ~25 tests
- Edge Case Tests: ~30 tests
- Performance Tests: ~10 tests (slow)
- CLI Tests: ~30 tests
- **Total**: ~155 comprehensive tests

## Common Test Patterns

### Testing with Metadata Return
```python
result = numberer.process_pdf(input_path, output_path, return_metadata=True)
assert result['success'] is True
assert result['first_bates'] == "EXPECTED-0001"
assert result['page_count'] == 5
```

### Testing Callbacks
```python
messages = []
def status_callback(message, progress_dict=None):
    messages.append(message)

numberer = BatesNumberer(status_callback=status_callback)
# ... process ...
assert len(messages) > 0
```

### Testing Cancellation
```python
cancel_flag = [False]
def cancel_callback():
    return cancel_flag[0]

numberer = BatesNumberer(cancel_callback=cancel_callback)
cancel_flag[0] = True  # Trigger cancellation
result = numberer.process_pdf(...)
assert result.get('cancelled') is True
```

## Debugging Tests

### Run with Verbose Output
```bash
pytest tests/test_name.py -vv
```

### Run with Print Statements
```bash
pytest tests/test_name.py -s
```

### Run with PDB on Failure
```bash
pytest tests/test_name.py --pdb
```

### Show Full Traceback
```bash
pytest tests/test_name.py --tb=long
```

## Adding New Tests

1. Choose appropriate test file based on category
2. Add test class if needed (e.g., `TestNewFeature`)
3. Use descriptive test method names starting with `test_`
4. Include docstrings explaining what is tested
5. Use setup/teardown for temporary resources
6. Assert specific conditions, not general success
7. Mark slow tests with `@pytest.mark.slow`

### Example Test Template
```python
class TestNewFeature:
    """Test cases for new feature."""

    def setup_method(self):
        """Create temporary resources."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary resources."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_feature_basic_case(self):
        """Test basic functionality of new feature."""
        # Arrange
        numberer = BatesNumberer(new_feature=True)

        # Act
        result = numberer.do_something()

        # Assert
        assert result is not None
        assert result == expected_value
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run in milliseconds
3. **Descriptive**: Test names explain what is being tested
4. **Cleanup**: Always clean up temporary files
5. **Assertions**: Use specific assertions, not just "not None"
6. **Coverage**: Aim for high coverage but prioritize critical paths
7. **Documentation**: Include docstrings for complex tests
8. **Markers**: Use `@pytest.mark.slow` for time-consuming tests

## Troubleshooting

### Tests Fail Due to Missing Dependencies
```bash
# Install test dependencies
pip install pytest pytest-cov

# Or with poetry
poetry install --with dev
```

### Temporary File Cleanup Issues
Tests create temporary files and should clean them up. If you see leftover files:
- Check `teardown_method()` is being called
- Look for exceptions preventing cleanup
- Use `pytest --tb=short` to see failures

### Performance Tests Too Slow
Performance tests are marked with `@pytest.mark.slow`:
```bash
# Skip them by default
pytest tests/ -v

# Run them explicitly when needed
pytest tests/ -v --runslow
```

## Future Enhancements

- Add UI tests for Streamlit app (using Selenium or similar)
- Add security tests for PDF encryption
- Add accessibility tests for generated PDFs
- Add regression tests for specific bug fixes
- Improve CLI test coverage with more edge cases
- Add property-based testing with Hypothesis
