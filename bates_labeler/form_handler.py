"""PDF Form Field Preservation for Bates-Labeler.

This module preserves interactive PDF form fields during Bates numbering:
- Detect and preserve form fields
- Maintain field functionality
- Support for AcroForms and XFA forms
- Preserve JavaScript actions
- Handle digital signatures appropriately
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DictionaryObject
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        from PyPDF2.generic import DictionaryObject
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class FormFieldInfo:
    """Information about a PDF form field.

    Attributes:
        field_type: Field type (text, checkbox, radio, etc.)
        field_name: Field name
        field_value: Current field value
        rect: Field rectangle coordinates
        flags: Field flags
        options: Field options (for choice fields)
    """

    def __init__(
        self,
        field_type: str,
        field_name: str,
        field_value: Any = None,
        rect: Optional[tuple] = None,
        flags: int = 0,
        options: Optional[List[str]] = None
    ):
        """Initialize form field info.

        Args:
            field_type: Field type
            field_name: Field name
            field_value: Field value
            rect: Field rectangle
            flags: Field flags
            options: Field options
        """
        self.field_type = field_type
        self.field_name = field_name
        self.field_value = field_value
        self.rect = rect
        self.flags = flags
        self.options = options or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'field_type': self.field_type,
            'field_name': self.field_name,
            'field_value': self.field_value,
            'rect': self.rect,
            'flags': self.flags,
            'options': self.options
        }


class PDFFormHandler:
    """Handler for preserving PDF form fields during processing.

    Features:
    - Detect interactive form fields
    - Extract form field information
    - Preserve form fields during Bates numbering
    - Maintain field functionality
    - Handle digital signatures
    """

    # Form field types
    FIELD_TYPES = {
        '/Tx': 'text',
        '/Btn': 'button',
        '/Ch': 'choice',
        '/Sig': 'signature'
    }

    def __init__(self):
        """Initialize form handler."""
        if not PYPDF_AVAILABLE:
            raise ImportError(
                "pypdf not installed. Install with: pip install pypdf"
            )

    def has_form_fields(self, pdf_path: Union[str, Path]) -> bool:
        """Check if PDF has interactive form fields.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if PDF has form fields
        """
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)

                if '/AcroForm' in reader.trailer['/Root']:
                    return True

                # Check for XFA forms
                if '/XFA' in reader.trailer['/Root']:
                    return True

        except Exception as e:
            logger.error(f"Error checking form fields: {e}")

        return False

    def extract_form_fields(self, pdf_path: Union[str, Path]) -> List[FormFieldInfo]:
        """Extract form field information from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of form field information
        """
        fields = []

        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)

                if '/AcroForm' not in reader.trailer['/Root']:
                    return fields

                acroform = reader.trailer['/Root']['/AcroForm']

                if '/Fields' in acroform:
                    field_list = acroform['/Fields']

                    for field_ref in field_list:
                        field = field_ref.get_object()

                        field_info = self._parse_field(field)
                        if field_info:
                            fields.append(field_info)

        except Exception as e:
            logger.error(f"Error extracting form fields: {e}")

        return fields

    def _parse_field(self, field: DictionaryObject) -> Optional[FormFieldInfo]:
        """Parse a form field object.

        Args:
            field: PDF field dictionary

        Returns:
            FormFieldInfo or None
        """
        try:
            # Get field type
            field_type_key = field.get('/FT', '/Tx')
            field_type = self.FIELD_TYPES.get(field_type_key, 'unknown')

            # Get field name
            field_name = field.get('/T', 'unnamed')
            if hasattr(field_name, 'get_original_bytes'):
                field_name = field_name.get_original_bytes().decode('utf-8', errors='ignore')

            # Get field value
            field_value = field.get('/V')

            # Get field rectangle
            rect = field.get('/Rect')
            if rect:
                rect = tuple(float(x) for x in rect)

            # Get field flags
            flags = int(field.get('/Ff', 0))

            # Get options (for choice fields)
            options = []
            if '/Opt' in field:
                opt = field['/Opt']
                if isinstance(opt, list):
                    options = [str(o) for o in opt]

            return FormFieldInfo(
                field_type=field_type,
                field_name=field_name,
                field_value=field_value,
                rect=rect,
                flags=flags,
                options=options
            )

        except Exception as e:
            logger.error(f"Error parsing field: {e}")
            return None

    def preserve_form_fields(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        processed_pdf_data: bytes
    ) -> bool:
        """Preserve form fields in processed PDF.

        This method takes the processed PDF (with Bates numbers added)
        and reapplies the original form fields.

        Args:
            input_path: Original PDF path
            output_path: Output PDF path
            processed_pdf_data: Processed PDF bytes

        Returns:
            True if successful
        """
        try:
            # Read original PDF to get form fields
            with open(input_path, 'rb') as f:
                original_reader = PdfReader(f)

                if '/AcroForm' not in original_reader.trailer['/Root']:
                    # No forms, just save processed PDF
                    with open(output_path, 'wb') as out:
                        out.write(processed_pdf_data)
                    return True

                # Get original AcroForm
                original_acroform = original_reader.trailer['/Root']['/AcroForm']

            # Read processed PDF
            import io
            processed_reader = PdfReader(io.BytesIO(processed_pdf_data))

            # Create writer
            writer = PdfWriter()

            # Copy pages from processed PDF
            for page in processed_reader.pages:
                writer.add_page(page)

            # Copy form fields from original PDF
            if '/AcroForm' in original_reader.trailer['/Root']:
                writer._root_object.update({
                    '/AcroForm': original_acroform
                })

            # Write output
            with open(output_path, 'wb') as out:
                writer.write(out)

            logger.info(f"Preserved form fields in {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error preserving form fields: {e}")
            return False

    def validate_form_fields(
        self,
        original_path: Union[str, Path],
        processed_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """Validate that form fields were preserved correctly.

        Args:
            original_path: Original PDF path
            processed_path: Processed PDF path

        Returns:
            Validation results dictionary
        """
        results = {
            'valid': False,
            'original_fields': 0,
            'preserved_fields': 0,
            'missing_fields': [],
            'errors': []
        }

        try:
            # Extract fields from both PDFs
            original_fields = self.extract_form_fields(original_path)
            processed_fields = self.extract_form_fields(processed_path)

            results['original_fields'] = len(original_fields)
            results['preserved_fields'] = len(processed_fields)

            # Check for missing fields
            original_names = {f.field_name for f in original_fields}
            processed_names = {f.field_name for f in processed_fields}

            missing = original_names - processed_names
            if missing:
                results['missing_fields'] = list(missing)

            # Validation passed if all fields preserved
            results['valid'] = len(missing) == 0

        except Exception as e:
            results['errors'].append(str(e))
            logger.error(f"Error validating form fields: {e}")

        return results

    def get_form_summary(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Get summary of form fields in PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Summary dictionary with field counts and types
        """
        summary = {
            'has_forms': False,
            'total_fields': 0,
            'field_types': {},
            'field_names': []
        }

        try:
            if not self.has_form_fields(pdf_path):
                return summary

            summary['has_forms'] = True

            fields = self.extract_form_fields(pdf_path)
            summary['total_fields'] = len(fields)

            # Count by type
            type_counts = {}
            for field in fields:
                field_type = field.field_type
                type_counts[field_type] = type_counts.get(field_type, 0) + 1
                summary['field_names'].append(field.field_name)

            summary['field_types'] = type_counts

        except Exception as e:
            logger.error(f"Error getting form summary: {e}")

        return summary
