# Bates-Labeler System Architecture

**Document Version:** 1.0
**Last Updated:** 2025-10-23
**Architect:** System Architecture Agent

## Executive Summary

This document outlines the technical architecture for implementing 4 high-priority features in the Bates-Labeler application:

1. **Undo/Redo (#1)** - Command pattern with state snapshots
2. **OCR Support (#4)** - Local Tesseract integration with cloud fallback
3. **Keyboard Shortcuts (#6)** - Event-driven hotkey system
4. **TIFF Export Enhancement (#5)** - Extended export format support

**Already Implemented:**
- Pre-flight Validation (#8) - `/bates_labeler/validation.py`
- Session Persistence (#2) - `app.py` lines 110-187
- Batch Export (partial) (#5) - `/bates_labeler/export.py`

---

## Table of Contents

1. [Current System Overview](#1-current-system-overview)
2. [Feature 1: Undo/Redo System](#2-feature-1-undoredo-system)
3. [Feature 2: OCR Support](#3-feature-2-ocr-support)
4. [Feature 3: Keyboard Shortcuts](#4-feature-3-keyboard-shortcuts)
5. [Feature 4: TIFF Export Enhancement](#5-feature-4-tiff-export-enhancement)
6. [Integration Strategy](#6-integration-strategy)
7. [Data Flow Diagrams](#7-data-flow-diagrams)
8. [Technology Stack](#8-technology-stack)
9. [Risk Assessment](#9-risk-assessment)

---

## 1. Current System Overview

### 1.1 Module Structure

```
bates_labeler/
├── core.py                 # BatesNumberer class (main engine)
├── validation.py           # Pre-flight PDF validation
├── export.py              # Batch metadata export (JSON, CSV, XML, HTML, MD)
├── rotation.py            # PDF page manipulation
├── bates_validation.py    # Bates number conflict detection
├── cli.py                 # Command-line interface
└── __init__.py

app.py                     # Streamlit web UI (1377 lines)
└── Session persistence implemented (lines 110-187)
```

### 1.2 Key Technologies

- **PDF Processing:** `pypdf` (formerly PyPDF2)
- **Web UI:** Streamlit 1.30.0+
- **Graphics:** ReportLab for PDF generation
- **File Handling:** Python standard library (tempfile, os, pathlib)

### 1.3 Current Processing Flow

```
[PDF Upload] → [Validation] → [Bates Processing] → [Export]
                    ↓                ↓                  ↓
              validation.py    core.py           export.py
```

---

## 2. Feature 1: Undo/Redo System

### 2.1 Design Pattern: Command Pattern + Memento

**Architecture Decision:**
- Use **Command Pattern** for user actions
- Use **Memento Pattern** for state snapshots
- Store operations in a bi-directional stack

### 2.2 Module Structure

**New Module:** `/bates_labeler/history.py`

```python
class Operation(ABC):
    """Abstract base class for undoable operations"""
    @abstractmethod
    def execute(self) -> bool

    @abstractmethod
    def undo(self) -> bool

    @abstractmethod
    def get_description(self) -> str

class HistoryManager:
    """Manages undo/redo stacks"""
    def __init__(self, max_history: int = 50):
        self.undo_stack: List[Operation] = []
        self.redo_stack: List[Operation] = []
        self.max_history = max_history

    def execute(self, operation: Operation) -> bool
    def undo(self) -> Optional[Operation]
    def redo(self) -> Optional[Operation]
    def can_undo(self) -> bool
    def can_redo(self) -> bool
    def get_history(self) -> List[str]
    def clear(self) -> None

# Concrete Operations
class BatesNumberOperation(Operation):
    """Represents a Bates numbering operation"""

class FileReorderOperation(Operation):
    """Represents file reordering"""

class ConfigurationChangeOperation(Operation):
    """Represents configuration changes"""
```

### 2.3 State Management Strategy

**Option 1: Full State Snapshots (Chosen)**
- **Pros:** Simple to implement, guaranteed consistency
- **Cons:** Higher memory usage
- **Mitigation:** Limit history to 50 operations, compress snapshots

**Option 2: Differential State (Rejected)**
- **Pros:** Lower memory usage
- **Cons:** Complex to implement, potential for state corruption

### 2.4 Integration Points

**Streamlit Session State:**
```python
# app.py additions
if 'history_manager' not in st.session_state:
    st.session_state.history_manager = HistoryManager()

# After each operation
operation = BatesNumberOperation(config, files, result)
st.session_state.history_manager.execute(operation)
```

**UI Components:**
```python
# Keyboard shortcuts integration
col1, col2 = st.columns(2)
with col1:
    if st.button("⏪ Undo (Ctrl+Z)",
                 disabled=not st.session_state.history_manager.can_undo()):
        st.session_state.history_manager.undo()
        st.rerun()
with col2:
    if st.button("⏩ Redo (Ctrl+Y)",
                 disabled=not st.session_state.history_manager.can_redo()):
        st.session_state.history_manager.redo()
        st.rerun()
```

### 2.5 Snapshot Storage

```python
@dataclass
class ProcessingSnapshot:
    """Immutable snapshot of processing state"""
    timestamp: datetime
    config: Dict
    file_order: List[str]
    processed_files: List[Dict]
    current_bates_number: int

    def compress(self) -> bytes:
        """Compress snapshot to reduce memory"""
        import zlib
        import pickle
        return zlib.compress(pickle.dumps(self))

    @classmethod
    def decompress(cls, data: bytes) -> 'ProcessingSnapshot':
        import zlib
        import pickle
        return pickle.loads(zlib.decompress(data))
```

### 2.6 Performance Considerations

- **Memory Budget:** ~100MB for 50 snapshots (2MB per snapshot)
- **Compression:** Use zlib for snapshots >500KB
- **Garbage Collection:** Auto-clear history on session end

---

## 3. Feature 2: OCR Support

### 3.1 Architecture Strategy: Hybrid Local/Cloud

**Decision Rationale:**
- **Primary:** Local Tesseract OCR (free, private, offline)
- **Fallback:** Cloud OCR APIs (Google Vision, AWS Textract) - optional
- **Use Case:** Scanned PDFs without searchable text

### 3.2 Module Structure

**New Module:** `/bates_labeler/ocr.py`

```python
class OCREngine(ABC):
    """Abstract base class for OCR engines"""
    @abstractmethod
    def extract_text(self, image: Image) -> str

    @abstractmethod
    def is_available(self) -> bool

class TesseractOCR(OCREngine):
    """Local Tesseract OCR implementation"""
    def __init__(self, language: str = 'eng', config: str = '--psm 1'):
        self.language = language
        self.config = config

    def extract_text(self, image: Image) -> str:
        import pytesseract
        return pytesseract.image_to_string(image, lang=self.language, config=self.config)

    def is_available(self) -> bool:
        # Check if tesseract is installed
        import shutil
        return shutil.which('tesseract') is not None

class GoogleVisionOCR(OCREngine):
    """Google Cloud Vision API (optional)"""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def extract_text(self, image: Image) -> str:
        # Implement Google Vision API call
        pass

class PDFOCRProcessor:
    """Orchestrates OCR on PDF documents"""
    def __init__(self, engine: OCREngine, dpi: int = 300):
        self.engine = engine
        self.dpi = dpi

    def process_pdf(self, pdf_path: str, output_path: str) -> Dict:
        """Convert scanned PDF to searchable PDF"""
        # 1. Extract images from PDF pages
        # 2. Run OCR on each page
        # 3. Overlay text on original PDF
        # 4. Save as searchable PDF
        pass

    def is_searchable(self, pdf_path: str) -> bool:
        """Check if PDF already has text layer"""
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text()
            if text.strip():
                return True
        return False
```

### 3.3 OCR Processing Pipeline

```
[PDF Upload] → [Searchability Check] → [Decision]
                                          ↓
                                    Is Searchable?
                                    ↙         ↘
                                  Yes          No
                                   ↓            ↓
                          [Skip OCR]    [Extract Images]
                                               ↓
                                        [Run OCR Engine]
                                               ↓
                                        [Overlay Text]
                                               ↓
                                        [Searchable PDF]
                                               ↓
                          [Continue Bates Processing]
```

### 3.4 Integration with Validation

```python
# validation.py enhancement
class ValidationIssue:
    # Add new issue type
    NO_TEXT_LAYER = "no_text_layer"

class PDFValidator:
    def validate_file(self, file_path: str) -> ValidationResult:
        # ... existing validation ...

        # Check for text layer
        if self.check_ocr_needed(file_path):
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                code="NO_TEXT_LAYER",
                message="PDF appears to be scanned image. OCR recommended.",
                details={'ocr_available': OCREngine.is_tesseract_installed()}
            ))
```

### 3.5 UI Integration

```python
# app.py additions
with st.expander("🔍 OCR Settings", expanded=False):
    enable_ocr = st.checkbox(
        "Enable OCR for Scanned PDFs",
        help="Automatically detect and OCR scanned documents"
    )

    if enable_ocr:
        ocr_language = st.selectbox(
            "OCR Language",
            options=['eng', 'spa', 'fra', 'deu', 'chi_sim'],
            help="Language for text recognition"
        )

        ocr_dpi = st.slider(
            "OCR Quality (DPI)",
            min_value=150,
            max_value=600,
            value=300,
            step=50,
            help="Higher DPI = better quality, slower processing"
        )

        # Check Tesseract availability
        if not TesseractOCR.is_available():
            st.warning("⚠️ Tesseract not installed. Install: `sudo apt-get install tesseract-ocr`")
```

### 3.6 Dependencies

```toml
# pyproject.toml additions
[project.optional-dependencies]
ocr = [
    "pytesseract>=0.3.10",
    "pdf2image>=1.16.3",
    "Pillow>=10.0.0"
]
```

### 3.7 Performance Optimization

- **Parallel Processing:** Use ThreadPoolExecutor for multi-page OCR
- **Caching:** Store OCR results in temporary cache
- **Progress Tracking:** Report OCR progress per page
- **Memory Management:** Process pages in batches (10 pages at a time)

---

## 4. Feature 3: Keyboard Shortcuts

### 4.1 Architecture: Event-Driven Hotkey System

**Challenge:** Streamlit doesn't natively support keyboard events

**Solution:** JavaScript bridge + custom component

### 4.2 Implementation Strategy

**Option 1: Streamlit Custom Component (Chosen)**
```javascript
// frontend/keyboard_shortcuts.js
const KeyboardShortcuts = (props) => {
    useEffect(() => {
        const handleKeyPress = (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch(event.key) {
                    case 'z':
                        Streamlit.setComponentValue({action: 'undo'});
                        event.preventDefault();
                        break;
                    case 'y':
                        Streamlit.setComponentValue({action: 'redo'});
                        event.preventDefault();
                        break;
                    case 'p':
                        Streamlit.setComponentValue({action: 'process'});
                        event.preventDefault();
                        break;
                    // ... more shortcuts
                }
            }
        };

        document.addEventListener('keydown', handleKeyPress);
        return () => document.removeEventListener('keydown', handleKeyPress);
    }, []);

    return null; // Invisible component
};
```

**Option 2: st.components.html (Simpler, Chosen for MVP)**
```python
# bates_labeler/shortcuts.py
def register_keyboard_shortcuts():
    """Register keyboard shortcuts using HTML/JS injection"""
    shortcuts_html = """
    <script>
    const shortcuts = {
        'ctrl+z': 'undo',
        'ctrl+y': 'redo',
        'ctrl+p': 'process',
        'ctrl+o': 'open',
        'ctrl+s': 'save',
        'ctrl+shift+z': 'redo',
        'escape': 'cancel'
    };

    document.addEventListener('keydown', function(e) {
        const key = (e.ctrlKey ? 'ctrl+' : '') +
                   (e.shiftKey ? 'shift+' : '') +
                   e.key.toLowerCase();

        if (shortcuts[key]) {
            e.preventDefault();
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: {action: shortcuts[key]}
            }, '*');
        }
    });
    </script>
    """
    return st.components.v1.html(shortcuts_html, height=0)
```

### 4.3 Module Structure

**New Module:** `/bates_labeler/shortcuts.py`

```python
from dataclasses import dataclass
from typing import Callable, Dict, Optional
from enum import Enum

class ShortcutAction(Enum):
    UNDO = "undo"
    REDO = "redo"
    PROCESS = "process"
    OPEN_FILE = "open"
    SAVE_CONFIG = "save"
    CANCEL = "cancel"
    TOGGLE_PREVIEW = "preview"
    NEXT_FILE = "next"
    PREV_FILE = "prev"

@dataclass
class Shortcut:
    """Keyboard shortcut definition"""
    key: str
    action: ShortcutAction
    description: str
    handler: Callable
    enabled: bool = True
    modifier: str = "ctrl"  # ctrl, alt, shift

class ShortcutManager:
    """Manages keyboard shortcuts"""
    def __init__(self):
        self.shortcuts: Dict[str, Shortcut] = {}
        self._register_defaults()

    def register(self, shortcut: Shortcut) -> None:
        """Register a new shortcut"""
        key = f"{shortcut.modifier}+{shortcut.key}"
        self.shortcuts[key] = shortcut

    def handle_action(self, action: str, context: Dict) -> None:
        """Handle keyboard action"""
        for shortcut in self.shortcuts.values():
            if shortcut.action.value == action and shortcut.enabled:
                shortcut.handler(context)
                break

    def get_help_text(self) -> str:
        """Generate help text for all shortcuts"""
        lines = ["## Keyboard Shortcuts\n"]
        for key, shortcut in self.shortcuts.items():
            lines.append(f"- **{key.upper()}**: {shortcut.description}")
        return "\n".join(lines)

    def _register_defaults(self) -> None:
        """Register default shortcuts"""
        self.register(Shortcut(
            key="z",
            action=ShortcutAction.UNDO,
            description="Undo last operation",
            handler=lambda ctx: ctx['history'].undo()
        ))
        # ... more defaults
```

### 4.4 UI Integration

```python
# app.py modifications
def main():
    initialize_session_state()

    # Initialize keyboard shortcuts
    if 'shortcut_manager' not in st.session_state:
        st.session_state.shortcut_manager = ShortcutManager()

    # Register shortcuts component
    shortcut_action = register_keyboard_shortcuts()

    # Handle shortcut actions
    if shortcut_action:
        context = {
            'history': st.session_state.history_manager,
            'files': st.session_state.file_order,
            'config': st.session_state.current_config
        }
        st.session_state.shortcut_manager.handle_action(shortcut_action['action'], context)
        st.rerun()

    # Add help button
    with st.sidebar:
        with st.expander("⌨️ Keyboard Shortcuts"):
            st.markdown(st.session_state.shortcut_manager.get_help_text())
```

### 4.5 Default Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Z` | Undo | Undo last operation |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Redo | Redo operation |
| `Ctrl+P` | Process | Start processing PDFs |
| `Ctrl+O` | Open | Upload files dialog |
| `Ctrl+S` | Save | Save current configuration |
| `Escape` | Cancel | Cancel processing |
| `Ctrl+H` | Help | Show shortcuts help |
| `Ctrl+←` | Previous | Previous file in preview |
| `Ctrl+→` | Next | Next file in preview |

### 4.6 Accessibility Considerations

- Display shortcut hints on hover
- Support alternative shortcuts (e.g., Cmd on Mac)
- Allow users to customize shortcuts
- Ensure screen reader compatibility

---

## 5. Feature 4: TIFF Export Enhancement

### 5.1 Architecture: Export Format Extension

**Current State:** `export.py` supports JSON, CSV, TSV, XML, Markdown, HTML

**Enhancement:** Add TIFF/Multi-page TIFF export

### 5.2 Module Enhancement

**Update:** `/bates_labeler/export.py`

```python
# Add TIFF export methods to MetadataExporter class

class MetadataExporter:
    def export_to_tiff(
        self,
        pdf_path: str,
        output_path: str,
        dpi: int = 300,
        compression: str = 'tiff_lzw',
        color_mode: str = 'RGB'
    ) -> bool:
        """
        Export PDF to TIFF format.

        Args:
            pdf_path: Path to input PDF
            output_path: Path for output TIFF
            dpi: Resolution in dots per inch
            compression: Compression algorithm ('tiff_lzw', 'tiff_deflate', 'jpeg')
            color_mode: Color mode ('RGB', 'L' for grayscale, '1' for B&W)

        Returns:
            True if successful, False otherwise
        """
        try:
            from pdf2image import convert_from_path
            from PIL import Image

            # Convert PDF pages to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt='tiff'
            )

            # Convert color mode if specified
            if color_mode != 'RGB':
                images = [img.convert(color_mode) for img in images]

            # Save as multi-page TIFF
            if len(images) == 1:
                images[0].save(
                    output_path,
                    compression=compression,
                    dpi=(dpi, dpi)
                )
            else:
                images[0].save(
                    output_path,
                    save_all=True,
                    append_images=images[1:],
                    compression=compression,
                    dpi=(dpi, dpi)
                )

            logger.info(f"TIFF export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to TIFF: {str(e)}")
            return False

    def export_to_tiff_sequence(
        self,
        pdf_path: str,
        output_dir: str,
        dpi: int = 300,
        compression: str = 'tiff_lzw',
        naming_pattern: str = "page_{:04d}.tiff"
    ) -> List[str]:
        """
        Export PDF to sequence of TIFF files (one per page).

        Args:
            pdf_path: Path to input PDF
            output_dir: Directory for output TIFF files
            dpi: Resolution in dots per inch
            compression: Compression algorithm
            naming_pattern: Filename pattern (must include {:04d} placeholder)

        Returns:
            List of created TIFF file paths
        """
        try:
            from pdf2image import convert_from_path
            import os

            os.makedirs(output_dir, exist_ok=True)

            images = convert_from_path(pdf_path, dpi=dpi)

            output_files = []
            for i, image in enumerate(images):
                output_path = os.path.join(
                    output_dir,
                    naming_pattern.format(i + 1)
                )

                image.save(
                    output_path,
                    compression=compression,
                    dpi=(dpi, dpi)
                )
                output_files.append(output_path)

            logger.info(f"Exported {len(output_files)} TIFF files to {output_dir}")
            return output_files

        except Exception as e:
            logger.error(f"Error exporting TIFF sequence: {str(e)}")
            return []
```

### 5.3 Integration with BatesNumberer

**Update:** `/bates_labeler/core.py`

```python
class BatesNumberer:
    def export_as_tiff(
        self,
        pdf_path: str,
        output_path: str,
        dpi: int = 300,
        compression: str = 'tiff_lzw',
        color_mode: str = 'RGB'
    ) -> bool:
        """
        Export Bates-numbered PDF as TIFF.

        This is a convenience method that delegates to MetadataExporter.
        """
        exporter = MetadataExporter()
        return exporter.export_to_tiff(
            pdf_path, output_path, dpi, compression, color_mode
        )
```

### 5.4 UI Integration

```python
# app.py additions
with st.expander("📄 Export Formats", expanded=False):
    st.markdown("### Additional Export Options")

    export_tiff = st.checkbox(
        "Export as TIFF",
        help="Convert processed PDFs to TIFF format"
    )

    if export_tiff:
        col1, col2 = st.columns(2)

        with col1:
            tiff_format = st.selectbox(
                "TIFF Format",
                options=['Single Multi-page TIFF', 'Separate TIFF per Page'],
                help="Choose between single file or multiple files"
            )

            tiff_dpi = st.slider(
                "TIFF Resolution (DPI)",
                min_value=150,
                max_value=600,
                value=300,
                step=50,
                help="Higher DPI = larger file size"
            )

        with col2:
            tiff_compression = st.selectbox(
                "Compression",
                options=['tiff_lzw', 'tiff_deflate', 'jpeg', 'none'],
                index=0,
                help="LZW recommended for legal documents"
            )

            tiff_color_mode = st.selectbox(
                "Color Mode",
                options=['RGB', 'L (Grayscale)', '1 (Black & White)'],
                help="Grayscale/B&W reduces file size"
            )
```

### 5.5 Enhanced Export Workflow

```python
# After Bates processing
if export_tiff:
    status_callback("Exporting to TIFF...")

    exporter = MetadataExporter()

    for processed_file in st.session_state.processed_files:
        # Save PDF to temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(processed_file['data'])
            tmp_path = tmp.name

        # Export to TIFF
        tiff_path = tmp_path.replace('.pdf', '.tiff')

        if tiff_format == 'Single Multi-page TIFF':
            success = exporter.export_to_tiff(
                tmp_path, tiff_path,
                dpi=tiff_dpi,
                compression=tiff_compression,
                color_mode=tiff_color_mode.split()[0]
            )

            if success:
                with open(tiff_path, 'rb') as f:
                    st.session_state.processed_files.append({
                        'name': processed_file['name'].replace('.pdf', '.tiff'),
                        'data': f.read()
                    })

        os.unlink(tmp_path)
        if os.path.exists(tiff_path):
            os.unlink(tiff_path)
```

### 5.6 Dependencies

```toml
# pyproject.toml additions
[project.optional-dependencies]
tiff = [
    "pdf2image>=1.16.3",
    "Pillow>=10.0.0"
]
```

---

## 6. Integration Strategy

### 6.1 Phased Rollout Plan

**Phase 1: Foundation (Week 1)**
- Implement `history.py` module
- Add undo/redo to session state
- Unit tests for command pattern

**Phase 2: OCR Integration (Week 2)**
- Implement `ocr.py` module
- Integrate with validation pipeline
- Add UI controls

**Phase 3: User Experience (Week 3)**
- Implement keyboard shortcuts
- Add TIFF export
- Integration testing

**Phase 4: Polish & Testing (Week 4)**
- End-to-end testing
- Performance optimization
- Documentation updates

### 6.2 Module Dependency Graph

```
app.py
  ├── shortcuts.py (new)
  │   └── No dependencies
  ├── history.py (new)
  │   └── core.py
  ├── ocr.py (new)
  │   ├── validation.py
  │   └── core.py
  ├── export.py (enhanced)
  │   └── core.py
  └── validation.py (enhanced)
      └── ocr.py (optional)
```

### 6.3 Backward Compatibility

- All new features are **opt-in** (disabled by default)
- Existing workflows remain unchanged
- Configuration files remain compatible
- No breaking changes to core API

### 6.4 Testing Strategy

```python
# tests/test_history.py
def test_undo_redo_operations()
def test_snapshot_compression()
def test_max_history_limit()

# tests/test_ocr.py
def test_tesseract_detection()
def test_searchability_check()
def test_ocr_quality()

# tests/test_shortcuts.py
def test_shortcut_registration()
def test_action_handling()

# tests/test_tiff_export.py
def test_single_page_tiff()
def test_multipage_tiff()
def test_compression_options()
```

---

## 7. Data Flow Diagrams

### 7.1 Undo/Redo Flow

```
[User Action] → [Create Operation] → [Execute Operation]
                                            ↓
                                    [Save Snapshot]
                                            ↓
                                    [Push to Undo Stack]
                                            ↓
                                    [Clear Redo Stack]

[Undo Request] → [Pop from Undo Stack] → [Restore Snapshot] → [Push to Redo Stack]

[Redo Request] → [Pop from Redo Stack] → [Restore Snapshot] → [Push to Undo Stack]
```

### 7.2 OCR Processing Flow

```
[PDF Upload] → [Is Searchable?] ──YES──→ [Skip OCR]
                    │                          │
                    NO                         ↓
                    ↓                    [Bates Processing]
            [Extract Images]
                    ↓
            [Run OCR Engine]
                    ↓
            [Overlay Text Layer]
                    ↓
            [Save Searchable PDF]
                    ↓
            [Bates Processing]
```

### 7.3 Keyboard Shortcut Flow

```
[User Keypress] → [JS Event Listener] → [PostMessage to Streamlit]
                                                  ↓
                                        [ShortcutManager.handle_action()]
                                                  ↓
                                        [Execute Registered Handler]
                                                  ↓
                                        [Update UI State]
                                                  ↓
                                        [st.rerun()]
```

---

## 8. Technology Stack

### 8.1 New Dependencies

| Dependency | Version | Purpose | Optional |
|------------|---------|---------|----------|
| `pytesseract` | >=0.3.10 | OCR text extraction | Yes (OCR feature) |
| `pdf2image` | >=1.16.3 | PDF to image conversion | Yes (OCR/TIFF) |
| `Pillow` | >=10.0.0 | Image processing | Yes (OCR/TIFF) |

### 8.2 System Dependencies

| Dependency | Installation | Purpose |
|------------|--------------|---------|
| Tesseract OCR | `sudo apt-get install tesseract-ocr` | OCR engine |
| Poppler | `sudo apt-get install poppler-utils` | PDF rendering |

### 8.3 Browser Requirements

- **Keyboard Shortcuts:** Modern browser with ES6 support
- **Minimum:** Chrome 90+, Firefox 88+, Safari 14+

---

## 9. Risk Assessment

### 9.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Streamlit keyboard event limitations | High | High | Use JavaScript bridge + fallback UI buttons |
| OCR accuracy on poor scans | Medium | Medium | Allow manual text correction, configurable OCR settings |
| Memory usage with undo history | Medium | Low | Limit history size, compress snapshots, clear on session end |
| TIFF export performance | Low | Low | Process in background, show progress bar |

### 9.2 User Experience Risks

| Risk | Mitigation |
|------|------------|
| Confusion about new features | Progressive disclosure, tooltips, help documentation |
| Keyboard shortcuts conflict with browser | Use Ctrl+Shift combinations, allow customization |
| OCR processing time | Clear progress indicators, allow cancellation |

### 9.3 Security Considerations

- **OCR:** Local Tesseract prevents data exposure (no cloud upload)
- **History:** Snapshots stored in session state only (not persisted)
- **TIFF Export:** Uses trusted libraries (Pillow, pdf2image)

---

## 10. Performance Benchmarks

### 10.1 Expected Performance

| Operation | Baseline | With Features | Impact |
|-----------|----------|---------------|--------|
| PDF Processing (10 pages) | 2.5s | 2.8s | +12% (undo snapshot) |
| OCR Processing (10 pages) | N/A | 15-30s | New feature |
| TIFF Export (10 pages, 300 DPI) | N/A | 8-12s | New feature |
| Undo/Redo | N/A | <100ms | New feature |

### 10.2 Optimization Targets

- **Undo/Redo:** <100ms response time
- **OCR:** <3s per page at 300 DPI
- **TIFF Export:** <1s per page
- **Memory:** <150MB total for all features

---

## 11. Future Enhancements

### 11.1 Potential Extensions

1. **Advanced OCR:**
   - Table detection and preservation
   - Handwriting recognition
   - Multi-language detection

2. **Enhanced History:**
   - Persistent history across sessions
   - History export/import
   - Visual diff viewer

3. **Keyboard Shortcuts:**
   - User-customizable shortcuts
   - Shortcut recording
   - Context-sensitive shortcuts

4. **Export Formats:**
   - SVG export
   - PNG/JPG sequence export
   - Microsoft Word export

### 11.2 Scalability Considerations

- **Large Documents:** Implement page-level processing for 1000+ page PDFs
- **Batch Processing:** Support processing 100+ files concurrently
- **Cloud Storage:** Integration with S3, Google Drive, Dropbox

---

## 12. Architecture Decision Records (ADRs)

### ADR-001: Command Pattern for Undo/Redo

**Status:** Accepted
**Context:** Need reversible operations for Bates numbering
**Decision:** Use Command Pattern with Memento for state snapshots
**Consequences:**
- ✅ Clean separation of concerns
- ✅ Easy to extend with new operations
- ❌ Higher memory usage (mitigated by compression)

### ADR-002: Local Tesseract for OCR

**Status:** Accepted
**Context:** Need OCR without cloud dependencies
**Decision:** Use local Tesseract as primary OCR engine
**Consequences:**
- ✅ Privacy-preserving (no data upload)
- ✅ Free and open-source
- ✅ Works offline
- ❌ Requires system installation
- ❌ Lower accuracy than cloud services (acceptable trade-off)

### ADR-003: JavaScript Bridge for Keyboard Shortcuts

**Status:** Accepted
**Context:** Streamlit lacks native keyboard event support
**Decision:** Use `st.components.html` with JavaScript
**Consequences:**
- ✅ Works with current Streamlit version
- ✅ No custom component build required
- ❌ Limited to visible component instances
- ❌ Potential browser compatibility issues

### ADR-004: TIFF via Pillow/pdf2image

**Status:** Accepted
**Context:** Need TIFF export for legal compliance
**Decision:** Use pdf2image + Pillow for TIFF conversion
**Consequences:**
- ✅ Mature, well-tested libraries
- ✅ Supports multi-page TIFF
- ✅ Multiple compression options
- ❌ Requires Poppler system dependency

---

## 13. Conclusion

This architecture provides a solid foundation for implementing the 4 remaining high-priority features:

1. **Undo/Redo** - Robust command pattern with compressed snapshots
2. **OCR Support** - Privacy-preserving local Tesseract integration
3. **Keyboard Shortcuts** - JavaScript bridge with fallback UI
4. **TIFF Export** - Standards-compliant legal document format

**Key Strengths:**
- Modular design allows independent development
- Backward compatible with existing workflows
- Opt-in features reduce risk
- Clear integration points with current codebase

**Next Steps:**
1. Review and approve architecture
2. Create detailed implementation tickets
3. Begin Phase 1 development (Undo/Redo)
4. Continuous integration with existing features

---

**Document Prepared By:** System Architecture Agent
**For Questions:** Coordinate via swarm memory at `swarm/architect/architecture-design`
**Version Control:** Track changes in `/docs/ARCHITECTURE.md`
