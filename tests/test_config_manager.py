"""Tests for configuration manager module."""

import json
import os
import pytest
from pathlib import Path
from bates_labeler.config_manager import (
    BatesConfig,
    ConfigManager,
    load_config_from_env,
    PYDANTIC_AVAILABLE
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def config_manager(temp_config_dir):
    """Create ConfigManager instance."""
    return ConfigManager(config_dir=temp_config_dir)


class TestBatesConfig:
    """Test BatesConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        if PYDANTIC_AVAILABLE:
            config = BatesConfig()
            assert config.prefix == ""
            assert config.suffix == ""
            assert config.start_number == 1
            assert config.padding == 6
            assert config.position == "top-right"
            assert config.font_name == "Helvetica"
            assert config.font_size == 10

    def test_custom_config(self):
        """Test custom configuration."""
        if PYDANTIC_AVAILABLE:
            config = BatesConfig(
                prefix="CASE-",
                suffix="-CONF",
                start_number=100,
                padding=4
            )
            assert config.prefix == "CASE-"
            assert config.suffix == "-CONF"
            assert config.start_number == 100
            assert config.padding == 4

    def test_rgb_validation(self):
        """Test RGB color validation."""
        if PYDANTIC_AVAILABLE:
            # Valid RGB
            config = BatesConfig(font_color=(255, 0, 0))
            assert config.font_color == (255, 0, 0)

            # Invalid RGB should raise error
            with pytest.raises(Exception):
                BatesConfig(font_color=(300, 0, 0))  # > 255


class TestConfigManager:
    """Test ConfigManager class."""

    def test_initialization(self, config_manager, temp_config_dir):
        """Test manager initialization."""
        assert config_manager.config_dir == temp_config_dir
        assert temp_config_dir.exists()

    def test_create_config(self, config_manager):
        """Test configuration creation."""
        config = config_manager.create_config(
            "test_config",
            {"prefix": "TEST-", "start_number": 1}
        )

        assert config is not None
        assert config_manager.get_config("test_config") == config

    def test_get_config(self, config_manager):
        """Test configuration retrieval."""
        config_manager.create_config("test", {})

        retrieved = config_manager.get_config("test")
        assert retrieved is not None

        # Non-existent config
        assert config_manager.get_config("nonexistent") is None

    def test_list_configs(self, config_manager):
        """Test configuration listing."""
        config_manager.create_config("config1", {})
        config_manager.create_config("config2", {})

        configs = config_manager.list_configs()
        assert "config1" in configs
        assert "config2" in configs

    def test_delete_config(self, config_manager):
        """Test configuration deletion."""
        config_manager.create_config("test", {})
        assert config_manager.get_config("test") is not None

        deleted = config_manager.delete_config("test")
        assert deleted is True
        assert config_manager.get_config("test") is None

        # Delete non-existent
        deleted = config_manager.delete_config("nonexistent")
        assert deleted is False

    def test_save_and_load_config(self, config_manager):
        """Test configuration persistence."""
        config = config_manager.create_config(
            "save_test",
            {"prefix": "SAVE-", "start_number": 50}
        )

        # Save
        saved_path = config_manager.save_config("save_test")
        assert saved_path.exists()

        # Create new manager and load
        new_manager = ConfigManager(config_dir=config_manager.config_dir)
        loaded = new_manager.load_config("save_test")

        if PYDANTIC_AVAILABLE:
            assert loaded.prefix == "SAVE-"
            assert loaded.start_number == 50

    def test_export_import_config(self, config_manager, tmp_path):
        """Test configuration export/import."""
        config_manager.create_config(
            "export_test",
            {"prefix": "EXP-"}
        )

        # Export
        export_path = tmp_path / "exported.json"
        config_manager.export_config("export_test", export_path)
        assert export_path.exists()

        # Import with new name
        imported = config_manager.import_config("imported", export_path)
        assert imported is not None
        assert config_manager.get_config("imported") is not None

    def test_config_inheritance(self, config_manager):
        """Test configuration inheritance."""
        # Create parent config
        parent = config_manager.create_config(
            "parent",
            {"prefix": "PARENT-", "start_number": 1}
        )

        # Create child with inheritance
        child = config_manager.create_config(
            "child",
            {"suffix": "-CHILD"},
            parent="parent"
        )

        if PYDANTIC_AVAILABLE:
            # Child should inherit parent's prefix
            assert child.prefix == "PARENT-"
            # But have its own suffix
            assert child.suffix == "-CHILD"

    def test_default_config(self, config_manager):
        """Test default configuration."""
        default = config_manager.get_default_config()
        assert default is not None

        # Set different config as default
        config_manager.create_config("custom", {"prefix": "CUSTOM-"})
        config_manager.set_as_default("custom")

        assert config_manager._default_config_name == "custom"


class TestEnvironmentConfig:
    """Test environment variable configuration."""

    def test_load_from_env(self):
        """Test loading config from environment variables."""
        # Set environment variables
        os.environ['BATES_PREFIX'] = 'ENV-'
        os.environ['BATES_START_NUMBER'] = '100'
        os.environ['BATES_ENABLE_OCR'] = 'true'

        config = load_config_from_env()

        assert config['prefix'] == 'ENV-'
        assert config['start_number'] == 100
        assert config['enable_ocr'] is True

        # Cleanup
        del os.environ['BATES_PREFIX']
        del os.environ['BATES_START_NUMBER']
        del os.environ['BATES_ENABLE_OCR']

    def test_env_type_conversion(self):
        """Test environment variable type conversion."""
        os.environ['BATES_TEST_INT'] = '42'
        os.environ['BATES_TEST_FLOAT'] = '3.14'
        os.environ['BATES_TEST_BOOL'] = 'false'
        os.environ['BATES_TEST_STRING'] = 'hello'

        config = load_config_from_env()

        assert config['test_int'] == 42
        assert config['test_float'] == 3.14
        assert config['test_bool'] is False
        assert config['test_string'] == 'hello'

        # Cleanup
        for key in list(os.environ.keys()):
            if key.startswith('BATES_TEST'):
                del os.environ[key]


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_padding(self):
        """Test invalid padding value."""
        if PYDANTIC_AVAILABLE:
            with pytest.raises(Exception):
                BatesConfig(padding=0)  # < 1

            with pytest.raises(Exception):
                BatesConfig(padding=20)  # > 10

    def test_invalid_position(self):
        """Test invalid position value."""
        if PYDANTIC_AVAILABLE:
            with pytest.raises(Exception):
                BatesConfig(position="invalid-position")

    def test_logo_path_validation(self):
        """Test logo path validation."""
        if PYDANTIC_AVAILABLE:
            # Should fail if enable_logo but no logo_path
            with pytest.raises(Exception):
                BatesConfig(enable_logo=True, logo_path=None)
