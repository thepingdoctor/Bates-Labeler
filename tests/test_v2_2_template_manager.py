"""
Comprehensive Test Suite for Template Manager (v2.2.0 Feature #2)

Tests template management functionality including:
- Template creation and validation
- Template search and filtering
- Template categorization and tagging
- Template import/export
- Template duplication
- Default template creation
"""

import json
import pytest
import tempfile
from pathlib import Path
from bates_labeler.template_manager import (
    Template,
    TemplateMetadata,
    TemplateManager
)


class TestTemplateMetadata:
    """Test TemplateMetadata class."""

    def test_create_metadata(self):
        """Test creating template metadata."""
        metadata = TemplateMetadata(
            name="Test Template",
            description="A test template",
            author="Tester",
            category="legal-discovery",
            tags=["legal", "discovery"]
        )

        assert metadata.name == "Test Template"
        assert metadata.description == "A test template"
        assert metadata.author == "Tester"
        assert metadata.category == "legal-discovery"
        assert metadata.tags == ["legal", "discovery"]
        assert metadata.version == "1.0.0"

    def test_metadata_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = TemplateMetadata(
            name="Test",
            description="Desc",
            category="general"
        )

        data = metadata.to_dict()

        assert data["name"] == "Test"
        assert data["description"] == "Desc"
        assert data["category"] == "general"
        assert "created" in data
        assert "modified" in data

    def test_metadata_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "name": "Test Template",
            "description": "Description",
            "author": "Author",
            "version": "2.0.0",
            "category": "confidential",
            "tags": ["tag1", "tag2"],
            "created": "2024-01-01T00:00:00",
            "modified": "2024-01-02T00:00:00"
        }

        metadata = TemplateMetadata.from_dict(data)

        assert metadata.name == "Test Template"
        assert metadata.author == "Author"
        assert metadata.version == "2.0.0"
        assert metadata.tags == ["tag1", "tag2"]


class TestTemplate:
    """Test Template class."""

    def test_create_template(self):
        """Test creating a template."""
        metadata = TemplateMetadata(name="Test", category="general")
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        template = Template(metadata, config)

        assert template.metadata.name == "Test"
        assert template.config["prefix"] == "TEST-"

    def test_template_to_dict(self):
        """Test converting template to dictionary."""
        metadata = TemplateMetadata(name="Test", category="general")
        config = {"prefix": "TEST-", "start_number": 1}

        template = Template(metadata, config)
        data = template.to_dict()

        assert "metadata" in data
        assert "config" in data
        assert data["metadata"]["name"] == "Test"
        assert data["config"]["prefix"] == "TEST-"

    def test_template_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            "metadata": {
                "name": "Test",
                "description": "Desc",
                "category": "general"
            },
            "config": {
                "prefix": "TEST-",
                "start_number": 100
            }
        }

        template = Template.from_dict(data)

        assert template.metadata.name == "Test"
        assert template.config["prefix"] == "TEST-"
        assert template.config["start_number"] == 100

    def test_template_validation(self):
        """Test template validation."""
        metadata = TemplateMetadata(name="Test", category="general")

        # Valid config
        valid_config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }
        valid_template = Template(metadata, valid_config)
        assert valid_template.validate()

        # Invalid config (missing required fields)
        invalid_config = {"prefix": "TEST-"}
        invalid_template = Template(metadata, invalid_config)
        assert not invalid_template.validate()


class TestTemplateManager:
    """Test TemplateManager functionality."""

    @pytest.fixture
    def temp_template_dir(self):
        """Create temporary template directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_template_dir):
        """Create TemplateManager with temp directory."""
        return TemplateManager(template_dir=temp_template_dir)

    def test_default_templates_created(self, manager):
        """Test that default templates are created."""
        templates = manager.list_templates()

        # Should have at least 3 default templates
        assert len(templates) >= 3

        template_names = [t.metadata.name for t in templates]
        assert "Legal Discovery" in template_names
        assert "Confidential Documents" in template_names
        assert "Exhibit Marking" in template_names

    def test_create_template(self, manager):
        """Test creating a new template."""
        config = {
            "prefix": "CUSTOM-",
            "suffix": "-END",
            "start_number": 1,
            "padding": 6,
            "position": "top-left",
            "font_size": 12
        }

        template = manager.create_template(
            name="Custom Template",
            config=config,
            description="A custom template",
            category="custom",
            tags=["custom", "test"]
        )

        assert template is not None
        assert template.metadata.name == "Custom Template"
        assert template.config["prefix"] == "CUSTOM-"
        assert "custom" in template.metadata.tags

    def test_create_duplicate_template_error(self, manager):
        """Test error when creating template with existing name."""
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template("Test", config)

        with pytest.raises(ValueError, match="Template already exists"):
            manager.create_template("Test", config)

    def test_create_invalid_template_error(self, manager):
        """Test error when creating template with invalid config."""
        invalid_config = {"prefix": "TEST-"}  # Missing required fields

        with pytest.raises(ValueError, match="Invalid template configuration"):
            manager.create_template("Invalid", invalid_config)

    def test_get_template(self, manager):
        """Test getting a template by name."""
        # Get default template
        template = manager.get_template("Legal Discovery")

        assert template is not None
        assert template.metadata.name == "Legal Discovery"
        assert template.config["prefix"] == "DISC-"

    def test_get_nonexistent_template(self, manager):
        """Test getting template that doesn't exist."""
        template = manager.get_template("Nonexistent")
        assert template is None

    def test_list_templates_by_category(self, manager):
        """Test listing templates filtered by category."""
        # Create templates in different categories
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template("Legal1", config, category="legal-discovery")
        manager.create_template("Legal2", config, category="legal-discovery")
        manager.create_template("Conf1", config, category="confidential")

        legal_templates = manager.list_templates(category="legal-discovery")

        # Should have at least 3 (2 created + default Legal Discovery)
        assert len(legal_templates) >= 3
        assert all(t.metadata.category == "legal-discovery" for t in legal_templates)

    def test_list_templates_by_tags(self, manager):
        """Test listing templates filtered by tags."""
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template("Tagged1", config, tags=["legal", "important"])
        manager.create_template("Tagged2", config, tags=["legal", "standard"])
        manager.create_template("Tagged3", config, tags=["financial"])

        legal_templates = manager.list_templates(tags=["legal"])

        assert len(legal_templates) >= 2
        assert all(
            any("legal" in tag.lower() for tag in t.metadata.tags)
            for t in legal_templates
        )

    def test_search_templates(self, manager):
        """Test searching templates."""
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template(
            "Discovery Template",
            config,
            description="For legal discovery",
            tags=["discovery"]
        )

        # Search by name
        results = manager.search_templates("discovery")
        assert len(results) >= 1
        assert any("discovery" in t.metadata.name.lower() for t in results)

        # Search by description
        results = manager.search_templates("legal")
        assert len(results) >= 1

        # Search by tag
        results = manager.search_templates("discovery")
        assert len(results) >= 1

    def test_update_template(self, manager):
        """Test updating a template."""
        config = {
            "prefix": "OLD-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        template = manager.create_template("UpdateTest", config)

        # Update config
        new_config = config.copy()
        new_config["prefix"] = "NEW-"

        updated = manager.update_template(
            "UpdateTest",
            config=new_config,
            metadata_updates={"description": "Updated description"}
        )

        assert updated.config["prefix"] == "NEW-"
        assert updated.metadata.description == "Updated description"

    def test_update_nonexistent_template_error(self, manager):
        """Test error when updating nonexistent template."""
        with pytest.raises(ValueError, match="Template not found"):
            manager.update_template("Nonexistent", config={"prefix": "TEST-"})

    def test_delete_template(self, manager, temp_template_dir):
        """Test deleting a template."""
        config = {
            "prefix": "DEL-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template("ToDelete", config)
        manager.save_template("ToDelete")

        # Verify exists
        assert manager.get_template("ToDelete") is not None
        template_file = temp_template_dir / "ToDelete.json"
        assert template_file.exists()

        # Delete
        success = manager.delete_template("ToDelete")
        assert success

        # Verify deleted
        assert manager.get_template("ToDelete") is None
        assert not template_file.exists()

    def test_save_and_load_template(self, manager, temp_template_dir):
        """Test saving and loading templates."""
        config = {
            "prefix": "SAVE-",
            "start_number": 100,
            "padding": 8,
            "position": "top-center",
            "font_size": 14
        }

        template = manager.create_template(
            "SaveTest",
            config,
            description="Test template",
            category="custom"
        )

        # Save
        template_file = manager.save_template("SaveTest")
        assert template_file.exists()

        # Verify JSON structure
        with open(template_file) as f:
            data = json.load(f)
            assert "metadata" in data
            assert "config" in data
            assert data["metadata"]["name"] == "SaveTest"
            assert data["config"]["prefix"] == "SAVE-"

        # Load in new manager
        new_manager = TemplateManager(template_dir=temp_template_dir)
        loaded = new_manager.get_template("SaveTest")

        assert loaded is not None
        assert loaded.config["prefix"] == "SAVE-"
        assert loaded.config["start_number"] == 100

    def test_export_import_template(self, manager, temp_template_dir):
        """Test exporting and importing templates."""
        config = {
            "prefix": "EXP-",
            "suffix": "-IMP",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        template = manager.create_template(
            "ExportTest",
            config,
            description="Export test",
            category="custom"
        )

        # Export
        export_path = temp_template_dir / "exported_template.json"
        manager.export_template("ExportTest", export_path)

        assert export_path.exists()

        # Import into new manager
        new_manager = TemplateManager(template_dir=temp_template_dir / "new")
        imported = new_manager.import_template(export_path)

        assert imported is not None
        assert imported.metadata.name == "ExportTest"
        assert imported.config["prefix"] == "EXP-"
        assert imported.config["suffix"] == "-IMP"

    def test_import_overwrite_protection(self, manager, temp_template_dir):
        """Test that import protects against overwriting by default."""
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        # Create and export template
        manager.create_template("OverwriteTest", config)
        export_path = temp_template_dir / "overwrite.json"
        manager.export_template("OverwriteTest", export_path)

        # Try to import again (should fail)
        with pytest.raises(ValueError, match="Template already exists"):
            manager.import_template(export_path, overwrite=False)

        # Import with overwrite should work
        imported = manager.import_template(export_path, overwrite=True)
        assert imported is not None

    def test_duplicate_template(self, manager):
        """Test duplicating a template."""
        config = {
            "prefix": "ORIG-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right",
            "font_size": 12
        }

        original = manager.create_template(
            "Original",
            config,
            description="Original template",
            category="custom",
            tags=["original"]
        )

        # Duplicate
        duplicate = manager.duplicate_template("Original", "Duplicate")

        assert duplicate is not None
        assert duplicate.metadata.name == "Duplicate"
        assert duplicate.config["prefix"] == "ORIG-"  # Config copied
        assert duplicate.config["font_size"] == 12
        assert "original" in duplicate.metadata.tags  # Tags copied

    def test_duplicate_nonexistent_template_error(self, manager):
        """Test error when duplicating nonexistent template."""
        with pytest.raises(ValueError, match="Source template not found"):
            manager.duplicate_template("Nonexistent", "NewName")

    def test_duplicate_to_existing_name_error(self, manager):
        """Test error when duplicating to existing name."""
        config = {
            "prefix": "TEST-",
            "start_number": 1,
            "padding": 6,
            "position": "bottom-right"
        }

        manager.create_template("Template1", config)
        manager.create_template("Template2", config)

        with pytest.raises(ValueError, match="Template already exists"):
            manager.duplicate_template("Template1", "Template2")

    def test_get_categories(self, manager):
        """Test getting template categories."""
        categories = manager.get_categories()

        assert "legal-discovery" in categories
        assert "confidential" in categories
        assert "exhibits" in categories
        assert "general" in categories
        assert "custom" in categories

    def test_get_templates_by_category(self, manager):
        """Test getting templates by category."""
        legal_templates = manager.get_templates_by_category("legal-discovery")

        # Should have at least the default Legal Discovery template
        assert len(legal_templates) >= 1
        assert all(t.metadata.category == "legal-discovery" for t in legal_templates)


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def manager(self):
        """Create TemplateManager with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield TemplateManager(template_dir=tmpdir)

    def test_save_nonexistent_template(self, manager):
        """Test saving template that doesn't exist."""
        with pytest.raises(ValueError, match="Template not found"):
            manager.save_template("Nonexistent")

    def test_export_nonexistent_template(self, manager):
        """Test exporting template that doesn't exist."""
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
            with pytest.raises(ValueError, match="Template not found"):
                manager.export_template("Nonexistent", tmp.name)

    def test_import_nonexistent_file(self, manager):
        """Test importing from file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            manager.import_template("/nonexistent/path.json")

    def test_empty_search_query(self, manager):
        """Test search with empty query."""
        results = manager.search_templates("")
        # Should return all templates
        assert len(results) >= 0

    def test_list_templates_invalid_category(self, manager):
        """Test listing templates with invalid category."""
        results = manager.list_templates(category="nonexistent")
        assert len(results) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
