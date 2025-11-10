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

# v2.3.0 Advanced features - gracefully degrade if dependencies not available
try:
    from bates_labeler.pdf_validator_advanced import (
        PDFValidatorAdvanced, ValidationReport as AdvancedValidationReport,
        ValidationIssue as AdvancedValidationIssue, RepairStrategy,
        validate_before_processing
    )
    ADVANCED_VALIDATOR_AVAILABLE = True
except ImportError:
    ADVANCED_VALIDATOR_AVAILABLE = False
    PDFValidatorAdvanced = None
    AdvancedValidationReport = None
    AdvancedValidationIssue = None
    RepairStrategy = None
    validate_before_processing = None

try:
    from bates_labeler.redaction import (
        RedactionEngine, RedactionType, RedactionMethod,
        RedactionPattern, RedactionZone, RedactionResult, quick_redact
    )
    REDACTION_AVAILABLE = True
except ImportError:
    REDACTION_AVAILABLE = False
    RedactionEngine = None
    RedactionType = None
    RedactionMethod = None
    RedactionPattern = None
    RedactionZone = None
    RedactionResult = None
    quick_redact = None

try:
    from bates_labeler.i18n import (
        I18nManager, Language, LocaleInfo, TextDirection,
        get_i18n, init_i18n, t
    )
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    I18nManager = None
    Language = None
    LocaleInfo = None
    TextDirection = None
    get_i18n = None
    init_i18n = None
    t = None

try:
    from bates_labeler.pdf_compare import (
        PDFComparator, ComparisonResult, PageDifference,
        DifferenceType, ComparisonMode, quick_compare, verify_bates_numbering
    )
    PDF_COMPARE_AVAILABLE = True
except ImportError:
    PDF_COMPARE_AVAILABLE = False
    PDFComparator = None
    ComparisonResult = None
    PageDifference = None
    DifferenceType = None
    ComparisonMode = None
    quick_compare = None
    verify_bates_numbering = None

try:
    from bates_labeler.audit_log import (
        AuditLogger, AuditEvent, AuditReport,
        EventType, EventSeverity, ComplianceStandard,
        get_audit_logger, init_audit_logger
    )
    AUDIT_LOG_AVAILABLE = True
except ImportError:
    AUDIT_LOG_AVAILABLE = False
    AuditLogger = None
    AuditEvent = None
    AuditReport = None
    EventType = None
    EventSeverity = None
    ComplianceStandard = None
    get_audit_logger = None
    init_audit_logger = None

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
    # Advanced PDF Validation (v2.3.0+)
    'ADVANCED_VALIDATOR_AVAILABLE',
    'PDFValidatorAdvanced',
    'AdvancedValidationReport',
    'AdvancedValidationIssue',
    'RepairStrategy',
    'validate_before_processing',
    # Redaction System (v2.3.0+)
    'REDACTION_AVAILABLE',
    'RedactionEngine',
    'RedactionType',
    'RedactionMethod',
    'RedactionPattern',
    'RedactionZone',
    'RedactionResult',
    'quick_redact',
    # Multi-Language Support (v2.3.0+)
    'I18N_AVAILABLE',
    'I18nManager',
    'Language',
    'LocaleInfo',
    'TextDirection',
    'get_i18n',
    'init_i18n',
    't',
    # PDF Comparison (v2.3.0+)
    'PDF_COMPARE_AVAILABLE',
    'PDFComparator',
    'ComparisonResult',
    'PageDifference',
    'DifferenceType',
    'ComparisonMode',
    'quick_compare',
    'verify_bates_numbering',
    # Audit Logging (v2.3.0+)
    'AUDIT_LOG_AVAILABLE',
    'AuditLogger',
    'AuditEvent',
    'AuditReport',
    'EventType',
    'EventSeverity',
    'ComplianceStandard',
    'get_audit_logger',
    'init_audit_logger',
]
