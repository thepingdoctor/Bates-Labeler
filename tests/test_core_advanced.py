"""Tests for advanced BatesNumberer features (logo, QR, watermark, borders)."""

import pytest
import os
import tempfile
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

from bates_labeler import BatesNumberer


class TestLogoFeatures:
    """Test cases for logo upload and placement functionality."""

    def setup_method(self):
        """Create temporary test logo files."""
        self.temp_dir = tempfile.mkdtemp()

        # Create a simple PNG logo
        self.png_logo = os.path.join(self.temp_dir, "logo.png")
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(self.png_logo)

    def teardown_method(self):
        """Clean up temporary files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_logo_loading_png(self):
        """Test loading PNG logo file."""
        numberer = BatesNumberer(logo_path=self.png_logo)
        assert numberer.logo_image is not None
        assert numberer.logo_image['type'] == 'raster'
        assert 'width' in numberer.logo_image
        assert 'height' in numberer.logo_image

    def test_logo_loading_nonexistent(self):
        """Test handling of nonexistent logo file."""
        numberer = BatesNumberer(logo_path="/nonexistent/logo.png")
        assert numberer.logo_image is None

    def test_logo_placement_options(self):
        """Test all logo placement options initialize correctly."""
        placements = [
            'above_bates', 'top-left', 'top-center', 'top-right',
            'bottom-left', 'bottom-center', 'bottom-right'
        ]

        for placement in placements:
            numberer = BatesNumberer(
                logo_path=self.png_logo,
                logo_placement=placement
            )
            assert numberer.logo_placement == placement
            assert numberer.logo_image is not None

    def test_logo_size_constraints(self):
        """Test logo max width and height settings."""
        numberer = BatesNumberer(
            logo_path=self.png_logo,
            logo_max_width=1.5,
            logo_max_height=1.5
        )
        # Sizes should be converted to points (inches * 72)
        assert numberer.logo_max_width == 1.5 * 72
        assert numberer.logo_max_height == 1.5 * 72


class TestQRCodeFeatures:
    """Test cases for QR code generation and placement."""

    def test_qr_code_initialization(self):
        """Test QR code feature initialization."""
        numberer = BatesNumberer(
            enable_qr=True,
            qr_placement='all_pages',
            qr_position='bottom-right',
            qr_size=1.0
        )
        assert numberer.enable_qr is True
        assert numberer.qr_placement == 'all_pages'
        assert numberer.qr_position == 'bottom-right'
        assert numberer.qr_size == 72.0  # 1 inch = 72 points

    def test_qr_code_disabled(self):
        """Test QR code disabled by default."""
        numberer = BatesNumberer()
        assert numberer.enable_qr is False

    def test_qr_code_colors(self):
        """Test QR code color customization."""
        numberer = BatesNumberer(
            enable_qr=True,
            qr_color='blue',
            qr_background_color='white'
        )
        assert numberer.qr_color == 'blue'
        assert numberer.qr_background_color == 'white'

    def test_qr_code_generation(self):
        """Test QR code image generation."""
        numberer = BatesNumberer(enable_qr=True)
        qr_path = numberer._create_qr_code("TEST-0001")

        assert qr_path is not None
        assert os.path.exists(qr_path)

        # Verify it's a valid PNG image
        img = Image.open(qr_path)
        assert img.format == 'PNG'

        # Clean up
        os.remove(qr_path)

    def test_qr_placement_modes(self):
        """Test different QR placement modes."""
        modes = ['all_pages', 'separator_only', 'disabled']

        for mode in modes:
            numberer = BatesNumberer(
                enable_qr=(mode != 'disabled'),
                qr_placement=mode
            )
            assert numberer.qr_placement == mode


class TestWatermarkFeatures:
    """Test cases for watermark functionality."""

    def test_watermark_initialization(self):
        """Test watermark feature initialization."""
        numberer = BatesNumberer(
            enable_watermark=True,
            watermark_text="CONFIDENTIAL",
            watermark_scope='all_pages',
            watermark_opacity=0.5,
            watermark_rotation=45
        )
        assert numberer.enable_watermark is True
        assert numberer.watermark_text == "CONFIDENTIAL"
        assert numberer.watermark_scope == 'all_pages'
        assert numberer.watermark_opacity == 0.5
        assert numberer.watermark_rotation == 45

    def test_watermark_disabled(self):
        """Test watermark disabled by default."""
        numberer = BatesNumberer()
        assert numberer.enable_watermark is False

    def test_watermark_opacity_range(self):
        """Test watermark opacity accepts valid range."""
        # Valid opacity values
        for opacity in [0.0, 0.3, 0.5, 0.7, 1.0]:
            numberer = BatesNumberer(
                enable_watermark=True,
                watermark_opacity=opacity
            )
            assert numberer.watermark_opacity == opacity

    def test_watermark_rotation_angles(self):
        """Test watermark rotation with different angles."""
        for angle in [0, 45, 90, 180, 270, 360]:
            numberer = BatesNumberer(
                enable_watermark=True,
                watermark_rotation=angle
            )
            assert numberer.watermark_rotation == angle

    def test_watermark_positions(self):
        """Test all watermark position options."""
        positions = [
            'center', 'top-left', 'top-center', 'top-right',
            'bottom-left', 'bottom-center', 'bottom-right'
        ]

        for position in positions:
            numberer = BatesNumberer(
                enable_watermark=True,
                watermark_position=position
            )
            assert numberer.watermark_position == position

    def test_watermark_scope_options(self):
        """Test watermark scope settings."""
        scopes = ['all_pages', 'document_only', 'disabled']

        for scope in scopes:
            numberer = BatesNumberer(
                enable_watermark=(scope != 'disabled'),
                watermark_scope=scope
            )
            assert numberer.watermark_scope == scope


class TestBorderFeatures:
    """Test cases for border styling on separator pages."""

    def test_border_initialization(self):
        """Test border feature initialization."""
        numberer = BatesNumberer(
            enable_border=True,
            border_style='solid',
            border_color='black',
            border_width=2.0
        )
        assert numberer.enable_border is True
        assert numberer.border_style == 'solid'
        assert numberer.border_width == 2.0

    def test_border_disabled(self):
        """Test border disabled by default."""
        numberer = BatesNumberer()
        assert numberer.enable_border is False

    def test_border_styles(self):
        """Test all border style options."""
        styles = ['solid', 'dashed', 'double', 'asterisks']

        for style in styles:
            numberer = BatesNumberer(
                enable_border=True,
                border_style=style
            )
            assert numberer.border_style == style

    def test_border_colors(self):
        """Test border color options."""
        colors = ['black', 'blue', 'red', 'green', 'gray']

        for color in colors:
            numberer = BatesNumberer(
                enable_border=True,
                border_color=color
            )
            # Color should be parsed to reportlab Color object
            assert numberer.border_color is not None

    def test_border_width_range(self):
        """Test border width accepts various values."""
        for width in [1.0, 2.0, 5.0, 10.0]:
            numberer = BatesNumberer(
                enable_border=True,
                border_width=width
            )
            assert numberer.border_width == width

    def test_border_corner_radius(self):
        """Test border corner radius for rounded borders."""
        for radius in [0, 5, 10, 20]:
            numberer = BatesNumberer(
                enable_border=True,
                border_style='solid',
                border_corner_radius=radius
            )
            assert numberer.border_corner_radius == radius


class TestCustomFontFeatures:
    """Test cases for custom font upload and registration."""

    def test_custom_font_path_nonexistent(self):
        """Test handling of nonexistent custom font file."""
        numberer = BatesNumberer(custom_font_path="/nonexistent/font.ttf")
        # Should fall back to default font
        assert numberer.custom_font_name is None
        assert numberer.font_name in ['Helvetica', 'Helvetica-Bold']

    def test_custom_font_unsupported_format(self):
        """Test handling of unsupported font format."""
        temp_dir = tempfile.mkdtemp()
        fake_font = os.path.join(temp_dir, "font.txt")

        # Create fake file
        with open(fake_font, 'w') as f:
            f.write("not a font")

        numberer = BatesNumberer(custom_font_path=fake_font)
        # Should fall back to default font
        assert numberer.custom_font_name is None

        # Clean up
        import shutil
        shutil.rmtree(temp_dir)


class TestCallbackFeatures:
    """Test cases for status and cancel callbacks."""

    def test_status_callback(self):
        """Test status callback is called during processing."""
        messages = []

        def status_callback(message, progress_dict=None):
            messages.append(message)

        numberer = BatesNumberer(status_callback=status_callback)
        assert numberer.status_callback is not None

        # Callback should be stored
        numberer.status_callback("Test message")
        assert "Test message" in messages

    def test_cancel_callback(self):
        """Test cancel callback functionality."""
        cancel_flag = [False]

        def cancel_callback():
            return cancel_flag[0]

        numberer = BatesNumberer(cancel_callback=cancel_callback)
        assert numberer.cancel_callback is not None

        # Initially should not be cancelled
        assert numberer.cancel_callback() is False

        # Set cancel flag
        cancel_flag[0] = True
        assert numberer.cancel_callback() is True


class TestColorParsing:
    """Test cases for color parsing functionality."""

    def test_named_colors(self):
        """Test parsing of named colors."""
        colors = ['black', 'blue', 'red', 'green', 'gray', 'grey']

        for color_name in colors:
            numberer = BatesNumberer(font_color=color_name)
            assert numberer.font_color is not None

    def test_hex_colors(self):
        """Test parsing of hex color codes."""
        hex_colors = ['#000000', '#FF0000', '#00FF00', '#0000FF', '#FFFFFF']

        for hex_color in hex_colors:
            numberer = BatesNumberer(font_color=hex_color)
            assert numberer.font_color is not None

    def test_invalid_color_fallback(self):
        """Test fallback to black for invalid colors."""
        numberer = BatesNumberer(font_color="invalid_color")
        # Should fall back to black
        assert numberer.font_color is not None


class TestDateTimestamp:
    """Test cases for date/time stamping functionality."""

    def test_date_stamp_enabled(self):
        """Test date stamp can be enabled."""
        numberer = BatesNumberer(include_date=True)
        assert numberer.include_date is True

    def test_date_stamp_disabled(self):
        """Test date stamp disabled by default."""
        numberer = BatesNumberer()
        assert numberer.include_date is False

    def test_date_format_customization(self):
        """Test custom date format strings."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%b-%Y', '%Y/%m/%d %H:%M']

        for date_format in formats:
            numberer = BatesNumberer(
                include_date=True,
                date_format=date_format
            )
            assert numberer.date_format == date_format


class TestBackgroundPadding:
    """Test cases for text background and padding."""

    def test_background_enabled(self):
        """Test white background is enabled by default."""
        numberer = BatesNumberer()
        assert numberer.add_background is True

    def test_background_disabled(self):
        """Test background can be disabled."""
        numberer = BatesNumberer(add_background=False)
        assert numberer.add_background is False

    def test_background_padding_values(self):
        """Test various background padding values."""
        for padding in [0, 3, 5, 10]:
            numberer = BatesNumberer(background_padding=padding)
            assert numberer.background_padding == padding
