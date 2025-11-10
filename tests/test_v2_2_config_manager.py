"""
Comprehensive Test Suite for Configuration Manager (v2.2.0 Feature #1)

Tests configuration management functionality including:
- Configuration creation and validation
- Configuration inheritance
- Import/export functionality
- Environment variable loading
- Default configuration management
"""

import json
import os
import pytest
import tempfile
from pathlib import Path
from bates_labeler.config_manager import (
    BatesConfig,
    ConfigManager,
    load_config_from_env,
    PYDANTIC_AVAILABLE
)


class TestBatesConfig:
    """Test BatesConfig model validation."""

    def test_default_config_creation(self):
        """Test creating config with default values."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        config = BatesConfig()
        assert config.prefix == ""
        assert config.suffix == ""
        assert config.start_number == 1
        assert config.padding == 6
        assert config.position == "top-right"
        assert config.font_name == "Helvetica"
        assert config.font_size == 10

    def test_custom_config_creation(self):
        """Test creating config with custom values."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        config = BatesConfig(
            prefix="TEST-",
            suffix="-CONF",
            start_number=100,
            padding=8,
            font_size=14
        )
        assert config.prefix == "TEST-"
        assert config.suffix == "-CONF"
        assert config.start_number == 100
        assert config.padding == 8
        assert config.font_size == 14

    def test_position_validation(self):
        """Test position field validation."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        # Valid positions
        config = BatesConfig(position="top-left")
        assert config.position == "top-left"

        config = BatesConfig(position="bottom-right")
        assert config.position == "bottom-right"

    def test_rgb_color_validation(self):
        """Test RGB color tuple validation."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        # Valid RGB
        config = BatesConfig(font_color=(255, 0, 0))
        assert config.font_color == (255, 0, 0)

        # Invalid RGB should raise error
        with pytest.raises(ValueError):
            BatesConfig(font_color=(256, 0, 0))  # Out of range

        with pytest.raises(ValueError):
            BatesConfig(font_color=(255, 0))  # Wrong length

    def test_number_range_validation(self):
        """Test number range validation."""
        if not PYDANTIC_AVAILABLE:
            pytest.skip("Pydantic not available")

        # Valid ranges
        config = BatesConfig(start_number=1, padding=6, font_size=10)
        assert config.start_number == 1
        assert config.padding == 6
        assert config.font_size == 10

        # Invalid ranges should raise error
        with pytest.raises(ValueError):
            BatesConfig(start_number=0)  # Below minimum

        with pytest.raises(ValueError):
            BatesConfig(padding=11)  # Above maximum


class TestConfigManager:
    """Test ConfigManager functionality."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_config_dir):
        """Create ConfigManager with temp directory."""
        return ConfigManager(config_dir=temp_config_dir)

    def test_create_config(self, manager):
        """Test creating a new configuration."""
        config = manager.create_config(
            name="test_config",
            config_dict={
                "prefix": "TEST-",
                "start_number": 100,
                "padding": 6
            }
        )

        assert config is not None
        if PYDANTIC_AVAILABLE:
            assert config.prefix == "TEST-"
            assert config.start_number == 100

        # Verify it's stored
        retrieved = manager.get_config("test_config")
        assert retrieved is not None

    def test_config_inheritance(self, manager):
        """Test configuration inheritance."""
        # Create parent config
        parent = manager.create_config(
            name="parent",
            config_dict={
                "prefix": "PARENT-",
                "start_number": 1,
                "padding": 6,
                "font_size": 12
            }
        )

        # Create child with inheritance
        child = manager.create_config(
            name="child",
            config_dict={
                "prefix": "CHILD-",  # Override
                "suffix": "-TEST"    # New
            },
            parent="parent"
        )

        if PYDANTIC_AVAILABLE:
            assert child.prefix == "CHILD-"  # Overridden
            assert child.suffix == "-TEST"   # New
            assert child.start_number == 1   # Inherited
            assert child.padding == 6        # Inherited
            assert child.font_size == 12     # Inherited

    def test_save_and_load_config(self, manager, temp_config_dir):
        """Test saving and loading configurations."""
        # Create and save
        config = manager.create_config(
            name="save_test",
            config_dict={
                "prefix": "SAVE-",
                "start_number": 50
            }
        )
        config_file = manager.save_config("save_test")

        assert config_file.exists()
        assert config_file.name == "save_test.json"

        # Verify JSON structure
        with open(config_file) as f:
            data = json.load(f)
            assert "_metadata" in data
            assert data["_metadata"]["name"] == "save_test"
            assert data["_metadata"]["version"] == "1.1.1"

        # Load in new manager
        new_manager = ConfigManager(config_dir=temp_config_dir)
        loaded = new_manager.load_config("save_test")

        assert loaded is not None
        if PYDANTIC_AVAILABLE:
            assert loaded.prefix == "SAVE-"
            assert loaded.start_number == 50

    def test_export_import_config(self, manager, temp_config_dir):
        """Test exporting and importing configurations."""
        # Create config
        config = manager.create_config(
            name="export_test",
            config_dict={
                "prefix": "EXP-",
                "suffix": "-IMP",
                "padding": 8
            }
        )

        # Export
        export_path = temp_config_dir / "exported.json"
        manager.export_config("export_test", export_path)

        assert export_path.exists()

        # Import into new manager
        new_manager = ConfigManager(config_dir=temp_config_dir / "new")
        imported = new_manager.import_config("imported_config", export_path)

        assert imported is not None
        if PYDANTIC_AVAILABLE:
            assert imported.prefix == "EXP-"
            assert imported.suffix == "-IMP"
            assert imported.padding == 8

    def test_default_config(self, manager):
        """Test default configuration management."""
        default = manager.get_default_config()
        assert default is not None

        # Create custom config and set as default
        manager.create_config(
            name="custom_default",
            config_dict={"prefix": "DEFAULT-"}
        )
        manager.set_as_default("custom_default")

        assert manager._default_config_name == "custom_default"

    def test_list_configs(self, manager):
        """Test listing configurations."""
        # Create multiple configs
        manager.create_config("config1", {"prefix": "C1-"})
        manager.create_config("config2", {"prefix": "C2-"})
        manager.create_config("config3", {"prefix": "C3-"})

        configs = manager.list_configs()
        assert len(configs) >= 3
        assert "config1" in configs
        assert "config2" in configs
        assert "config3" in configs

    def test_delete_config(self, manager, temp_config_dir):
        """Test deleting configurations."""
        # Create and save config
        manager.create_config("to_delete", {"prefix": "DEL-"})
        manager.save_config("to_delete")

        # Verify it exists
        assert manager.get_config("to_delete") is not None
        config_file = temp_config_dir / "to_delete.json"
        assert config_file.exists()

        # Delete
        success = manager.delete_config("to_delete")
        assert success

        # Verify deleted
        assert manager.get_config("to_delete") is None
        assert not config_file.exists()

    def test_invalid_parent_inheritance(self, manager):
        """Test error handling for invalid parent."""
        with pytest.raises(ValueError, match="Parent configuration not found"):
            manager.create_config(
                name="child",
                config_dict={"prefix": "CHILD-"},
                parent="nonexistent"
            )


class TestEnvironmentLoading:
    """Test loading configuration from environment variables."""

    def test_load_from_env(self, monkeypatch):
        """Test loading config from environment variables."""
        # Set environment variables
        monkeypatch.setenv("BATES_PREFIX", "ENV-")
        monkeypatch.setenv("BATES_SUFFIX", "-TEST")
        monkeypatch.setenv("BATES_START_NUMBER", "100")
        monkeypatch.setenv("BATES_PADDING", "8")
        monkeypatch.setenv("BATES_ENABLE_WATERMARK", "true")
        monkeypatch.setenv("BATES_FONT_SIZE", "12")

        config = load_config_from_env()

        assert config["prefix"] == "ENV-"
        assert config["suffix"] == "-TEST"
        assert config["start_number"] == 100  # Converted to int
        assert config["padding"] == 8
        assert config["enable_watermark"] is True  # Converted to bool
        assert config["font_size"] == 12

    def test_env_boolean_parsing(self, monkeypatch):
        """Test boolean environment variable parsing."""
        monkeypatch.setenv("BATES_ENABLE_QR", "true")
        monkeypatch.setenv("BATES_ENABLE_LOGO", "false")

        config = load_config_from_env()

        assert config["enable_qr"] is True
        assert config["enable_logo"] is False

    def test_env_empty_when_no_vars(self, monkeypatch):
        """Test that config is empty when no BATES_ vars set."""
        # Clear any BATES_ variables
        for key in list(os.environ.keys()):
            if key.startswith("BATES_"):
                monkeypatch.delenv(key, raising=False)

        config = load_config_from_env()
        assert config == {}


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def manager(self):
        """Create ConfigManager with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ConfigManager(config_dir=tmpdir)

    def test_get_nonexistent_config(self, manager):
        """Test getting config that doesn't exist."""
        config = manager.get_config("nonexistent")
        assert config is None

    def test_save_nonexistent_config(self, manager):
        """Test saving config that doesn't exist."""
        with pytest.raises(ValueError, match="Configuration not found"):
            manager.save_config("nonexistent")

    def test_load_nonexistent_file(self, manager):
        """Test loading config file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            manager.load_config("nonexistent")

    def test_export_nonexistent_config(self, manager):
        """Test exporting config that doesn't exist."""
        with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
            with pytest.raises(ValueError, match="Configuration not found"):
                manager.export_config("nonexistent", tmp.name)

    def test_set_nonexistent_as_default(self, manager):
        """Test setting nonexistent config as default."""
        with pytest.raises(ValueError, match="Configuration not found"):
            manager.set_as_default("nonexistent")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
