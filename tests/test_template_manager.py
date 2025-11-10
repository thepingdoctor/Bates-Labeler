"""Tests for template manager module."""

import json
import pytest
from pathlib import Path
from bates_labeler.template_manager import (
    Template,
    TemplateMetadata,
    TemplateManager
)


@pytest.fixture
def temp_template_dir(tmp_path):
    """Create temporary template directory."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


@pytest.fixture
def template_manager(temp_template_dir):
    """Create TemplateManager instance."""
    return TemplateManager(template_dir=temp_template_dir)


class TestTemplateMetadata:
    """Test TemplateMetadata class."""

    def test_initialization(self):
        """Test metadata initialization."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="Test description",
            author="Test Author",
            category="test"
        )

        assert metadata.name == "Test Template"
        assert metadata.description == "Test description"
        assert metadata.author == "Test Author"
        assert metadata.category == "test"
        assert metadata.tags == []

    def test_to_dict(self):
        """Test metadata serialization."""
        metadata = TemplateMetadata(
            name="Test",
            tags=["tag1", "tag2"]
        )

        data = metadata.to_dict()
        assert data['name'] == "Test"
        assert data['tags'] == ["tag1", "tag2"]
        assert 'created' in data
        assert 'modified' in data

    def test_from_dict(self):
        """Test metadata deserialization."""
        data = {
            'name': 'Test',
            'description': 'Desc',
            'author': 'Author',
            'category': 'test',
            'tags': ['tag1'],
            'created': '2025-01-01T00:00:00',
            'modified': '2025-01-01T00:00:00'
        }

        metadata = TemplateMetadata.from_dict(data)
        assert metadata.name == 'Test'
        assert metadata.description == 'Desc'
        assert metadata.tags == ['tag1']


class TestTemplate:
    """Test Template class."""

    def test_initialization(self):
        """Test template initialization."""
        metadata = TemplateMetadata(name="Test")
        config = {
            'prefix': 'TEST-',
            'start_number': 1,
            'padding': 6,
            'position': 'top-right'
        }

        template = Template(metadata, config)
        assert template.metadata.name == "Test"
        assert template.config['prefix'] == 'TEST-'

    def test_validation(self):
        """Test template validation."""
        metadata = TemplateMetadata(name="Test")

        # Valid template
        valid_config = {
            'prefix': 'TEST-',
            'start_number': 1,
            'padding': 6,
            'position': 'top-right'
        }
        template = Template(metadata, valid_config)
        assert template.validate() is True

        # Invalid template (missing required fields)
        invalid_config = {'prefix': 'TEST-'}
        template = Template(metadata, invalid_config)
        assert template.validate() is False

    def test_to_dict(self):
        """Test template serialization."""
        metadata = TemplateMetadata(name="Test")
        config = {'prefix': 'TEST-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}

        template = Template(metadata, config)
        data = template.to_dict()

        assert 'metadata' in data
        assert 'config' in data
        assert data['metadata']['name'] == "Test"

    def test_from_dict(self):
        """Test template deserialization."""
        data = {
            'metadata': {
                'name': 'Test',
                'description': 'Desc'
            },
            'config': {
                'prefix': 'TEST-',
                'start_number': 1,
                'padding': 6,
                'position': 'top-right'
            }
        }

        template = Template.from_dict(data)
        assert template.metadata.name == 'Test'
        assert template.config['prefix'] == 'TEST-'


class TestTemplateManager:
    """Test TemplateManager class."""

    def test_initialization(self, template_manager, temp_template_dir):
        """Test manager initialization."""
        assert template_manager.template_dir == temp_template_dir
        assert temp_template_dir.exists()

        # Should have default templates
        default_templates = template_manager.list_templates()
        assert len(default_templates) >= 3  # At least 3 default templates

    def test_create_template(self, template_manager):
        """Test template creation."""
        config = {
            'prefix': 'NEW-',
            'start_number': 1,
            'padding': 6,
            'position': 'bottom-right'
        }

        template = template_manager.create_template(
            name="New Template",
            config=config,
            description="Test template",
            category="custom"
        )

        assert template is not None
        assert template.metadata.name == "New Template"
        assert template.config['prefix'] == 'NEW-'

        # Duplicate name should fail
        with pytest.raises(ValueError):
            template_manager.create_template("New Template", config)

    def test_get_template(self, template_manager):
        """Test template retrieval."""
        config = {'prefix': 'GET-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Get Test", config)

        retrieved = template_manager.get_template("Get Test")
        assert retrieved is not None
        assert retrieved.metadata.name == "Get Test"

        # Non-existent template
        assert template_manager.get_template("nonexistent") is None

    def test_list_templates(self, template_manager):
        """Test template listing."""
        # Create templates in different categories
        template_manager.create_template(
            "Custom 1",
            {'prefix': 'C1-', 'start_number': 1, 'padding': 6, 'position': 'top-right'},
            category="custom"
        )
        template_manager.create_template(
            "Custom 2",
            {'prefix': 'C2-', 'start_number': 1, 'padding': 6, 'position': 'top-right'},
            category="custom"
        )

        # List all
        all_templates = template_manager.list_templates()
        assert len(all_templates) >= 5  # 3 default + 2 custom

        # Filter by category
        custom_templates = template_manager.list_templates(category="custom")
        assert len(custom_templates) == 2

    def test_list_templates_with_tags(self, template_manager):
        """Test template listing with tag filtering."""
        template_manager.create_template(
            "Tagged 1",
            {'prefix': 'T1-', 'start_number': 1, 'padding': 6, 'position': 'top-right'},
            tags=["legal", "confidential"]
        )
        template_manager.create_template(
            "Tagged 2",
            {'prefix': 'T2-', 'start_number': 1, 'padding': 6, 'position': 'top-right'},
            tags=["legal"]
        )

        # Filter by tag
        legal_templates = template_manager.list_templates(tags=["legal"])
        assert len(legal_templates) == 2

        conf_templates = template_manager.list_templates(tags=["confidential"])
        assert len(conf_templates) == 1

    def test_search_templates(self, template_manager):
        """Test template search."""
        template_manager.create_template(
            "Legal Discovery",
            {'prefix': 'LD-', 'start_number': 1, 'padding': 6, 'position': 'top-right'},
            description="For legal discovery documents",
            tags=["legal"]
        )

        # Search by name
        results = template_manager.search_templates("discovery")
        assert len(results) >= 1

        # Search by tag
        results = template_manager.search_templates("legal")
        assert len(results) >= 1

    def test_update_template(self, template_manager):
        """Test template update."""
        config = {'prefix': 'OLD-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Update Test", config)

        # Update config
        new_config = {'prefix': 'NEW-', 'start_number': 10, 'padding': 4, 'position': 'bottom-right'}
        updated = template_manager.update_template(
            "Update Test",
            config=new_config
        )

        assert updated.config['prefix'] == 'NEW-'
        assert updated.config['start_number'] == 10

        # Update metadata
        updated = template_manager.update_template(
            "Update Test",
            metadata_updates={'description': 'Updated description'}
        )
        assert updated.metadata.description == 'Updated description'

    def test_delete_template(self, template_manager):
        """Test template deletion."""
        config = {'prefix': 'DEL-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Delete Test", config)

        assert template_manager.get_template("Delete Test") is not None

        deleted = template_manager.delete_template("Delete Test")
        assert deleted is True
        assert template_manager.get_template("Delete Test") is None

        # Delete non-existent
        deleted = template_manager.delete_template("nonexistent")
        assert deleted is False

    def test_save_template(self, template_manager):
        """Test template persistence."""
        config = {'prefix': 'SAVE-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Save Test", config)

        saved_path = template_manager.save_template("Save Test")
        assert saved_path.exists()

        # Verify file content
        with open(saved_path, 'r') as f:
            data = json.load(f)
            assert data['metadata']['name'] == "Save Test"
            assert data['config']['prefix'] == 'SAVE-'

    def test_export_import_template(self, template_manager, tmp_path):
        """Test template export/import."""
        config = {'prefix': 'EXP-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Export Test", config)

        # Export
        export_path = tmp_path / "exported.json"
        template_manager.export_template("Export Test", export_path)
        assert export_path.exists()

        # Import
        imported = template_manager.import_template(export_path)
        assert imported.metadata.name == "Export Test"
        assert template_manager.get_template("Export Test") is not None

    def test_duplicate_template(self, template_manager):
        """Test template duplication."""
        config = {'prefix': 'ORIG-', 'start_number': 1, 'padding': 6, 'position': 'top-right'}
        template_manager.create_template("Original", config)

        duplicated = template_manager.duplicate_template("Original", "Copy")

        assert duplicated.metadata.name == "Copy"
        assert duplicated.config['prefix'] == 'ORIG-'
        assert template_manager.get_template("Copy") is not None

        # Duplicate to existing name should fail
        with pytest.raises(ValueError):
            template_manager.duplicate_template("Original", "Copy")

    def test_get_categories(self, template_manager):
        """Test category listing."""
        categories = template_manager.get_categories()
        assert "legal-discovery" in categories
        assert "confidential" in categories
        assert "custom" in categories

    def test_get_templates_by_category(self, template_manager):
        """Test getting templates by category."""
        # Default templates should exist
        legal_templates = template_manager.get_templates_by_category("legal-discovery")
        assert len(legal_templates) >= 1

        confidential_templates = template_manager.get_templates_by_category("confidential")
        assert len(confidential_templates) >= 1

    def test_default_templates_creation(self, template_manager):
        """Test that default templates are created."""
        # Should have at least 3 default templates
        templates = template_manager.list_templates()
        template_names = [t.metadata.name for t in templates]

        assert "Legal Discovery" in template_names
        assert "Confidential Documents" in template_names
        assert "Exhibit Marking" in template_names
