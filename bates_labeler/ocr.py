"""
OCR Text Extraction Module for Bates Labeler

Provides OCR capabilities for extracting text from scanned PDFs and embedding as metadata.
Supports both local (pytesseract) and cloud (Google Cloud Vision) backends.
"""

import os
import io
from typing import Optional, Dict, List, Union
from enum import Enum
from dataclasses import dataclass


class OCRBackend(Enum):
    """OCR backend options."""
    PYTESSERACT = "pytesseract"
    GOOGLE_VISION = "google_vision"


@dataclass
class OCRResult:
    """Result of OCR text extraction."""
    success: bool
    text: str
    confidence: Optional[float] = None
    error: Optional[str] = None
    backend: Optional[str] = None


class OCRExtractor:
    """
    Main OCR extractor class supporting multiple backends.

    Provides privacy-first local OCR with pytesseract and optional
    cloud-based OCR with Google Cloud Vision API.
    """

    def __init__(self,
                 backend: OCRBackend = OCRBackend.PYTESSERACT,
                 google_credentials_path: Optional[str] = None,
                 language: str = "eng"):
        """
        Initialize OCR extractor.

        Args:
            backend: OCR backend to use (pytesseract or google_vision)
            google_credentials_path: Path to Google Cloud credentials JSON (for Google Vision)
            language: OCR language code (default: "eng" for English)
        """
        self.backend = backend
        self.google_credentials_path = google_credentials_path
        self.language = language

        # Validate backend availability
        if backend == OCRBackend.PYTESSERACT:
            if not self._check_pytesseract_available():
                raise ImportError(
                    "pytesseract is not installed or tesseract binary is not found. "
                    "Install with: pip install pytesseract and install Tesseract OCR binary. "
                    "See: https://github.com/tesseract-ocr/tesseract"
                )

        elif backend == OCRBackend.GOOGLE_VISION:
            if not self._check_google_vision_available():
                raise ImportError(
                    "Google Cloud Vision library is not installed. "
                    "Install with: pip install google-cloud-vision"
                )

            if google_credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path

    def _check_pytesseract_available(self) -> bool:
        """Check if pytesseract is available."""
        try:
            import pytesseract
            from PIL import Image
            # Quick test to ensure tesseract binary is available
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _check_google_vision_available(self) -> bool:
        """Check if Google Cloud Vision is available."""
        try:
            from google.cloud import vision
            return True
        except ImportError:
            return False

    def extract_text_from_image(self, image_data: bytes) -> OCRResult:
        """
        Extract text from an image using configured OCR backend.

        Args:
            image_data: Image data as bytes

        Returns:
            OCRResult with extracted text and metadata
        """
        if self.backend == OCRBackend.PYTESSERACT:
            return self._extract_with_pytesseract(image_data)
        elif self.backend == OCRBackend.GOOGLE_VISION:
            return self._extract_with_google_vision(image_data)
        else:
            return OCRResult(
                success=False,
                text="",
                error=f"Unsupported backend: {self.backend}"
            )

    def _extract_with_pytesseract(self, image_data: bytes) -> OCRResult:
        """
        Extract text using pytesseract (local, privacy-first).

        Args:
            image_data: Image data as bytes

        Returns:
            OCRResult with extracted text
        """
        try:
            import pytesseract
            from PIL import Image

            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))

            # Perform OCR with language setting
            text = pytesseract.image_to_string(image, lang=self.language)

            # Optional: Get confidence data
            try:
                data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
                confidences = [float(conf) for conf in data['conf'] if conf != '-1']
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            except Exception:
                avg_confidence = None

            return OCRResult(
                success=True,
                text=text.strip(),
                confidence=avg_confidence,
                backend="pytesseract"
            )

        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                error=f"Pytesseract error: {str(e)}",
                backend="pytesseract"
            )

    def _extract_with_google_vision(self, image_data: bytes) -> OCRResult:
        """
        Extract text using Google Cloud Vision API (cloud-based, premium).

        Args:
            image_data: Image data as bytes

        Returns:
            OCRResult with extracted text
        """
        try:
            from google.cloud import vision

            client = vision.ImageAnnotatorClient()

            # Create image object
            image = vision.Image(content=image_data)

            # Perform OCR
            response = client.document_text_detection(image=image)

            if response.error.message:
                return OCRResult(
                    success=False,
                    text="",
                    error=f"Google Vision API error: {response.error.message}",
                    backend="google_vision"
                )

            # Extract text
            text = response.full_text_annotation.text if response.full_text_annotation else ""

            # Calculate average confidence
            confidences = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    confidences.append(block.confidence)

            avg_confidence = sum(confidences) / len(confidences) if confidences else None

            return OCRResult(
                success=True,
                text=text.strip(),
                confidence=avg_confidence,
                backend="google_vision"
            )

        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                error=f"Google Vision error: {str(e)}",
                backend="google_vision"
            )

    def extract_text_from_pdf_page(self, pdf_path: str, page_num: int = 0) -> OCRResult:
        """
        Extract text from a specific PDF page using OCR.

        Converts PDF page to image first, then performs OCR.

        Args:
            pdf_path: Path to PDF file
            page_num: Page number to extract (0-indexed)

        Returns:
            OCRResult with extracted text
        """
        try:
            from pypdf import PdfReader
            from pdf2image import convert_from_path

            # Try native text extraction first
            reader = PdfReader(pdf_path)
            if page_num < len(reader.pages):
                native_text = reader.pages[page_num].extract_text().strip()

                # If native extraction yields substantial text, use it
                if len(native_text) > 50:
                    return OCRResult(
                        success=True,
                        text=native_text,
                        backend="native_pdf_extraction"
                    )

            # Fall back to OCR for scanned PDFs
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_num + 1,
                last_page=page_num + 1,
                dpi=300
            )

            if not images:
                return OCRResult(
                    success=False,
                    text="",
                    error="Failed to convert PDF page to image"
                )

            # Convert PIL Image to bytes
            image = images[0]
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

            # Perform OCR on image
            return self.extract_text_from_image(img_byte_arr.read())

        except ImportError as e:
            return OCRResult(
                success=False,
                text="",
                error=f"Missing dependency: {str(e)}. Install with: pip install pdf2image"
            )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                error=f"PDF OCR error: {str(e)}"
            )

    def extract_text_from_all_pages(self, pdf_path: str, max_pages: Optional[int] = None) -> List[OCRResult]:
        """
        Extract text from all pages in a PDF.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to process (None for all)

        Returns:
            List of OCRResult objects, one per page
        """
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)

            if max_pages:
                total_pages = min(total_pages, max_pages)

            results = []
            for page_num in range(total_pages):
                result = self.extract_text_from_pdf_page(pdf_path, page_num)
                results.append(result)

            return results

        except Exception as e:
            return [OCRResult(
                success=False,
                text="",
                error=f"Error processing PDF: {str(e)}"
            )]


def embed_ocr_text_as_metadata(pdf_path: str, output_path: str,
                              ocr_extractor: OCRExtractor) -> Dict[str, Union[bool, str, List[str]]]:
    """
    Extract OCR text from PDF and embed as metadata.

    Args:
        pdf_path: Path to input PDF
        output_path: Path to save output PDF with embedded text metadata
        ocr_extractor: Configured OCRExtractor instance

    Returns:
        Dict with success status and extracted texts
    """
    try:
        from pypdf import PdfReader, PdfWriter

        # Extract text from all pages
        ocr_results = ocr_extractor.extract_text_from_all_pages(pdf_path)

        # Read original PDF
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Process each page
        for page_num, (page, ocr_result) in enumerate(zip(reader.pages, ocr_results)):
            writer.add_page(page)

            # Add OCR text as metadata if successful
            if ocr_result.success and ocr_result.text:
                # Note: PyPDF doesn't support per-page metadata easily
                # This adds to document-level metadata instead
                # For per-page text, consider using page annotations
                pass

        # Add OCR metadata to document
        extracted_texts = [r.text for r in ocr_results if r.success]
        combined_text = "\n\n--- Page Break ---\n\n".join(extracted_texts)

        metadata = {
            '/OCRText': combined_text[:1000],  # Limit to 1000 chars for metadata
            '/OCRBackend': ocr_results[0].backend if ocr_results else "unknown",
            '/OCRProcessed': 'True'
        }

        # Copy original metadata
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        # Add OCR metadata
        writer.add_metadata(metadata)

        # Write output
        with open(output_path, 'wb') as f:
            writer.write(f)

        return {
            'success': True,
            'extracted_texts': extracted_texts,
            'total_pages': len(ocr_results),
            'successful_pages': sum(1 for r in ocr_results if r.success)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'extracted_texts': []
        }
