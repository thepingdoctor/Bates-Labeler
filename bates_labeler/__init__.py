"""
Bates Labeler - Professional Bates numbering for legal documents.

A comprehensive Python tool for adding Bates numbers to PDF documents,
commonly used in legal document management and discovery processes.
"""

from bates_labeler.__version__ import __version__, __author__, __license__
from bates_labeler.core import BatesNumberer, POSITION_COORDINATES
from bates_labeler.validation import (
    PDFValidator, ValidationResult, ValidationIssue, ValidationSeverity
)
from bates_labeler.export import MetadataExporter
from bates_labeler.rotation import PageManipulator, RotationAngle
from bates_labeler.bates_validation import (
    BatesValidator, BatesRange, BatesConflict,
    validate_bates_pattern, parse_bates_number, generate_bates_number
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__license__',
    # Core functionality
    'BatesNumberer',
    'POSITION_COORDINATES',
    # PDF validation
    'PDFValidator',
    'ValidationResult',
    'ValidationIssue',
    'ValidationSeverity',
    # Metadata export
    'MetadataExporter',
    # Page manipulation
    'PageManipulator',
    'RotationAngle',
    # Bates validation
    'BatesValidator',
    'BatesRange',
    'BatesConflict',
    'validate_bates_pattern',
    'parse_bates_number',
    'generate_bates_number',
]
