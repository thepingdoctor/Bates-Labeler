"""Core Bates numbering functionality."""

import os
import csv
import io
import zipfile
from datetime import datetime
from typing import Tuple, Optional, List, Dict
import getpass

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from tqdm import tqdm

# New imports for additional features
import qrcode
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


# Position mappings
POSITION_COORDINATES = {
    'top-left': (0.5, 10.5),
    'top-center': (4.25, 10.5),
    'top-right': (7.0, 10.5),
    'bottom-left': (0.5, 0.5),
    'bottom-center': (4.25, 0.5),
    'bottom-right': (7.0, 0.5),
    'center': (4.25, 5.5)
}


class BatesNumberer:
    """Main class for applying Bates numbers to PDF documents."""
    
    def __init__(self, 
                 prefix: str = "",
                 start_number: int = 1,
                 padding: int = 4,
                 suffix: str = "",
                 position: str = "bottom-left",
                 font_name: str = "Helvetica",
                 font_size: int = 12,
                 font_color: str = "black",
                 bold: bool = True,
                 italic: bool = False,
                 include_date: bool = False,
                 date_format: str = "%Y-%m-%d",
                 add_background: bool = True,
                 background_padding: int = 3,
                 custom_font_path: Optional[str] = None,
                 # Logo settings
                 logo_path: Optional[str] = None,
                 logo_placement: str = "above_bates",
                 logo_max_width: float = 2.0,
                 logo_max_height: float = 2.0,
                 # QR code settings
                 enable_qr: bool = False,
                 qr_placement: str = "disabled",
                 qr_position: str = "bottom-left",
                 qr_size: float = 1.0,
                 qr_color: str = "black",
                 qr_background_color: str = "white",
                 # Border settings (for separator pages)
                 enable_border: bool = False,
                 border_style: str = "solid",
                 border_color: str = "black",
                 border_width: float = 2.0,
                 border_corner_radius: float = 0,
                 # Watermark settings
                 enable_watermark: bool = False,
                 watermark_text: str = "CONFIDENTIAL",
                 watermark_scope: str = "disabled",
                 watermark_opacity: float = 0.3,
                 watermark_rotation: float = 45,
                 watermark_position: str = "center",
                 watermark_font_size: int = 72,
                 watermark_color: str = "gray",
                 # Callback functions
                 status_callback: Optional[callable] = None,
                 cancel_callback: Optional[callable] = None):
        """
        Initialize Bates numbering configuration.
        
        Args:
            prefix: Prefix for Bates number (e.g., "CASE123-")
            start_number: Starting number
            padding: Number of digits for padding (e.g., 4 -> "0001")
            suffix: Suffix for Bates number
            position: Position on page (top-left, bottom-right, etc.)
            font_name: Font family name (or custom font name if using custom font)
            font_size: Font size in points
            font_color: Font color name or hex
            bold: Use bold font (ignored if using custom font)
            italic: Use italic font (ignored if using custom font)
            include_date: Include date/time stamp
            date_format: Format for date stamp
            add_background: Add white background behind text
            background_padding: Padding around text background in pixels
            custom_font_path: Path to custom TrueType (.ttf) or OpenType (.otf) font file
            logo_path: Path to logo file (SVG, PNG, JPG, WEBP)
            logo_placement: Logo placement (above_bates, top-left, top-center, top-right, bottom-left, bottom-center, bottom-right)
            logo_max_width: Maximum logo width in inches
            logo_max_height: Maximum logo height in inches
            enable_qr: Enable QR code generation
            qr_placement: QR code placement (all_pages, separator_only, disabled)
            qr_position: QR code position on page
            qr_size: QR code size in inches
            qr_color: QR code fill color
            qr_background_color: QR code background color
            enable_border: Enable border on separator pages
            border_style: Border style (solid, dashed, double, asterisks)
            border_color: Border color
            border_width: Border width in points
            border_corner_radius: Corner radius for rounded borders
            enable_watermark: Enable watermark
            watermark_text: Watermark text
            watermark_scope: Watermark scope (all_pages, document_only, disabled)
            watermark_opacity: Watermark opacity (0-1)
            watermark_rotation: Watermark rotation in degrees
            watermark_position: Watermark position
            watermark_font_size: Watermark font size
            watermark_color: Watermark color
            status_callback: Optional callback function for status updates (message, progress_dict)
            cancel_callback: Optional callback function to check if processing should be cancelled
        """
        self.prefix = prefix
        self.current_number = start_number
        
        # Callback functions
        self.status_callback = status_callback
        self.cancel_callback = cancel_callback
        self.padding = padding
        self.suffix = suffix
        self.position = position
        self.custom_font_path = custom_font_path
        self.custom_font_name = None
        
        # Register custom font if provided
        if custom_font_path:
            self.custom_font_name = self._register_custom_font(custom_font_path)
            self.font_name = self.custom_font_name if self.custom_font_name else self._get_font_name(font_name, bold, italic)
        else:
            self.font_name = self._get_font_name(font_name, bold, italic)
        
        self.font_size = font_size
        self.font_color = self._parse_color(font_color)
        self.include_date = include_date
        self.date_format = date_format
        self.add_background = add_background
        self.background_padding = background_padding
        
        # Logo settings
        self.logo_path = logo_path
        self.logo_placement = logo_placement
        self.logo_max_width = logo_max_width * inch
        self.logo_max_height = logo_max_height * inch
        self.logo_image = None
        if logo_path:
            self.logo_image = self._load_and_scale_logo(logo_path)
        
        # QR code settings
        self.enable_qr = enable_qr
        self.qr_placement = qr_placement
        self.qr_position = qr_position
        self.qr_size = qr_size * inch
        self.qr_color = qr_color
        self.qr_background_color = qr_background_color
        
        # Border settings
        self.enable_border = enable_border
        self.border_style = border_style
        self.border_color = self._parse_color(border_color)
        self.border_width = border_width
        self.border_corner_radius = border_corner_radius
        
        # Watermark settings
        self.enable_watermark = enable_watermark
        self.watermark_text = watermark_text
        self.watermark_scope = watermark_scope
        self.watermark_opacity = watermark_opacity
        self.watermark_rotation = watermark_rotation
        self.watermark_position = watermark_position
        self.watermark_font_size = watermark_font_size
        self.watermark_color = self._parse_color(watermark_color)
        
    def _get_font_name(self, base_font: str, bold: bool, italic: bool) -> str:
        """Get the appropriate font name based on style options."""
        if base_font == "Helvetica":
            if bold and italic:
                return "Helvetica-BoldOblique"
            elif bold:
                return "Helvetica-Bold"
            elif italic:
                return "Helvetica-Oblique"
        elif base_font == "Times-Roman":
            if bold and italic:
                return "Times-BoldItalic"
            elif bold:
                return "Times-Bold"
            elif italic:
                return "Times-Italic"
        elif base_font == "Courier":
            if bold and italic:
                return "Courier-BoldOblique"
            elif bold:
                return "Courier-Bold"
            elif italic:
                return "Courier-Oblique"
        return base_font
    
    def _parse_color(self, color_str: str) -> colors.Color:
        """Parse color string to reportlab Color object."""
        color_map = {
            'black': colors.black,
            'blue': colors.blue,
            'red': colors.red,
            'green': colors.green,
            'gray': colors.gray,
            'grey': colors.gray
        }
        
        if color_str.lower() in color_map:
            return color_map[color_str.lower()]
        
        # Handle hex colors
        if color_str.startswith('#'):
            try:
                return colors.HexColor(color_str)
            except:
                print(f"Warning: Invalid color '{color_str}', using black")
                return colors.black
        
        return colors.black
    
    def _register_custom_font(self, font_path: str) -> Optional[str]:
        """
        Register a custom TrueType or OpenType font with reportlab.
        
        Args:
            font_path: Path to the .ttf or .otf font file
            
        Returns:
            Registered font name if successful, None otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(font_path):
                print(f"Warning: Custom font file not found: {font_path}")
                return None
            
            # Validate file extension
            file_ext = os.path.splitext(font_path)[1].lower()
            if file_ext not in ['.ttf', '.otf']:
                print(f"Warning: Unsupported font format '{file_ext}'. Only .ttf and .otf files are supported.")
                return None
            
            # Generate a unique font name from the file
            font_name = f"CustomFont_{os.path.splitext(os.path.basename(font_path))[0]}"
            
            # Register the font
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            
            print(f"Successfully registered custom font: {font_name}")
            return font_name
            
        except Exception as e:
            print(f"Error registering custom font: {str(e)}")
            print("Falling back to default font...")
            return None
    
    def _load_and_scale_logo(self, logo_path: str) -> Optional[Dict]:
        """
        Load and scale a logo image.
        
        Args:
            logo_path: Path to logo file (SVG, PNG, JPG, WEBP)
            
        Returns:
            Dict with 'type', 'data', 'width', 'height' or None if failed
        """
        try:
            if not os.path.exists(logo_path):
                print(f"Warning: Logo file not found: {logo_path}")
                return None
            
            file_ext = os.path.splitext(logo_path)[1].lower()
            
            # Handle SVG files
            if file_ext == '.svg':
                drawing = svg2rlg(logo_path)
                if not drawing:
                    print(f"Warning: Could not load SVG: {logo_path}")
                    return None
                
                # Scale to fit within max dimensions
                scale_x = self.logo_max_width / drawing.width if drawing.width > 0 else 1
                scale_y = self.logo_max_height / drawing.height if drawing.height > 0 else 1
                scale = min(scale_x, scale_y, 1.0)  # Don't scale up, only down
                
                return {
                    'type': 'svg',
                    'data': drawing,
                    'width': drawing.width * scale,
                    'height': drawing.height * scale,
                    'scale': scale
                }
            
            # Handle raster formats (PNG, JPG, WEBP)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.webp']:
                img = Image.open(logo_path)
                
                # Get original dimensions in points (assuming 72 DPI)
                width_pts = img.width * 72 / img.info.get('dpi', (72, 72))[0]
                height_pts = img.height * 72 / img.info.get('dpi', (72, 72))[1]
                
                # Scale to fit within max dimensions
                scale_x = self.logo_max_width / width_pts if width_pts > 0 else 1
                scale_y = self.logo_max_height / height_pts if height_pts > 0 else 1
                scale = min(scale_x, scale_y, 1.0)
                
                # Save to temporary file for reportlab
                temp_img_path = f"temp_logo{file_ext}"
                img.save(temp_img_path)
                
                return {
                    'type': 'raster',
                    'data': temp_img_path,
                    'width': width_pts * scale,
                    'height': height_pts * scale,
                    'original_path': logo_path
                }
            else:
                print(f"Warning: Unsupported logo format: {file_ext}")
                return None
                
        except Exception as e:
            print(f"Error loading logo: {str(e)}")
            return None
    
    def _create_qr_code(self, data: str) -> Optional[str]:
        """
        Generate a QR code image.
        
        Args:
            data: Data to encode in QR code
            
        Returns:
            Path to temporary QR code image file or None if failed
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=1,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Use configurable colors
            img = qr.make_image(fill_color=self.qr_color, back_color=self.qr_background_color)
            
            # Save to temporary file
            temp_path = f"temp_qr_{abs(hash(data))}.png"
            img.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating QR code: {str(e)}")
            return None
    
    def _draw_border(self, c: canvas.Canvas, page_width: float, page_height: float,
                    margin: float = 36) -> None:
        """
        Draw a border on the canvas based on border settings.
        
        Args:
            c: ReportLab canvas object
            page_width: Page width in points
            page_height: Page height in points
            margin: Margin from page edges in points
        """
        if not self.enable_border:
            return
        
        try:
            c.setStrokeColor(self.border_color)
            c.setLineWidth(self.border_width)
            
            x1, y1 = margin, margin
            x2, y2 = page_width - margin, page_height - margin
            
            if self.border_style == "solid":
                if self.border_corner_radius > 0:
                    c.roundRect(x1, y1, x2 - x1, y2 - y1, self.border_corner_radius)
                else:
                    c.rect(x1, y1, x2 - x1, y2 - y1)
                    
            elif self.border_style == "dashed":
                c.setDash(6, 3)
                if self.border_corner_radius > 0:
                    c.roundRect(x1, y1, x2 - x1, y2 - y1, self.border_corner_radius)
                else:
                    c.rect(x1, y1, x2 - x1, y2 - y1)
                c.setDash()  # Reset to solid
                
            elif self.border_style == "double":
                offset = self.border_width * 2
                # Outer rectangle
                c.rect(x1, y1, x2 - x1, y2 - y1)
                # Inner rectangle
                c.rect(x1 + offset, y1 + offset, (x2 - x1) - (2 * offset), (y2 - y1) - (2 * offset))
                
            elif self.border_style == "asterisks":
                # Draw asterisks around the border
                c.setFont("Helvetica", 12)
                c.setFillColor(self.border_color)
                
                # Top and bottom borders
                spacing = 20
                for x in range(int(x1), int(x2), spacing):
                    c.drawString(x, y2 + 5, "*")  # Top
                    c.drawString(x, y1 - 15, "*")  # Bottom
                
                # Left and right borders
                for y in range(int(y1), int(y2), spacing):
                    c.drawString(x1 - 10, y, "*")  # Left
                    c.drawString(x2 + 2, y, "*")  # Right
                    
        except Exception as e:
            print(f"Error drawing border: {str(e)}")
    
    def _draw_logo_on_canvas(self, c: canvas.Canvas, page_width: float, page_height: float,
                            bates_y: Optional[float] = None) -> None:
        """
        Draw logo on canvas based on logo settings.
        
        Args:
            c: ReportLab canvas object
            page_width: Page width in points
            page_height: Page height in points
            bates_y: Y position of Bates number (for above_bates placement)
        """
        if not self.logo_image:
            return
        
        try:
            logo_width = self.logo_image['width']
            logo_height = self.logo_image['height']
            
            # Calculate position based on placement
            if self.logo_placement == "above_bates" and bates_y:
                x = (page_width - logo_width) / 2
                y = bates_y + 30  # 30 points above Bates number
            elif self.logo_placement == "top-left":
                x, y = 0.5 * inch, page_height - logo_height - (0.5 * inch)
            elif self.logo_placement == "top-center":
                x = (page_width - logo_width) / 2
                y = page_height - logo_height - (0.5 * inch)
            elif self.logo_placement == "top-right":
                x = page_width - logo_width - (0.5 * inch)
                y = page_height - logo_height - (0.5 * inch)
            elif self.logo_placement == "bottom-left":
                x, y = 0.5 * inch, 0.5 * inch
            elif self.logo_placement == "bottom-center":
                x = (page_width - logo_width) / 2
                y = 0.5 * inch
            elif self.logo_placement == "bottom-right":
                x = page_width - logo_width - (0.5 * inch)
                y = 0.5 * inch
            else:
                # Default to center
                x = (page_width - logo_width) / 2
                y = (page_height - logo_height) / 2
            
            # Draw logo based on type
            if self.logo_image['type'] == 'svg':
                drawing = self.logo_image['data']
                scale = self.logo_image['scale']
                drawing.scale(scale, scale)
                renderPDF.draw(drawing, c, x, y)
            else:  # raster
                c.drawImage(self.logo_image['data'], x, y, 
                          width=logo_width, height=logo_height,
                          preserveAspectRatio=True, mask='auto')
                
        except Exception as e:
            print(f"Error drawing logo: {str(e)}")
    
    def _draw_qr_on_canvas(self, c: canvas.Canvas, page_width: float, page_height: float,
                          qr_data: str) -> None:
        """
        Draw QR code on canvas.
        
        Args:
            c: ReportLab canvas object
            page_width: Page width in points
            page_height: Page height in points
            qr_data: Data to encode in QR code
        """
        try:
            qr_path = self._create_qr_code(qr_data)
            if not qr_path:
                return
            
            # Calculate position based on qr_position
            if self.qr_position in POSITION_COORDINATES:
                x, y = POSITION_COORDINATES[self.qr_position]
                x = x * inch
                y = y * inch
            else:
                x, y = 0.5 * inch, 0.5 * inch
            
            # Adjust position based on page size
            if 'right' in self.qr_position:
                x = page_width - self.qr_size - (0.5 * inch)
            elif 'center' in self.qr_position:
                x = (page_width - self.qr_size) / 2
            
            if 'top' in self.qr_position:
                y = page_height - self.qr_size - (0.5 * inch)
            
            # Draw QR code
            c.drawImage(qr_path, x, y, width=self.qr_size, height=self.qr_size)
            
            # Clean up temp file
            if os.path.exists(qr_path):
                os.remove(qr_path)
                
        except Exception as e:
            print(f"Error drawing QR code: {str(e)}")
    
    def create_watermark_overlay(self, page_width: float, page_height: float,
                                output_path: str) -> None:
        """
        Create a PDF overlay with watermark.
        
        Args:
            page_width: Width of the page in points
            page_height: Height of the page in points
            output_path: Path to save the watermark overlay PDF
        """
        try:
            c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
            
            # Set transparency
            c.setFillAlpha(self.watermark_opacity)
            c.setFillColor(self.watermark_color)
            
            # Set font
            c.setFont("Helvetica-Bold", self.watermark_font_size)
            
            # Calculate position
            if self.watermark_position == "center" or self.watermark_rotation != 0:
                # For rotated text, use center of page
                center_x = page_width / 2
                center_y = page_height / 2
                
                # Save state, rotate, draw, restore
                c.saveState()
                c.translate(center_x, center_y)
                c.rotate(self.watermark_rotation)
                
                text_width = c.stringWidth(self.watermark_text, "Helvetica-Bold", 
                                          self.watermark_font_size)
                c.drawString(-text_width / 2, 0, self.watermark_text)
                c.restoreState()
            else:
                # Use position coordinates
                if self.watermark_position in POSITION_COORDINATES:
                    x, y = POSITION_COORDINATES[self.watermark_position]
                    x = x * inch
                    y = y * inch
                else:
                    x, y = page_width / 2, page_height / 2
                
                c.drawString(x, y, self.watermark_text)
            
            c.save()
            
        except Exception as e:
            print(f"Error creating watermark: {str(e)}")
    
    def get_next_bates_number(self) -> str:
        """Generate the next Bates number in sequence."""
        # Format the number with padding
        number_str = str(self.current_number).zfill(self.padding)
        bates_number = f"{self.prefix}{number_str}{self.suffix}"
        
        # Increment for next call
        self.current_number += 1
        
        return bates_number
    
    def create_separator_page(self, page_width: float, page_height: float,
                            first_bates: str, last_bates: str, output_path: str,
                            document_name: Optional[str] = None) -> None:
        """
        Create a separator page with Bates range information.
        
        Args:
            page_width: Width of the page in points
            page_height: Height of the page in points  
            first_bates: First Bates number in the document
            last_bates: Last Bates number in the document
            output_path: Path to save the separator page PDF
            document_name: Optional document name (kept for backward compatibility but not displayed)
        """
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        # Draw border if enabled
        self._draw_border(c, page_width, page_height)
        
        # Center position
        center_x = page_width / 2
        center_y = page_height / 2
        
        # Draw logo if enabled and placement is above_bates
        if self.logo_image and self.logo_placement == "above_bates":
            self._draw_logo_on_canvas(c, page_width, page_height, bates_y=center_y)
        elif self.logo_image:
            # For other placements, don't pass bates_y
            self._draw_logo_on_canvas(c, page_width, page_height)
        
        # Draw first Bates number (large, bold)
        c.setFont(self._get_font_name("Helvetica", True, False), 20)
        c.setFillColor(colors.black)
        c.drawCentredString(center_x, center_y, first_bates)
        
        # Draw Bates range (smaller, italic)
        range_text = f"{first_bates} - {last_bates}"
        c.setFont(self._get_font_name("Helvetica", False, True), 14)
        c.drawCentredString(center_x, center_y - 30, range_text)
        
        # Draw QR code if enabled and placement is separator_only
        if self.enable_qr and self.qr_placement == "separator_only":
            self._draw_qr_on_canvas(c, page_width, page_height, first_bates)
        
        c.save()
    
    def create_index_page(self, documents: List[Dict], output_path: str,
                         page_width: float = 612, page_height: float = 792) -> None:
        """
        Create an index page listing all documents with their Bates ranges.
        
        Args:
            documents: List of dicts with original_filename, first_bates, last_bates, page_count
            output_path: Path to save the index page PDF
            page_width: Page width in points (default: letter size)
            page_height: Page height in points (default: letter size)
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=(page_width, page_height))
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>BATES NUMBERING INDEX</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 30))
            
            # Table header
            table_data = [['Document Name', 'First Bates', 'Last Bates', 'Pages']]
            
            # Add document rows
            for doc_info in documents:
                table_data.append([
                    doc_info.get('original_filename', ''),
                    doc_info.get('first_bates', ''),
                    doc_info.get('last_bates', ''),
                    str(doc_info.get('page_count', 0))
                ])
            
            # Create table with appropriate column widths
            table = Table(table_data, colWidths=[240, 120, 120, 60])
            table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align document names
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),  # Center align other columns
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
                
                # Alternating row colors for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')])
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            print(f"Index page saved to: {output_path}")
            
        except Exception as e:
            print(f"Error creating index page: {str(e)}")
    
    def create_bates_overlay(self, page_width: float, page_height: float, 
                           bates_number: str, output_path: str) -> None:
        """
        Create a PDF overlay with the Bates number.
        
        Args:
            page_width: Width of the page in points
            page_height: Height of the page in points
            bates_number: The Bates number to apply
            output_path: Path to save the overlay PDF
        """
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        # Set font
        c.setFont(self.font_name, self.font_size)
        
        # Get position coordinates
        if self.position in POSITION_COORDINATES:
            x, y = POSITION_COORDINATES[self.position]
            x = x * inch
            y = y * inch
        else:
            # Default to bottom-left
            x, y = 0.5 * inch, 0.5 * inch
        
        # Adjust position based on page size
        if 'right' in self.position:
            x = page_width - (1.5 * inch)
        elif 'center' in self.position and 'top' not in self.position and 'bottom' not in self.position:
            x = page_width / 2
        
        if 'top' in self.position:
            y = page_height - (0.5 * inch)
        
        # Calculate text width and height for background
        text_width = c.stringWidth(bates_number, self.font_name, self.font_size)
        text_height = self.font_size
        
        # Draw white background if enabled
        if self.add_background:
            padding = self.background_padding
            c.setFillColor(colors.white)
            c.rect(
                x - padding,
                y - padding,
                text_width + (2 * padding),
                text_height + (2 * padding),
                fill=True,
                stroke=False
            )
        
        # Draw Bates number
        c.setFillColor(self.font_color)
        c.drawString(x, y, bates_number)
        
        # Add date if requested
        if self.include_date:
            date_str = datetime.now().strftime(self.date_format)
            date_y = y - (self.font_size + 2)
            
            # Draw background for date if enabled
            if self.add_background:
                date_width = c.stringWidth(date_str, self.font_name, self.font_size)
                c.setFillColor(colors.white)
                c.rect(
                    x - padding,
                    date_y - padding,
                    date_width + (2 * padding),
                    text_height + (2 * padding),
                    fill=True,
                    stroke=False
                )
            
            c.setFillColor(self.font_color)
            c.drawString(x, date_y, date_str)
        
        # Draw QR code if enabled and placement is all_pages
        if self.enable_qr and self.qr_placement == "all_pages":
            self._draw_qr_on_canvas(c, page_width, page_height, bates_number)
        
        c.save()
    
    def process_pdf(self, input_path: str, output_path: str, 
                   password: Optional[str] = None,
                   add_separator: bool = False,
                   return_metadata: bool = False) -> Dict:
        """
        Process a PDF file and add Bates numbers.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save output PDF
            password: Password for encrypted PDFs
            add_separator: Add separator page at the beginning
            return_metadata: If True, return metadata dict instead of bool
            
        Returns:
            If return_metadata is True: dict with success, first_bates, last_bates, page_count
            Otherwise: bool indicating success
        """
        metadata = {
            'success': False,
            'cancelled': False,
            'first_bates': None,
            'last_bates': None,
            'page_count': 0,
            'original_filename': os.path.basename(input_path)
        }
        try:
            # Check for cancellation
            if self.cancel_callback and self.cancel_callback():
                metadata['cancelled'] = True
                return metadata if return_metadata else False
            
            # Read the input PDF
            if self.status_callback:
                self.status_callback(f"Reading PDF: {os.path.basename(input_path)}", {
                    'operation': 'reading',
                    'file': os.path.basename(input_path)
                })
            print(f"Reading PDF: {input_path}")
            reader = PdfReader(input_path)
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                if password:
                    if not reader.decrypt(password):
                        print("Error: Invalid password")
                        return False
                else:
                    # Prompt for password
                    password = getpass.getpass("PDF is password protected. Enter password: ")
                    if not reader.decrypt(password):
                        print("Error: Invalid password")
                        return False
            
            writer = PdfWriter()
            
            # Get total pages for progress bar
            total_pages = len(reader.pages)
            metadata['page_count'] = total_pages
            print(f"Processing {total_pages} pages...")
            
            # Track first and last Bates numbers
            first_bates_number = f"{self.prefix}{str(self.current_number).zfill(self.padding)}{self.suffix}"
            last_number = self.current_number + total_pages - 1
            last_bates_number = f"{self.prefix}{str(last_number).zfill(self.padding)}{self.suffix}"
            
            metadata['first_bates'] = first_bates_number
            metadata['last_bates'] = last_bates_number
            
            if add_separator:
                # Calculate Bates range
                first_bates_number = f"{self.prefix}{str(self.current_number).zfill(self.padding)}{self.suffix}"
                last_number = self.current_number + total_pages - 1
                last_bates_number = f"{self.prefix}{str(last_number).zfill(self.padding)}{self.suffix}"
                
                # Get page dimensions from first page
                first_page = reader.pages[0]
                page_width = float(first_page.mediabox.width)
                page_height = float(first_page.mediabox.height)
                
                # Create separator page
                print("Adding separator page...")
                separator_path = "temp_separator.pdf"
                self.create_separator_page(page_width, page_height, 
                                         first_bates_number, last_bates_number, 
                                         separator_path)
                
                # Add separator page to writer
                separator_reader = PdfReader(separator_path)
                writer.add_page(separator_reader.pages[0])
                
                # Clean up temp file
                os.remove(separator_path)
            
            # Process each page with progress bar
            for page_num in tqdm(range(total_pages), desc="Adding Bates numbers", disable=bool(self.status_callback)):
                # Check for cancellation
                if self.cancel_callback and self.cancel_callback():
                    if self.status_callback:
                        self.status_callback("Processing cancelled by user", {
                            'operation': 'cancelled',
                            'current': page_num,
                            'total': total_pages
                        })
                    metadata['cancelled'] = True
                    return metadata if return_metadata else False
                
                # Status update
                if self.status_callback:
                    self.status_callback(f"Processing page {page_num + 1}/{total_pages}", {
                        'operation': 'processing_page',
                        'current': page_num + 1,
                        'total': total_pages,
                        'file': os.path.basename(input_path)
                    })
                
                page = reader.pages[page_num]
                
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Generate Bates number for this page
                bates_number = self.get_next_bates_number()
                
                # Apply watermark if enabled and scope includes document pages
                if self.enable_watermark and self.watermark_scope in ["all_pages", "document_only"]:
                    if self.status_callback:
                        self.status_callback(f"Applying watermark to page {page_num + 1}/{total_pages}", {
                            'operation': 'applying_watermark',
                            'current': page_num + 1,
                            'total': total_pages
                        })
                    
                    watermark_path = f"temp_watermark_{page_num}.pdf"
                    self.create_watermark_overlay(page_width, page_height, watermark_path)
                    
                    watermark_reader = PdfReader(watermark_path)
                    watermark_page = watermark_reader.pages[0]
                    page.merge_page(watermark_page)
                    os.remove(watermark_path)
                
                # Status update for Bates numbering
                if self.status_callback:
                    self.status_callback(f"Adding Bates number {bates_number}", {
                        'operation': 'applying_bates',
                        'current': page_num + 1,
                        'total': total_pages,
                        'bates': bates_number
                    })
                
                # Create overlay
                overlay_path = f"temp_overlay_{page_num}.pdf"
                self.create_bates_overlay(page_width, page_height, 
                                        bates_number, overlay_path)
                
                # Read overlay
                overlay_reader = PdfReader(overlay_path)
                overlay_page = overlay_reader.pages[0]
                
                # Merge overlay with original page
                page.merge_page(overlay_page)
                writer.add_page(page)
                
                # Clean up temp file
                os.remove(overlay_path)
            
            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)
            
            # Write output
            if self.status_callback:
                self.status_callback(f"Saving PDF to {os.path.basename(output_path)}", {
                    'operation': 'saving',
                    'file': os.path.basename(output_path)
                })
            print(f"Saving to: {output_path}")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            pages_processed = total_pages + (1 if add_separator else 0)
            if self.status_callback:
                self.status_callback(f"Successfully processed {pages_processed} pages", {
                    'operation': 'complete',
                    'total_pages': pages_processed
                })
            print(f"Successfully processed {pages_processed} pages")
            metadata['success'] = True
            
            return metadata if return_metadata else True
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return metadata if return_metadata else False
    
    def process_batch(self, input_files: List[str], output_dir: str = None,
                     add_separator: bool = False) -> None:
        """
        Process multiple PDF files in batch.
        
        Args:
            input_files: List of input PDF file paths
            output_dir: Directory to save output files (default: same as input)
            add_separator: Add separator page at the beginning of each document
        """
        successful = 0
        failed = 0
        
        for input_path in input_files:
            if not os.path.exists(input_path):
                print(f"Warning: File not found: {input_path}")
                failed += 1
                continue
            
            # Generate output path
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_name = f"{base_name}_bates.pdf"
            
            if output_dir:
                output_path = os.path.join(output_dir, output_name)
            else:
                output_path = os.path.join(os.path.dirname(input_path), output_name)
            
            print(f"\nProcessing: {input_path}")
            if self.process_pdf(input_path, output_path, add_separator=add_separator):
                successful += 1
            else:
                failed += 1
        
        print(f"\nBatch processing complete: {successful} successful, {failed} failed")
    
    def combine_and_process_pdfs(self, input_files: List[str], output_path: str,
                                 add_document_separators: bool = False,
                                 add_index_page: bool = False,
                                 password: Optional[str] = None) -> Dict:
        """
        Combine multiple PDFs and add Bates numbers to the combined document.
        
        Args:
            input_files: List of input PDF file paths
            output_path: Path for the combined output PDF
            add_document_separators: Add separator pages between documents
            add_index_page: Add index page at the beginning listing all documents
            password: Password for encrypted PDFs
            
        Returns:
            Dict with success status and document metadata list
        """
        result = {
            'success': False,
            'documents': [],
            'combined_file': output_path,
            'total_pages': 0
        }
        
        try:
            writer = PdfWriter()
            all_documents = []
            total_pages = 0
            
            print(f"Combining {len(input_files)} PDF files...")
            
            for file_idx, input_path in enumerate(input_files, 1):
                if not os.path.exists(input_path):
                    print(f"Warning: File not found: {input_path}")
                    continue
                
                print(f"Processing file {file_idx}/{len(input_files)}: {os.path.basename(input_path)}")
                reader = PdfReader(input_path)
                
                # Handle encryption
                if reader.is_encrypted:
                    if password:
                        if not reader.decrypt(password):
                            print(f"Error: Invalid password for {input_path}")
                            continue
                    else:
                        print(f"Warning: Skipping encrypted file {input_path}")
                        continue
                
                num_pages = len(reader.pages)
                first_bates = f"{self.prefix}{str(self.current_number).zfill(self.padding)}{self.suffix}"
                last_number = self.current_number + num_pages - 1
                last_bates = f"{self.prefix}{str(last_number).zfill(self.padding)}{self.suffix}"
                
                # Add document separator if requested
                if add_document_separators and num_pages > 0:
                    first_page = reader.pages[0]
                    page_width = float(first_page.mediabox.width)
                    page_height = float(first_page.mediabox.height)
                    
                    separator_path = f"temp_doc_separator_{file_idx}.pdf"
                    self.create_separator_page(
                        page_width, page_height,
                        first_bates, last_bates,
                        separator_path,
                        document_name=os.path.basename(input_path)
                    )
                    
                    separator_reader = PdfReader(separator_path)
                    writer.add_page(separator_reader.pages[0])
                    os.remove(separator_path)
                
                # Process each page
                for page in reader.pages:
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    
                    bates_number = self.get_next_bates_number()
                    
                    overlay_path = f"temp_combine_overlay_{total_pages}.pdf"
                    self.create_bates_overlay(page_width, page_height, bates_number, overlay_path)
                    
                    overlay_reader = PdfReader(overlay_path)
                    overlay_page = overlay_reader.pages[0]
                    
                    page.merge_page(overlay_page)
                    writer.add_page(page)
                    os.remove(overlay_path)
                    
                    total_pages += 1
                
                # Track document metadata
                doc_info = {
                    'original_filename': os.path.basename(input_path),
                    'first_bates': first_bates,
                    'last_bates': last_bates,
                    'page_count': num_pages
                }
                all_documents.append(doc_info)
            
            # Add index page at the beginning if requested
            if add_index_page and all_documents:
                print("Creating index page...")
                index_path = "temp_index.pdf"
                # Use letter size for index page
                self.create_index_page(all_documents, index_path)
                
                # Read index page
                index_reader = PdfReader(index_path)
                
                # Create a new writer with index page first
                new_writer = PdfWriter()
                
                # Add index page
                for page in index_reader.pages:
                    new_writer.add_page(page)
                
                # Add all existing pages from the original writer
                for page_num in range(len(writer.pages)):
                    new_writer.add_page(writer.pages[page_num])
                
                # Replace writer with new_writer
                writer = new_writer
                
                # Clean up temp file
                os.remove(index_path)
            
            # Write combined output
            print(f"Writing combined PDF to: {output_path}")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            result['success'] = True
            result['documents'] = all_documents
            result['total_pages'] = total_pages
            
            print(f"Successfully combined {len(all_documents)} documents ({total_pages} pages)")
            return result
            
        except Exception as e:
            print(f"Error combining PDFs: {str(e)}")
            return result
    
    def generate_filename_mapping_csv(self, mappings: List[Dict], output_path: str) -> bool:
        """
        Generate a CSV file mapping original filenames to Bates-numbered filenames.
        
        Args:
            mappings: List of dicts with original_filename, new_filename, first_bates, last_bates, page_count
            output_path: Path for the output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Original Filename', 'New Filename', 'First Bates', 'Last Bates', 'Page Count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for mapping in mappings:
                    writer.writerow({
                        'Original Filename': mapping.get('original_filename', ''),
                        'New Filename': mapping.get('new_filename', ''),
                        'First Bates': mapping.get('first_bates', ''),
                        'Last Bates': mapping.get('last_bates', ''),
                        'Page Count': mapping.get('page_count', 0)
                    })
            
            print(f"CSV mapping saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error generating CSV mapping: {str(e)}")
            return False
    
    def generate_filename_mapping_pdf(self, mappings: List[Dict], output_path: str) -> bool:
        """
        Generate a PDF document showing filename mappings.
        
        Args:
            mappings: List of dicts with original_filename, new_filename, first_bates, last_bates, page_count
            output_path: Path for the output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph("<b>Bates Numbering Filename Mapping</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Timestamp
            timestamp = Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles['Normal']
            )
            elements.append(timestamp)
            elements.append(Spacer(1, 20))
            
            # Table data
            table_data = [['Original Filename', 'New Filename', 'First Bates', 'Last Bates', 'Pages']]
            
            for mapping in mappings:
                table_data.append([
                    mapping.get('original_filename', ''),
                    mapping.get('new_filename', ''),
                    mapping.get('first_bates', ''),
                    mapping.get('last_bates', ''),
                    str(mapping.get('page_count', 0))
                ])
            
            # Create table
            table = Table(table_data, colWidths=[120, 120, 90, 90, 50])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            print(f"PDF mapping saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error generating PDF mapping: {str(e)}")
            return False
