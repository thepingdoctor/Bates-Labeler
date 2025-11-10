# Changelog

All notable changes to the Bates-Labeler project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-01-10

### Added - 5 Major Enterprise Features

#### 1. Enhanced Configuration Manager (`bates_labeler/config_manager.py`)
- Type-safe configuration management with Pydantic validation
- Configuration inheritance for template hierarchies
- Environment variable support (BATES_* prefix)
- JSON import/export for team collaboration
- Default configuration management
- Configuration namespacing
- Integrated into Streamlit UI

#### 2. Template Management System (`bates_labeler/template_manager.py`)
- Complete template library with categorization and tagging
- Pre-built templates: Legal Discovery, Confidential Documents, Exhibits
- Template search and filtering capabilities
- Template duplication for creating variations
- Import/export for team sharing
- Full Streamlit UI integration with save/load/browse tabs

#### 3. Batch Job Scheduler (`bates_labeler/scheduler.py`)
- One-time and recurring job scheduling (cron-like)
- Watch folder automation for automatic file processing
- Job queue management with concurrent job limits
- Job status tracking and monitoring
- Error handling with automatic retries
- APScheduler integration (optional dependency)

#### 4. Cloud Storage Integration (`bates_labeler/cloud_storage.py`)
- Google Drive integration with service account support
- Dropbox integration with OAuth tokens
- AWS S3 support via boto3
- Unified API across all providers
- Upload/download with progress tracking
- File listing and searching
- Full Streamlit UI for cloud operations

#### 5. PDF Form Field Preservation (`bates_labeler/form_handler.py`)
- Automatic detection of interactive PDF forms
- Preservation of form functionality during Bates numbering
- Support for AcroForms and XFA forms
- Form field validation before/after processing
- Form summary generation
- Automatic form detection display in Streamlit UI

### Changed
- **Version bumped from 1.1.1 to 2.2.0** (major feature release)
- **Streamlit UI** - Added dedicated sections for all new features
- **Package exports** - Added 5 availability flags for graceful degradation
- **pyproject.toml** - Added 8 new optional dependencies with extras groups
- **Documentation** - Added comprehensive FEATURES_V2_2.md guide
- **README.md** - Updated with v2.2.0 features section and installation guides

### Documentation
- Added `docs/FEATURES_V2_2.md` (700+ lines) - Complete feature guide with examples
- Added `docs/QA_REPORT.md` - Quality assurance report
- Updated `README.md` - Added v2.2.0 features section with code examples
- Added `CHANGELOG.md` - This file for version tracking

### Testing
- Added `tests/test_config_manager.py` (350+ lines, 25+ tests)
- Added `tests/test_template_manager.py` (400+ lines, 30+ tests)
- Added `tests/test_scheduler.py` (450+ lines, 25+ tests)
- Added `tests/test_cloud_storage.py` (350+ lines, 20+ tests)
- Added `tests/test_form_handler.py` (400+ lines, 25+ tests)
- **Total: 125+ new test cases, ~2,000 lines of test code**

### Infrastructure
- Added `bates_labeler/streamlit_ui_extensions.py` - UI components for new features
- New Poetry extras:
  - `advanced` - Configuration Manager + Batch Scheduler
  - `cloud-storage` - All cloud provider integrations
  - `ai-analysis` - AI document analysis
  - `all` - Complete feature set
- All new features use graceful degradation pattern

### Fixed
- Updated version test assertion in `tests/test_bates_numberer.py` (line 104)

### Technical Details
- **Lines of Code Added:** ~5,200 lines (2,000 feature code, 2,000 tests, 1,000+ docs)
- **Files Created:** 12 new files
- **Files Modified:** 5 existing files
- **Backward Compatibility:** 100% - All features are optional
- **Dependencies:** All optional, core functionality unchanged

---

## [1.1.1] - 2025-01-09

### Fixed
- Configuration import error handling
- File extension validation for config files
- Clearer error messages with examples

### Documentation
- Added example configuration file
- Updated import/export documentation

---

## [1.1.0] - 2024-12-15

### Added
- Streamlit web UI with drag-and-drop interface
- Configuration presets (Legal Discovery, Confidential, Exhibits)
- Real-time preview of Bates format
- Session persistence (save/load configurations)
- Undo/Redo functionality
- Keyboard shortcuts (Ctrl+Z, Ctrl+Y, Ctrl+S, etc.)
- PDF preview panel
- Processing history
- ZIP download for batch results

### Changed
- Improved UI layout (420px sidebar width)
- Enhanced progress tracking with per-file status
- Better error handling and user feedback

---

## [1.0.0] - 2024-11-01

### Added
- Initial release
- Core Bates numbering functionality
- Command-line interface
- Support for password-protected PDFs
- Batch processing capabilities
- Custom fonts, logos, QR codes
- Watermarks and separator pages
- OCR support (local and cloud)
- Pre-flight PDF validation
- Multi-format export (JSON, CSV, Excel, TIFF)

---

## Release Notes

### v2.2.0 Highlights
This is a **major feature release** focused on enterprise workflows, team collaboration, and automation:

- **Enterprise-ready:** Configuration management and template libraries for teams
- **Automation:** Batch scheduling and watch folder processing
- **Cloud integration:** Direct upload/download from Google Drive, Dropbox, S3
- **Form preservation:** Maintain interactive PDF forms during processing
- **Fully tested:** 125+ new test cases ensuring production quality
- **Well documented:** 1,000+ lines of comprehensive documentation

### Upgrade Path
All features are **backward compatible**. Existing v1.x code works without changes. New features are opt-in via optional dependencies:

```bash
# Upgrade to v2.2.0
pip install --upgrade bates-labeler

# Install new features
pip install "bates-labeler[all]"
```

### Support
- **Documentation:** [https://github.com/thepingdoctor/Bates-Labeler](https://github.com/thepingdoctor/Bates-Labeler)
- **Issues:** [https://github.com/thepingdoctor/Bates-Labeler/issues](https://github.com/thepingdoctor/Bates-Labeler/issues)
- **v2.2.0 Features Guide:** [docs/FEATURES_V2_2.md](docs/FEATURES_V2_2.md)
