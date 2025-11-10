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

# New features - gracefully degrade if dependencies not available
try:
    from bates_labeler.config_manager import BatesConfig, ConfigManager, load_config_from_env
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    BatesConfig = None
    ConfigManager = None
    load_config_from_env = None

try:
    from bates_labeler.template_manager import Template, TemplateMetadata, TemplateManager
    TEMPLATE_MANAGER_AVAILABLE = True
except ImportError:
    TEMPLATE_MANAGER_AVAILABLE = False
    Template = None
    TemplateMetadata = None
    TemplateManager = None

try:
    from bates_labeler.scheduler import BatchScheduler, Job, JobStatus, JobType
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    BatchScheduler = None
    Job = None
    JobStatus = None
    JobType = None

try:
    from bates_labeler.cloud_storage import (
        CloudStorageManager, GoogleDriveProvider, DropboxProvider
    )
    CLOUD_STORAGE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_AVAILABLE = False
    CloudStorageManager = None
    GoogleDriveProvider = None
    DropboxProvider = None

try:
    from bates_labeler.form_handler import PDFFormHandler, FormFieldInfo
    FORM_HANDLER_AVAILABLE = True
except ImportError:
    FORM_HANDLER_AVAILABLE = False
    PDFFormHandler = None
    FormFieldInfo = None

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
    # Configuration management (v2.2.0+)
    'CONFIG_MANAGER_AVAILABLE',
    'BatesConfig',
    'ConfigManager',
    'load_config_from_env',
    # Template management (v2.2.0+)
    'TEMPLATE_MANAGER_AVAILABLE',
    'Template',
    'TemplateMetadata',
    'TemplateManager',
    # Batch scheduling (v2.2.0+)
    'SCHEDULER_AVAILABLE',
    'BatchScheduler',
    'Job',
    'JobStatus',
    'JobType',
    # Cloud storage (v2.2.0+)
    'CLOUD_STORAGE_AVAILABLE',
    'CloudStorageManager',
    'GoogleDriveProvider',
    'DropboxProvider',
    # Form field preservation (v2.2.0+)
    'FORM_HANDLER_AVAILABLE',
    'PDFFormHandler',
    'FormFieldInfo',
]
