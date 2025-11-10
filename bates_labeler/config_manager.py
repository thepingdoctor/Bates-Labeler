"""Enhanced Configuration Manager for Bates-Labeler.

This module provides centralized, validated configuration management with support for:
- Environment-specific configurations
- Configuration inheritance
- Type validation with Pydantic
- JSON/YAML import/export
- Default value management
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from datetime import datetime

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # type: ignore


class BatesConfig(BaseModel if PYDANTIC_AVAILABLE else object):
    """Configuration model for Bates numbering operations.

    Attributes:
        prefix: Bates number prefix
        suffix: Bates number suffix
        start_number: Starting number for sequence
        padding: Number of digits to pad
        position: Position on page (top-left, top-center, etc.)
        font_name: Font name for Bates numbers
        font_size: Font size in points
        font_color: RGB tuple for font color
        opacity: Opacity level (0.0-1.0)
        enable_watermark: Whether to add watermark
        watermark_text: Text for watermark
        enable_qr: Whether to add QR codes
        enable_logo: Whether to add logo
        logo_path: Path to logo file
    """

    # Core Bates settings
    prefix: str = Field(default="", description="Bates number prefix")
    suffix: str = Field(default="", description="Bates number suffix")
    start_number: int = Field(default=1, ge=1, description="Starting number")
    padding: int = Field(default=6, ge=1, le=10, description="Number padding")

    # Positioning
    position: str = Field(
        default="top-right",
        description="Position on page",
        pattern="^(top|bottom)-(left|center|right)$"
    )

    # Font settings
    font_name: str = Field(default="Helvetica", description="Font name")
    font_size: int = Field(default=10, ge=6, le=72, description="Font size")
    font_color: tuple = Field(default=(0, 0, 0), description="RGB color")

    # Visual effects
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Opacity")
    enable_watermark: bool = Field(default=False, description="Enable watermark")
    watermark_text: Optional[str] = Field(default=None, description="Watermark text")

    # Advanced features
    enable_qr: bool = Field(default=False, description="Enable QR codes")
    enable_logo: bool = Field(default=False, description="Enable logo")
    logo_path: Optional[str] = Field(default=None, description="Logo file path")

    # Processing options
    enable_ocr: bool = Field(default=False, description="Enable OCR")
    enable_ai_analysis: bool = Field(default=False, description="Enable AI analysis")

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    @validator('font_color')
    def validate_rgb(cls, v):
        """Validate RGB color tuple."""
        if not isinstance(v, (tuple, list)) or len(v) != 3:
            raise ValueError("font_color must be RGB tuple with 3 values")
        if not all(0 <= x <= 255 for x in v):
            raise ValueError("RGB values must be between 0 and 255")
        return tuple(v)

    @validator('logo_path')
    def validate_logo_path(cls, v, values):
        """Validate logo path if logo is enabled."""
        if values.get('enable_logo') and not v:
            raise ValueError("logo_path required when enable_logo is True")
        if v and not Path(v).exists():
            raise ValueError(f"Logo file not found: {v}")
        return v


class ConfigManager:
    """Centralized configuration management system.

    Features:
    - Load/save configurations from JSON
    - Environment-specific configs
    - Configuration inheritance
    - Validation with Pydantic
    - Default value management
    """

    def __init__(self, config_dir: Optional[Union[str, Path]] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Directory for storing configurations.
                       Defaults to ~/.bates-labeler/configs
        """
        if config_dir is None:
            config_dir = Path.home() / ".bates-labeler" / "configs"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._configs: Dict[str, BatesConfig] = {}
        self._default_config_name = "default"

    def create_config(
        self,
        name: str,
        config_dict: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None
    ) -> BatesConfig:
        """Create a new configuration.

        Args:
            name: Configuration name
            config_dict: Configuration parameters
            parent: Parent configuration for inheritance

        Returns:
            Created configuration object

        Raises:
            ValueError: If parent doesn't exist or validation fails
        """
        if config_dict is None:
            config_dict = {}

        # Handle inheritance
        if parent:
            parent_config = self.get_config(parent)
            if not parent_config:
                raise ValueError(f"Parent configuration not found: {parent}")

            # Merge parent config with new config
            parent_dict = parent_config.dict() if PYDANTIC_AVAILABLE else vars(parent_config)
            merged_dict = {**parent_dict, **config_dict}
            config_dict = merged_dict

        # Create and validate config
        if PYDANTIC_AVAILABLE:
            config = BatesConfig(**config_dict)
        else:
            # Fallback for no Pydantic
            config = type('BatesConfig', (), config_dict)()

        self._configs[name] = config
        return config

    def get_config(self, name: str) -> Optional[BatesConfig]:
        """Get configuration by name.

        Args:
            name: Configuration name

        Returns:
            Configuration object or None if not found
        """
        return self._configs.get(name)

    def list_configs(self) -> list:
        """List all available configuration names.

        Returns:
            List of configuration names
        """
        return list(self._configs.keys())

    def delete_config(self, name: str) -> bool:
        """Delete a configuration.

        Args:
            name: Configuration name

        Returns:
            True if deleted, False if not found
        """
        if name in self._configs:
            del self._configs[name]

            # Delete saved file
            config_file = self.config_dir / f"{name}.json"
            if config_file.exists():
                config_file.unlink()

            return True
        return False

    def save_config(self, name: str, config: Optional[BatesConfig] = None) -> Path:
        """Save configuration to disk.

        Args:
            name: Configuration name
            config: Configuration object (uses cached if None)

        Returns:
            Path to saved configuration file

        Raises:
            ValueError: If configuration not found
        """
        if config is None:
            config = self.get_config(name)
            if config is None:
                raise ValueError(f"Configuration not found: {name}")

        # Convert to dict
        if PYDANTIC_AVAILABLE:
            config_dict = config.dict()
        else:
            config_dict = vars(config)

        # Add metadata
        config_dict['_metadata'] = {
            'name': name,
            'created': datetime.now().isoformat(),
            'version': '1.1.1'
        }

        # Save to file
        config_file = self.config_dir / f"{name}.json"
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

        return config_file

    def load_config(self, name: str) -> BatesConfig:
        """Load configuration from disk.

        Args:
            name: Configuration name

        Returns:
            Loaded configuration object

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
        """
        config_file = self.config_dir / f"{name}.json"

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_file, 'r') as f:
            config_dict = json.load(f)

        # Remove metadata
        config_dict.pop('_metadata', None)

        # Create config
        config = self.create_config(name, config_dict)
        return config

    def export_config(self, name: str, output_path: Union[str, Path]) -> Path:
        """Export configuration to specified path.

        Args:
            name: Configuration name
            output_path: Output file path

        Returns:
            Path to exported file
        """
        config = self.get_config(name)
        if config is None:
            raise ValueError(f"Configuration not found: {name}")

        output_path = Path(output_path)

        if PYDANTIC_AVAILABLE:
            config_dict = config.dict()
        else:
            config_dict = vars(config)

        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2)

        return output_path

    def import_config(self, name: str, input_path: Union[str, Path]) -> BatesConfig:
        """Import configuration from file.

        Args:
            name: Name for imported configuration
            input_path: Input file path

        Returns:
            Imported configuration object

        Raises:
            FileNotFoundError: If input file doesn't exist
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {input_path}")

        with open(input_path, 'r') as f:
            config_dict = json.load(f)

        config = self.create_config(name, config_dict)
        self.save_config(name, config)

        return config

    def get_default_config(self) -> BatesConfig:
        """Get or create default configuration.

        Returns:
            Default configuration object
        """
        config = self.get_config(self._default_config_name)

        if config is None:
            config = self.create_config(self._default_config_name, {})
            self.save_config(self._default_config_name, config)

        return config

    def set_as_default(self, name: str) -> None:
        """Set a configuration as the default.

        Args:
            name: Configuration name to set as default

        Raises:
            ValueError: If configuration doesn't exist
        """
        config = self.get_config(name)
        if config is None:
            raise ValueError(f"Configuration not found: {name}")

        self._default_config_name = name


def load_config_from_env() -> Dict[str, Any]:
    """Load configuration from environment variables.

    Environment variables should be prefixed with BATES_

    Returns:
        Dictionary of configuration values
    """
    config = {}
    prefix = "BATES_"

    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()

            # Type conversion
            if value.lower() in ('true', 'false'):
                config[config_key] = value.lower() == 'true'
            elif value.isdigit():
                config[config_key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                config[config_key] = float(value)
            else:
                config[config_key] = value

    return config
