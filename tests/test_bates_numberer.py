"""Tests for BatesNumberer class."""

import pytest
from bates_labeler import BatesNumberer


class TestBatesNumberer:
    """Test cases for BatesNumberer class."""
    
    def test_initialization_defaults(self):
        """Test BatesNumberer initializes with default values."""
        numberer = BatesNumberer()
        assert numberer.prefix == ""
        assert numberer.current_number == 1
        assert numberer.padding == 4
        assert numberer.suffix == ""
        assert numberer.position == "bottom-left"
    
    def test_initialization_custom(self):
        """Test BatesNumberer initializes with custom values."""
        numberer = BatesNumberer(
            prefix="CASE-",
            start_number=100,
            padding=6,
            suffix="-CONF"
        )
        assert numberer.prefix == "CASE-"
        assert numberer.current_number == 100
        assert numberer.padding == 6
        assert numberer.suffix == "-CONF"
    
    def test_get_next_bates_number(self):
        """Test Bates number generation."""
        numberer = BatesNumberer(prefix="TEST-", start_number=1, padding=4)
        
        # First number
        bates1 = numberer.get_next_bates_number()
        assert bates1 == "TEST-0001"
        
        # Second number
        bates2 = numberer.get_next_bates_number()
        assert bates2 == "TEST-0002"
        
        # Third number
        bates3 = numberer.get_next_bates_number()
        assert bates3 == "TEST-0003"
    
    def test_get_next_bates_number_with_suffix(self):
        """Test Bates number generation with suffix."""
        numberer = BatesNumberer(
            prefix="DOC-",
            suffix="-CONF",
            start_number=50,
            padding=3
        )
        
        bates = numberer.get_next_bates_number()
        assert bates == "DOC-050-CONF"
    
    def test_padding_various_widths(self):
        """Test different padding widths."""
        # Padding of 6
        numberer1 = BatesNumberer(prefix="A-", padding=6, start_number=1)
        assert numberer1.get_next_bates_number() == "A-000001"
        
        # Padding of 2
        numberer2 = BatesNumberer(prefix="B-", padding=2, start_number=99)
        assert numberer2.get_next_bates_number() == "B-99"
        
        # Padding of 8
        numberer3 = BatesNumberer(prefix="C-", padding=8, start_number=1)
        assert numberer3.get_next_bates_number() == "C-00000001"
    
    def test_font_name_bold(self):
        """Test bold font selection."""
        numberer = BatesNumberer(font_name="Helvetica", bold=True, italic=False)
        assert numberer.font_name == "Helvetica-Bold"
    
    def test_font_name_italic(self):
        """Test italic font selection."""
        numberer = BatesNumberer(font_name="Helvetica", bold=False, italic=True)
        assert numberer.font_name == "Helvetica-Oblique"
    
    def test_font_name_bold_italic(self):
        """Test bold italic font selection."""
        numberer = BatesNumberer(font_name="Helvetica", bold=True, italic=True)
        assert numberer.font_name == "Helvetica-BoldOblique"
    
    def test_color_parsing_named_colors(self):
        """Test color parsing with named colors."""
        numberer_black = BatesNumberer(font_color="black")
        assert numberer_black.font_color is not None
        
        numberer_red = BatesNumberer(font_color="red")
        assert numberer_red.font_color is not None
        
        numberer_blue = BatesNumberer(font_color="blue")
        assert numberer_blue.font_color is not None


def test_version():
    """Test that version is defined."""
    from bates_labeler import __version__
    assert __version__ == "2.2.0"


def test_module_imports():
    """Test that all expected exports are available."""
    from bates_labeler import BatesNumberer, POSITION_COORDINATES, __version__
    assert BatesNumberer is not None
    assert POSITION_COORDINATES is not None
    assert __version__ is not None
