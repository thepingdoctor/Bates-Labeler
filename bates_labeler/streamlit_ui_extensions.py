"""
Streamlit UI Extensions for v2.2.0 Features

This module provides UI components for the new v2.2.0 features:
- Template Manager
- Configuration Manager
- Cloud Storage
- Form Handler
- Batch Scheduler

These are imported and used by app.py when the features are available.
"""

import streamlit as st
from typing import Dict, List, Optional, Any
import json
from datetime import datetime


def render_template_manager_ui(template_manager) -> Optional[Dict]:
    """
    Render the Template Manager UI component.

    Args:
        template_manager: TemplateManager instance

    Returns:
        Selected template configuration or None
    """
    with st.expander("📋 Template Library (v2.2.0)", expanded=False):
        st.markdown("**Save and load configuration templates**")

        # List available templates
        templates = template_manager.list_templates()
        template_names = [t.metadata.name for t in templates]

        tab1, tab2, tab3 = st.tabs(["📖 Load", "💾 Save", "🔍 Browse"])

        with tab1:
            # Load template
            if template_names:
                selected_template = st.selectbox(
                    "Select Template",
                    options=template_names,
                    help="Choose a template to load"
                )

                if st.button("Load Template", use_container_width=True):
                    template = template_manager.get_template(selected_template)
                    st.success(f"Loaded template: {selected_template}")
                    return template.config
            else:
                st.info("No templates available. Create one in the 'Save' tab.")

        with tab2:
            # Save current config as template
            template_name = st.text_input("Template Name", placeholder="My Custom Template")
            template_desc = st.text_area("Description", placeholder="Describe this template...")
            template_category = st.selectbox(
                "Category",
                options=["custom", "legal-discovery", "confidential", "exhibits", "general"]
            )
            template_tags = st.text_input("Tags (comma-separated)", placeholder="legal, confidential")

            if st.button("Save Current Config as Template", use_container_width=True):
                if template_name:
                    try:
                        tags = [t.strip() for t in template_tags.split(",")] if template_tags else []
                        current_config = st.session_state.get('current_config', {})

                        template_manager.create_template(
                            name=template_name,
                            config=current_config,
                            description=template_desc,
                            category=template_category,
                            tags=tags
                        )
                        template_manager.save_template(template_name)
                        st.success(f"Template '{template_name}' saved!")
                    except Exception as e:
                        st.error(f"Error saving template: {str(e)}")
                else:
                    st.warning("Please enter a template name")

        with tab3:
            # Browse and manage templates
            if templates:
                for template in templates:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{template.metadata.name}**")
                            st.caption(f"{template.metadata.description or 'No description'}")
                            st.caption(f"Category: {template.metadata.category} | Tags: {', '.join(template.metadata.tags)}")
                        with col2:
                            if st.button("🗑️", key=f"del_{template.metadata.name}", help="Delete template"):
                                template_manager.delete_template(template.metadata.name)
                                st.success(f"Deleted: {template.metadata.name}")
                                st.rerun()
                        st.divider()
            else:
                st.info("No templates to browse")

    return None


def render_form_detection_ui(uploaded_files) -> Dict[str, Any]:
    """
    Render form field detection UI.

    Args:
        uploaded_files: List of uploaded PDF files

    Returns:
        Dictionary with form detection results
    """
    try:
        from bates_labeler import PDFFormHandler, FORM_HANDLER_AVAILABLE

        if not FORM_HANDLER_AVAILABLE:
            return {"has_forms": False, "message": "Form handler not available"}

        with st.expander("📝 PDF Form Detection (v2.2.0)", expanded=False):
            if not uploaded_files:
                st.info("Upload PDFs to detect form fields")
                return {"has_forms": False}

            handler = PDFFormHandler()
            form_results = []

            for uploaded_file in uploaded_files:
                # Save temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                try:
                    if handler.has_form_fields(tmp_path):
                        summary = handler.get_form_summary(tmp_path)
                        form_results.append({
                            'filename': uploaded_file.name,
                            'has_forms': True,
                            'total_fields': summary['total_fields'],
                            'field_types': summary['field_types']
                        })
                finally:
                    import os
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

            if form_results:
                st.warning(f"⚠️ Found {len(form_results)} file(s) with interactive forms")
                for result in form_results:
                    with st.container():
                        st.markdown(f"**{result['filename']}**")
                        st.caption(f"Fields: {result['total_fields']} | Types: {', '.join(result['field_types'].keys())}")
                st.info("Form fields will be preserved during Bates numbering!")
                return {"has_forms": True, "results": form_results}
            else:
                st.success("✓ No interactive forms detected")
                return {"has_forms": False}

    except Exception as e:
        st.error(f"Form detection error: {str(e)}")
        return {"has_forms": False, "error": str(e)}


def render_cloud_storage_ui() -> Optional[Any]:
    """
    Render cloud storage integration UI.

    Returns:
        Cloud storage provider instance or None
    """
    try:
        from bates_labeler import CloudStorageManager, CLOUD_STORAGE_AVAILABLE

        if not CLOUD_STORAGE_AVAILABLE:
            with st.expander("☁️ Cloud Storage (v2.2.0)", expanded=False):
                st.info("Install cloud storage support: `pip install 'bates-labeler[cloud-storage]'`")
            return None

        with st.expander("☁️ Cloud Storage Integration (v2.2.0)", expanded=False):
            st.markdown("**Upload/download files from cloud storage**")

            # Initialize manager in session state
            if 'cloud_manager' not in st.session_state:
                st.session_state.cloud_manager = CloudStorageManager()

            manager = st.session_state.cloud_manager

            tab1, tab2 = st.tabs(["⚙️ Setup", "📤 Upload/Download"])

            with tab1:
                st.markdown("**Configure Cloud Providers:**")

                provider_type = st.selectbox(
                    "Provider",
                    options=["google_drive", "dropbox"],
                    help="Select cloud storage provider"
                )

                provider_name = st.text_input("Provider Name", placeholder="my_drive")

                if provider_type == "google_drive":
                    creds_file = st.file_uploader("Upload credentials.json", type=["json"])
                    if creds_file and provider_name and st.button("Connect Google Drive"):
                        try:
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
                                tmp.write(creds_file.getvalue())
                                tmp_path = tmp.name

                            manager.add_provider(
                                name=provider_name,
                                provider_type='google_drive',
                                credentials={'credentials_file': tmp_path}
                            )
                            st.success(f"Connected to Google Drive as '{provider_name}'")
                        except Exception as e:
                            st.error(f"Connection failed: {str(e)}")

                elif provider_type == "dropbox":
                    access_token = st.text_input("Access Token", type="password")
                    if access_token and provider_name and st.button("Connect Dropbox"):
                        try:
                            manager.add_provider(
                                name=provider_name,
                                provider_type='dropbox',
                                credentials={'access_token': access_token}
                            )
                            st.success(f"Connected to Dropbox as '{provider_name}'")
                        except Exception as e:
                            st.error(f"Connection failed: {str(e)}")

                # List connected providers
                providers = manager.list_providers()
                if providers:
                    st.markdown("**Connected Providers:**")
                    for prov in providers:
                        st.text(f"✓ {prov}")

            with tab2:
                providers = manager.list_providers()
                if not providers:
                    st.info("Connect a provider in the Setup tab first")
                else:
                    selected_provider = st.selectbox("Select Provider", options=providers)

                    upload_download = st.radio("Action", ["Download", "Upload"])

                    if upload_download == "Download":
                        file_id = st.text_input("File ID or Path", help="Google Drive: file ID, Dropbox: /path/to/file.pdf")
                        local_name = st.text_input("Save As", placeholder="document.pdf")

                        if st.button("Download from Cloud"):
                            if file_id and local_name:
                                try:
                                    provider = manager.get_provider(selected_provider)
                                    import tempfile
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                        provider.download_file(file_id, tmp.name)
                                        with open(tmp.name, 'rb') as f:
                                            file_data = f.read()

                                    st.download_button(
                                        label="📥 Download File",
                                        data=file_data,
                                        file_name=local_name,
                                        mime="application/pdf"
                                    )
                                    st.success(f"Downloaded: {local_name}")
                                except Exception as e:
                                    st.error(f"Download failed: {str(e)}")

                    elif upload_download == "Upload":
                        uploaded_file = st.file_uploader("Select file to upload", type=['pdf'])
                        remote_path = st.text_input("Remote Path", placeholder="folder/document.pdf")

                        if uploaded_file and remote_path and st.button("Upload to Cloud"):
                            try:
                                provider = manager.get_provider(selected_provider)
                                import tempfile
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                    tmp.write(uploaded_file.getvalue())
                                    tmp_path = tmp.name

                                result = provider.upload_file(tmp_path, remote_path)
                                st.success(f"Uploaded to: {result}")
                            except Exception as e:
                                st.error(f"Upload failed: {str(e)}")

            return manager

    except Exception as e:
        st.error(f"Cloud storage error: {str(e)}")
        return None


def render_scheduler_ui() -> None:
    """
    Render batch scheduler UI (informational only in web UI).
    """
    try:
        from bates_labeler import SCHEDULER_AVAILABLE

        with st.expander("⏰ Batch Scheduler (v2.2.0)", expanded=False):
            if not SCHEDULER_AVAILABLE:
                st.info("Install scheduler: `pip install 'bates-labeler[advanced]'`")
            else:
                st.markdown("**Automated Batch Processing**")
                st.info("""
                The Batch Scheduler is designed for programmatic use (Python API).

                **Features:**
                - Schedule one-time or recurring jobs
                - Watch folders for auto-processing
                - Job queue management
                - Status tracking

                📖 See [documentation](docs/FEATURES_V2_2.md#3-batch-job-scheduler) for Python examples.
                """)
    except Exception as e:
        st.error(f"Scheduler UI error: {str(e)}")


def render_config_manager_ui(config_manager) -> Optional[Dict]:
    """
    Render configuration manager UI.

    Args:
        config_manager: ConfigManager instance

    Returns:
        Selected configuration or None
    """
    with st.expander("🎛️ Configuration Manager (v2.2.0)", expanded=False):
        st.markdown("**Advanced configuration management**")

        tab1, tab2 = st.tabs(["📂 Load", "💾 Save"])

        with tab1:
            configs = config_manager.list_configs()
            if configs:
                selected_config = st.selectbox("Select Configuration", options=configs)
                if st.button("Load Configuration", use_container_width=True):
                    try:
                        config = config_manager.load_config(selected_config)
                        st.success(f"Loaded: {selected_config}")
                        # Convert to dict for Streamlit
                        if hasattr(config, 'dict'):
                            return config.dict()
                        else:
                            return vars(config)
                    except Exception as e:
                        st.error(f"Load failed: {str(e)}")
            else:
                st.info("No saved configurations")

        with tab2:
            config_name = st.text_input("Configuration Name", placeholder="my_config")
            if st.button("Save Current Configuration", use_container_width=True):
                if config_name:
                    try:
                        current_config = st.session_state.get('current_config', {})
                        config_manager.create_config(config_name, current_config)
                        config_manager.save_config(config_name)
                        st.success(f"Saved: {config_name}")
                    except Exception as e:
                        st.error(f"Save failed: {str(e)}")
                else:
                    st.warning("Enter a configuration name")

    return None
