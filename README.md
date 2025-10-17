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
- ✨ **Drag & drop file upload** - Upload single or multiple PDFs
- 🎯 **Configuration presets** - Pre-configured for Legal Discovery, Confidential, Exhibits
- 👁️ **Real-time preview** - See your Bates format before processing
- 📊 **Visual progress tracking** - Watch your files being processed
- ⚡ **Instant downloads** - Get your Bates-numbered PDFs immediately
- 🎨 **Improved UI** - Wider sidebar (420px), collapsible sections, professional design
- 📱 **Responsive layout** - Works on different screen sizes

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
- ✅ Batch processing of multiple PDFs
- ✅ Progress tracking for large documents

### Customization Options
- **Position**: Place Bates numbers at various positions on the page
- **Font**: Customize font family, size, color, and style (bold/italic)
- **Date/Time**: Include optional timestamp with Bates numbers
- **Padding**: Configure number padding (e.g., 4 digits: "0001")
- **Formatting**: Full control over prefix/suffix format

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
# - Core dependencies: PyPDF2, reportlab, tqdm
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
- **PyPDF2** ^3.0.1 - PDF manipulation
- **reportlab** ^4.0.7 - PDF generation  
- **tqdm** ^4.66.1 - Progress bars
- **streamlit** ^1.28.0 - Web interface (optional for CLI-only use)

📖 **[Detailed Installation Guide](PACKAGING.md)** - Poetry setup, publishing to PyPI, and more

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

## 📚 Documentation

- **[WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)** - Complete guide to the Streamlit web interface
  - Installation methods (Poetry, pip, Docker)
  - Step-by-step usage instructions
  - Configuration presets and options
  - Deployment options (local, cloud, Docker, self-hosted)
  - Security considerations and troubleshooting

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

Planned for future versions:
- [ ] Support for custom TrueType/OpenType fonts
- [ ] QR code generation alongside Bates numbers
- [ ] CSV/Excel logging of applied Bates numbers
- [ ] Integration with document management systems
- [ ] OCR support for scanned documents
- [ ] Watermark capabilities
- [ ] Multi-threaded processing for large batches
- [ ] Cloud storage integration (Google Drive, Dropbox, OneDrive)
- [ ] Batch job scheduling and automation
- [ ] PDF form field preservation
