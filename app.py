"""
Streamlit Web UI for Bates-Labeler
A user-friendly web interface for adding Bates numbers to PDF documents.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import List, Optional
from io import BytesIO

from bates_labeler import BatesNumberer, __version__

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


def generate_preview(prefix: str, start_number: int, padding: int, suffix: str) -> str:
    """Generate a preview of the Bates number format."""
    number_str = str(start_number).zfill(padding)
    return f"{prefix}{number_str}{suffix}"


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
            
            add_separator = st.checkbox(
                "Add Separator Page",
                help="Add a page at the beginning showing Bates range"
            )
            
            st.divider()
            
            # Combine PDFs option
            combine_pdfs = st.checkbox(
                "📑 Combine All PDFs into Single File",
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
            
            st.divider()
            
            # Bates filename option
            use_bates_filenames = st.checkbox(
                "📝 Use Bates Number as Filename",
                help="Name output files with their first Bates number (e.g., CASE-0001.pdf)"
            )
            
            if use_bates_filenames:
                st.info("📊 Will generate CSV and PDF mapping files")
    
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
            
            # Display file names
            with st.expander("📋 Uploaded Files", expanded=True):
                for i, file in enumerate(uploaded_files, 1):
                    st.text(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
    
    with col2:
        st.subheader("👁️ Preview")
        
        # Generate and display preview
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
    
    st.divider()
    
    # Process button
    if uploaded_files:
        if st.button("🚀 Process PDF(s)", type="primary", use_container_width=True):
            # Handle custom font if uploaded
            custom_font_path = None
            if custom_font:
                # Save custom font to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(custom_font.name)[1]) as tmp_font:
                    tmp_font.write(custom_font.read())
                    custom_font_path = tmp_font.name
            
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
                'custom_font_path': custom_font_path
            }
            
            # Process files based on selected options
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            st.session_state.processed_files = []
            
            # Option 1: Combine PDFs
            if combine_pdfs:
                status_text.text("Combining and processing PDFs...")
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
                
                progress_bar.progress(1.0)
            
            # Option 2: Bates filenames (without combine)
            elif use_bates_filenames:
                status_text.text("Processing with Bates number filenames...")
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
                
                progress_bar.progress(1.0)
            
            # Option 3: Standard processing (original behavior)
            else:
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    
                    # Process the file
                    output_data = process_pdf(uploaded_file, numberer_config, add_separator)
                    
                    if output_data:
                        st.session_state.processed_files.append({
                            'name': uploaded_file.name.replace('.pdf', '_bates.pdf'),
                            'data': output_data
                        })
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.empty()
            progress_bar.empty()
            
            # Show success message
            if st.session_state.processed_files:
                st.markdown(f"""
                <div class="success-box">
                    <strong>✅ Success!</strong><br>
                    Processed {len(st.session_state.processed_files)} file(s) successfully.
                </div>
                """, unsafe_allow_html=True)
    
    # Download section
    if st.session_state.processed_files:
        st.subheader("📥 Download Processed Files")
        
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
        
        if st.button("🗑️ Clear Processed Files", use_container_width=True):
            st.session_state.processed_files = []
            st.rerun()
    
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
