"""Template Management System for Bates-Labeler.

This module provides comprehensive template management for saving, loading,
and sharing Bates numbering configurations and workflows.

Features:
- Template creation from configurations
- Template library with categorization
- Template sharing (import/export)
- Template validation
- Template versioning
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from .config_manager import BatesConfig, ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False


class TemplateMetadata:
    """Metadata for configuration templates.

    Attributes:
        name: Template name
        description: Template description
        author: Template author
        version: Template version
        created: Creation timestamp
        modified: Last modification timestamp
        category: Template category
        tags: Template tags for searchability
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        author: str = "",
        version: str = "1.0.0",
        category: str = "general",
        tags: Optional[List[str]] = None
    ):
        """Initialize template metadata.

        Args:
            name: Template name
            description: Template description
            author: Template author
            version: Template version
            category: Template category
            tags: Template tags
        """
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.category = category
        self.tags = tags or []
        self.created = datetime.now().isoformat()
        self.modified = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'version': self.version,
            'category': self.category,
            'tags': self.tags,
            'created': self.created,
            'modified': self.modified
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateMetadata':
        """Create metadata from dictionary.

        Args:
            data: Dictionary containing metadata

        Returns:
            TemplateMetadata instance
        """
        metadata = cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            author=data.get('author', ''),
            version=data.get('version', '1.0.0'),
            category=data.get('category', 'general'),
            tags=data.get('tags', [])
        )
        metadata.created = data.get('created', metadata.created)
        metadata.modified = data.get('modified', metadata.modified)
        return metadata


class Template:
    """Configuration template with metadata and validation.

    Attributes:
        metadata: Template metadata
        config: Configuration data
    """

    def __init__(self, metadata: TemplateMetadata, config: Dict[str, Any]):
        """Initialize template.

        Args:
            metadata: Template metadata
            config: Configuration dictionary
        """
        self.metadata = metadata
        self.config = config

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'metadata': self.metadata.to_dict(),
            'config': self.config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create template from dictionary.

        Args:
            data: Dictionary containing template data

        Returns:
            Template instance
        """
        metadata = TemplateMetadata.from_dict(data.get('metadata', {}))
        config = data.get('config', {})
        return cls(metadata, config)

    def validate(self) -> bool:
        """Validate template configuration.

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['prefix', 'start_number', 'padding', 'position']
        return all(field in self.config for field in required_fields)


class TemplateManager:
    """Template management system.

    Features:
    - Create templates from configurations
    - Save/load templates
    - Template library with categories
    - Template search and filtering
    - Template sharing (import/export)
    """

    # Predefined template categories
    CATEGORIES = [
        "legal-discovery",
        "confidential",
        "exhibits",
        "general",
        "custom"
    ]

    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """Initialize template manager.

        Args:
            template_dir: Directory for storing templates.
                         Defaults to ~/.bates-labeler/templates
        """
        if template_dir is None:
            template_dir = Path.home() / ".bates-labeler" / "templates"

        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self._templates: Dict[str, Template] = {}
        self._load_all_templates()
        self._create_default_templates()

    def _load_all_templates(self) -> None:
        """Load all templates from disk."""
        for template_file in self.template_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    template = Template.from_dict(data)
                    self._templates[template.metadata.name] = template
            except Exception as e:
                print(f"Warning: Failed to load template {template_file}: {e}")

    def _create_default_templates(self) -> None:
        """Create default templates if they don't exist."""
        default_templates = [
            {
                'name': 'Legal Discovery',
                'description': 'Standard legal discovery document template',
                'category': 'legal-discovery',
                'config': {
                    'prefix': 'DISC-',
                    'suffix': '',
                    'start_number': 1,
                    'padding': 6,
                    'position': 'bottom-right',
                    'font_size': 10,
                    'font_color': (0, 0, 0),
                    'enable_watermark': False
                }
            },
            {
                'name': 'Confidential Documents',
                'description': 'Template for confidential documents with watermark',
                'category': 'confidential',
                'config': {
                    'prefix': 'CONF-',
                    'suffix': '-CONFIDENTIAL',
                    'start_number': 1,
                    'padding': 6,
                    'position': 'top-right',
                    'font_size': 10,
                    'font_color': (255, 0, 0),
                    'enable_watermark': True,
                    'watermark_text': 'CONFIDENTIAL'
                }
            },
            {
                'name': 'Exhibit Marking',
                'description': 'Template for court exhibits',
                'category': 'exhibits',
                'config': {
                    'prefix': 'EXH-',
                    'suffix': '',
                    'start_number': 1,
                    'padding': 4,
                    'position': 'bottom-center',
                    'font_size': 12,
                    'font_color': (0, 0, 0),
                    'enable_watermark': False
                }
            }
        ]

        for template_data in default_templates:
            if template_data['name'] not in self._templates:
                metadata = TemplateMetadata(
                    name=template_data['name'],
                    description=template_data['description'],
                    author='Bates-Labeler',
                    category=template_data['category']
                )
                template = Template(metadata, template_data['config'])
                self._templates[template.metadata.name] = template
                self.save_template(template.metadata.name)

    def create_template(
        self,
        name: str,
        config: Dict[str, Any],
        description: str = "",
        author: str = "",
        category: str = "custom",
        tags: Optional[List[str]] = None
    ) -> Template:
        """Create a new template.

        Args:
            name: Template name
            config: Configuration dictionary
            description: Template description
            author: Template author
            category: Template category
            tags: Template tags

        Returns:
            Created template

        Raises:
            ValueError: If template already exists or is invalid
        """
        if name in self._templates:
            raise ValueError(f"Template already exists: {name}")

        metadata = TemplateMetadata(
            name=name,
            description=description,
            author=author,
            category=category,
            tags=tags
        )

        template = Template(metadata, config)

        if not template.validate():
            raise ValueError("Invalid template configuration")

        self._templates[name] = template
        return template

    def get_template(self, name: str) -> Optional[Template]:
        """Get template by name.

        Args:
            name: Template name

        Returns:
            Template or None if not found
        """
        return self._templates.get(name)

    def list_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Template]:
        """List templates with optional filtering.

        Args:
            category: Filter by category
            tags: Filter by tags (any match)

        Returns:
            List of matching templates
        """
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.metadata.category == category]

        if tags:
            templates = [
                t for t in templates
                if any(tag in t.metadata.tags for tag in tags)
            ]

        return templates

    def search_templates(self, query: str) -> List[Template]:
        """Search templates by name, description, or tags.

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query = query.lower()
        results = []

        for template in self._templates.values():
            if (query in template.metadata.name.lower() or
                query in template.metadata.description.lower() or
                any(query in tag.lower() for tag in template.metadata.tags)):
                results.append(template)

        return results

    def update_template(
        self,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> Template:
        """Update an existing template.

        Args:
            name: Template name
            config: New configuration (optional)
            metadata_updates: Metadata updates (optional)

        Returns:
            Updated template

        Raises:
            ValueError: If template not found
        """
        template = self.get_template(name)
        if template is None:
            raise ValueError(f"Template not found: {name}")

        if config is not None:
            template.config = config

        if metadata_updates:
            for key, value in metadata_updates.items():
                if hasattr(template.metadata, key):
                    setattr(template.metadata, key, value)

        template.metadata.modified = datetime.now().isoformat()

        return template

    def delete_template(self, name: str) -> bool:
        """Delete a template.

        Args:
            name: Template name

        Returns:
            True if deleted, False if not found
        """
        if name in self._templates:
            del self._templates[name]

            # Delete file
            template_file = self.template_dir / f"{name}.json"
            if template_file.exists():
                template_file.unlink()

            return True
        return False

    def save_template(self, name: str) -> Path:
        """Save template to disk.

        Args:
            name: Template name

        Returns:
            Path to saved template file

        Raises:
            ValueError: If template not found
        """
        template = self.get_template(name)
        if template is None:
            raise ValueError(f"Template not found: {name}")

        template_file = self.template_dir / f"{name}.json"
        with open(template_file, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)

        return template_file

    def export_template(self, name: str, output_path: Union[str, Path]) -> Path:
        """Export template to specified path.

        Args:
            name: Template name
            output_path: Output file path

        Returns:
            Path to exported file
        """
        template = self.get_template(name)
        if template is None:
            raise ValueError(f"Template not found: {name}")

        output_path = Path(output_path)

        with open(output_path, 'w') as f:
            json.dump(template.to_dict(), f, indent=2)

        return output_path

    def import_template(self, input_path: Union[str, Path], overwrite: bool = False) -> Template:
        """Import template from file.

        Args:
            input_path: Input file path
            overwrite: Whether to overwrite existing template

        Returns:
            Imported template

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If template exists and overwrite is False
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Template file not found: {input_path}")

        with open(input_path, 'r') as f:
            data = json.load(f)

        template = Template.from_dict(data)

        if template.metadata.name in self._templates and not overwrite:
            raise ValueError(
                f"Template already exists: {template.metadata.name}. "
                "Use overwrite=True to replace."
            )

        self._templates[template.metadata.name] = template
        self.save_template(template.metadata.name)

        return template

    def duplicate_template(self, source_name: str, new_name: str) -> Template:
        """Duplicate an existing template.

        Args:
            source_name: Source template name
            new_name: New template name

        Returns:
            Duplicated template

        Raises:
            ValueError: If source not found or new name exists
        """
        source = self.get_template(source_name)
        if source is None:
            raise ValueError(f"Source template not found: {source_name}")

        if new_name in self._templates:
            raise ValueError(f"Template already exists: {new_name}")

        # Create new metadata
        new_metadata = TemplateMetadata(
            name=new_name,
            description=f"Copy of {source.metadata.name}",
            author=source.metadata.author,
            category=source.metadata.category,
            tags=source.metadata.tags.copy()
        )

        # Copy configuration
        new_config = source.config.copy()

        new_template = Template(new_metadata, new_config)
        self._templates[new_name] = new_template

        return new_template

    def get_categories(self) -> List[str]:
        """Get list of template categories.

        Returns:
            List of category names
        """
        return self.CATEGORIES.copy()

    def get_templates_by_category(self, category: str) -> List[Template]:
        """Get all templates in a category.

        Args:
            category: Category name

        Returns:
            List of templates in category
        """
        return self.list_templates(category=category)
