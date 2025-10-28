"""
Streamlit Web UI for Bates-Labeler
A user-friendly web interface for adding Bates numbers to PDF documents.
"""

import streamlit as st
import tempfile
import os
import zipfile
from pathlib import Path
from typing import List, Optional, Dict
from io import BytesIO

from bates_labeler import BatesNumberer, __version__
import json
import base64
from datetime import datetime

# Import keyboard shortcuts component
try:
    from st_keyup import st_keyup
    KEYUP_AVAILABLE = True
except ImportError:
    KEYUP_AVAILABLE = False
    print("Warning: streamlit-keyup not installed. Keyboard shortcuts will be disabled.")

# Import OCR module (optional)
try:
    from bates_labeler.ocr import OCRExtractor, OCRBackend
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR dependencies not installed. OCR features will be disabled.")

# Page configuration
st.set_page_config(
    page_title="Bates Numbering Tool",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Widen sidebar more */
    [data-testid="stSidebar"] {
        min-width: 420px;
        max-width: 420px;
    }
    
    /* Reduce sidebar padding */
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem 1.5rem 1rem 1.5rem;
    }
    
    /* Better form element sizing */
    .stTextInput > div > div > input {
        padding: 0.5rem 0.75rem;
        font-size: 0.95rem;
    }
    
    .stNumberInput > div > div > input {
        padding: 0.5rem 0.75rem;
        font-size: 0.95rem;
    }
    
    .stSelectbox > div > div > div {
        padding: 0.5rem 0.75rem;
        font-size: 0.95rem;
    }
    
    /* Ensure select boxes show full text */
    .stSelectbox {
        width: 100%;
    }
    
    /* Labels more compact */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    /* Better expander styling */
    .streamlit-expanderHeader {
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* Main content styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .preview-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        font-size: 1.1rem;
    }
    
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'cancel_requested' not in st.session_state:
        st.session_state.cancel_requested = False
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = ""
    if 'file_order' not in st.session_state:
        st.session_state.file_order = []
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    if 'current_config' not in st.session_state:
        st.session_state.current_config = {}
    if 'preview_file_index' not in st.session_state:
        st.session_state.preview_file_index = 0
    if 'file_progress' not in st.session_state:
        st.session_state.file_progress = {}
    if 'ai_analysis_results' not in st.session_state:
        st.session_state.ai_analysis_results = []
    if 'config_presets' not in st.session_state:
        st.session_state.config_presets = {
            'Default': {
                'prefix': '',
                'suffix': '',
                'start_number': 1,
                'padding': 4,
                'position': 'bottom-right'
            },
            'Legal Discovery': {
                'prefix': 'PLAINTIFF-PROD-',
                'suffix': '',
                'start_number': 1,
                'padding': 6,
                'position': 'bottom-right'
            },
            'Confidential': {
                'prefix': 'CONFIDENTIAL-',
                'suffix': '-AEO',
                'start_number': 1,
                'padding': 4,
                'position': 'top-center'
            },
            'Exhibit': {
                'prefix': 'EXHIBIT-',
                'suffix': '',
                'start_number': 101,
                'padding': 3,
                'position': 'top-right'
            }
        }

    # Initialize undo/redo state history (last 20 states)
    if 'state_history' not in st.session_state:
        st.session_state.state_history = []
    if 'state_history_index' not in st.session_state:
        st.session_state.state_history_index = -1
    if 'keyboard_command' not in st.session_state:
        st.session_state.keyboard_command = None


def save_state_to_history(config_state: dict):
    """
    Save current configuration state to history for undo/redo.

    Args:
        config_state: Dictionary containing all configuration values
    """
    # Remove any states after current index (when user made changes after undo)
    if st.session_state.state_history_index < len(st.session_state.state_history) - 1:
        st.session_state.state_history = st.session_state.state_history[:st.session_state.state_history_index + 1]

    # Add new state
    st.session_state.state_history.append(config_state.copy())

    # Limit to last 20 states
    if len(st.session_state.state_history) > 20:
        st.session_state.state_history = st.session_state.state_history[-20:]

    # Update index to point to latest state
    st.session_state.state_history_index = len(st.session_state.state_history) - 1


def undo_state():
    """Undo to previous configuration state."""
    if st.session_state.state_history_index > 0:
        st.session_state.state_history_index -= 1
        return st.session_state.state_history[st.session_state.state_history_index]
    return None


def redo_state():
    """Redo to next configuration state."""
    if st.session_state.state_history_index < len(st.session_state.state_history) - 1:
        st.session_state.state_history_index += 1
        return st.session_state.state_history[st.session_state.state_history_index]
    return None


def can_undo() -> bool:
    """Check if undo is available."""
    return st.session_state.state_history_index > 0


def can_redo() -> bool:
    """Check if redo is available."""
    return st.session_state.state_history_index < len(st.session_state.state_history) - 1


def handle_keyboard_shortcuts():
    """
    Handle keyboard shortcuts using streamlit-keyup.

    Shortcuts:
    - Ctrl+Z: Undo
    - Ctrl+Y: Redo
    - Ctrl+P: Process PDFs
    - Ctrl+S: Save configuration
    - Ctrl+D: Download files
    - Ctrl+R: Reset settings
    """
    if not KEYUP_AVAILABLE:
        return None

    # Hidden input field to capture keyboard events
    shortcut = st_keyup("", key="keyboard_shortcuts", placeholder="Press keyboard shortcuts...")

    # Parse keyboard shortcuts (streamlit-keyup returns the key pressed)
    if shortcut:
        # Store command in session state for processing
        if shortcut == "ctrl+z":
            return "undo"
        elif shortcut == "ctrl+y":
            return "redo"
        elif shortcut == "ctrl+p":
            return "process"
        elif shortcut == "ctrl+s":
            return "save"
        elif shortcut == "ctrl+d":
            return "download"
        elif shortcut == "ctrl+r":
            return "reset"

    return None


def generate_preview(prefix: str, start_number: int, padding: int, suffix: str) -> str:
    """Generate a preview of the Bates number format."""
    number_str = str(start_number).zfill(padding)
    return f"{prefix}{number_str}{suffix}"


def save_config_to_history(config: dict, name: str = None):
    """Save current configuration to processing history."""
    if name is None:
        name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    history_entry = {
        'name': name,
        'timestamp': datetime.now().isoformat(),
        'config': config.copy()
    }

    # Add to history (keep last 10 entries)
    st.session_state.processing_history.insert(0, history_entry)
    if len(st.session_state.processing_history) > 10:
        st.session_state.processing_history = st.session_state.processing_history[:10]


def load_config_from_history(history_entry: dict):
    """Load configuration from history entry."""
    return history_entry['config'].copy()


def export_config_as_json(config: dict) -> str:
    """Export configuration as JSON string."""
    # Filter out non-serializable items (like functions)
    serializable_config = {
        k: v for k, v in config.items() 
        if not callable(v) and k not in ['status_callback', 'cancel_callback']
    }
    return json.dumps(serializable_config, indent=2)


def import_config_from_json(json_str: str) -> dict:
    """Import configuration from JSON string."""
    try:
        config = json.loads(json_str)
        # Validate that it's a dictionary
        if not isinstance(config, dict):
            return None
        return config
    except json.JSONDecodeError as e:
        return None


def render_pdf_preview(uploaded_file, page_num: int = 0):
    """Render a preview of a PDF page using PyPDF."""
    try:
        from pypdf import PdfReader
        import io

        # Read PDF
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))

        # Reset file pointer for later use
        uploaded_file.seek(0)

        total_pages = len(pdf_reader.pages)

        if page_num >= total_pages:
            page_num = 0

        # Get page info
        page = pdf_reader.pages[page_num]

        # Extract page dimensions
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)

        # Display page info
        st.markdown(f"""
        **Page {page_num + 1} of {total_pages}**
        Size: {width:.0f} x {height:.0f} pts
        Orientation: {"Portrait" if height > width else "Landscape"}
        """)

        # Extract text preview (first 500 chars)
        text = page.extract_text()[:500]
        if text.strip():
            with st.expander("Text Preview", expanded=False):
                st.text(text)

        return total_pages

    except Exception as e:
        st.error(f"Error rendering preview: {str(e)}")
        return 0


def reorder_files_ui(uploaded_files):
    """UI component for drag-and-drop file reordering."""
    if not uploaded_files or len(uploaded_files) <= 1:
        return uploaded_files

    st.markdown("##### 📋 File Processing Order")
    st.markdown("*Reorder files by selecting and using arrows below*")

    # Initialize file order if needed
    if len(st.session_state.file_order) != len(uploaded_files):
        st.session_state.file_order = list(range(len(uploaded_files)))

    # Create ordered list based on current order
    ordered_files = [uploaded_files[i] for i in st.session_state.file_order]

    # Display files with reorder controls
    for idx, file_idx in enumerate(st.session_state.file_order):
        file = uploaded_files[file_idx]
        col1, col2, col3, col4 = st.columns([0.5, 3, 0.5, 0.5])

        with col1:
            st.markdown(f"**{idx + 1}.**")

        with col2:
            st.markdown(f"{file.name} ({file.size / 1024:.1f} KB)")

        with col3:
            # Move up button
            if idx > 0:
                if st.button("⬆", key=f"up_{idx}_{file_idx}"):
                    # Swap with previous
                    st.session_state.file_order[idx], st.session_state.file_order[idx - 1] = \
                        st.session_state.file_order[idx - 1], st.session_state.file_order[idx]
                    st.rerun()

        with col4:
            # Move down button
            if idx < len(st.session_state.file_order) - 1:
                if st.button("⬇", key=f"down_{idx}_{file_idx}"):
                    # Swap with next
                    st.session_state.file_order[idx], st.session_state.file_order[idx + 1] = \
                        st.session_state.file_order[idx + 1], st.session_state.file_order[idx]
                    st.rerun()

    return ordered_files


def process_pdf(uploaded_file, config: dict, add_separator: bool = False, return_metadata: bool = False, numberer=None):
    """Process a single PDF file with Bates numbering."""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            tmp_input.write(uploaded_file.read())
            tmp_input_path = tmp_input.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='_bates.pdf') as tmp_output:
            tmp_output_path = tmp_output.name
        
        # Create BatesNumberer instance if not provided
        if numberer is None:
            numberer = BatesNumberer(**config)
        
        # Process the PDF
        result = numberer.process_pdf(
            tmp_input_path,
            tmp_output_path,
            add_separator=add_separator,
            return_metadata=return_metadata
        )
        
        if return_metadata:
            if result['success']:
                # Read the processed file
                with open(tmp_output_path, 'rb') as f:
                    output_data = f.read()
                
                # Clean up temporary files
                os.unlink(tmp_input_path)
                os.unlink(tmp_output_path)
                
                result['data'] = output_data
                return result
            else:
                # Clean up temporary files
                os.unlink(tmp_input_path)
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
                return result
        else:
            # Original behavior for backwards compatibility
            if result:
                # Read the processed file
                with open(tmp_output_path, 'rb') as f:
                    output_data = f.read()
                
                # Clean up temporary files
                os.unlink(tmp_input_path)
                os.unlink(tmp_output_path)
                
                return output_data
            else:
                # Clean up temporary files
                os.unlink(tmp_input_path)
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
                return None
            
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None if not return_metadata else {'success': False, 'data': None}


def process_combined_pdfs(uploaded_files, config: dict, add_document_separators: bool = False, add_index_page: bool = False):
    """Process and combine multiple PDFs into a single file."""
    try:
        # Create temporary input files
        temp_files = []
        for uploaded_file in uploaded_files:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            tmp_file.write(uploaded_file.read())
            tmp_file.close()
            temp_files.append(tmp_file.name)
        
        # Create temporary output file
        tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix='_combined_bates.pdf')
        tmp_output_path = tmp_output.name
        tmp_output.close()
        
        # Create BatesNumberer instance
        numberer = BatesNumberer(**config)
        
        # Combine and process PDFs
        result = numberer.combine_and_process_pdfs(
            temp_files,
            tmp_output_path,
            add_document_separators=add_document_separators,
            add_index_page=add_index_page
        )
        
        # Clean up temporary input files
        for temp_file in temp_files:
            os.unlink(temp_file)
        
        if result['success']:
            # Read the combined file
            with open(tmp_output_path, 'rb') as f:
                output_data = f.read()
            
            # Clean up temporary output file
            os.unlink(tmp_output_path)
            
            result['data'] = output_data
            return result
        else:
            # Clean up temporary output file
            if os.path.exists(tmp_output_path):
                os.unlink(tmp_output_path)
            return result
            
    except Exception as e:
        st.error(f"Error combining PDFs: {str(e)}")
        return {'success': False, 'data': None}


def process_with_bates_filenames(uploaded_files, config: dict, add_separator: bool = False):
    """Process multiple PDFs with Bates number filenames and generate mappings."""
    try:
        processed_files = []
        mappings = []
        
        # Create a single BatesNumberer instance to maintain continuous numbering
        numberer = BatesNumberer(**config)
        
        for uploaded_file in uploaded_files:
            # Process with metadata, passing the shared numberer instance
            result = process_pdf(uploaded_file, config, add_separator, return_metadata=True, numberer=numberer)
            
            if result and result['success']:
                # Generate new filename from first Bates number
                new_filename = f"{result['first_bates']}.pdf"
                
                processed_files.append({
                    'name': new_filename,
                    'data': result['data']
                })
                
                mappings.append({
                    'original_filename': uploaded_file.name,
                    'new_filename': new_filename,
                    'first_bates': result['first_bates'],
                    'last_bates': result['last_bates'],
                    'page_count': result['page_count']
                })
        
        # Generate mapping files
        csv_data = None
        pdf_data = None
        
        if mappings:
            # Reuse the same numberer instance for mapping generation
            
            # Generate CSV mapping
            csv_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            csv_tmp.close()
            if numberer.generate_filename_mapping_csv(mappings, csv_tmp.name):
                with open(csv_tmp.name, 'rb') as f:
                    csv_data = f.read()
            os.unlink(csv_tmp.name)
            
            # Generate PDF mapping
            pdf_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            pdf_tmp.close()
            if numberer.generate_filename_mapping_pdf(mappings, pdf_tmp.name):
                with open(pdf_tmp.name, 'rb') as f:
                    pdf_data = f.read()
            os.unlink(pdf_tmp.name)
        
        return {
            'success': len(processed_files) > 0,
            'files': processed_files,
            'csv_mapping': csv_data,
            'pdf_mapping': pdf_data
        }
        
    except Exception as e:
        st.error(f"Error processing with Bates filenames: {str(e)}")
        return {'success': False, 'files': [], 'csv_mapping': None, 'pdf_mapping': None}


def create_zip_archive(files_list: List[Dict]) -> bytes:
    """
    Create a ZIP archive containing all processed files.
    
    Args:
        files_list: List of dicts with 'name' and 'data' keys
        
    Returns:
        ZIP file as bytes
    """
    try:
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_info in files_list:
                zip_file.writestr(file_info['name'], file_info['data'])
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error creating ZIP archive: {str(e)}")
        return None


def main():
    """Main application function."""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">📄 Bates Numbering Tool</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sub-header">Professional Bates numbering for legal documents • Version {__version__}</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Undo/Redo buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("↶ Undo", disabled=not can_undo(), use_container_width=True, help="Undo last change (Ctrl+Z)"):
                restored_state = undo_state()
                if restored_state:
                    st.session_state.current_config = restored_state
                    st.success("Undone!")
                    st.rerun()
        with col2:
            if st.button("↷ Redo", disabled=not can_redo(), use_container_width=True, help="Redo last undone change (Ctrl+Y)"):
                restored_state = redo_state()
                if restored_state:
                    st.session_state.current_config = restored_state
                    st.success("Redone!")
                    st.rerun()
        with col3:
            st.caption(f"History: {st.session_state.state_history_index + 1}/{len(st.session_state.state_history)}")

        st.divider()

        # Keyboard shortcuts legend
        with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
            if KEYUP_AVAILABLE:
                st.markdown("""
                **Available Shortcuts:**
                - `Ctrl+Z` - Undo
                - `Ctrl+Y` - Redo
                - `Ctrl+P` - Process PDFs
                - `Ctrl+S` - Save Configuration
                - `Ctrl+D` - Download Files
                - `Ctrl+R` - Reset Settings
                """)
            else:
                st.warning("Install `streamlit-keyup` to enable keyboard shortcuts: `pip install streamlit-keyup`")

        st.divider()

        # Configuration presets
        preset = st.selectbox(
            "Configuration Preset",
            options=list(st.session_state.config_presets.keys()),
            help="Select a pre-configured template or use Default for custom settings"
        )

        if preset != 'Default':
            preset_config = st.session_state.config_presets[preset]
            st.info(f"Using **{preset}** preset. Modify settings below to customize.")
        else:
            preset_config = st.session_state.config_presets['Default']

        # Processing History - Load previous configurations
        with st.expander("📚 Processing History", expanded=False):
            if st.session_state.processing_history:
                st.markdown("**Recent Configurations:**")
                for i, entry in enumerate(st.session_state.processing_history):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text(f"{entry['name']}")
                        st.caption(f"{entry['timestamp'][:19]}")
                    with col2:
                        if st.button("Load", key=f"load_history_{i}"):
                            # Load this configuration
                            loaded_config = load_config_from_history(entry)
                            st.session_state.current_config = loaded_config
                            st.success(f"Loaded: {entry['name']}")
                            st.rerun()
            else:
                st.info("No processing history yet. Configurations will be saved automatically after processing.")

            st.divider()

            # Export/Import configuration
            st.markdown("**Export/Import Configuration:**")

            # Export current config
            if st.session_state.current_config:
                config_json = export_config_as_json(st.session_state.current_config)
                st.download_button(
                    label="📤 Export Config (JSON)",
                    data=config_json,
                    file_name=f"bates_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

            # Import config
            uploaded_config = st.file_uploader(
                "📥 Import Config (JSON)",
                type=['json'],
                help="Upload a previously exported configuration file"
            )

            if uploaded_config:
                try:
                    # Check file extension
                    if not uploaded_config.name.endswith('.json'):
                        st.error("❌ Invalid file type. Only JSON files (.json) are supported for configuration import.")
                    else:
                        config_str = uploaded_config.read().decode('utf-8')
                        imported_config = import_config_from_json(config_str)
                        if imported_config:
                            st.session_state.current_config = imported_config
                            st.success("✅ Configuration imported successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid JSON format. Please ensure the file contains valid JSON with configuration keys. See docs/example_config.json for the correct format.")
                except UnicodeDecodeError:
                    st.error("❌ Unable to read file. Please ensure it's a text-based JSON file, not a binary file.")
                except Exception as e:
                    st.error(f"❌ Error importing configuration: {str(e)}\n\nPlease check that your file is a valid JSON configuration file. See docs/example_config.json for an example.")

        st.divider()
        
        # Basic Settings - Always visible
        st.subheader("📝 Basic Settings")
        
        prefix = st.text_input(
            "Bates Prefix",
            value=preset_config['prefix'],
            help="Text to appear before the number (e.g., 'CASE123-')"
        )
        
        suffix = st.text_input(
            "Bates Suffix",
            value=preset_config['suffix'],
            help="Text to appear after the number (e.g., '-CONF')"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            start_number = st.number_input(
                "Start Number",
                min_value=1,
                value=preset_config['start_number'],
                help="First Bates number to use"
            )
        with col2:
            padding = st.number_input(
                "Padding",
                min_value=1,
                max_value=10,
                value=preset_config['padding'],
                help="Number of digits (e.g., 4 = '0001')"
            )
        
        st.divider()
        
        # Output Options - Always visible
        st.subheader("📑 Output Options")
        
        # Add Separator Page
        add_separator = st.checkbox(
            "Add Separator Page",
            help="Add a page at the beginning showing Bates range"
        )
        
        # Border settings for separator pages (nested option)
        if add_separator:
            st.markdown("##### Border Settings")
            
            enable_border = st.checkbox(
                "Enable Border on Separator Page",
                help="Add decorative border to separator page"
            )
            
            if enable_border:
                col1, col2 = st.columns(2)
                with col1:
                    border_style = st.selectbox(
                        "Border Style",
                        options=['solid', 'dashed', 'double', 'asterisks'],
                        format_func=lambda x: x.capitalize(),
                        help="Style of border"
                    )
                with col2:
                    border_color = st.selectbox(
                        "Border Color",
                        options=['black', 'blue', 'red', 'green', 'gray'],
                        help="Color of border"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    border_width = st.slider(
                        "Border Width",
                        min_value=1.0,
                        max_value=10.0,
                        value=2.0,
                        step=0.5,
                        help="Width of border in points"
                    )
                with col2:
                    if border_style in ['solid', 'dashed', 'double']:
                        border_corner_radius = st.slider(
                            "Corner Radius",
                            min_value=0.0,
                            max_value=20.0,
                            value=0.0,
                            step=1.0,
                            help="Radius for rounded corners (0 for sharp corners)"
                        )
                    else:
                        border_corner_radius = 0.0
            else:
                border_style = "solid"
                border_color = "black"
                border_width = 2.0
                border_corner_radius = 0.0
        else:
            # Set defaults when separator page is not enabled
            enable_border = False
            border_style = "solid"
            border_color = "black"
            border_width = 2.0
            border_corner_radius = 0.0
        
        # Combine PDFs option
        combine_pdfs = st.checkbox(
            "Combine All PDFs into Single File",
            help="Merge all uploaded PDFs into one output file with continuous Bates numbering"
        )
        
        if combine_pdfs:
            add_document_separators = st.checkbox(
                "Insert Separator Pages Between Documents",
                value=True,
                help="Add separator pages showing Bates range for each document"
            )
            add_index_page = st.checkbox(
                "Generate Index Page",
                value=False,
                help="Add an index page at the beginning listing all documents with their Bates ranges"
            )
        else:
            add_document_separators = False
            add_index_page = False
        
        # Bates filename option
        use_bates_filenames = st.checkbox(
            "Use Bates Number as Filename",
            help="Name output files with their first Bates number (e.g., CASE-0001.pdf)"
        )
        
        if use_bates_filenames:
            st.info("📊 Will generate CSV and PDF mapping files")
        
        st.divider()
        
        # Position & Appearance - Collapsible
        with st.expander("🎨 Position & Appearance", expanded=True):
            position = st.selectbox(
                "Position",
                options=['top-left', 'top-center', 'top-right', 
                        'bottom-left', 'bottom-center', 'bottom-right', 'center'],
                index=['top-left', 'top-center', 'top-right', 
                       'bottom-left', 'bottom-center', 'bottom-right', 'center'].index(preset_config['position']),
                help="Where to place the Bates number on the page"
            )
            
            # Custom font upload
            custom_font = st.file_uploader(
                "Upload Custom Font (optional)",
                type=['ttf', 'otf'],
                help="Upload a TrueType (.ttf) or OpenType (.otf) font file. If uploaded, this will override the font selection below."
            )
            
            if custom_font:
                st.info(f"✅ Custom font loaded: {custom_font.name}")
                font_name = "Helvetica"  # Default for config, will be overridden
            else:
                font_name = st.selectbox(
                    "Font",
                    options=['Helvetica', 'Times-Roman', 'Courier'],
                    help="Font family for Bates numbers"
                )
            
            font_size = st.slider(
                "Font Size",
                min_value=6,
                max_value=24,
                value=12,
                help="Size of the Bates number text"
            )
            
            font_color = st.selectbox(
                "Color",
                options=['black', 'blue', 'red', 'green', 'gray'],
                help="Color of the Bates number"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                bold = st.checkbox("Bold", value=True)
            with col2:
                italic = st.checkbox("Italic", value=False)
        
        # Logo Upload - Collapsible
        with st.expander("🖼️ Logo Upload", expanded=False):
            logo_file = st.file_uploader(
                "Upload Logo",
                type=['svg', 'png', 'jpg', 'jpeg', 'webp'],
                help="Upload a logo image (SVG, PNG, JPG, WEBP)"
            )
            
            if logo_file:
                st.success(f"✅ Logo loaded: {logo_file.name}")
                
                logo_placement = st.selectbox(
                    "Logo Placement",
                    options=['above_bates', 'top-left', 'top-center', 'top-right', 
                            'bottom-left', 'bottom-center', 'bottom-right'],
                    help="Where to place the logo on separator pages"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    logo_max_width = st.slider(
                        "Max Width (in)",
                        min_value=0.5,
                        max_value=3.0,
                        value=2.0,
                        step=0.1,
                        help="Maximum logo width in inches"
                    )
                with col2:
                    logo_max_height = st.slider(
                        "Max Height (in)",
                        min_value=0.5,
                        max_value=3.0,
                        value=2.0,
                        step=0.1,
                        help="Maximum logo height in inches"
                    )
            else:
                logo_placement = "above_bates"
                logo_max_width = 2.0
                logo_max_height = 2.0
        
        # QR Code Settings - Collapsible
        with st.expander("📱 QR Code Settings", expanded=False):
            enable_qr = st.checkbox(
                "Enable QR Codes",
                help="Generate QR codes containing Bates numbers"
            )
            
            if enable_qr:
                qr_placement = st.selectbox(
                    "QR Placement",
                    options=['all_pages', 'separator_only'],
                    format_func=lambda x: 'All Pages' if x == 'all_pages' else 'Separator Pages Only',
                    help="Where to place QR codes"
                )
                
                qr_position = st.selectbox(
                    "QR Position",
                    options=['top-left', 'top-center', 'top-right', 
                            'bottom-left', 'bottom-center', 'bottom-right'],
                    index=3,  # Default to bottom-left
                    help="Position of QR code on page"
                )
                
                qr_size = st.slider(
                    "QR Size (inches)",
                    min_value=0.06,
                    max_value=0.24,
                    value=0.12,
                    step=0.01,
                    help="Size of QR code (12% of original range)"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    qr_color = st.selectbox(
                        "QR Color",
                        options=['black', 'blue', 'red', 'green'],
                        help="Fill color of QR code"
                    )
                with col2:
                    qr_background_color = st.selectbox(
                        "QR Background",
                        options=['white', 'gray', 'black'],
                        help="Background color of QR code"
                    )
            else:
                qr_placement = "disabled"
                qr_position = "bottom-left"
                qr_size = 0.12
                qr_color = "black"
                qr_background_color = "white"
        
        # Watermark Settings - Collapsible
        with st.expander("💧 Watermark Settings", expanded=False):
            enable_watermark = st.checkbox(
                "Enable Watermark",
                help="Add watermark text to pages"
            )
            
            if enable_watermark:
                watermark_text = st.text_input(
                    "Watermark Text",
                    value="CONFIDENTIAL",
                    help="Text to display as watermark"
                )
                
                watermark_scope = st.selectbox(
                    "Watermark Scope",
                    options=['all_pages', 'document_only'],
                    format_func=lambda x: 'All Pages' if x == 'all_pages' else 'Document Pages Only',
                    help="Where to apply watermark"
                )
                
                watermark_opacity = st.slider(
                    "Opacity (%)",
                    min_value=0,
                    max_value=100,
                    value=30,
                    step=5,
                    help="Transparency of watermark (0=invisible, 100=opaque)"
                ) / 100.0
                
                watermark_rotation = st.slider(
                    "Rotation (degrees)",
                    min_value=0,
                    max_value=360,
                    value=45,
                    step=5,
                    help="Rotation angle of watermark text"
                )
                
                watermark_position = st.selectbox(
                    "Position",
                    options=['center', 'top-left', 'top-center', 'top-right', 
                            'bottom-left', 'bottom-center', 'bottom-right'],
                    help="Position of watermark"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    watermark_font_size = st.slider(
                        "Font Size",
                        min_value=24,
                        max_value=120,
                        value=72,
                        step=6,
                        help="Size of watermark text"
                    )
                with col2:
                    watermark_color = st.selectbox(
                        "Color",
                        options=['gray', 'black', 'red', 'blue'],
                        help="Color of watermark"
                    )
            else:
                watermark_text = "CONFIDENTIAL"
                watermark_scope = "disabled"
                watermark_opacity = 0.3
                watermark_rotation = 45
                watermark_position = "center"
                watermark_font_size = 72
                watermark_color = "gray"
        
        # Advanced Options - Collapsible
        with st.expander("⚙️ Advanced Options", expanded=False):
            include_date = st.checkbox(
                "Include Date Stamp",
                help="Add date/time below Bates number"
            )

            if include_date:
                date_format = st.text_input(
                    "Date Format",
                    value="%Y-%m-%d",
                    help="Python date format string (e.g., %Y-%m-%d for 2023-12-31)"
                )
            else:
                date_format = "%Y-%m-%d"

            add_background = st.checkbox(
                "White Background",
                value=True,
                help="Add white background behind text for better visibility"
            )

            if add_background:
                background_padding = st.slider(
                    "Background Padding",
                    min_value=0,
                    max_value=10,
                    value=3,
                    help="Padding around text background in pixels"
                )
            else:
                background_padding = 3

            st.divider()

            # OCR Settings
            if OCR_AVAILABLE:
                st.markdown("##### 🔍 OCR Text Extraction")
                enable_ocr = st.checkbox(
                    "Enable OCR",
                    help="Extract text from scanned PDFs and embed as metadata"
                )

                if enable_ocr:
                    ocr_backend = st.selectbox(
                        "OCR Backend",
                        options=["pytesseract", "google_vision"],
                        format_func=lambda x: "Local (Pytesseract - Privacy First)" if x == "pytesseract" else "Cloud (Google Vision - Premium)",
                        help="Choose OCR backend: Local (free, private) or Cloud (premium, high accuracy)"
                    )

                    if ocr_backend == "google_vision":
                        google_credentials = st.file_uploader(
                            "Google Cloud Credentials (JSON)",
                            type=['json'],
                            help="Upload your Google Cloud Vision API credentials file"
                        )
                    else:
                        google_credentials = None

                    ocr_language = st.text_input(
                        "OCR Language",
                        value="eng",
                        help="Language code (e.g., 'eng' for English, 'spa' for Spanish)"
                    )
                else:
                    ocr_backend = None
                    google_credentials = None
                    ocr_language = "eng"
            else:
                st.info("📦 OCR features not installed. Install with:\n`pip install bates-labeler[ocr-local]` or `pip install bates-labeler[ocr-cloud]`")
                enable_ocr = False
                ocr_backend = None
                google_credentials = None
                ocr_language = "eng"

            st.divider()

            # AI Document Analysis Settings
            st.markdown("##### 🤖 AI Document Analysis")
            enable_ai_analysis = st.checkbox(
                "Enable AI Analysis",
                help="Use AI to analyze documents for discrimination patterns, problematic content, and metadata extraction"
            )

            if enable_ai_analysis:
                ai_provider = st.selectbox(
                    "AI Provider",
                    options=["OpenRouter", "Google Cloud", "Anthropic"],
                    help="Select your preferred AI provider for document analysis"
                )

                ai_api_key = st.text_input(
                    "API Key",
                    type="password",
                    help=f"Enter your {ai_provider} API key (kept secure and not stored)"
                )

                st.markdown("**Analysis Options:**")

                ai_detect_discrimination = st.checkbox(
                    "Detect Discrimination Patterns",
                    value=True,
                    help="Identify potential discriminatory language or content"
                )

                ai_identify_problematic = st.checkbox(
                    "Identify Problematic Content",
                    value=True,
                    help="Flag potentially sensitive, inappropriate, or legally concerning content"
                )

                ai_extract_metadata = st.checkbox(
                    "Extract Metadata",
                    value=True,
                    help="Extract document metadata, key entities, and important information"
                )

                if not ai_api_key:
                    st.warning("⚠️ Please enter an API key to enable AI analysis")
            else:
                ai_provider = None
                ai_api_key = None
                ai_detect_discrimination = False
                ai_identify_problematic = False
                ai_extract_metadata = False

        # Save current configuration state to history (at end of sidebar config)
        current_state = {
            'prefix': prefix,
            'suffix': suffix,
            'start_number': start_number,
            'padding': padding,
            'position': position,
            'font_name': font_name,
            'font_size': font_size,
            'font_color': font_color,
            'bold': bold,
            'italic': italic,
            'enable_ai_analysis': enable_ai_analysis,
            'ai_provider': ai_provider if enable_ai_analysis else None,
            'ai_detect_discrimination': ai_detect_discrimination,
            'ai_identify_problematic': ai_identify_problematic,
            'ai_extract_metadata': ai_extract_metadata,
            'timestamp': datetime.now().isoformat()
        }

        # Check if state has changed (compare with last saved state)
        if (not st.session_state.state_history or
            current_state != st.session_state.state_history[st.session_state.state_history_index]):
            # Only save if there's an actual change
            if st.session_state.state_history:
                last_state = st.session_state.state_history[st.session_state.state_history_index]
                # Compare without timestamp
                last_state_copy = {k: v for k, v in last_state.items() if k != 'timestamp'}
                current_state_copy = {k: v for k, v in current_state.items() if k != 'timestamp'}
                if last_state_copy != current_state_copy:
                    save_state_to_history(current_state)
            else:
                # First state
                save_state_to_history(current_state)

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📤 Upload PDF Files")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose PDF file(s)",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload one or more PDF files to add Bates numbers"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

            # File reordering UI (for multiple files)
            if len(uploaded_files) > 1:
                with st.expander("📋 Uploaded Files - Reorder Processing Order", expanded=True):
                    uploaded_files = reorder_files_ui(uploaded_files)
            else:
                # Display single file
                with st.expander("📋 Uploaded Files", expanded=True):
                    st.text(f"1. {uploaded_files[0].name} ({uploaded_files[0].size / 1024:.1f} KB)")
    
    with col2:
        st.subheader("👁️ Preview")

        # Generate and display Bates number preview
        preview = generate_preview(prefix, start_number, padding, suffix)

        st.markdown(f"""
        <div class="preview-box">
            <strong>Bates Number Format:</strong><br>
            <span style="font-size: 1.5rem; font-family: monospace;">{preview}</span><br>
            <small style="color: #666;">Next: {generate_preview(prefix, start_number + 1, padding, suffix)}</small>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**Position:** {position}")
        st.markdown(f"**Font:** {font_name} {font_size}pt")
        st.markdown(f"**Color:** {font_color}")
        if bold or italic:
            style = []
            if bold:
                style.append("Bold")
            if italic:
                style.append("Italic")
            st.markdown(f"**Style:** {', '.join(style)}")

        # PDF Page Preview (if files uploaded)
        if uploaded_files:
            st.divider()
            st.markdown("##### 📄 PDF Preview")

            # File selector for preview
            if len(uploaded_files) > 1:
                preview_file = st.selectbox(
                    "Select file to preview",
                    options=range(len(uploaded_files)),
                    format_func=lambda i: uploaded_files[i].name,
                    key="preview_file_selector"
                )
            else:
                preview_file = 0

            # Page navigation
            file_to_preview = uploaded_files[preview_file]
            total_pages = render_pdf_preview(file_to_preview, st.session_state.preview_file_index)

            if total_pages > 1:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if st.button("◀ Prev", disabled=st.session_state.preview_file_index == 0):
                        st.session_state.preview_file_index -= 1
                        st.rerun()
                with col2:
                    st.markdown(f"<center>Page {st.session_state.preview_file_index + 1} / {total_pages}</center>", unsafe_allow_html=True)
                with col3:
                    if st.button("Next ▶", disabled=st.session_state.preview_file_index >= total_pages - 1):
                        st.session_state.preview_file_index += 1
                        st.rerun()
    
    st.divider()
    
    # Process button
    if uploaded_files:
        if st.button("🚀 Process PDF(s)", type="primary", use_container_width=True):
            # Reset cancel flag
            st.session_state.cancel_requested = False
            
            # Handle custom font if uploaded
            custom_font_path = None
            if custom_font:
                # Save custom font to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(custom_font.name)[1]) as tmp_font:
                    tmp_font.write(custom_font.read())
                    custom_font_path = tmp_font.name
            
            # Handle logo if uploaded
            logo_path = None
            if logo_file:
                # Save logo to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(logo_file.name)[1]) as tmp_logo:
                    tmp_logo.write(logo_file.read())
                    logo_path = tmp_logo.name
            
            # Create status display containers
            status_container = st.empty()
            progress_container = st.empty()
            cancel_container = st.empty()
            
            # Status callback function with per-file progress tracking
            def status_callback(message, progress_dict=None):
                st.session_state.processing_status = message
                status_container.info(f"⚙️ {message}")

                # Update overall progress
                if progress_dict and 'current' in progress_dict and 'total' in progress_dict:
                    overall_progress = progress_dict['current'] / progress_dict['total']
                    progress_container.progress(overall_progress)

                    # Track individual file progress
                    if 'file_name' in progress_dict:
                        st.session_state.file_progress[progress_dict['file_name']] = {
                            'status': 'processing',
                            'progress': progress_dict.get('file_progress', 0)
                        }
            
            # Cancel callback function  
            def cancel_callback():
                return st.session_state.cancel_requested
            
            # Add cancel button
            if cancel_container.button("❌ Cancel Processing", key="cancel_btn"):
                st.session_state.cancel_requested = True
                status_container.warning("⚠️ Cancellation requested...")
            
            # Initialize file progress tracking
            st.session_state.file_progress = {}
            for file in uploaded_files:
                st.session_state.file_progress[file.name] = {
                    'status': 'pending',
                    'progress': 0
                }

            # Build configuration for BatesNumberer (constructor parameters only)
            numberer_config = {
                'prefix': prefix,
                'suffix': suffix,
                'start_number': start_number,
                'padding': padding,
                'position': position,
                'font_name': font_name,
                'font_size': font_size,
                'font_color': font_color,
                'bold': bold,
                'italic': italic,
                'include_date': include_date,
                'date_format': date_format,
                'add_background': add_background,
                'background_padding': background_padding,
                'custom_font_path': custom_font_path,
                # Logo settings
                'logo_path': logo_path,
                'logo_placement': logo_placement,
                'logo_max_width': logo_max_width,
                'logo_max_height': logo_max_height,
                # QR code settings
                'enable_qr': enable_qr,
                'qr_placement': qr_placement,
                'qr_position': qr_position,
                'qr_size': qr_size,
                'qr_color': qr_color,
                'qr_background_color': qr_background_color,
                # Border settings
                'enable_border': enable_border,
                'border_style': border_style,
                'border_color': border_color,
                'border_width': border_width,
                'border_corner_radius': border_corner_radius,
                # Watermark settings
                'enable_watermark': enable_watermark,
                'watermark_text': watermark_text,
                'watermark_scope': watermark_scope,
                'watermark_opacity': watermark_opacity,
                'watermark_rotation': watermark_rotation,
                'watermark_position': watermark_position,
                'watermark_font_size': watermark_font_size,
                'watermark_color': watermark_color,
                # Callback functions
                'status_callback': status_callback,
                'cancel_callback': cancel_callback
            }
            
            # Process files based on selected options (hide default progress bar)
            status_callback("Starting processing...")

            st.session_state.processed_files = []
            st.session_state.ai_analysis_results = []

            # AI Analysis placeholder (will be implemented by AI integration task)
            if enable_ai_analysis and ai_api_key:
                status_callback("🤖 AI analysis will be performed after PDF processing...")
                st.info("🤖 AI Document Analysis is enabled and will analyze processed documents")
            
            # Option 1: Combine PDFs
            if combine_pdfs:
                status_callback("Combining and processing PDFs...")
                result = process_combined_pdfs(uploaded_files, numberer_config, add_document_separators, add_index_page)
                
                if result['success']:
                    # Generate combined filename
                    if result['documents']:
                        first_bates = result['documents'][0]['first_bates']
                        last_bates = result['documents'][-1]['last_bates']
                        
                        if use_bates_filenames:
                            combined_filename = f"{first_bates}_to_{last_bates}.pdf"
                        else:
                            combined_filename = "combined_bates.pdf"
                        
                        st.session_state.processed_files.append({
                            'name': combined_filename,
                            'data': result['data']
                        })
                        
                        # Generate mappings if Bates filenames is enabled
                        if use_bates_filenames:
                            numberer = BatesNumberer(**numberer_config)
                            
                            # Generate CSV mapping
                            csv_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
                            csv_tmp.close()
                            if numberer.generate_filename_mapping_csv(result['documents'], csv_tmp.name):
                                with open(csv_tmp.name, 'rb') as f:
                                    st.session_state.processed_files.append({
                                        'name': 'bates_mapping.csv',
                                        'data': f.read()
                                    })
                            os.unlink(csv_tmp.name)
                            
                            # Generate PDF mapping
                            pdf_tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                            pdf_tmp.close()
                            if numberer.generate_filename_mapping_pdf(result['documents'], pdf_tmp.name):
                                with open(pdf_tmp.name, 'rb') as f:
                                    st.session_state.processed_files.append({
                                        'name': 'bates_mapping.pdf',
                                        'data': f.read()
                                    })
                            os.unlink(pdf_tmp.name)
                
                status_callback("Processing complete!")
                progress_container.progress(1.0)
            
            # Option 2: Bates filenames (without combine)
            elif use_bates_filenames:
                status_callback("Processing with Bates number filenames...")
                result = process_with_bates_filenames(uploaded_files, numberer_config, add_separator)
                
                if result['success']:
                    # Add processed files
                    st.session_state.processed_files.extend(result['files'])
                    
                    # Add mapping files
                    if result['csv_mapping']:
                        st.session_state.processed_files.append({
                            'name': 'bates_mapping.csv',
                            'data': result['csv_mapping']
                        })
                    
                    if result['pdf_mapping']:
                        st.session_state.processed_files.append({
                            'name': 'bates_mapping.pdf',
                            'data': result['pdf_mapping']
                        })
                
                status_callback("Processing complete!")
                progress_container.progress(1.0)
            
            # Option 3: Standard processing (original behavior)
            else:
                # Create container for individual file progress bars
                file_progress_container = st.container()

                with file_progress_container:
                    st.markdown("#### 📊 File Processing Progress")
                    file_progress_bars = {}
                    file_status_texts = {}

                    for file in uploaded_files:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            file_status_texts[file.name] = st.empty()
                            file_status_texts[file.name].text(f"⏳ {file.name}: Waiting...")
                        with col2:
                            file_progress_bars[file.name] = st.empty()

                for i, uploaded_file in enumerate(uploaded_files):
                    # Update file status
                    file_status_texts[uploaded_file.name].text(f"🔄 {uploaded_file.name}: Processing...")

                    status_callback(f"Processing {uploaded_file.name}...", {
                        'current': i + 1,
                        'total': len(uploaded_files),
                        'file_name': uploaded_file.name,
                        'file_progress': 0.5
                    })

                    # Show progress bar for this file
                    file_progress_bars[uploaded_file.name].progress(0.5)

                    # Process the file
                    output_data = process_pdf(uploaded_file, numberer_config, add_separator)

                    if output_data:
                        st.session_state.processed_files.append({
                            'name': uploaded_file.name.replace('.pdf', '_bates.pdf'),
                            'data': output_data
                        })
                        # Mark as complete
                        file_status_texts[uploaded_file.name].text(f"✅ {uploaded_file.name}: Complete")
                        file_progress_bars[uploaded_file.name].progress(1.0)
                        st.session_state.file_progress[uploaded_file.name]['status'] = 'complete'
                    else:
                        # Mark as failed
                        file_status_texts[uploaded_file.name].text(f"❌ {uploaded_file.name}: Failed")
                        file_progress_bars[uploaded_file.name].progress(0.0)
                        st.session_state.file_progress[uploaded_file.name]['status'] = 'failed'

                status_callback("Processing complete!")
                progress_container.progress(1.0)
            
            # Clean up status displays
            status_container.empty()
            progress_container.empty()
            cancel_container.empty()
            
            # Save configuration to history
            st.session_state.current_config = numberer_config.copy()
            save_config_to_history(numberer_config)

            # Show success message
            if st.session_state.processed_files:
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Success!</strong><br>
                    Processed {len(st.session_state.processed_files)} file(s) successfully.<br>
                    <small>Configuration saved to history.</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Download section
    if st.session_state.processed_files:
        st.subheader("📥 Download Processed Files")
        
        # Download options (only show if multiple files)
        if len(st.session_state.processed_files) > 1:
            download_mode = st.radio(
                "Download Options",
                options=["Individual Files", "Download as ZIP"],
                horizontal=True,
                help="Choose to download files individually or bundled in a ZIP archive"
            )
        else:
            download_mode = "Individual Files"
        
        if download_mode == "Download as ZIP":
            # Create and offer ZIP download
            zip_data = create_zip_archive(st.session_state.processed_files)
            
            if zip_data:
                st.download_button(
                    label=f"📦 Download All Files as ZIP ({len(st.session_state.processed_files)} files)",
                    data=zip_data,
                    file_name="bates_numbered_files.zip",
                    mime="application/zip",
                    use_container_width=True,
                    type="primary"
                )
        else:
            # Individual file downloads (original behavior)
            col1, col2, col3 = st.columns(3)
            
            for i, processed_file in enumerate(st.session_state.processed_files):
                with [col1, col2, col3][i % 3]:
                    # Determine MIME type based on file extension
                    mime_type = 'text/csv' if processed_file['name'].endswith('.csv') else 'application/pdf'
                    
                    st.download_button(
                        label=f"⬇️ {processed_file['name']}",
                        data=processed_file['data'],
                        file_name=processed_file['name'],
                        mime=mime_type,
                        use_container_width=True,
                        key=f"download_btn_{i}_{processed_file['name']}"
                    )
        
        st.divider()

        if st.button("🗑️ Clear Processed Files", use_container_width=True):
            st.session_state.processed_files = []
            st.session_state.ai_analysis_results = []
            st.rerun()

    # AI Analysis Results Display
    if st.session_state.ai_analysis_results:
        st.divider()
        st.subheader("🤖 AI Document Analysis Results")

        with st.expander("📊 Analysis Summary", expanded=True):
            for result in st.session_state.ai_analysis_results:
                st.markdown(f"**Document:** {result.get('filename', 'Unknown')}")

                # Discrimination findings
                if result.get('discrimination_findings'):
                    st.markdown("##### 🚨 Discrimination Patterns Detected")
                    for finding in result['discrimination_findings']:
                        severity = finding.get('severity', 'medium')
                        severity_color = {
                            'critical': 'red',
                            'high': 'orange',
                            'medium': 'yellow',
                            'low': 'green'
                        }.get(severity, 'gray')

                        st.markdown(f"""
                        <div style="background-color: #{severity_color}22; padding: 10px; border-radius: 5px; border-left: 4px solid {severity_color}; margin: 10px 0;">
                            <strong style="color: {severity_color};">⚠️ {severity.upper()}</strong><br>
                            {finding.get('description', 'No description available')}
                        </div>
                        """, unsafe_allow_html=True)

                # Problematic content
                if result.get('problematic_content'):
                    st.markdown("##### ⚠️ Problematic Content Identified")
                    for content in result['problematic_content']:
                        severity = content.get('severity', 'medium')
                        severity_color = {
                            'critical': 'red',
                            'high': 'orange',
                            'medium': 'yellow',
                            'low': 'green'
                        }.get(severity, 'gray')

                        st.markdown(f"""
                        <div style="background-color: #{severity_color}22; padding: 10px; border-radius: 5px; border-left: 4px solid {severity_color}; margin: 10px 0;">
                            <strong style="color: {severity_color};">⚠️ {severity.upper()}</strong><br>
                            {content.get('description', 'No description available')}
                        </div>
                        """, unsafe_allow_html=True)

                # Metadata insights
                if result.get('metadata'):
                    st.markdown("##### 📋 Document Metadata")
                    metadata_col1, metadata_col2 = st.columns(2)

                    with metadata_col1:
                        if result['metadata'].get('key_entities'):
                            st.markdown("**Key Entities:**")
                            for entity in result['metadata']['key_entities']:
                                st.markdown(f"- {entity}")

                    with metadata_col2:
                        if result['metadata'].get('document_type'):
                            st.markdown(f"**Document Type:** {result['metadata']['document_type']}")
                        if result['metadata'].get('language'):
                            st.markdown(f"**Language:** {result['metadata']['language']}")
                        if result['metadata'].get('summary'):
                            st.markdown(f"**Summary:** {result['metadata']['summary']}")

                # Overall analysis status
                analysis_complete = result.get('analysis_complete', False)
                if analysis_complete:
                    st.success("✅ Analysis completed successfully")
                else:
                    st.warning("⚠️ Analysis incomplete or encountered errors")

                st.divider()

        # Export analysis results
        if st.button("📤 Export AI Analysis Results (JSON)", use_container_width=True):
            analysis_json = json.dumps(st.session_state.ai_analysis_results, indent=2)
            st.download_button(
                label="Download AI Analysis Results",
                data=analysis_json,
                file_name=f"ai_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Bates-Labeler • Professional legal document numbering • 
        <a href="https://github.com/thepingdoctor/Bates-Labeler" target="_blank">GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
