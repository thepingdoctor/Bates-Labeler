"""Core Bates numbering functionality."""

import os
from datetime import datetime
from typing import Tuple, Optional, List
import getpass

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from tqdm import tqdm


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
                 background_padding: int = 3):
        """
        Initialize Bates numbering configuration.
        
        Args:
            prefix: Prefix for Bates number (e.g., "CASE123-")
            start_number: Starting number
            padding: Number of digits for padding (e.g., 4 -> "0001")
            suffix: Suffix for Bates number
            position: Position on page (top-left, bottom-right, etc.)
            font_name: Font family name
            font_size: Font size in points
            font_color: Font color name or hex
            bold: Use bold font
            italic: Use italic font
            include_date: Include date/time stamp
            date_format: Format for date stamp
            add_background: Add white background behind text
            background_padding: Padding around text background in pixels
        """
        self.prefix = prefix
        self.current_number = start_number
        self.padding = padding
        self.suffix = suffix
        self.position = position
        self.font_name = self._get_font_name(font_name, bold, italic)
        self.font_size = font_size
        self.font_color = self._parse_color(font_color)
        self.include_date = include_date
        self.date_format = date_format
        self.add_background = add_background
        self.background_padding = background_padding
        
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
    
    def get_next_bates_number(self) -> str:
        """Generate the next Bates number in sequence."""
        # Format the number with padding
        number_str = str(self.current_number).zfill(self.padding)
        bates_number = f"{self.prefix}{number_str}{self.suffix}"
        
        # Increment for next call
        self.current_number += 1
        
        return bates_number
    
    def create_separator_page(self, page_width: float, page_height: float,
                            first_bates: str, last_bates: str, output_path: str) -> None:
        """
        Create a separator page with Bates range information.
        
        Args:
            page_width: Width of the page in points
            page_height: Height of the page in points  
            first_bates: First Bates number in the document
            last_bates: Last Bates number in the document
            output_path: Path to save the separator page PDF
        """
        c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
        
        # Center position
        center_x = page_width / 2
        center_y = page_height / 2
        
        # Draw first Bates number (large, bold)
        c.setFont(self._get_font_name("Helvetica", True, False), 20)
        c.setFillColor(colors.black)
        c.drawCentredString(center_x, center_y, first_bates)
        
        # Draw Bates range (smaller, italic)
        range_text = f"{first_bates} - {last_bates}"
        c.setFont(self._get_font_name("Helvetica", False, True), 14)
        c.drawCentredString(center_x, center_y - 30, range_text)
        
        c.save()
    
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
        
        c.save()
    
    def process_pdf(self, input_path: str, output_path: str, 
                   password: Optional[str] = None,
                   add_separator: bool = False) -> bool:
        """
        Process a PDF file and add Bates numbers.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save output PDF
            password: Password for encrypted PDFs
            add_separator: Add separator page at the beginning
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the input PDF
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
            print(f"Processing {total_pages} pages...")
            
            # Calculate the first and last Bates numbers if separator is needed
            first_bates_number = None
            last_bates_number = None
            
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
            for page_num in tqdm(range(total_pages), desc="Adding Bates numbers"):
                page = reader.pages[page_num]
                
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Generate Bates number for this page
                bates_number = self.get_next_bates_number()
                
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
            print(f"Saving to: {output_path}")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            pages_processed = total_pages + (1 if add_separator else 0)
            print(f"Successfully processed {pages_processed} pages")
            return True
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return False
    
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
