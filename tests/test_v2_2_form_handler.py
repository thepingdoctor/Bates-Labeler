"""
Comprehensive Test Suite for PDF Form Handler (v2.2.0 Feature #5)

Tests PDF form field preservation functionality including:
- Form field detection
- Form field extraction
- Form field preservation during Bates numbering
- Form field validation
- Support for various field types
- Form summary generation
"""

import io
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from bates_labeler.form_handler import (
    FormFieldInfo,
    PDFFormHandler,
    PYPDF_AVAILABLE
)


# Skip all tests if pypdf not available
pytestmark = pytest.mark.skipif(
    not PYPDF_AVAILABLE,
    reason="pypdf not installed"
)


class TestFormFieldInfo:
    """Test FormFieldInfo class."""

    def test_create_form_field_info(self):
        """Test creating form field info."""
        field = FormFieldInfo(
            field_type="text",
            field_name="FirstName",
            field_value="John",
            rect=(100, 200, 300, 220),
            flags=0,
            options=[]
        )

        assert field.field_type == "text"
        assert field.field_name == "FirstName"
        assert field.field_value == "John"
        assert field.rect == (100, 200, 300, 220)
        assert field.flags == 0

    def test_field_info_to_dict(self):
        """Test converting field info to dictionary."""
        field = FormFieldInfo(
            field_type="checkbox",
            field_name="AcceptTerms",
            field_value=True,
            rect=(50, 50, 70, 70),
            flags=1
        )

        field_dict = field.to_dict()

        assert field_dict["field_type"] == "checkbox"
        assert field_dict["field_name"] == "AcceptTerms"
        assert field_dict["field_value"] is True
        assert field_dict["rect"] == (50, 50, 70, 70)
        assert field_dict["flags"] == 1

    def test_field_with_options(self):
        """Test field with options (choice field)."""
        field = FormFieldInfo(
            field_type="choice",
            field_name="Country",
            field_value="USA",
            options=["USA", "Canada", "Mexico"]
        )

        assert field.field_type == "choice"
        assert len(field.options) == 3
        assert "USA" in field.options


class TestPDFFormHandler:
    """Test PDFFormHandler functionality."""

    @pytest.fixture
    def handler(self):
        """Create PDFFormHandler instance."""
        return PDFFormHandler()

    @pytest.fixture
    def mock_pdf_with_forms(self):
        """Create mock PDF reader with form fields."""
        mock_reader = MagicMock()
        mock_reader.trailer = {
            '/Root': {
                '/AcroForm': {
                    '/Fields': [
                        MagicMock(),  # Field 1
                        MagicMock()   # Field 2
                    ]
                }
            }
        }
        return mock_reader

    @pytest.fixture
    def mock_pdf_without_forms(self):
        """Create mock PDF reader without form fields."""
        mock_reader = MagicMock()
        mock_reader.trailer = {
            '/Root': {}
        }
        return mock_reader

    def test_handler_initialization(self, handler):
        """Test PDFFormHandler initialization."""
        assert handler is not None

    def test_has_form_fields_true(self, handler):
        """Test detecting PDF with form fields."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {'/AcroForm': {}}
                }
                mock_reader_class.return_value = mock_reader

                result = handler.has_form_fields(tmp_path)

                assert result is True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_has_form_fields_false(self, handler):
        """Test detecting PDF without form fields."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {}
                }
                mock_reader_class.return_value = mock_reader

                result = handler.has_form_fields(tmp_path)

                assert result is False
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_has_xfa_forms(self, handler):
        """Test detecting XFA forms."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {'/XFA': {}}
                }
                mock_reader_class.return_value = mock_reader

                result = handler.has_form_fields(tmp_path)

                assert result is True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_extract_form_fields(self, handler):
        """Test extracting form fields from PDF."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                # Create mock field
                mock_field = MagicMock()
                mock_field.get.side_effect = lambda key, default=None: {
                    '/FT': '/Tx',
                    '/T': 'FirstName',
                    '/V': 'John',
                    '/Rect': [100, 200, 300, 220],
                    '/Ff': 0
                }.get(key, default)

                mock_field_ref = MagicMock()
                mock_field_ref.get_object.return_value = mock_field

                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {
                        '/AcroForm': {
                            '/Fields': [mock_field_ref]
                        }
                    }
                }
                mock_reader_class.return_value = mock_reader

                fields = handler.extract_form_fields(tmp_path)

                assert len(fields) == 1
                assert fields[0].field_name == 'FirstName'
                assert fields[0].field_type == 'text'
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_extract_fields_no_acroform(self, handler):
        """Test extracting fields from PDF without AcroForm."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {}
                }
                mock_reader_class.return_value = mock_reader

                fields = handler.extract_form_fields(tmp_path)

                assert len(fields) == 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_parse_field_types(self, handler):
        """Test parsing different field types."""
        # Mock field for each type
        field_types = [
            ('/Tx', 'text'),
            ('/Btn', 'button'),
            ('/Ch', 'choice'),
            ('/Sig', 'signature')
        ]

        for ft_key, expected_type in field_types:
            mock_field = MagicMock()
            mock_field.get.side_effect = lambda key, default=None: {
                '/FT': ft_key,
                '/T': 'TestField',
                '/Ff': 0
            }.get(key, default)

            field_info = handler._parse_field(mock_field)

            assert field_info is not None
            assert field_info.field_type == expected_type

    def test_preserve_form_fields(self, handler):
        """Test preserving form fields in processed PDF."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_tmp:
            input_path = input_tmp.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_tmp:
            output_path = output_tmp.name

        try:
            processed_data = b"mock processed PDF data"

            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                with patch('bates_labeler.form_handler.PdfWriter') as mock_writer_class:
                    # Setup mock original PDF with forms
                    mock_original = MagicMock()
                    mock_original.trailer = {
                        '/Root': {
                            '/AcroForm': {'mock': 'acroform'}
                        }
                    }

                    # Setup mock processed PDF
                    mock_processed = MagicMock()
                    mock_processed.pages = [MagicMock()]

                    # Setup mock writer
                    mock_writer = MagicMock()
                    mock_writer_class.return_value = mock_writer

                    # Configure PdfReader to return different mocks for different calls
                    call_count = [0]

                    def reader_side_effect(*args, **kwargs):
                        call_count[0] += 1
                        if call_count[0] == 1:
                            return mock_original  # First call for original
                        else:
                            return mock_processed  # Second call for processed

                    mock_reader_class.side_effect = reader_side_effect

                    success = handler.preserve_form_fields(
                        input_path,
                        output_path,
                        processed_data
                    )

                    assert success
                    mock_writer.write.assert_called_once()

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_preserve_fields_no_forms(self, handler):
        """Test preserving when no forms exist."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_tmp:
            input_path = input_tmp.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_tmp:
            output_path = output_tmp.name

        try:
            processed_data = b"mock processed PDF data"

            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader = MagicMock()
                mock_reader.trailer = {
                    '/Root': {}  # No AcroForm
                }
                mock_reader_class.return_value = mock_reader

                success = handler.preserve_form_fields(
                    input_path,
                    output_path,
                    processed_data
                )

                assert success
                # Should just save the processed data
                assert Path(output_path).exists()

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def test_validate_form_fields(self, handler):
        """Test validating form field preservation."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as original_tmp:
            original_path = original_tmp.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as processed_tmp:
            processed_path = processed_tmp.name

        try:
            with patch.object(handler, 'extract_form_fields') as mock_extract:
                # Mock original fields
                original_fields = [
                    FormFieldInfo('text', 'Field1'),
                    FormFieldInfo('text', 'Field2')
                ]

                # Mock preserved fields (same as original)
                preserved_fields = [
                    FormFieldInfo('text', 'Field1'),
                    FormFieldInfo('text', 'Field2')
                ]

                mock_extract.side_effect = [original_fields, preserved_fields]

                results = handler.validate_form_fields(original_path, processed_path)

                assert results['valid'] is True
                assert results['original_fields'] == 2
                assert results['preserved_fields'] == 2
                assert len(results['missing_fields']) == 0

        finally:
            Path(original_path).unlink(missing_ok=True)
            Path(processed_path).unlink(missing_ok=True)

    def test_validate_with_missing_fields(self, handler):
        """Test validation with missing fields."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as original_tmp:
            original_path = original_tmp.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as processed_tmp:
            processed_path = processed_tmp.name

        try:
            with patch.object(handler, 'extract_form_fields') as mock_extract:
                # Mock original fields
                original_fields = [
                    FormFieldInfo('text', 'Field1'),
                    FormFieldInfo('text', 'Field2'),
                    FormFieldInfo('text', 'Field3')
                ]

                # Mock preserved fields (missing Field3)
                preserved_fields = [
                    FormFieldInfo('text', 'Field1'),
                    FormFieldInfo('text', 'Field2')
                ]

                mock_extract.side_effect = [original_fields, preserved_fields]

                results = handler.validate_form_fields(original_path, processed_path)

                assert results['valid'] is False
                assert results['original_fields'] == 3
                assert results['preserved_fields'] == 2
                assert 'Field3' in results['missing_fields']

        finally:
            Path(original_path).unlink(missing_ok=True)
            Path(processed_path).unlink(missing_ok=True)

    def test_get_form_summary(self, handler):
        """Test getting form summary."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch.object(handler, 'has_form_fields', return_value=True):
                with patch.object(handler, 'extract_form_fields') as mock_extract:
                    # Mock fields of different types
                    mock_fields = [
                        FormFieldInfo('text', 'FirstName'),
                        FormFieldInfo('text', 'LastName'),
                        FormFieldInfo('button', 'Submit'),
                        FormFieldInfo('choice', 'Country')
                    ]
                    mock_extract.return_value = mock_fields

                    summary = handler.get_form_summary(tmp_path)

                    assert summary['has_forms'] is True
                    assert summary['total_fields'] == 4
                    assert summary['field_types']['text'] == 2
                    assert summary['field_types']['button'] == 1
                    assert summary['field_types']['choice'] == 1
                    assert len(summary['field_names']) == 4

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_get_form_summary_no_forms(self, handler):
        """Test getting summary for PDF without forms."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch.object(handler, 'has_form_fields', return_value=False):
                summary = handler.get_form_summary(tmp_path)

                assert summary['has_forms'] is False
                assert summary['total_fields'] == 0
                assert len(summary['field_types']) == 0

        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def handler(self):
        """Create PDFFormHandler instance."""
        return PDFFormHandler()

    def test_extract_fields_with_error(self, handler):
        """Test handling errors during field extraction."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader_class.side_effect = Exception("Read error")

                fields = handler.extract_form_fields(tmp_path)

                # Should return empty list on error
                assert len(fields) == 0

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_parse_field_with_error(self, handler):
        """Test handling errors during field parsing."""
        mock_field = MagicMock()
        mock_field.get.side_effect = Exception("Parse error")

        field_info = handler._parse_field(mock_field)

        # Should return None on error
        assert field_info is None

    def test_preserve_fields_with_error(self, handler):
        """Test handling errors during field preservation."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_tmp:
            input_path = input_tmp.name

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_tmp:
            output_path = output_tmp.name

        try:
            with patch('bates_labeler.form_handler.PdfReader') as mock_reader_class:
                mock_reader_class.side_effect = Exception("Preservation error")

                success = handler.preserve_form_fields(
                    input_path,
                    output_path,
                    b"data"
                )

                assert success is False

        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
