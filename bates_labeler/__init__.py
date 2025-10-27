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

# Optional AI analysis support - gracefully degrades if not available
try:
    from bates_labeler.ai_analysis import (
        AIAnalyzer, AIProvider, CacheManager, AIAnalysisConfig,
        OpenRouterProvider, GoogleCloudProvider, AnthropicProvider
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    AIAnalyzer = None
    AIProvider = None
    CacheManager = None
    AIAnalysisConfig = None
    OpenRouterProvider = None
    GoogleCloudProvider = None
    AnthropicProvider = None

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
    # AI analysis (optional)
    'AI_AVAILABLE',
    'AIAnalyzer',
    'AIProvider',
    'CacheManager',
    'AIAnalysisConfig',
    'OpenRouterProvider',
    'GoogleCloudProvider',
    'AnthropicProvider',
]
