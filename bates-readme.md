# PDF Bates Numbering Script

A comprehensive Python tool for adding Bates numbers to PDF documents, commonly used in legal document management and discovery processes.

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

## Installation

### Requirements
- Python 3.6 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install PyPDF2 reportlab tqdm
```

Or create a `requirements.txt` file:

```txt
PyPDF2==3.0.1
reportlab==4.0.7
tqdm==4.66.1
```

Then install with:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Add Bates numbers to a single PDF:

```bash
python bates_stamp.py --input "evidence.pdf" --bates-prefix "CASE123-"
```

This will create `evidence_bates.pdf` with Bates numbers like "CASE123-0001", "CASE123-0002", etc.

### Advanced Examples

#### Custom Position and Formatting

```bash
python bates_stamp.py \
  --input "contract.pdf" \
  --bates-prefix "SMITH-v-JONES-" \
  --bates-suffix "-CONFIDENTIAL" \
  --start-number 100 \
  --position top-right \
  --font-size 12 \
  --font-color red \
  --bold
```

#### Include Date Stamp

```bash
python bates_stamp.py \
  --input "deposition.pdf" \
  --bates-prefix "DEP-" \
  --include-date \
  --date-format "%Y/%m/%d %H:%M" \
  --position bottom-center
```

#### Batch Processing

Process multiple PDFs with continuous numbering:

```bash
python bates_stamp.py \
  --batch doc1.pdf doc2.pdf doc3.pdf \
  --bates-prefix "DISCOVERY-" \
  --output-dir "./bates_stamped/"
```

#### Password-Protected PDFs

```bash
python bates_stamp.py \
  --input "secured.pdf" \
  --bates-prefix "SECURE-" \
  --password "mypassword"
```

Or omit the password flag to be prompted securely:

```bash
python bates_stamp.py --input "secured.pdf" --bates-prefix "SECURE-"
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

## Python API Usage

You can also use the script as a Python module:

```python
from bates_stamp import BatesNumberer

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

# Process multiple PDFs
numberer.process_batch(
    ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    output_dir="./stamped/"
)
```

## Common Use Cases

### Legal Discovery
```bash
python bates_stamp.py \
  --batch *.pdf \
  --bates-prefix "PLAINTIFF-PROD-" \
  --start-number 1 \
  --padding 6 \
  --position bottom-right \
  --font-size 8
```

### Confidential Documents
```bash
python bates_stamp.py \
  --input "trade_secrets.pdf" \
  --bates-prefix "CONFIDENTIAL-" \
  --bates-suffix "-AEO" \
  --font-color red \
  --bold \
  --position top-center
```

### Exhibit Marking
```bash
python bates_stamp.py \
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
python bates_stamp.py \
  --batch archive/*.pdf \
  --bates-prefix "ARCH-" \
  --include-date \
  --date-format "%Y%m%d" \
  --position bottom-left \
  --output-dir "./archived_bates/"
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed:
   ```bash
   pip install PyPDF2 reportlab tqdm
   ```

2. **Font Not Displaying Correctly**: The script uses standard PDF fonts. For custom fonts, you'll need to register them with reportlab.

3. **Large Files Running Slowly**: The script shows a progress bar. For very large files (1000+ pages), processing may take several minutes.

4. **Password Protected PDFs**: Use the `--password` flag or wait for the secure prompt.

5. **Overlapping with Existing Content**: Try different positions or adjust font size.

### Error Messages

- `Error: Input file not found`: Check the file path
- `Error: Invalid password`: Verify the PDF password
- `Warning: Invalid color`: Color name not recognized, defaulting to black

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

This script is provided as-is for legal document management purposes. Ensure compliance with your jurisdiction's requirements for legal document numbering.

## Future Enhancements

Planned features for future versions:
- [ ] Support for custom TrueType/OpenType fonts
- [ ] QR code generation alongside Bates numbers
- [ ] CSV/Excel logging of applied Bates numbers
- [ ] GUI interface for non-technical users
- [ ] Integration with document management systems
- [ ] OCR support for scanned documents
- [ ] Watermark capabilities
- [ ] Multi-threaded processing for large batches