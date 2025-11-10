# Bates-Labeler v2.3.0 - New Features Documentation

## Overview

Version 2.3.0 introduces five powerful new features that significantly enhance the Bates-Labeler toolkit with advanced validation, security, internationalization, quality control, and compliance capabilities.

---

## 🚀 New Features in v2.3.0

### 1. Advanced PDF Validation & Repair

**Module:** `bates_labeler.pdf_validator_advanced`

Comprehensive PDF health checking, corruption detection, and automatic repair capabilities for batch processing.

#### Key Features:
- **Deep PDF structure validation** - Validates PDF integrity, page structure, and metadata
- **Corruption detection** - Identifies corrupted or damaged PDFs
- **Automatic repair** - Attempts to repair corrupted PDFs using multiple strategies
- **Multi-strategy repair** - Supports qpdf, Ghostscript, and pypdf-based repair methods
- **Batch validation** - Validate multiple PDFs in parallel
- **Detailed reporting** - Comprehensive validation reports with severity levels

#### Usage Example:

```python
from bates_labeler import PDFValidatorAdvanced, RepairStrategy

# Initialize validator
validator = PDFValidatorAdvanced(
    enable_repair=True,
    repair_strategy=RepairStrategy.AUTO
)

# Validate a PDF
report = validator.validate_pdf("document.pdf")

print(report.summary())
# Output: PDF Validation Report: VALID
#         File: document.pdf
#         Pages: 25 | Size: 1024.50 KB
#         Issues: 0 critical, 0 errors, 0 warnings

# Repair corrupted PDF if needed
if not report.is_valid and report.is_repairable:
    success, message = validator.repair_pdf(
        "corrupted.pdf",
        "repaired.pdf"
    )
    print(f"Repair: {message}")
```

#### Validation Before Processing:

```python
from bates_labeler import validate_before_processing

# Automatically validate and repair before Bates numbering
is_valid, repaired_path, message = validate_before_processing(
    "input.pdf",
    auto_repair=True
)

if is_valid:
    # Proceed with Bates numbering
    if repaired_path:
        process_pdf(repaired_path)  # Use repaired version
    else:
        process_pdf("input.pdf")  # Use original
```

---

### 2. Advanced Redaction System

**Module:** `bates_labeler.redaction`

Automatically detect and redact sensitive information in PDF documents including SSNs, credit cards, emails, and custom patterns.

#### Key Features:
- **Pattern-based detection** - Built-in regex patterns for common sensitive data
- **Custom patterns** - Add your own redaction patterns
- **Multiple redaction methods** - Black box, white box, blur, strikethrough
- **Audit logging** - Track all redactions for compliance
- **Preview mode** - Preview redactions before applying
- **Batch redaction** - Redact multiple PDFs at once

#### Supported Information Types:
- Social Security Numbers (SSN)
- Credit Card Numbers
- Email Addresses
- Phone Numbers
- Dates
- Account Numbers
- Custom patterns

#### Usage Example:

```python
from bates_labeler import RedactionEngine, RedactionType, RedactionMethod

# Initialize redaction engine
engine = RedactionEngine(
    default_method=RedactionMethod.BLACK_BOX,
    create_audit_log=True
)

# Quick redaction with defaults
from bates_labeler import quick_redact

result = quick_redact(
    "document.pdf",
    "redacted.pdf",
    redaction_types=[
        RedactionType.SSN,
        RedactionType.CREDIT_CARD,
        RedactionType.EMAIL
    ]
)

print(f"Redacted {result.redaction_count} items")
print(result.audit_log)
```

#### Custom Redaction Patterns:

```python
import re
from bates_labeler import RedactionPattern, RedactionType

# Create custom pattern
custom_pattern = RedactionPattern(
    name="Internal ID",
    pattern=re.compile(r'ID-\d{6}'),
    redaction_type=RedactionType.CUSTOM,
    description="Internal employee ID numbers",
    replacement_text="[ID REDACTED]"
)

engine.add_custom_pattern(custom_pattern)

# Scan document for all patterns
zones = engine.scan_pdf("document.pdf", [
    RedactionType.SSN,
    RedactionType.CUSTOM
])

print(f"Found {len(zones)} items to redact")
```

---

### 3. Multi-Language Support (i18n)

**Module:** `bates_labeler.i18n`

Internationalization support enabling translation of UI elements and messages into multiple languages.

#### Key Features:
- **10+ languages supported** - English, Spanish, French, German, Chinese, Japanese, and more
- **Dynamic language switching** - Change language at runtime
- **Locale-specific formatting** - Dates, numbers, currencies formatted per locale
- **Translation management** - Import/export translation files
- **RTL language support** - Right-to-left text direction for Arabic, Hebrew
- **Custom translations** - Add your own translation files

#### Supported Languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Chinese Simplified (zh-CN)
- Japanese (ja)
- Portuguese (pt)
- Italian (it)
- Russian (ru)
- Korean (ko)

#### Usage Example:

```python
from bates_labeler import I18nManager, Language, get_i18n, t

# Initialize with Spanish
i18n = I18nManager(default_language=Language.SPANISH)

# Translate UI elements
title = i18n.translate("app_title")
# Output: "Herramienta de Numeración Bates"

# Use shorthand function
from bates_labeler import t

button_text = t("process")  # "Procesar PDF(s)"
success_msg = t("success")  # "¡Éxito!"

# Change language dynamically
i18n.set_language(Language.FRENCH)
button_text = t("process")  # "Traiter PDF(s)"

# Format numbers and dates per locale
locale = i18n.get_locale()
formatted_num = i18n.format_number(1234.56)
# Spanish: "1.234,56"
# English: "1,234.56"
# French: "1 234,56"
```

#### Custom Translations:

```python
# Export translations
i18n.export_translations("translations/", language=Language.ENGLISH)

# Import custom translations
i18n.import_translations("translations/custom_es.json")

# Get available languages
languages = i18n.get_available_languages()
for lang, native_name in languages.items():
    print(f"{lang.value}: {native_name}")
```

---

### 4. PDF Comparison & Diff Viewer

**Module:** `bates_labeler.pdf_compare`

Compare PDFs to identify differences between original and processed documents for quality control and verification.

#### Key Features:
- **Text-based comparison** - Compare extracted text content
- **Metadata comparison** - Compare PDF properties and metadata
- **Page-by-page analysis** - Detailed per-page difference detection
- **Similarity scoring** - Quantitative similarity measurement (0-100%)
- **Multiple report formats** - HTML, JSON, CSV reports
- **Bates numbering verification** - Verify correct application

#### Comparison Modes:
- **TEXT_ONLY** - Compare only text content
- **METADATA_ONLY** - Compare only metadata
- **FULL** - Complete comparison (text + metadata)
- **VISUAL** - Visual rendering comparison

#### Usage Example:

```python
from bates_labeler import PDFComparator, ComparisonMode, quick_compare

# Quick comparison
result = quick_compare("original.pdf", "bates_numbered.pdf")

print(result.summary)
# Output: Found 1 difference(s)
#         Similarity: 99.5%
#         Text modifications: 1
#         Metadata changes: 0

print(f"Documents identical: {result.are_identical}")
print(f"Similarity score: {result.similarity_score * 100:.1f}%")

# Detailed comparison
comparator = PDFComparator(comparison_mode=ComparisonMode.FULL)
result = comparator.compare_pdfs(
    "original.pdf",
    "processed.pdf",
    ignore_whitespace=True,
    ignore_case=False
)

# Get specific differences
for diff in result.differences:
    print(f"Page {diff.page_num}: {diff.description}")
```

#### Verify Bates Numbering:

```python
from bates_labeler import verify_bates_numbering

is_valid, result = verify_bates_numbering(
    "original.pdf",
    "bates_numbered.pdf"
)

if is_valid:
    print("✓ Bates numbering applied correctly")
else:
    print("✗ Bates numbering verification failed")
    for diff in result.differences:
        print(f"  - {diff.description}")
```

#### Generate Reports:

```python
# HTML report
comparator.generate_html_report(result, "comparison_report.html")

# JSON report
comparator.generate_json_report(result, "comparison_report.json")
```

---

### 5. Audit Trail & Compliance Logging

**Module:** `bates_labeler.audit_log`

Comprehensive audit logging system for legal compliance, tracking all operations with tamper-proof logging.

#### Key Features:
- **Tamper-proof logging** - Blockchain-style event chaining for integrity
- **Comprehensive event tracking** - Tracks all PDF operations and user actions
- **SQLite-based storage** - Efficient, portable audit database
- **Compliance reporting** - Reports for HIPAA, SOC2, GDPR, ISO27001
- **Multiple export formats** - JSON, CSV, PDF audit reports
- **Chain of custody** - Complete document processing history
- **Event severity levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL

#### Tracked Events:
- PDF Upload/Download/Delete
- Configuration Changes
- Processing Operations
- Validation/Redaction/Comparison
- User Login/Logout
- System Events
- Errors and Warnings

#### Usage Example:

```python
from bates_labeler import (
    AuditLogger, EventType, EventSeverity,
    get_audit_logger, init_audit_logger
)

# Initialize audit logger
audit = init_audit_logger(
    db_path=".bates_audit.db",
    enable_blockchain=True,
    compliance_standards=[ComplianceStandard.SOC2, ComplianceStandard.HIPAA]
)

# Log events
audit.log_event(
    event_type=EventType.PDF_PROCESS,
    severity=EventSeverity.INFO,
    user_id="john.doe@example.com",
    session_id="session-12345",
    description="Processed legal-brief.pdf with Bates numbering",
    details={
        "prefix": "CASE-001",
        "start_number": 1,
        "page_count": 25
    },
    file_path="legal-brief.pdf",
    success=True
)

# Retrieve audit events
from datetime import datetime, timedelta

events = audit.get_events(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    event_type=EventType.PDF_PROCESS,
    user_id="john.doe@example.com"
)

print(f"Found {len(events)} events in last 30 days")
```

#### Generate Compliance Reports:

```python
from datetime import datetime, timedelta

# Generate monthly audit report
report = audit.generate_report(
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now(),
    include_details=True
)

print(f"Total events: {report.total_events}")
print(f"Unique users: {report.unique_users}")
print(f"Success rate: {report.successful_operations / report.total_events * 100:.1f}%")

if report.compliance_issues:
    print("Compliance issues detected:")
    for issue in report.compliance_issues:
        print(f"  - {issue}")
```

#### Verify Audit Trail Integrity:

```python
# Verify blockchain integrity
is_valid = audit.verify_chain_integrity()

if is_valid:
    print("✓ Audit trail integrity verified - no tampering detected")
else:
    print("✗ Audit trail integrity check failed - possible tampering")
```

#### Export Audit Logs:

```python
# Export to JSON
audit.export_to_json(
    "audit_log_2025.json",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31)
)

# Export to CSV
audit.export_to_csv(
    "audit_log_2025.csv",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31)
)
```

---

## Installation

### Install v2.3.0 Features

All v2.3.0 features are included in the base installation:

```bash
# Standard installation
pip install bates-labeler

# Or with Poetry
poetry add bates-labeler
```

### Optional Dependencies

Some features have optional dependencies for enhanced functionality:

```bash
# For PDF repair with qpdf
sudo apt-get install qpdf  # Linux
brew install qpdf          # macOS

# For PDF repair with Ghostscript
sudo apt-get install ghostscript  # Linux
brew install ghostscript          # macOS
```

---

## Integration Examples

### Complete Workflow with All v2.3.0 Features

```python
from bates_labeler import (
    # Core
    BatesNumberer,
    # v2.3.0 Features
    PDFValidatorAdvanced,
    RedactionEngine, RedactionType,
    I18nManager, Language,
    PDFComparator,
    AuditLogger, EventType, EventSeverity
)

# 1. Initialize systems
audit = AuditLogger(enable_blockchain=True)
i18n = I18nManager(default_language=Language.ENGLISH)
validator = PDFValidatorAdvanced(enable_repair=True)
redactor = RedactionEngine()
comparator = PDFComparator()

# 2. Validate PDF
audit.log_event(
    EventType.VALIDATION, EventSeverity.INFO,
    "user@example.com", "session-123",
    "Validating document.pdf"
)

report = validator.validate_pdf("document.pdf")
if not report.is_valid and report.is_repairable:
    success, msg = validator.repair_pdf("document.pdf", "repaired.pdf")
    audit.log_event(
        EventType.VALIDATION, EventSeverity.INFO,
        "user@example.com", "session-123",
        f"PDF repair: {msg}"
    )

# 3. Redact sensitive information
redaction_result = redactor.auto_redact(
    "repaired.pdf",
    "redacted.pdf",
    redaction_types=[RedactionType.SSN, RedactionType.EMAIL]
)

audit.log_event(
    EventType.REDACTION, EventSeverity.INFO,
    "user@example.com", "session-123",
    f"Redacted {redaction_result.redaction_count} items"
)

# 4. Apply Bates numbering
numberer = BatesNumberer(prefix="CASE-001-", start_number=1)
numberer.process_pdf("redacted.pdf", "bates_numbered.pdf")

audit.log_event(
    EventType.PDF_PROCESS, EventSeverity.INFO,
    "user@example.com", "session-123",
    "Applied Bates numbering"
)

# 5. Verify result
comparison = comparator.compare_pdfs("redacted.pdf", "bates_numbered.pdf")
print(f"Similarity: {comparison.similarity_score * 100:.1f}%")

# 6. Generate audit report
audit_report = audit.generate_report(
    start_date=datetime.now() - timedelta(hours=1),
    end_date=datetime.now()
)
print(f"Total operations: {audit_report.total_events}")
```

---

## API Reference

### PDFValidatorAdvanced

```python
class PDFValidatorAdvanced:
    def __init__(
        self,
        enable_repair: bool = True,
        repair_strategy: RepairStrategy = RepairStrategy.AUTO
    ):
        """Initialize advanced PDF validator."""

    def validate_pdf(self, pdf_path: str) -> ValidationReport:
        """Validate a PDF file."""

    def repair_pdf(
        self,
        pdf_path: str,
        output_path: str,
        strategy: Optional[RepairStrategy] = None
    ) -> Tuple[bool, str]:
        """Repair a corrupted PDF."""

    def batch_validate(
        self,
        pdf_paths: List[str],
        stop_on_error: bool = False
    ) -> List[ValidationReport]:
        """Validate multiple PDFs."""
```

### RedactionEngine

```python
class RedactionEngine:
    def __init__(
        self,
        default_method: RedactionMethod = RedactionMethod.BLACK_BOX,
        create_audit_log: bool = True
    ):
        """Initialize redaction engine."""

    def scan_pdf(
        self,
        pdf_path: str,
        redaction_types: List[RedactionType]
    ) -> List[RedactionZone]:
        """Scan PDF for sensitive information."""

    def apply_redactions(
        self,
        pdf_path: str,
        output_path: str,
        redaction_zones: List[RedactionZone],
        permanent: bool = True
    ) -> RedactionResult:
        """Apply redactions to PDF."""

    def auto_redact(
        self,
        pdf_path: str,
        output_path: str,
        redaction_types: List[RedactionType]
    ) -> RedactionResult:
        """Automatically detect and redact."""
```

### I18nManager

```python
class I18nManager:
    def __init__(
        self,
        default_language: Language = Language.ENGLISH,
        translations_dir: Optional[str] = None
    ):
        """Initialize i18n manager."""

    def set_language(self, language: Language) -> None:
        """Set current language."""

    def translate(self, key: str, **kwargs) -> str:
        """Get translation for key."""

    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate()."""

    def export_translations(
        self,
        output_dir: str,
        language: Optional[Language] = None
    ) -> None:
        """Export translation files."""
```

### PDFComparator

```python
class PDFComparator:
    def __init__(
        self,
        comparison_mode: ComparisonMode = ComparisonMode.FULL
    ):
        """Initialize PDF comparator."""

    def compare_pdfs(
        self,
        pdf1_path: str,
        pdf2_path: str,
        ignore_whitespace: bool = True,
        ignore_case: bool = False
    ) -> ComparisonResult:
        """Compare two PDFs."""

    def generate_html_report(
        self,
        result: ComparisonResult,
        output_path: str
    ) -> bool:
        """Generate HTML comparison report."""
```

### AuditLogger

```python
class AuditLogger:
    def __init__(
        self,
        db_path: Optional[str] = None,
        enable_blockchain: bool = True,
        compliance_standards: Optional[List[ComplianceStandard]] = None
    ):
        """Initialize audit logger."""

    def log_event(
        self,
        event_type: EventType,
        severity: EventSeverity,
        user_id: str,
        session_id: str,
        description: str,
        **kwargs
    ) -> AuditEvent:
        """Log an audit event."""

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **filters
    ) -> List[AuditEvent]:
        """Retrieve audit events."""

    def generate_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> AuditReport:
        """Generate compliance report."""
```

---

## Migration from v2.2.0

All v2.3.0 features are optional and backward compatible:

```python
# Check feature availability
from bates_labeler import (
    ADVANCED_VALIDATOR_AVAILABLE,
    REDACTION_AVAILABLE,
    I18N_AVAILABLE,
    PDF_COMPARE_AVAILABLE,
    AUDIT_LOG_AVAILABLE
)

if ADVANCED_VALIDATOR_AVAILABLE:
    # Use advanced validation features
    pass

if REDACTION_AVAILABLE:
    # Use redaction features
    pass
```

---

## Performance Considerations

### Validation & Repair
- Ghostscript repair: Slower but handles complex corruptions
- qpdf repair: Faster, recommended for most cases
- pypdf rewrite: Fastest, basic repairs only

### Redaction
- Pattern matching: O(n) where n = document size
- Large documents: Consider processing in chunks
- Audit logging: Minimal overhead (<1% performance impact)

### Comparison
- Text comparison: Fast for most documents
- Visual comparison: Slower, requires rendering
- Use `ignore_whitespace=True` for better performance

### Audit Logging
- Blockchain mode: Minimal overhead, worth the security
- SQLite storage: Efficient for millions of events
- Export only needed date ranges for faster processing

---

## Troubleshooting

### PDF Validation Issues

**Problem**: Validation reports false positives
- Solution: Check PDF with external tools (Adobe Acrobat)
- Try different repair strategies

**Problem**: Repair fails consistently
- Solution: Install qpdf and Ghostscript
- Try manual repair with external tools

### Redaction Issues

**Problem**: Patterns not detected
- Solution: Test regex patterns separately
- Add custom patterns for specific formats

**Problem**: Redaction zones incorrect
- Solution: This is a limitation of text extraction
- Use manual redaction zones for precision

### Internationalization Issues

**Problem**: Missing translations
- Solution: Check language is in DEFAULT_TRANSLATIONS
- Import custom translation file

**Problem**: Incorrect formatting
- Solution: Verify locale configuration
- Check date/number format strings

### Comparison Issues

**Problem**: High false positive rate
- Solution: Use `ignore_whitespace=True` and `ignore_case=True`
- Try TEXT_ONLY mode

### Audit Log Issues

**Problem**: Database locked
- Solution: Close all connections before accessing
- Use separate audit logger instances per process

---

## Support & Feedback

- **Documentation**: [GitHub Wiki](https://github.com/thepingdoctor/Bates-Labeler)
- **Issues**: [GitHub Issues](https://github.com/thepingdoctor/Bates-Labeler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thepingdoctor/Bates-Labeler/discussions)

---

## License

All v2.3.0 features are released under the same license as Bates-Labeler core.
