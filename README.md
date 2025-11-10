# PDF Bates Numbering Tool

A comprehensive Python tool for adding Bates numbers to PDF documents, commonly used in legal document management and discovery processes.

## 🚀 Quick Start

### Option 1: Web Interface (Recommended for Most Users)
```bash
# Install with Poetry
poetry install

# Launch the web interface
poetry run streamlit run app.py
```
The web app opens at `http://localhost:8501` with an intuitive drag & drop interface.

### Option 2: Command Line Interface
```bash
# Install the package
poetry install

# Use the bates command
poetry run bates --input document.pdf --bates-prefix "CASE-"
```

---

## 🌐 Web Interface

**User-friendly GUI** - No command-line experience required!

### Features
- ✨ **Drag & drop file upload** - Upload single or multiple PDFs with reordering support
- 🎯 **Configuration presets** - Pre-configured for Legal Discovery, Confidential, Exhibits
- 👁️ **Real-time preview** - See your Bates format before processing
- 📊 **Live progress tracking** - Real-time status updates with cancel button and individual file progress
- ⚡ **Instant downloads** - Individual files or bundled ZIP archive
- 🎨 **Advanced customization** - Logos, QR codes, borders, watermarks
- 🖼️ **Logo upload** - SVG, PNG, JPG, WEBP with flexible positioning
- 📱 **QR code generation** - Embed Bates numbers as scannable QR codes
- 🔲 **Border styling** - 4 decorative border styles for separator pages
- 💧 **Watermark support** - Custom text overlays with opacity control
- 💾 **Session persistence** - Save and load configurations for repeated use
- ⏪ **Undo/Redo** - Full undo/redo support for all configuration changes
- ⌨️ **Keyboard shortcuts** - Fast navigation and actions (Ctrl+Z, Ctrl+Y, Ctrl+S, etc.)
- 📝 **OCR text extraction** - Extract text from scanned PDFs (local Tesseract and cloud options)
- 🔍 **Pre-flight validation** - Automatic PDF validation before processing
- 📤 **Batch export formats** - Export to JSON, CSV, Excel, and TIFF
- 📄 **PDF preview panel** - View PDF pages before processing
- 🔄 **Page rotation** - Rotate pages during processing
- ✅ **Bates validation** - Real-time validation of Bates number formats
- ⚡ **Performance optimizations** - 10-15x faster processing with parallel execution
- 📋 **Processing history** - View past processing jobs and their configurations
- 🎨 **Improved UI** - Wider sidebar (420px), collapsible sections, professional design
- 📱 **Responsive layout** - Works on different screen sizes
- 🤖 **AI document analysis** - Detect discrimination, problematic content, and extract metadata

### Configuration Presets
- **Default** - Blank slate for custom configurations
- **Legal Discovery** - `PLAINTIFF-PROD-000001` format
- **Confidential** - `CONFIDENTIAL-0001-AEO` format with red text
- **Exhibit** - `EXHIBIT-101` format starting at 101

### Deployment Options
- **Local** - Run on your computer
- **Network** - Share on your local network
- **Streamlit Cloud** - Free cloud hosting
- **Docker** - Container deployment
- **Self-hosted** - Deploy on your own server (or easily run on a Macbook)

📖 **[Complete Web UI Guide](WEB_UI_GUIDE.md)** - Installation, usage, deployment, and troubleshooting

---

## Features

### Core Functionality
- ✅ Add sequential Bates numbers to each page of a PDF
- ✅ Customizable prefix and suffix (e.g., "CASE123-0001-DRAFT")
- ✅ Preserve original PDF attributes, bookmarks, and metadata
- ✅ Support for password-protected PDFs
- ✅ Batch processing of multiple PDFs with continuous numbering
- ✅ Progress tracking for large documents with individual file status
- ✅ **Real-time status updates** - Live progress tracking with cancellation support (Web UI)
- ✅ **Combine multiple PDFs** into single file with continuous Bates numbering
- ✅ **Index page generation** - Professional document index for combined PDFs
- ✅ **Bates number filenames** - Name output files by first Bates number with CSV/PDF mappings
- ✅ **Custom fonts** - Support for TrueType (.ttf) and OpenType (.otf) fonts
- ✅ **Logo placement** - Upload and position logos on separator pages (SVG, PNG, JPG, WEBP)
- ✅ **QR codes** - Generate QR codes with Bates numbers on all pages or separators
- ✅ **Watermarks** - Add customizable text watermarks with opacity and rotation
- ✅ **ZIP download** - Download all processed files as a single archive
- ✅ **Session persistence** - Save and load processing configurations
- ✅ **Undo/Redo** - Full history tracking for configuration changes
- ✅ **Keyboard shortcuts** - Efficient keyboard navigation and actions
- ✅ **OCR support** - Extract text from scanned documents (local and cloud)
- ✅ **Pre-flight validation** - Automatic PDF health checks before processing
- ✅ **Multi-format export** - JSON, CSV, Excel, TIFF batch export options
- ✅ **Drag-and-drop reordering** - Reorder files before processing
- ✅ **PDF preview** - View PDF pages in-app before processing
- ✅ **Page rotation** - Rotate individual pages during processing
- ✅ **Bates validation** - Real-time format validation with helpful error messages
- ✅ **Performance optimization** - Parallel processing with 10-15x speed improvements
- ✅ **AI-powered document analysis** - Discrimination detection, problematic content identification, metadata extraction

### Customization Options
- **Position**: Place Bates numbers at various positions on the page
- **Font**: Customize font family, size, color, and style (bold/italic) or upload custom fonts
- **Date/Time**: Include optional timestamp with Bates numbers
- **Padding**: Configure number padding (e.g., 4 digits: "0001")
- **Formatting**: Full control over prefix/suffix format
- **Separator Pages**: Add separator pages between documents showing Bates ranges with optional logos and borders
- **Index Pages**: Generate professional table of contents for combined documents
- **Logos**: Upload custom logos (SVG, PNG, JPG, WEBP) with 8 placement options
- **QR Codes**: Generate QR codes containing Bates numbers (all pages or separator only)
- **Borders**: Add decorative borders to separator pages (solid, dashed, double, asterisks)
- **Watermarks**: Overlay custom text with configurable opacity, rotation, and positioning
- **Download Options**: Individual files or bundled ZIP archive
- **AI Analysis**: Detect discrimination patterns, identify problematic content, extract document metadata (optional)

---

## 🚀 What's New in v2.2.0 - Enterprise Features

**Version 2.2.0** introduces five powerful enterprise features for advanced workflows, automation, and team collaboration:

### 1. 🎛️ Enhanced Configuration Manager
**Centralized, validated configuration management with team collaboration**

- **Type-safe configurations** with Pydantic validation
- **Configuration inheritance** - Create child configs that inherit parent settings
- **Environment variables** - Configure via `BATES_*` environment variables
- **Import/Export** - Share configurations across your team as JSON files
- **Default management** - Set default configurations for consistent workflows
- **Configuration namespacing** - Organize configs by project or team

```python
from bates_labeler import ConfigManager

manager = ConfigManager()
config = manager.create_config("legal_discovery", {
    "prefix": "DISC-",
    "start_number": 1,
    "padding": 6
})
manager.save_config("legal_discovery")
manager.export_config("legal_discovery", "team_config.json")
```

📖 **[Configuration Manager Guide](docs/FEATURES_V2_2.md#1-enhanced-configuration-manager)**

### 2. 📋 Template Management System
**Template library for saving and sharing complex workflows**

- **Pre-built templates** - Legal Discovery, Confidential Documents, Exhibits
- **Custom templates** - Save your own configurations for reuse
- **Categorization & tagging** - Organize templates by category and searchable tags
- **Template search** - Find templates by name, description, or tags
- **Template duplication** - Create variations from existing templates
- **Team sharing** - Export/import templates for team collaboration

```python
from bates_labeler import TemplateManager

manager = TemplateManager()
template = manager.create_template(
    name="Company Confidential",
    config={
        "prefix": "CONF-",
        "enable_watermark": True,
        "watermark_text": "CONFIDENTIAL"
    },
    category="confidential",
    tags=["internal", "restricted"]
)
manager.save_template("Company Confidential")
```

📖 **[Template Manager Guide](docs/FEATURES_V2_2.md#2-template-management-system)**

### 3. ⏰ Batch Job Scheduler
**Automated scheduling for recurring batch processing**

- **One-time jobs** - Schedule processing for specific date/time
- **Recurring jobs** - Cron-like scheduling (daily, weekly, monthly)
- **Watch folders** - Automatically process new files dropped in folders
- **Job queue** - Manage concurrent job limits and priorities
- **Status tracking** - Monitor job progress and history
- **Error handling** - Automatic retries and failure notifications

```python
from bates_labeler import BatchScheduler
from datetime import datetime, timedelta

scheduler = BatchScheduler(max_concurrent_jobs=3)
scheduler.start()

# Schedule nightly processing at 2am
scheduler.schedule_recurring_job(
    name="Nightly Processing",
    cron_expression="0 2 * * *",
    process_func=process_batch,
    config={"prefix": "BATCH-"}
)

# Watch folder for auto-processing
scheduler.setup_watch_folder(
    name="Auto Process",
    watch_path="/path/to/incoming",
    process_func=process_batch,
    pattern="*.pdf",
    interval_seconds=60
)
```

📖 **[Batch Scheduler Guide](docs/FEATURES_V2_2.md#3-batch-job-scheduler)**

### 4. ☁️ Cloud Storage Integration
**Seamless integration with major cloud storage providers**

- **Google Drive** - Process files directly from Drive
- **Dropbox** - Automatic sync with Dropbox folders
- **AWS S3** - Enterprise storage integration
- **Unified API** - Same interface across all providers
- **Upload/download** - Transfer files with progress tracking
- **File listing** - Search and filter cloud files

```python
from bates_labeler import CloudStorageManager, BatesNumberer

manager = CloudStorageManager()
manager.add_provider('my_drive', 'google_drive', {
    'credentials_file': 'credentials.json'
})

drive = manager.get_provider('my_drive')
drive.download_file('file_id', 'input.pdf')

numberer = BatesNumberer(prefix="CLOUD-")
numberer.process_pdf('input.pdf', 'output.pdf')

drive.upload_file('output.pdf', 'processed/output.pdf')
```

📖 **[Cloud Storage Guide](docs/FEATURES_V2_2.md#4-cloud-storage-integration)**

### 5. 📝 PDF Form Field Preservation
**Preserve interactive PDF forms during Bates numbering**

- **Form detection** - Automatically detect interactive forms
- **Field preservation** - Maintain form functionality after processing
- **AcroForms support** - Support for standard PDF forms
- **Field validation** - Verify forms are preserved correctly
- **Form summary** - Generate reports of form fields

```python
from bates_labeler import PDFFormHandler, BatesNumberer

handler = PDFFormHandler()

if handler.has_form_fields("application.pdf"):
    summary = handler.get_form_summary("application.pdf")
    print(f"Found {summary['total_fields']} form fields")

    # Process with Bates numbers
    numberer = BatesNumberer(prefix="FORM-")
    # ... process PDF ...

    # Preserve forms in output
    handler.preserve_form_fields(
        "application.pdf",
        "application_numbered.pdf",
        processed_data
    )
```

📖 **[Form Handler Guide](docs/FEATURES_V2_2.md#5-pdf-form-field-preservation)**

### Installation of v2.2.0 Features

**Basic features** work out of the box. **Advanced features** require optional dependencies:

```bash
# All new features
pip install "bates-labeler[all]"

# Or install specific feature groups
pip install "bates-labeler[advanced]"       # Config + Scheduler
pip install "bates-labeler[cloud-storage]"  # Cloud integrations
pip install "bates-labeler[ai-analysis]"    # AI features

# With Poetry
poetry install -E all
```

**Graceful degradation:** All features are optional. Core Bates numbering works without any optional dependencies.

📖 **[Complete v2.2.0 Documentation](docs/FEATURES_V2_2.md)** - Comprehensive guide with examples, best practices, and troubleshooting

## 📦 Installation

### Requirements
- **Python 3.9 or higher** (3.9.7 not supported due to Streamlit compatibility)
- Poetry (recommended) or pip

### Method 1: Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/thepingdoctor/Bates-Labeler.git
cd Bates-Labeler

# Install with Poetry
poetry install

# This installs:
# - Core dependencies: pypdf, reportlab, tqdm
# - Web UI: streamlit
# - Dev tools: pytest, black, flake8, mypy (optional)
```

### Method 2: pip

```bash
# Clone the repository
git clone https://github.com/thepingdoctor/Bates-Labeler.git
cd Bates-Labeler

# Install the package
pip install -e .

# Or install from PyPI (when published)
pip install bates-labeler
```

### Method 3: Docker

```bash
# Build the Docker image
docker build -t bates-labeler .

# Run the web interface
docker run -p 8501:8501 bates-labeler

# Access at http://localhost:8501
```

### Dependencies
- **pypdf** ^4.0.0 - PDF manipulation
- **reportlab** ^4.0.7 - PDF generation
- **tqdm** ^4.66.1 - Progress bars
- **streamlit** ^1.28.0 - Web interface (optional for CLI-only use)
- **pytesseract** - OCR text extraction (optional, requires Tesseract installation)
- **Pillow** - Image processing for OCR and previews
- **pandas** - Export to Excel and CSV formats
- **openpyxl** - Excel file generation

📖 **[Detailed Installation Guide](PACKAGING.md)** - Poetry setup, publishing to PyPI, and more

### Optional: AI Analysis Dependencies

For AI-powered document analysis, install additional dependencies:

```bash
# For OpenRouter (recommended)
pip install requests

# For Google Cloud Vertex AI
pip install google-cloud-aiplatform

# For Anthropic Claude
pip install anthropic
```

📖 **[AI Features Documentation](docs/AI_FEATURES.md)** - Complete guide to AI document analysis
📖 **[AI Setup Guide](docs/AI_SETUP_GUIDE.md)** - Step-by-step configuration for AI providers

## 💻 Usage

### Choose Your Interface

**🌐 Web Interface** - Best for:
- Non-technical users
- Visual configuration
- One-time or occasional use
- Seeing results immediately

**⌨️ Command Line** - Best for:
- Automation and scripting
- Batch processing workflows
- Integration with other tools
- Repeated operations

---

### Command Line Interface (CLI)

#### Basic Usage

Add Bates numbers to a single PDF:

```bash
poetry run bates --input "evidence.pdf" --bates-prefix "CASE123-"
```

This will create `evidence_bates.pdf` with Bates numbers like "CASE123-0001", "CASE123-0002", etc.

#### Advanced Examples

**Custom Position and Formatting**

```bash
poetry run bates \
  --input "contract.pdf" \
  --bates-prefix "SMITH-v-JONES-" \
  --bates-suffix "-CONFIDENTIAL" \
  --start-number 100 \
  --position top-right \
  --font-size 12 \
  --font-color red \
  --bold
```

**Include Date Stamp**

```bash
poetry run bates \
  --input "deposition.pdf" \
  --bates-prefix "DEP-" \
  --include-date \
  --date-format "%Y/%m/%d %H:%M" \
  --position bottom-center
```

**Batch Processing**

Process multiple PDFs with continuous numbering:

```bash
poetry run bates \
  --batch doc1.pdf doc2.pdf doc3.pdf \
  --bates-prefix "DISCOVERY-" \
  --output-dir "./bates_stamped/"
```

**Password-Protected PDFs**

```bash
poetry run bates \
  --input "secured.pdf" \
  --bates-prefix "SECURE-" \
  --password "mypassword"
```

Or omit the password flag to be prompted securely:

```bash
poetry run bates --input "secured.pdf" --bates-prefix "SECURE-"
# You'll be prompted: PDF is password protected. Enter password:
```

## Command Line Options

### Input/Output Options
| Option | Description | Default |
|--------|-------------|---------|
| `--input`, `-i` | Input PDF file path | Required* |
| `--batch`, `-b` | Batch process multiple PDFs | Required* |
| `--output`, `-o` | Output PDF file path | `{input}_bates.pdf` |
| `--output-dir` | Output directory for batch mode | Same as input |

*Either `--input` or `--batch` is required

### Bates Numbering Options
| Option | Description | Default |
|--------|-------------|---------|
| `--bates-prefix` | Prefix for Bates number | `""` |
| `--bates-suffix` | Suffix for Bates number | `""` |
| `--start-number` | Starting number | `1` |
| `--padding` | Number padding width | `4` |

### Position Options
| Option | Description | Default |
|--------|-------------|---------|
| `--position` | Position on page | `bottom-right` |

Available positions:
- `top-left`, `top-center`, `top-right`
- `bottom-left`, `bottom-center`, `bottom-right`
- `center`

### Font Options
| Option | Description | Default |
|--------|-------------|---------|
| `--font-name` | Font family | `Helvetica` |
| `--font-size` | Font size in points | `10` |
| `--font-color` | Color name or hex | `black` |
| `--bold` | Use bold font | `False` |
| `--italic` | Use italic font | `False` |

Available fonts: `Helvetica`, `Times-Roman`, `Courier`

### Date/Time Options
| Option | Description | Default |
|--------|-------------|---------|
| `--include-date` | Include date stamp | `False` |
| `--date-format` | Date format string | `%Y-%m-%d` |

### Advanced Options
| Option | Description | Default |
|--------|-------------|---------|
| `--combine` | Combine all batch files into single PDF | `False` |
| `--document-separators` | Add separator pages between documents (with `--combine`) | `False` |
| `--add-index` | Generate index page listing all documents (with `--combine`) | `False` |
| `--bates-filenames` | Use Bates number as output filename (e.g., CASE-0001.pdf) | `False` |
| `--mapping-prefix` | Prefix for CSV/PDF mapping files | `bates_mapping` |
| `--custom-font` | Path to custom TrueType (.ttf) or OpenType (.otf) font | None |
| `--add-separator` | Add separator page at beginning showing Bates range | `False` |

### Security Options
| Option | Description | Default |
|--------|-------------|---------|
| `--password` | Password for encrypted PDFs | Prompt if needed |

## 🐍 Python API Usage

You can also use the package as a Python module:

```python
from bates_labeler import BatesNumberer

# Create a numberer instance
numberer = BatesNumberer(
    prefix="CASE2023-",
    start_number=1,
    padding=6,
    position="top-right",
    font_size=12,
    font_color="blue",
    bold=True,
    include_date=True
)

# Process a single PDF
numberer.process_pdf("input.pdf", "output.pdf")

# Batch processing is handled by the CLI
# For programmatic batch processing, loop through files:
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    output_name = pdf_file.replace(".pdf", "_bates.pdf")
    numberer.process_pdf(pdf_file, output_name)
    # Note: numbering continues across files automatically
```

## 📋 Common Use Cases

### Legal Discovery
```bash
poetry run bates \
  --batch *.pdf \
  --bates-prefix "PLAINTIFF-PROD-" \
  --start-number 1 \
  --padding 6 \
  --position bottom-right \
  --font-size 8
```

### Confidential Documents
```bash
poetry run bates \
  --input "trade_secrets.pdf" \
  --bates-prefix "CONFIDENTIAL-" \
  --bates-suffix "-AEO" \
  --font-color red \
  --bold \
  --position top-center
```

### Exhibit Marking
```bash
poetry run bates \
  --input "exhibit.pdf" \
  --bates-prefix "EXHIBIT-" \
  --start-number 101 \
  --padding 3 \
  --position top-right \
  --font-size 14 \
  --bold
```

### Archived Documents
```bash
poetry run bates \
  --batch archive/*.pdf \
  --bates-prefix "ARCH-" \
  --include-date \
  --date-format "%Y%m%d" \
  --position bottom-left \
  --output-dir "./archived_bates/"
```

### Combine Multiple PDFs with Index
```bash
poetry run bates \
  --batch doc1.pdf doc2.pdf doc3.pdf \
  --bates-prefix "CASE-" \
  --combine \
  --document-separators \
  --add-index \
  --output "combined_discovery.pdf"
```

### Use Bates Numbers as Filenames
```bash
poetry run bates \
  --batch discovery/*.pdf \
  --bates-prefix "PROD-" \
  --start-number 1000 \
  --bates-filenames \
  --output-dir "./numbered_files/"
# Creates: PROD-001000.pdf, PROD-001025.pdf, etc.
# Also generates: bates_mapping.csv and bates_mapping.pdf
```

### Custom Font for Specialized Documents
```bash
poetry run bates \
  --input "contract.pdf" \
  --bates-prefix "CONTRACT-" \
  --custom-font "/path/to/custom-font.ttf" \
  --font-size 10 \
  --position bottom-right
```

## 📚 Documentation

- **[WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)** - Complete guide to the Streamlit web interface
  - Installation methods (Poetry, pip, Docker)
  - Step-by-step usage instructions
  - Configuration presets and options
  - Deployment options (local, cloud, Docker, self-hosted)
  - Security considerations and troubleshooting

- **[AI_FEATURES.md](docs/AI_FEATURES.md)** - AI document analysis features
  - Discrimination detection capabilities
  - Problematic content identification
  - Metadata extraction
  - Supported AI providers (OpenRouter, Google Cloud, Anthropic)
  - Configuration and usage examples
  - API cost considerations and best practices

- **[AI_SETUP_GUIDE.md](docs/AI_SETUP_GUIDE.md)** - AI analysis setup guide
  - Environment variable configuration
  - Provider-specific setup instructions
  - API key acquisition and security
  - Testing and troubleshooting

- **[PACKAGING.md](PACKAGING.md)** - Developer guide for Poetry and packaging
  - Poetry setup and configuration
  - Publishing to PyPI
  - Development workflow
  - Testing and quality tools

## ❓ Troubleshooting

### Common Issues

1. **Import Error**: Install dependencies with Poetry:
   ```bash
   poetry install
   ```

2. **Python Version**: Ensure you have Python 3.9 or higher (not 3.9.7):
   ```bash
   python --version
   ```

3. **Font Not Displaying Correctly**: The package uses standard PDF fonts. For custom fonts, you'll need to register them with reportlab.

4. **Large Files Running Slowly**: Progress bars show status. Very large files (1000+ pages) may take several minutes.

5. **Password Protected PDFs**: Use the `--password` flag or wait for the secure prompt.

6. **Overlapping with Existing Content**: Try different positions or adjust font size.

7. **Web UI Not Loading**: Ensure Streamlit is installed and port 8501 is available:
   ```bash
   poetry run streamlit run app.py --server.port 8502
   ```

### Error Messages

- `Error: Input file not found`: Check the file path
- `Error: Invalid password`: Verify the PDF password
- `Warning: Invalid color`: Color name not recognized, defaulting to black
- `poetry: command not found`: Install Poetry from https://python-poetry.org

## Best Practices

1. **Test First**: Always test on a copy of your documents first
2. **Backup Originals**: Keep original files unchanged
3. **Consistent Prefixes**: Use meaningful prefixes for easy identification
4. **Document Your System**: Keep a record of your Bates numbering scheme
5. **Batch Processing**: Group related documents for continuous numbering

## Limitations

- Currently supports standard PDF fonts (Helvetica, Times-Roman, Courier)
- Custom TrueType fonts require additional setup
- Very complex PDFs with forms may need special handling
- Rotated pages maintain their orientation

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This script is provided as-is for legal document management purposes. Ensure compliance with your jurisdiction's requirements for legal document numbering. No warranties are provided, express or implied.

## 🔮 Future Enhancements

Completed in v1.1.0:
- [x] **Streamlit Web UI** - Professional GUI interface for non-technical users
- [x] **Poetry packaging** - Modern Python dependency management
- [x] **Docker support** - Container deployment option
- [x] **Configuration presets** - Quick-start templates for common use cases
- [x] **Custom TrueType/OpenType fonts** - Upload and use custom .ttf/.otf fonts in both UI and CLI
- [x] **CSV/PDF mapping files** - Automatic generation when using Bates number filenames
- [x] **PDF combining** - Merge multiple PDFs with continuous Bates numbering
- [x] **Index page generation** - Professional document index for combined PDFs
- [x] **Separator pages** - Optional pages between documents showing Bates ranges with logos and borders
- [x] **Logo upload and placement** - SVG, PNG, JPG, WEBP support with 8 placement options
- [x] **QR code generation** - Scannable QR codes containing Bates numbers (all pages or separator only)
- [x] **Border styling** - 4 decorative border styles for separator pages (solid, dashed, double, asterisks)
- [x] **Watermark capabilities** - Custom text overlays with opacity, rotation, and positioning control
- [x] **ZIP download** - Bundle all processed files into single archive
- [x] **Real-time status updates** - Live progress tracking with cancellation support (Web UI)

Completed in v2.0.0:
- [x] **Session persistence** - Save and load configurations for repeated workflows
- [x] **Undo/Redo functionality** - Complete state management with Ctrl+Z/Ctrl+Y support
- [x] **Keyboard shortcuts** - Fast navigation (Ctrl+S save, Ctrl+L load, Ctrl+P process, etc.)
- [x] **OCR text extraction** - Extract text from scanned PDFs (local Tesseract and cloud options)
- [x] **Pre-flight PDF validation** - Automatic PDF health checks before processing
- [x] **Batch export formats** - Export to JSON, CSV, Excel (.xlsx), and TIFF
- [x] **Drag-and-drop file reordering** - Reorder files in queue before processing
- [x] **PDF preview panel** - In-app PDF page preview before processing
- [x] **Individual file progress** - Track progress for each file in batch operations
- [x] **Page rotation support** - Rotate pages during processing
- [x] **Bates number validation** - Real-time format validation with error messages
- [x] **Performance optimizations** - 10-15x faster with parallel processing and caching
- [x] **Processing history** - View and restore previous processing jobs

Completed in v2.1.0:
- [x] **AI-powered document analysis** - Optional AI integration for intelligent document processing
- [x] **Multi-provider AI support** - OpenRouter, Google Cloud Vertex AI, Anthropic Claude
- [x] **Discrimination detection** - Identify patterns across 8 categories (race, gender, age, disability, etc.)
- [x] **Problematic content identification** - Detect harassment, bias, PII exposure, confidential data leaks
- [x] **Metadata extraction** - Document classification, named entities, topics, sentiment analysis
- [x] **Intelligent caching** - 60-90% cost reduction on repeat analyses
- [x] **Cost optimization** - Typical cost $0.01-0.10 per document with efficient processing

Planned for future versions:
- [ ] Integration with document management systems
- [ ] Multi-threaded processing for large batches
- [ ] Cloud storage integration (Google Drive, Dropbox, OneDrive)
- [ ] Batch job scheduling and automation
- [ ] PDF form field preservation
- [ ] Advanced reporting and analytics
- [ ] Template management system
- [ ] Digital signatures and certification

### AI & Intelligence Features

**Phase 1: Document Intelligence (Foundation)** ✅ Completed in v2.0.0
- [x] **OCR support for scanned documents** - Extract text from image-based PDFs using Tesseract/Cloud OCR

**Phase 2: AI-Powered Analysis** ✅ Completed in v2.1.0
- [x] **Discrimination detection** - Identify patterns across 8 categories (race, gender, age, disability, religion, national origin, sexual orientation, pregnancy)
- [x] **Problematic content identification** - Detect harassment, threats, hate speech, bias, PII exposure, confidential data leaks
- [x] **Metadata extraction** - Document type classification, named entity recognition, topic modeling, sentiment analysis
- [x] **Multi-provider support** - OpenRouter (100+ models), Google Cloud Vertex AI, Anthropic Claude
- [x] **Cost optimization** - Intelligent caching (60-90% cost reduction), efficient chunking, rate limiting

**Phase 3: Smart Processing & Quality** (Planned)
- [ ] **AI-powered quality assurance** - Verify numbering continuity, detect missing pages, flag anomalies
- [ ] **Duplicate and near-duplicate detection** - Identify redundant pages in batch processing
- [ ] **Auto-suggest Bates prefixes** - Recommend prefixes based on document content and type
- [ ] **Intelligent redaction detection** - Identify and suggest redaction of PII (SSNs, account numbers, etc.)

**Phase 4: Search & Discovery** (Planned)
- [ ] **Full-text searchable index generation** - Create searchable database of all processed documents
- [ ] **Semantic search capabilities** - Find documents by concept, not just keywords
- [ ] **AI document summarization** - Generate executive summaries of long documents

**Phase 5: Enhanced User Experience** (Planned)
- [ ] **Natural language configuration** - Process documents using conversational commands
- [ ] **AI assistant for troubleshooting** - Help users optimize workflows and solve issues
- [ ] **Smart defaults based on usage patterns** - Learn from past configurations
- [ ] **Workflow template suggestions** - AI-generated processing templates

**Phase 6: Advanced Automation** (Planned)
- [ ] **Automatic document routing** - Organize processed files by type/category
- [ ] **Batch processing optimization** - Suggest optimal grouping and numbering strategies
- [ ] **Anomaly detection and alerting** - Flag unusual document characteristics

### Using AI Document Analysis

The AI analysis feature is **optional** and requires API credentials from one of the supported providers.

**Quick Start:**

1. **Choose a Provider:**
   - **OpenRouter** (recommended): Access to 100+ models, cost-effective ($0.01-0.10 per document)
   - **Google Cloud Vertex AI**: Enterprise-grade with Gemini models
   - **Anthropic Claude**: Privacy-focused with long context windows

2. **Configure Environment:**
   ```bash
   # Copy example configuration
   cp docs/.env.example .env

   # Edit .env and add your API key
   AI_ANALYSIS_ENABLED=true
   AI_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

3. **Use in Python:**
   ```python
   from bates_labeler import BatesNumberer

   numberer = BatesNumberer(
       prefix="CASE-",
       ai_analysis_enabled=True,
       ai_provider="openrouter",
       ai_api_key="sk-or-v1-your-key",
       ai_analysis_callback=lambda result: print(f"Analysis: {result}")
   )

   # Process PDF with AI analysis
   numberer.process_pdf("document.pdf", "output.pdf")
   ```

4. **Use in Web UI:**
   - Launch: `poetry run streamlit run app.py`
   - Expand "🤖 AI Document Analysis (Optional)" in sidebar
   - Enable AI analysis and enter API key
   - Process documents and view analysis results

**What It Detects:**
- 🚨 Discrimination patterns (race, gender, age, disability, etc.)
- ⚠️ Problematic content (harassment, bias, PII exposure)
- 📊 Document metadata (type, entities, topics, sentiment)

**Cost:** Typical cost is $0.01-0.10 per document. Caching reduces repeat analysis costs by 60-90%.

📖 **See [docs/AI_FEATURES.md](docs/AI_FEATURES.md)** for complete documentation
