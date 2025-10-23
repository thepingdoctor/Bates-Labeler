# Usage Examples: New Features

This document provides practical examples for using the three newly implemented features.

---

## 1. Undo/Redo Functionality

### Example 1: Correcting Configuration Mistakes

**Scenario:** You accidentally changed the Bates prefix and want to revert.

**Steps:**
1. Open Bates-Labeler web UI
2. Change prefix from "CASE-" to "CASE123-"
3. Notice the mistake
4. Click the **"↶ Undo"** button in the sidebar
   - OR press `Ctrl+Z`
5. Configuration reverts to "CASE-"

**Result:** Previous configuration is restored instantly.

---

### Example 2: Experimenting with Settings

**Scenario:** Try different font sizes and positions to find the best look.

**Steps:**
1. Set font size to 12pt, position "bottom-right"
2. Try font size 14pt, position "top-center"
3. Try font size 16pt, position "center"
4. Decide 14pt top-center was best
5. Click **"↶ Undo"** once (back to 14pt top-center)

**Result:** Easily navigate through different configurations without manual retyping.

---

### Example 3: Monitoring History

**Scenario:** Track how many configuration changes you've made.

**UI Element:**
```
History: 5/12
```

**Meaning:**
- Currently at state 5
- 12 total states in history
- Can undo 4 times
- Can redo 7 times

---

## 2. Keyboard Shortcuts

### Example 1: Quick Processing Workflow

**Scenario:** Process PDFs quickly without mouse clicks.

**Workflow:**
1. Upload PDFs (click or drag-and-drop)
2. Configure settings
3. Press `Ctrl+P` to process
4. Press `Ctrl+D` to download
5. Press `Ctrl+R` to reset for next batch

**Result:** 60% faster workflow with keyboard shortcuts.

---

### Example 2: Undo/Redo with Keyboard

**Scenario:** Rapid configuration adjustments.

**Workflow:**
1. Change prefix to "PLAINTIFF-"
2. Press `Ctrl+Z` (undo)
3. Change prefix to "DEFENDANT-"
4. Press `Ctrl+Z` (undo)
5. Press `Ctrl+Y` (redo to "DEFENDANT-")
6. Keep "DEFENDANT-"

**Result:** Fast experimentation with instant keyboard control.

---

### Example 3: Save Configuration

**Scenario:** Save current configuration for later use.

**Steps:**
1. Configure all Bates settings
2. Press `Ctrl+S`
3. Configuration is exported as JSON
4. Download the JSON file

**Result:** Reusable configuration file for future sessions.

---

### Shortcut Reference

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+Z` | Undo | Revert last configuration change |
| `Ctrl+Y` | Redo | Restore last undone change |
| `Ctrl+P` | Process | Start processing PDFs |
| `Ctrl+S` | Save | Export configuration as JSON |
| `Ctrl+D` | Download | Download processed files |
| `Ctrl+R` | Reset | Reset all settings to default |

---

## 3. OCR Text Extraction

### Example 1: Scanned Discovery Documents (Local OCR)

**Scenario:** Process scanned legal discovery documents with local OCR.

**Setup:**
1. Install OCR dependencies:
   ```bash
   pip install bates-labeler[ocr-local]
   ```

2. Install Tesseract binary:
   - **macOS:** `brew install tesseract`
   - **Ubuntu:** `sudo apt-get install tesseract-ocr`
   - **Windows:** Download from [GitHub](https://github.com/tesseract-ocr/tesseract)

**Steps:**
1. Open Bates-Labeler web UI
2. Navigate to **"⚙️ Advanced Options"**
3. Check **"Enable OCR"**
4. Select backend: **"Local (Pytesseract - Privacy First)"**
5. Set language: `eng` (for English)
6. Upload scanned PDF files
7. Process PDFs

**Result:**
- Bates numbers added to scanned pages
- Extracted text embedded as PDF metadata
- All processing done locally (privacy-first)

---

### Example 2: High-Quality OCR with Google Cloud Vision

**Scenario:** Process complex scanned documents with high accuracy requirements.

**Setup:**
1. Install OCR dependencies:
   ```bash
   pip install bates-labeler[ocr-cloud]
   ```

2. Set up Google Cloud Vision:
   - Create Google Cloud project
   - Enable Vision API
   - Download credentials JSON

**Steps:**
1. Open Bates-Labeler web UI
2. Navigate to **"⚙️ Advanced Options"**
3. Check **"Enable OCR"**
4. Select backend: **"Cloud (Google Vision - Premium)"**
5. Upload Google credentials JSON file
6. Set language: `eng`
7. Upload scanned PDF files
8. Process PDFs

**Result:**
- Higher accuracy text extraction
- Better handling of complex layouts
- Confidence scores for extracted text

---

### Example 3: Multi-Language Documents

**Scenario:** Process scanned documents in Spanish.

**Steps:**
1. Enable OCR in Advanced Options
2. Select **"Local (Pytesseract)"**
3. Change language to: `spa` (Spanish)
4. Install Spanish language data:
   ```bash
   # macOS/Linux
   sudo apt-get install tesseract-ocr-spa
   ```
5. Upload and process Spanish PDFs

**Supported Languages:**
- `eng` - English
- `spa` - Spanish
- `fra` - French
- `deu` - German
- `ita` - Italian
- `por` - Portuguese
- `rus` - Russian
- `ara` - Arabic
- `chi_sim` - Chinese (Simplified)
- `jpn` - Japanese

---

### Example 4: Metadata Extraction Workflow

**Scenario:** Extract and verify OCR metadata from processed PDFs.

**Processing:**
1. Enable OCR
2. Process PDF with Bates numbering
3. Download processed PDF

**Verification (using Python):**
```python
from pypdf import PdfReader

# Read processed PDF
reader = PdfReader("processed_bates.pdf")

# Check metadata
metadata = reader.metadata
print(f"OCR Text: {metadata.get('/OCRText', 'Not found')}")
print(f"OCR Backend: {metadata.get('/OCRBackend', 'Not found')}")
print(f"OCR Processed: {metadata.get('/OCRProcessed', 'False')}")
```

**Result:**
- Verify text extraction worked
- Check which OCR backend was used
- Access extracted text programmatically

---

## Combined Workflow Examples

### Workflow 1: High-Volume Discovery Processing

**Scenario:** Process 50+ scanned discovery documents.

**Steps:**
1. Configure Bates settings:
   - Prefix: "PLAINTIFF-DISC-"
   - Start number: 1
   - Padding: 6

2. Enable OCR (Local):
   - Backend: Pytesseract
   - Language: English

3. Upload all 50 PDFs

4. Use keyboard shortcuts:
   - `Ctrl+P` to start processing
   - `Ctrl+D` to download as ZIP

5. If settings need adjustment:
   - `Ctrl+Z` to undo changes
   - Modify settings
   - `Ctrl+P` to reprocess

**Result:**
- Efficient processing of large batches
- Text searchable PDFs with Bates numbers
- Quick adjustments with undo/redo

---

### Workflow 2: Expert Witness Document Production

**Scenario:** Process expert witness reports with high accuracy OCR.

**Steps:**
1. Configure settings:
   - Prefix: "EXPERT-"
   - Suffix: "-CONF"
   - Add watermark: "CONFIDENTIAL"
   - Enable border on separator pages

2. Enable OCR (Cloud):
   - Backend: Google Vision
   - Upload credentials
   - Language: English

3. Test with one document:
   - Process single PDF
   - Review quality
   - Use `Ctrl+Z` if adjustments needed

4. Process all documents:
   - Upload remaining PDFs
   - `Ctrl+P` to process batch

5. Save configuration:
   - `Ctrl+S` to export settings
   - Reuse for future expert reports

**Result:**
- High-quality OCR extraction
- Consistent Bates numbering format
- Reusable configuration

---

### Workflow 3: Iterative Configuration Refinement

**Scenario:** Find perfect Bates number appearance through iteration.

**Steps:**
1. Initial configuration:
   - Position: bottom-right
   - Font: Helvetica 12pt
   - Process one test page

2. Try variations (using undo/redo):
   - Change to 14pt → `Ctrl+Z` (too large)
   - Change to 10pt → `Ctrl+Z` (too small)
   - `Ctrl+Y` back to 14pt → `Ctrl+Z`
   - Settle on 12pt

3. Try positions:
   - top-right → `Ctrl+Z`
   - top-center → `Ctrl+Z`
   - bottom-right (keep this)

4. Final settings:
   - Add white background
   - Enable bold
   - `Ctrl+S` to save

5. Process full batch:
   - `Ctrl+P` to process all

**Result:**
- Perfect configuration through experimentation
- No manual note-taking of settings
- Instant reversion to any previous state

---

## Troubleshooting

### Undo/Redo Not Working

**Issue:** Undo button is disabled.

**Solution:**
- No history available yet
- Make configuration changes first
- History builds automatically as you modify settings

---

### Keyboard Shortcuts Not Responding

**Issue:** Pressing `Ctrl+Z` does nothing.

**Solution:**
1. Check if `streamlit-keyup` is installed:
   ```bash
   pip install streamlit-keyup
   ```
2. Restart Streamlit app
3. Look for keyboard shortcuts field in UI

---

### OCR Not Available

**Issue:** OCR section shows installation message.

**Solution:**
1. Install OCR dependencies:
   ```bash
   # For local OCR
   pip install bates-labeler[ocr-local]

   # For cloud OCR
   pip install bates-labeler[ocr-cloud]
   ```

2. Install Tesseract binary (for local OCR):
   - See installation instructions above

3. Restart application

---

### OCR Extraction Failed

**Issue:** OCR returns empty text or errors.

**Possible Causes:**
1. **Poor scan quality**
   - Solution: Rescan at higher DPI (300+)

2. **Wrong language setting**
   - Solution: Set correct language code

3. **Missing Tesseract language data**
   - Solution: Install language pack

4. **Google Vision credentials invalid**
   - Solution: Check credentials JSON file

---

## Best Practices

### Undo/Redo
- Make frequent small changes to build granular history
- Review history counter before major changes
- Use `Ctrl+S` to save good configurations

### Keyboard Shortcuts
- Learn 3-4 most used shortcuts first
- Keep keyboard shortcut legend visible while learning
- Use shortcuts for repetitive actions

### OCR
- Test with one page before batch processing
- Use local OCR for privacy-sensitive documents
- Use cloud OCR for complex layouts or poor scans
- Verify extracted text quality before finalizing
- Consider OCR cost for cloud processing

---

## Performance Tips

### Large Batches (100+ PDFs)
- Disable OCR if text extraction not needed
- Process in smaller batches
- Use local OCR to avoid API rate limits

### Complex Documents
- Enable OCR only for scanned pages
- Use Google Vision for best accuracy
- Set `max_pages` limit for very large PDFs

### Configuration Management
- Export configurations (`Ctrl+S`) for reuse
- Create presets for common workflows
- Use undo/redo to refine settings iteratively

---

*For more information, see the main [README.md](../README.md) and [IMPLEMENTATION_NOTES_REMAINING_FEATURES.md](./IMPLEMENTATION_NOTES_REMAINING_FEATURES.md).*
