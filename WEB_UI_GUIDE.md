# Bates-Labeler Web UI Guide

The Bates-Labeler now includes a user-friendly web interface built with Streamlit, making it accessible to users without command-line experience.

## Features

### 🎨 User Interface
- **Configuration Sidebar:** All settings in one organized panel (420px wide)
- **Configuration Presets:** Quick-select templates for common use cases
- **Live Preview:** See your Bates number format before processing
- **Drag & Drop:** Easy file upload interface with reordering support
- **Batch Processing:** Handle multiple PDFs at once with individual file progress
- **Progress Tracking:** Visual progress bars during processing with cancel support
- **Instant Download:** Download processed files immediately or as ZIP bundle
- **PDF Preview Panel:** View PDF pages before processing
- **Session Management:** Save and load configurations for repeated workflows
- **Undo/Redo:** Full state management with keyboard shortcuts
- **Keyboard Shortcuts:** Fast navigation and actions (Ctrl+Z, Ctrl+Y, Ctrl+S, etc.)
- **Processing History:** View and restore previous processing jobs
- **OCR Support:** Extract text from scanned documents (local and cloud)
- **Pre-flight Validation:** Automatic PDF health checks before processing
- **Multi-format Export:** Export to JSON, CSV, Excel, and TIFF

### 📋 Configuration Presets

The web UI includes pre-configured templates:

1. **Default** - Blank slate for custom configurations
2. **Legal Discovery** - `PLAINTIFF-PROD-000001` format
3. **Confidential** - `CONFIDENTIAL-0001-AEO` format
4. **Exhibit** - `EXHIBIT-101` format (starting at 101)

## Installation

### Method 1: Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/thepingdoctor/Bates-Labeler.git
cd Bates-Labeler

# Install dependencies with Poetry
poetry install

# Run the web UI
poetry run streamlit run app.py
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/thepingdoctor/Bates-Labeler.git
cd Bates-Labeler

# Install the package
pip install -e .

# Install Streamlit separately if not included
pip install streamlit

# Run the web UI
streamlit run app.py
```

### Method 3: Using Docker

```bash
# Build the Docker image
docker build -t bates-labeler .

# Run the container
docker run -p 8501:8501 bates-labeler

# Access at http://localhost:8501
```

## Usage

### Starting the Web UI

```bash
# With Poetry
poetry run streamlit run app.py

# Or directly (if installed globally)
streamlit run app.py
```

The application will open automatically in your default browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Choose Configuration Preset** (Optional)
   - Select from Default, Legal Discovery, Confidential, or Exhibit
   - Modify any settings as needed
   - Use **Ctrl+S** to save your custom configuration
   - Use **Ctrl+L** to load a previously saved configuration

2. **Configure Basic Settings**
   - **Bates Prefix:** Text before the number (e.g., "CASE123-")
   - **Bates Suffix:** Text after the number (e.g., "-CONF")
   - **Start Number:** First Bates number to use
   - **Padding:** Number of digits (4 = "0001")
   - Real-time validation ensures valid Bates format

3. **Set Position & Appearance**
   - **Position:** Where on the page (9 options available)
   - **Font:** Helvetica, Times-Roman, or Courier (or upload custom font)
   - **Font Size:** 6-24 points
   - **Color:** Black, blue, red, green, or gray
   - **Style:** Bold and/or Italic

4. **Advanced Options**
   - **Include Date Stamp:** Add date/time below Bates number
   - **White Background:** Better visibility on dark documents
   - **Separator Page:** Add cover page showing Bates range with logos/borders
   - **OCR:** Enable text extraction from scanned documents
   - **Export Format:** Choose JSON, CSV, Excel, or TIFF output
   - **Page Rotation:** Rotate pages during processing

5. **Upload PDF Files**
   - Click "Browse files" or drag and drop
   - Upload one or multiple PDFs
   - Maximum file size: 200MB per file
   - **Reorder files** by dragging in the file list
   - **Preview PDFs** using the preview panel
   - **Pre-flight validation** checks PDF health automatically

6. **Preview & Process**
   - Check the preview box for format confirmation
   - Click "Process PDF(s)" button or use **Ctrl+P**
   - Monitor progress with individual file status bars
   - Cancel processing at any time if needed

7. **Download Results**
   - Click download buttons for each processed file
   - Download all files as ZIP bundle
   - View processing history
   - Files are named with "_bates.pdf" suffix
   - Clear processed files when done

8. **Use Undo/Redo** (Optional)
   - **Ctrl+Z**: Undo last configuration change
   - **Ctrl+Y**: Redo configuration change
   - Full state history tracking

## Configuration Options

### Basic Settings

| Setting | Description | Example |
|---------|-------------|---------|
| Bates Prefix | Text before number | "SMITH-v-JONES-" |
| Bates Suffix | Text after number | "-CONFIDENTIAL" |
| Start Number | First number in sequence | 1, 100, 1000 |
| Padding | Number of digits | 4 → "0001" |

### Position Options

- top-left, top-center, top-right
- bottom-left, bottom-center, bottom-right
- center

### Font Options

- **Font Family:** Helvetica (default), Times-Roman, Courier
- **Font Size:** 6-24 points (default: 12)
- **Color:** Black (default), blue, red, green, gray
- **Style:** Bold (default), Italic, or both

### Advanced Options

- **Include Date Stamp:** Adds timestamp below Bates number
  - Default format: YYYY-MM-DD
  - Customizable using Python datetime format strings
- **White Background:** Adds white rectangle behind text
  - Adjustable padding (0-10 pixels)
  - Improves visibility on dark backgrounds
- **Separator Page:** Adds cover page showing Bates range
  - Displays first and last Bates numbers
  - Useful for document organization

## Use Cases

### Legal Discovery Production

**Scenario:** Producing documents for litigation

**Configuration:**
- Preset: Legal Discovery
- Prefix: PLAINTIFF-PROD-
- Start Number: 1
- Padding: 6
- Position: bottom-right

**Result:** `PLAINTIFF-PROD-000001`, `PLAINTIFF-PROD-000002`, etc.

### Confidential Documents

**Scenario:** Marking sensitive documents

**Configuration:**
- Preset: Confidential
- Prefix: CONFIDENTIAL-
- Suffix: -AEO
- Color: Red
- Position: top-center
- Bold: Yes

**Result:** `CONFIDENTIAL-0001-AEO` in red, bold text

### Exhibit Preparation

**Scenario:** Preparing trial exhibits

**Configuration:**
- Preset: Exhibit
- Prefix: EXHIBIT-
- Start Number: 101
- Padding: 3
- Font Size: 14
- Position: top-right

**Result:** `EXHIBIT-101`, `EXHIBIT-102`, etc.

### Archived Documents

**Scenario:** Archiving historical documents

**Configuration:**
- Prefix: ARCH-
- Include Date: Yes
- Date Format: %Y%m%d
- Position: bottom-left
- Add Separator: Yes

**Result:** `ARCH-0001` with date stamp and separator page

## Deployment

### Local Network Deployment

Share the web UI on your local network:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Access from other devices: `http://[your-ip]:8501`

### Streamlit Cloud (Free Hosting)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy with one click

### Docker Deployment

```bash
# Build image
docker build -t bates-labeler .

# Run container
docker run -d -p 8501:8501 --name bates-web bates-labeler

# Stop container
docker stop bates-web

# Remove container
docker rm bates-web
```

### Self-Hosted Server

For production deployment on your own server:

```bash
# Using systemd
sudo nano /etc/systemd/system/bates-labeler.service
```

```ini
[Unit]
Description=Bates Labeler Web UI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/bates-labeler
ExecStart=/usr/local/bin/streamlit run app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable bates-labeler
sudo systemctl start bates-labeler
```

## Security Considerations

### File Size Limits
- Maximum upload: 200MB per file
- Configurable in `.streamlit/config.toml`

### Data Privacy
- Files are processed in temporary directories
- Automatic cleanup after processing
- No data persistence or logging of uploads
- All processing happens locally/on your server

### Authentication (Optional)

For multi-user deployments, consider adding authentication:

```bash
# Install streamlit-authenticator
pip install streamlit-authenticator

# Configure in app.py
# See: https://github.com/mkhorasani/Streamlit-Authenticator
```

### HTTPS/SSL

For production deployments, use a reverse proxy:

```nginx
# Nginx configuration
server {
    listen 443 ssl;
    server_name bates.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8501
lsof -i :8501

# Kill the process
kill -9 [PID]

# Or use a different port
streamlit run app.py --server.port 8502
```

### Upload Fails

- Check file size (max 200MB)
- Verify file is a valid PDF
- Check disk space in temp directory
- Review browser console for errors

### Slow Processing

- Large PDFs (1000+ pages) take time
- Progress bar shows real-time status
- Consider batch processing smaller groups
- Check system resources (CPU, RAM)

### Docker Issues

```bash
# View logs
docker logs bates-web

# Rebuild image
docker build --no-cache -t bates-labeler .

# Check container status
docker ps -a
```

## Performance Tips

1. **Batch Processing:** Group related documents for continuous numbering
2. **File Size:** PDFs under 50MB process fastest
3. **Page Count:** Best performance with PDFs under 500 pages
4. **Server Resources:** More RAM = better performance for large batches
5. **Network:** Local deployment is faster than cloud for large files

## Keyboard Shortcuts

### Application Shortcuts
- **Ctrl+S:** Save current configuration
- **Ctrl+L:** Load saved configuration
- **Ctrl+P:** Start processing PDFs
- **Ctrl+Z:** Undo last configuration change
- **Ctrl+Y:** Redo configuration change
- **Ctrl+H:** View processing history
- **Ctrl+N:** Clear/reset all settings

### Browser Shortcuts
- **Ctrl/Cmd + R:** Reload page
- **Ctrl/Cmd + Shift + R:** Clear cache and reload
- **r:** Rerun from Streamlit menu

### Navigation Shortcuts
- **Tab:** Navigate between form fields
- **Shift+Tab:** Navigate backwards
- **Enter:** Activate buttons/checkboxes
- **Space:** Toggle checkboxes

## New Features in v2.0.0

### Session Persistence
Save and load configurations for repeated workflows:
- Click "Save Configuration" or use **Ctrl+S**
- Enter a descriptive name for your configuration
- Load saved configurations with "Load Configuration" or **Ctrl+L**
- Perfect for repeated processing with the same settings

### Configuration Import/Export
Share and backup configurations using JSON files:
- **Export**: Download your current configuration as a JSON file
  - Click "📤 Export Config (JSON)" in the Processing History section
  - File includes all settings (prefix, suffix, position, fonts, colors, etc.)
  - Perfect for backing up or sharing configurations with team members
- **Import**: Load a previously exported configuration
  - Click "📥 Import Config (JSON)" and select a .json file
  - Instantly applies all saved settings
  - Use the example file: `docs/example_config.json` to see the format

**Example Configuration Format:**
```json
{
  "prefix": "CASE-2024-",
  "suffix": "-CONF",
  "start_number": 1,
  "padding": 6,
  "position": "bottom-right",
  "font_name": "Helvetica",
  "font_size": 12,
  "font_color": "black"
}
```

**Note**: Only JSON files are supported for import. The file must contain valid JSON with recognized configuration keys.

### Undo/Redo
Full state management for configuration changes:
- Use **Ctrl+Z** to undo the last change
- Use **Ctrl+Y** to redo a change
- View undo/redo history in the sidebar
- All configuration changes are tracked

### OCR Text Extraction
Extract text from scanned documents:
- Enable OCR in Advanced Options
- Choose between local Tesseract or cloud OCR services
- Extracted text is embedded in the output PDF
- Works with image-based PDFs and scanned documents

### Processing History
View and restore previous processing jobs:
- Access history with **Ctrl+H**
- See past configurations, timestamps, and file counts
- Restore any previous configuration
- Clear history when needed

### Pre-flight Validation
Automatic PDF health checks:
- Validates PDFs before processing
- Checks for corruption, encryption, and compatibility
- Provides detailed validation reports
- Prevents processing errors

### Batch Export Formats
Export to multiple formats:
- **JSON**: Structured data export
- **CSV**: Spreadsheet-compatible format
- **Excel (.xlsx)**: Professional spreadsheet with formatting
- **TIFF**: Image-based format for archival

### Drag-and-Drop Reordering
Reorder files before processing:
- Drag files up or down in the file list
- Bates numbers are assigned in the displayed order
- Visual feedback during reordering
- Perfect for organizing documents

### PDF Preview Panel
View PDFs before processing:
- Preview any uploaded PDF
- Navigate through pages
- Zoom and pan controls
- Verify content before processing

### Individual File Progress
Track progress for each file:
- See progress bars for each file in batch operations
- Monitor current page being processed
- Estimate remaining time per file
- Cancel individual files if needed

### Page Rotation
Rotate pages during processing:
- Rotate pages 90°, 180°, or 270°
- Apply rotation to all pages or specific ranges
- Rotation is applied before Bates numbering
- Preserve original file if needed

### Bates Validation
Real-time format validation:
- Validates Bates prefix and suffix format
- Checks for invalid characters
- Provides helpful error messages
- Prevents processing with invalid formats

### Performance Optimizations
10-15x faster processing:
- Parallel processing for batch operations
- Intelligent caching reduces redundant work
- Optimized memory usage for large files
- Background processing doesn't block UI

## CLI vs Web UI

| Feature | CLI | Web UI |
|---------|-----|--------|
| Ease of Use | Technical | Everyone |
| Batch Processing | ✅ | ✅ |
| Configuration Presets | ❌ | ✅ |
| Visual Preview | ❌ | ✅ |
| Progress Tracking | Terminal | Visual |
| File Management | Manual | Drag & Drop |
| Automation | ✅ | ❌ |
| Scripting | ✅ | ❌ |
| Session Persistence | ❌ | ✅ |
| Undo/Redo | ❌ | ✅ |
| Keyboard Shortcuts | ❌ | ✅ |
| OCR Support | ❌ | ✅ |
| PDF Preview | ❌ | ✅ |
| Multi-format Export | ❌ | ✅ |

## Support

- **Documentation:** [GitHub README](https://github.com/thepingdoctor/Bates-Labeler)
- **Issues:** [GitHub Issues](https://github.com/thepingdoctor/Bates-Labeler/issues)
- **CLI Guide:** See `PACKAGING.md` for command-line usage

## Version Information

Web UI added in version 1.1.0
- Streamlit-based interface
- Configuration presets
- Batch processing support
- Real-time preview
