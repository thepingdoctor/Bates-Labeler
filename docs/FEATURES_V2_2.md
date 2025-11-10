# Bates-Labeler v2.2.0 - New Features Documentation

## Overview

Version 2.2.0 introduces five major enhancements to the Bates-Labeler toolkit, focusing on enterprise workflows, automation, and advanced document processing capabilities.

---

## 🚀 New Features

### 1. Enhanced Configuration Manager

**Module:** `bates_labeler.config_manager`

Centralized configuration management with type validation, inheritance, and environment support.

#### Key Features:
- **Type-safe configurations** with Pydantic validation
- **Configuration inheritance** for template hierarchies
- **Environment variable support** (BATES_* prefix)
- **JSON import/export** for sharing configurations
- **Default value management**
- **Configuration namespacing**

#### Usage Example:

```python
from bates_labeler import ConfigManager, BatesConfig

# Initialize manager
manager = ConfigManager()

# Create configuration
config = manager.create_config(
    "legal_discovery",
    {
        "prefix": "DISC-",
        "start_number": 1,
        "padding": 6,
        "position": "bottom-right"
    }
)

# Save configuration
manager.save_config("legal_discovery")

# Load configuration
loaded = manager.load_config("legal_discovery")

# Export for sharing
manager.export_config("legal_discovery", "discovery_config.json")
```

#### Configuration Inheritance:

```python
# Create parent configuration
parent = manager.create_config(
    "parent",
    {"prefix": "CASE-", "start_number": 1}
)

# Create child with inheritance
child = manager.create_config(
    "child",
    {"suffix": "-CONF"},
    parent="parent"
)

# Child inherits parent's prefix
print(child.prefix)  # "CASE-"
print(child.suffix)  # "-CONF"
```

#### Environment Variables:

```bash
export BATES_PREFIX="ENV-"
export BATES_START_NUMBER="100"
export BATES_ENABLE_OCR="true"
```

```python
from bates_labeler import load_config_from_env

config = load_config_from_env()
# config = {'prefix': 'ENV-', 'start_number': 100, 'enable_ocr': True}
```

---

### 2. Template Management System

**Module:** `bates_labeler.template_manager`

Comprehensive template library for saving, loading, and sharing Bates numbering workflows.

#### Key Features:
- **Template library** with categories and tags
- **Default templates** (Legal Discovery, Confidential, Exhibits)
- **Template search and filtering**
- **Template duplication**
- **Import/export** for team sharing
- **Version metadata** tracking

#### Usage Example:

```python
from bates_labeler import TemplateManager

# Initialize manager
manager = TemplateManager()

# Create custom template
template = manager.create_template(
    name="Company Confidential",
    config={
        "prefix": "CONF-",
        "suffix": "-RESTRICTED",
        "start_number": 1,
        "padding": 6,
        "position": "top-right",
        "font_color": (255, 0, 0),  # Red text
        "enable_watermark": True,
        "watermark_text": "CONFIDENTIAL"
    },
    description="For confidential company documents",
    category="confidential",
    tags=["internal", "restricted"]
)

# Save template
manager.save_template("Company Confidential")

# Search templates
results = manager.search_templates("confidential")

# List by category
legal_templates = manager.list_templates(category="legal-discovery")

# Duplicate template
copy = manager.duplicate_template("Company Confidential", "Public Copy")

# Export for team
manager.export_template("Company Confidential", "conf_template.json")
```

#### Default Templates:

1. **Legal Discovery** - Standard discovery documents
2. **Confidential Documents** - Watermarked confidential files
3. **Exhibit Marking** - Court exhibit preparation

---

### 3. Batch Job Scheduler

**Module:** `bates_labeler.scheduler`

Automated scheduling for recurring batch processing jobs.

**Requires:** `APScheduler>=3.10.0`

#### Key Features:
- **One-time scheduled jobs** (specific date/time)
- **Recurring jobs** (cron-like scheduling)
- **Interval-based jobs** (every N seconds)
- **Watch folder automation** (auto-process new files)
- **Job queue management** (max concurrent jobs)
- **Job status tracking**
- **Email notifications** (optional)

#### Usage Example:

```python
from bates_labeler import BatchScheduler
from datetime import datetime, timedelta

# Initialize scheduler
scheduler = BatchScheduler(max_concurrent_jobs=3)
scheduler.start()

# Define processing function
def process_batch(config):
    from bates_labeler import BatesNumberer

    numberer = BatesNumberer(**config)
    for file in config['input_files']:
        output = file.replace('.pdf', '_numbered.pdf')
        numberer.process_pdf(file, output)

    return {'processed': len(config['input_files'])}

# Schedule one-time job
config = {
    'input_files': ['file1.pdf', 'file2.pdf'],
    'prefix': 'BATCH-',
    'start_number': 1
}

job_id = scheduler.schedule_one_time_job(
    name="Evening Batch",
    run_date=datetime.now() + timedelta(hours=2),
    process_func=process_batch,
    config=config
)

# Schedule recurring job (daily at 2am)
scheduler.schedule_recurring_job(
    name="Nightly Processing",
    cron_expression="0 2 * * *",
    process_func=process_batch,
    config=config
)

# Setup watch folder
scheduler.setup_watch_folder(
    name="Auto Process",
    watch_path="/path/to/incoming",
    process_func=process_batch,
    config=config,
    pattern="*.pdf",
    interval_seconds=60
)

# Check job status
status = scheduler.get_job_status(job_id)

# List all jobs
jobs = scheduler.list_jobs()

# Cancel job
scheduler.cancel_job(job_id)
```

#### Cron Expression Examples:

```python
"0 2 * * *"      # Daily at 2am
"0 */4 * * *"    # Every 4 hours
"0 0 * * MON"    # Every Monday at midnight
"0 8 1 * *"      # First day of month at 8am
"*/30 * * * *"   # Every 30 minutes
```

---

### 4. Cloud Storage Integration

**Module:** `bates_labeler.cloud_storage`

Seamless integration with major cloud storage providers.

**Supported Providers:**
- Google Drive
- Dropbox
- AWS S3 (via boto3)
- OneDrive/SharePoint (via onedrivesdk)

#### Key Features:
- **Upload/download** processed PDFs
- **File listing** with pattern filtering
- **Multi-provider support**
- **Unified API** across providers
- **Graceful degradation** if providers unavailable

#### Usage Example:

```python
from bates_labeler import CloudStorageManager, BatesNumberer

# Initialize manager
manager = CloudStorageManager()

# Add Google Drive provider
manager.add_provider(
    name='my_drive',
    provider_type='google_drive',
    credentials={
        'credentials_file': '/path/to/credentials.json'
    }
)

# Add Dropbox provider
manager.add_provider(
    name='my_dropbox',
    provider_type='dropbox',
    credentials={
        'access_token': 'YOUR_DROPBOX_TOKEN'
    }
)

# Get provider
drive = manager.get_provider('my_drive')

# Download file
drive.download_file(
    remote_path='file_id_in_drive',
    local_path='/tmp/input.pdf'
)

# Process locally
numberer = BatesNumberer(prefix="CLOUD-")
numberer.process_pdf('/tmp/input.pdf', '/tmp/output.pdf')

# Upload result
file_id = drive.upload_file(
    local_path='/tmp/output.pdf',
    remote_path='processed/output.pdf'
)

# List files
files = drive.list_files(folder_path='', pattern='.pdf')
for file in files:
    print(f"{file['name']} - {file['size']} bytes")
```

#### Google Drive Setup:

1. Create project in Google Cloud Console
2. Enable Google Drive API
3. Create service account
4. Download credentials JSON
5. Share Drive folders with service account email

#### Dropbox Setup:

1. Create Dropbox App
2. Generate access token
3. Use token in credentials

---

### 5. PDF Form Field Preservation

**Module:** `bates_labeler.form_handler`

Preserve interactive PDF forms during Bates numbering.

#### Key Features:
- **Detect form fields** (text, checkboxes, radio buttons, signatures)
- **Preserve field functionality** after processing
- **Support AcroForms** and XFA forms
- **Maintain JavaScript actions**
- **Form validation** before/after processing
- **Form summary** generation

#### Usage Example:

```python
from bates_labeler import PDFFormHandler, BatesNumberer

# Initialize handler
handler = PDFFormHandler()

# Check if PDF has forms
input_pdf = "application_form.pdf"
has_forms = handler.has_form_fields(input_pdf)

if has_forms:
    # Get form summary
    summary = handler.get_form_summary(input_pdf)
    print(f"Found {summary['total_fields']} form fields")
    print(f"Field types: {summary['field_types']}")

    # Extract field information
    fields = handler.extract_form_fields(input_pdf)
    for field in fields:
        print(f"- {field.field_name}: {field.field_type}")

    # Process PDF with Bates numbers
    numberer = BatesNumberer(prefix="FORM-")
    output_pdf = "application_form_numbered.pdf"

    # Standard processing
    with open(input_pdf, 'rb') as f:
        pdf_data = f.read()

    # ... process PDF data with Bates numbers ...

    # Preserve form fields in output
    handler.preserve_form_fields(
        input_path=input_pdf,
        output_path=output_pdf,
        processed_pdf_data=processed_data
    )

    # Validate preservation
    validation = handler.validate_form_fields(input_pdf, output_pdf)
    if validation['valid']:
        print("✓ All form fields preserved successfully")
    else:
        print(f"⚠ Missing fields: {validation['missing_fields']}")
```

---

## Installation

### Basic Installation (Core Features)

```bash
pip install bates-labeler
```

### With Advanced Features

```bash
# Configuration manager (Pydantic)
pip install "bates-labeler[advanced]"

# Batch scheduler
pip install "bates-labeler[advanced]"

# Cloud storage
pip install "bates-labeler[cloud-storage]"

# All new features
pip install "bates-labeler[all]"
```

### Poetry Installation

```bash
# Basic
poetry install

# With optional features
poetry install -E advanced
poetry install -E cloud-storage
poetry install -E all
```

---

## Migration Guide

### From v1.x to v2.2

All new features are **backward compatible** and **optional**. Existing code continues to work without changes.

#### Check Feature Availability:

```python
from bates_labeler import (
    CONFIG_MANAGER_AVAILABLE,
    TEMPLATE_MANAGER_AVAILABLE,
    SCHEDULER_AVAILABLE,
    CLOUD_STORAGE_AVAILABLE,
    FORM_HANDLER_AVAILABLE
)

if CONFIG_MANAGER_AVAILABLE:
    from bates_labeler import ConfigManager
    manager = ConfigManager()
else:
    print("Install with: pip install 'bates-labeler[advanced]'")
```

#### Graceful Degradation:

All new features gracefully degrade if optional dependencies are missing. The core Bates numbering functionality always works.

---

## Configuration Files

### Directory Structure:

```
~/.bates-labeler/
├── configs/
│   ├── default.json
│   ├── legal_discovery.json
│   └── confidential.json
└── templates/
    ├── Legal Discovery.json
    ├── Confidential Documents.json
    └── Exhibit Marking.json
```

### Example Configuration File:

```json
{
  "prefix": "CASE2025-",
  "suffix": "",
  "start_number": 1,
  "padding": 6,
  "position": "bottom-right",
  "font_name": "Helvetica",
  "font_size": 10,
  "font_color": [0, 0, 0],
  "opacity": 1.0,
  "enable_watermark": false,
  "enable_qr": false,
  "enable_ocr": false,
  "_metadata": {
    "name": "default",
    "created": "2025-01-10T12:00:00",
    "version": "1.1.1"
  }
}
```

---

## Best Practices

### 1. Configuration Management

- **Use templates** for recurring workflows
- **Version control** your configuration files
- **Share templates** with your team via export/import
- **Use inheritance** to avoid duplication

### 2. Batch Scheduling

- **Limit concurrent jobs** to avoid resource exhaustion
- **Use watch folders** for automated workflows
- **Schedule resource-intensive jobs** during off-hours
- **Monitor job status** regularly

### 3. Cloud Storage

- **Use service accounts** for Google Drive (not user credentials)
- **Implement retry logic** for network failures
- **Clean up temporary files** after processing
- **Use appropriate permissions** for shared folders

### 4. Form Preservation

- **Always validate** form preservation after processing
- **Test with sample forms** before production use
- **Document which form types** are supported
- **Provide fallback** for complex forms

---

## Troubleshooting

### Configuration Manager Issues

**Issue:** `ImportError: No module named 'pydantic'`

**Solution:**
```bash
pip install pydantic>=2.0.0
# Or
pip install "bates-labeler[advanced]"
```

### Scheduler Issues

**Issue:** `ImportError: No module named 'apscheduler'`

**Solution:**
```bash
pip install APScheduler>=3.10.0
# Or
pip install "bates-labeler[advanced]"
```

### Cloud Storage Issues

**Issue:** Google Drive authentication fails

**Solution:**
- Verify credentials.json is valid
- Check service account has Drive API enabled
- Ensure folders are shared with service account email

**Issue:** Dropbox access token invalid

**Solution:**
- Regenerate token in Dropbox App Console
- Check token hasn't expired
- Verify app has required permissions

### Form Handler Issues

**Issue:** Forms not preserved after processing

**Solution:**
- Check PDF uses AcroForms (not XFA)
- Validate input PDF has form fields
- Test with simpler forms first
- Check pypdf version (requires >=4.0.0)

---

## Performance Considerations

### Configuration Manager
- **Memory:** ~1-5 MB per configuration
- **Disk:** ~10-50 KB per saved configuration

### Template Manager
- **Memory:** ~5-10 MB for full library
- **Disk:** ~20-100 KB per template

### Batch Scheduler
- **Memory:** ~50-100 MB base + job memory
- **CPU:** Scales with concurrent jobs
- **Recommendation:** max_concurrent_jobs = CPU cores

### Cloud Storage
- **Memory:** ~100-200 MB during transfers
- **Network:** Bandwidth dependent
- **Recommendation:** Process locally, upload results

### Form Handler
- **Memory:** +20-50 MB per form PDF
- **CPU:** Minimal overhead
- **Recommendation:** Validate forms before batch processing

---

## Roadmap

### Planned for v2.3.0:
- **Database backend** for configuration persistence
- **REST API** for remote processing
- **Webhook support** for integrations
- **Advanced template sharing** (marketplace)
- **Multi-user collaboration** features

### Planned for v3.0.0:
- **Plugin architecture** for custom extensions
- **Machine learning** for intelligent defaults
- **Distributed processing** (Celery integration)
- **Advanced reporting** and analytics

---

## Support & Contributing

**Documentation:** https://github.com/thepingdoctor/Bates-Labeler
**Issues:** https://github.com/thepingdoctor/Bates-Labeler/issues
**Discussions:** https://github.com/thepingdoctor/Bates-Labeler/discussions

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

---

## License

MIT License - See LICENSE file for details.

© 2025 Bates-Labeler Contributors
