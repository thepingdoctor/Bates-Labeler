"""PDF page rotation and manipulation module for Bates-Labeler.

Provides functionality to rotate, reorder, and manipulate PDF pages
before or after Bates numbering.
"""

import os
import logging
from typing import List, Dict, Optional, Union, Tuple
from enum import Enum

from pypdf import PdfReader, PdfWriter, Transformation


logger = logging.getLogger(__name__)


class RotationAngle(Enum):
    """Standard rotation angles."""
    ROTATE_0 = 0
    ROTATE_90 = 90
    ROTATE_180 = 180
    ROTATE_270 = 270
    ROTATE_CLOCKWISE = 90
    ROTATE_COUNTERCLOCKWISE = 270
    ROTATE_FLIP = 180


class PageManipulator:
    """Manipulates PDF pages with rotation, reordering, and extraction."""

    def __init__(self):
        """Initialize page manipulator."""
        pass

    def rotate_pages(
        self,
        input_path: str,
        output_path: str,
        rotation: Union[int, RotationAngle],
        pages: Optional[List[int]] = None,
        password: Optional[str] = None
    ) -> bool:
        """
        Rotate specific pages or all pages in a PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            rotation: Rotation angle (0, 90, 180, 270) or RotationAngle enum
            pages: List of page numbers to rotate (1-indexed). If None, rotate all pages
            password: Password for encrypted PDFs

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert enum to int if necessary
            if isinstance(rotation, RotationAngle):
                angle = rotation.value
            else:
                angle = rotation

            # Validate rotation angle
            if angle not in [0, 90, 180, 270]:
                logger.error(f"Invalid rotation angle: {angle}. Must be 0, 90, 180, or 270")
                return False

            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password:
                    if not reader.decrypt(password):
                        logger.error("Invalid password")
                        return False
                else:
                    logger.error("PDF is encrypted and requires password")
                    return False

            writer = PdfWriter()
            total_pages = len(reader.pages)

            # If no specific pages specified, rotate all
            if pages is None:
                pages = list(range(1, total_pages + 1))

            # Validate page numbers
            invalid_pages = [p for p in pages if p < 1 or p > total_pages]
            if invalid_pages:
                logger.error(f"Invalid page numbers: {invalid_pages}")
                return False

            for page_num in range(total_pages):
                page = reader.pages[page_num]

                # Rotate if this page is in the list (convert to 1-indexed)
                if (page_num + 1) in pages:
                    page.rotate(angle)
                    logger.debug(f"Rotated page {page_num + 1} by {angle} degrees")

                writer.add_page(page)

            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            # Write output
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"Rotated {len(pages)} page(s) by {angle}° and saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error rotating pages: {str(e)}")
            return False

    def auto_rotate_pages(
        self,
        input_path: str,
        output_path: str,
        target_orientation: str = 'portrait',
        password: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Automatically rotate pages to match target orientation.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            target_orientation: Target orientation ('portrait' or 'landscape')
            password: Password for encrypted PDFs

        Returns:
            Dictionary with rotation results and statistics
        """
        try:
            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password and not reader.decrypt(password):
                    return {'success': False, 'error': 'Invalid password'}

            writer = PdfWriter()
            rotated_pages = []

            for page_num, page in enumerate(reader.pages):
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)

                is_landscape = width > height
                is_portrait = height > width

                # Determine if rotation is needed
                rotate_needed = False
                if target_orientation == 'portrait' and is_landscape:
                    rotate_needed = True
                    angle = 90
                elif target_orientation == 'landscape' and is_portrait:
                    rotate_needed = True
                    angle = 270

                if rotate_needed:
                    page.rotate(angle)
                    rotated_pages.append(page_num + 1)
                    logger.debug(f"Auto-rotated page {page_num + 1} to {target_orientation}")

                writer.add_page(page)

            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            # Write output
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"Auto-rotated {len(rotated_pages)} pages to {target_orientation}")

            return {
                'success': True,
                'rotated_pages': rotated_pages,
                'total_pages': len(reader.pages),
                'target_orientation': target_orientation
            }

        except Exception as e:
            logger.error(f"Error auto-rotating pages: {str(e)}")
            return {'success': False, 'error': str(e)}

    def reorder_pages(
        self,
        input_path: str,
        output_path: str,
        page_order: List[int],
        password: Optional[str] = None
    ) -> bool:
        """
        Reorder pages in a PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            page_order: List of page numbers in desired order (1-indexed)
            password: Password for encrypted PDFs

        Returns:
            True if successful, False otherwise
        """
        try:
            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password:
                    if not reader.decrypt(password):
                        logger.error("Invalid password")
                        return False
                else:
                    logger.error("PDF is encrypted and requires password")
                    return False

            total_pages = len(reader.pages)

            # Validate page order
            if len(page_order) != total_pages:
                logger.error(f"Page order must contain all {total_pages} pages")
                return False

            invalid_pages = [p for p in page_order if p < 1 or p > total_pages]
            if invalid_pages:
                logger.error(f"Invalid page numbers: {invalid_pages}")
                return False

            # Check for duplicates
            if len(set(page_order)) != len(page_order):
                logger.error("Page order contains duplicate page numbers")
                return False

            writer = PdfWriter()

            # Add pages in specified order
            for page_num in page_order:
                # Convert to 0-indexed
                page = reader.pages[page_num - 1]
                writer.add_page(page)

            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            # Write output
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"Reordered {total_pages} pages and saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error reordering pages: {str(e)}")
            return False

    def extract_pages(
        self,
        input_path: str,
        output_path: str,
        pages: List[int],
        password: Optional[str] = None
    ) -> bool:
        """
        Extract specific pages from a PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            pages: List of page numbers to extract (1-indexed)
            password: Password for encrypted PDFs

        Returns:
            True if successful, False otherwise
        """
        try:
            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password:
                    if not reader.decrypt(password):
                        logger.error("Invalid password")
                        return False
                else:
                    logger.error("PDF is encrypted and requires password")
                    return False

            total_pages = len(reader.pages)

            # Validate page numbers
            invalid_pages = [p for p in pages if p < 1 or p > total_pages]
            if invalid_pages:
                logger.error(f"Invalid page numbers: {invalid_pages}")
                return False

            writer = PdfWriter()

            # Extract specified pages
            for page_num in pages:
                # Convert to 0-indexed
                page = reader.pages[page_num - 1]
                writer.add_page(page)

            # Copy metadata
            if reader.metadata:
                writer.add_metadata(reader.metadata)

            # Write output
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

            logger.info(f"Extracted {len(pages)} pages and saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error extracting pages: {str(e)}")
            return False

    def split_pdf(
        self,
        input_path: str,
        output_dir: str,
        pages_per_file: int = 10,
        password: Optional[str] = None
    ) -> List[str]:
        """
        Split a PDF into multiple files.

        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            pages_per_file: Number of pages per output file
            password: Password for encrypted PDFs

        Returns:
            List of output file paths
        """
        try:
            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password and not reader.decrypt(password):
                    logger.error("Invalid password")
                    return []

            os.makedirs(output_dir, exist_ok=True)

            total_pages = len(reader.pages)
            output_files = []
            base_name = os.path.splitext(os.path.basename(input_path))[0]

            for start_page in range(0, total_pages, pages_per_file):
                end_page = min(start_page + pages_per_file, total_pages)

                writer = PdfWriter()

                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])

                # Copy metadata
                if reader.metadata:
                    writer.add_metadata(reader.metadata)

                # Generate output filename
                output_filename = f"{base_name}_part_{(start_page // pages_per_file) + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

                output_files.append(output_path)
                logger.debug(f"Created {output_filename} with pages {start_page + 1}-{end_page}")

            logger.info(f"Split PDF into {len(output_files)} files")
            return output_files

        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            return []

    def remove_pages(
        self,
        input_path: str,
        output_path: str,
        pages_to_remove: List[int],
        password: Optional[str] = None
    ) -> bool:
        """
        Remove specific pages from a PDF.

        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF
            pages_to_remove: List of page numbers to remove (1-indexed)
            password: Password for encrypted PDFs

        Returns:
            True if successful, False otherwise
        """
        try:
            reader = PdfReader(input_path)

            # Handle encryption
            if reader.is_encrypted:
                if password and not reader.decrypt(password):
                    logger.error("Invalid password")
                    return False

            total_pages = len(reader.pages)
            pages_to_keep = [p for p in range(1, total_pages + 1) if p not in pages_to_remove]

            return self.extract_pages(input_path, output_path, pages_to_keep, password)

        except Exception as e:
            logger.error(f"Error removing pages: {str(e)}")
            return False
