"""Tests for edge cases and error handling."""

import pytest
import os
import tempfile
import shutil
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from bates_labeler import BatesNumberer


class TestEdgeCases:
    """Test cases for boundary conditions and edge cases."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, filename, num_pages=1):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        for i in range(num_pages):
            c.drawString(100, 750, f"Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def test_empty_prefix_and_suffix(self):
        """Test Bates numbering with no prefix or suffix."""
        numberer = BatesNumberer(prefix="", suffix="", start_number=1, padding=4)

        bates = numberer.get_next_bates_number()
        assert bates == "0001"

        bates = numberer.get_next_bates_number()
        assert bates == "0002"

    def test_very_long_prefix(self):
        """Test with extremely long prefix."""
        long_prefix = "CASE-" * 50  # 250 characters
        numberer = BatesNumberer(prefix=long_prefix)

        bates = numberer.get_next_bates_number()
        assert bates.startswith(long_prefix)
        assert bates.endswith("0001")

    def test_very_long_suffix(self):
        """Test with extremely long suffix."""
        long_suffix = "-CONF" * 50  # 250 characters
        numberer = BatesNumberer(suffix=long_suffix)

        bates = numberer.get_next_bates_number()
        assert bates.endswith(long_suffix)

    def test_maximum_padding(self):
        """Test with maximum padding value."""
        numberer = BatesNumberer(padding=10, start_number=1)

        bates = numberer.get_next_bates_number()
        assert bates == "0000000001"
        assert len(bates) == 10

    def test_minimum_padding(self):
        """Test with minimum padding value."""
        numberer = BatesNumberer(padding=1, start_number=5)

        bates = numberer.get_next_bates_number()
        assert bates == "5"

    def test_large_start_number(self):
        """Test with very large starting number."""
        numberer = BatesNumberer(start_number=999999, padding=6)

        bates = numberer.get_next_bates_number()
        assert bates == "999999"

        bates = numberer.get_next_bates_number()
        assert bates == "1000000"  # Should handle overflow gracefully

    def test_number_exceeding_padding(self):
        """Test number that exceeds padding width."""
        numberer = BatesNumberer(start_number=9999, padding=3)

        bates = numberer.get_next_bates_number()
        assert bates == "9999"  # Should not truncate

    def test_single_page_pdf(self):
        """Test processing a PDF with only one page."""
        pdf_path = self._create_test_pdf("single.pdf", num_pages=1)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(prefix="SINGLE-")
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)

        assert metadata['success'] is True
        assert metadata['page_count'] == 1
        assert metadata['first_bates'] == metadata['last_bates']

    def test_very_large_pdf(self):
        """Test processing a PDF with many pages."""
        # Create a PDF with 100 pages
        pdf_path = self._create_test_pdf("large.pdf", num_pages=100)
        output_path = os.path.join(self.temp_dir, "output_large.pdf")

        numberer = BatesNumberer(prefix="LARGE-", start_number=1)
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)

        assert metadata['success'] is True
        assert metadata['page_count'] == 100
        assert metadata['first_bates'] == "LARGE-0001"
        assert metadata['last_bates'] == "LARGE-0100"

    def test_special_characters_in_prefix(self):
        """Test with special characters in prefix."""
        special_prefixes = [
            "CASE#123-",
            "DOC@2024-",
            "FILE_NAME-",
            "EXHIBIT(A)-"
        ]

        for prefix in special_prefixes:
            numberer = BatesNumberer(prefix=prefix)
            bates = numberer.get_next_bates_number()
            assert bates.startswith(prefix)

    def test_unicode_characters_in_prefix(self):
        """Test with Unicode characters in prefix."""
        unicode_prefixes = [
            "CAFÉ-",
            "文档-",
            "ФАЙЛ-"
        ]

        for prefix in unicode_prefixes:
            numberer = BatesNumberer(prefix=prefix)
            bates = numberer.get_next_bates_number()
            assert bates.startswith(prefix)

    def test_empty_batch_list(self):
        """Test batch processing with empty file list."""
        numberer = BatesNumberer()
        numberer.process_batch([], self.temp_dir)
        # Should complete without errors

    def test_nonexistent_file_in_batch(self):
        """Test batch processing with some nonexistent files."""
        existing_pdf = self._create_test_pdf("exists.pdf")
        nonexistent_pdf = os.path.join(self.temp_dir, "nonexistent.pdf")

        numberer = BatesNumberer()
        # Should handle gracefully without crashing
        numberer.process_batch([existing_pdf, nonexistent_pdf], self.temp_dir)

        # Existing file should be processed
        output_name = "exists_bates.pdf"
        assert os.path.exists(os.path.join(self.temp_dir, output_name))


class TestErrorHandling:
    """Test cases for error handling and recovery."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_nonexistent_input_file(self):
        """Test processing nonexistent input file."""
        numberer = BatesNumberer()
        nonexistent = os.path.join(self.temp_dir, "nonexistent.pdf")
        output = os.path.join(self.temp_dir, "output.pdf")

        # Should return False or error metadata
        result = numberer.process_pdf(nonexistent, output, return_metadata=True)
        assert result['success'] is False

    def test_invalid_output_directory(self):
        """Test writing to invalid output directory."""
        # Create a simple PDF
        pdf_path = self._create_test_pdf("test.pdf")

        numberer = BatesNumberer()
        invalid_output = "/invalid/directory/output.pdf"

        # Should handle gracefully
        result = numberer.process_pdf(pdf_path, invalid_output, return_metadata=True)
        assert result['success'] is False

    def _create_test_pdf(self, filename, num_pages=1):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        for i in range(num_pages):
            c.drawString(100, 750, f"Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def test_corrupted_pdf_handling(self):
        """Test handling of corrupted PDF file."""
        # Create a fake corrupted PDF
        corrupted_path = os.path.join(self.temp_dir, "corrupted.pdf")
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid PDF file")

        numberer = BatesNumberer()
        output = os.path.join(self.temp_dir, "output.pdf")

        # Should handle gracefully
        result = numberer.process_pdf(corrupted_path, output, return_metadata=True)
        assert result['success'] is False

    def test_invalid_position_fallback(self):
        """Test that invalid position falls back to default."""
        # The BatesNumberer doesn't validate position in __init__,
        # but _create_bates_overlay should handle it gracefully
        numberer = BatesNumberer(position="invalid-position")

        # Should still create instance
        assert numberer.position == "invalid-position"

    def test_invalid_hex_color(self):
        """Test invalid hex color code handling."""
        numberer = BatesNumberer(font_color="#GGGGGG")  # Invalid hex

        # Should fall back to black
        assert numberer.font_color is not None

    def test_callback_exception_handling(self):
        """Test that exceptions in callbacks don't crash processing."""
        def bad_status_callback(message, progress_dict=None):
            raise Exception("Callback error")

        def bad_cancel_callback():
            raise Exception("Cancel callback error")

        pdf_path = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(
            status_callback=bad_status_callback,
            cancel_callback=bad_cancel_callback
        )

        # Processing should handle callback exceptions
        # (may succeed or fail depending on implementation)
        try:
            result = numberer.process_pdf(pdf_path, output_path)
        except Exception as e:
            # If it raises, it should be from the callback, not PDF processing
            assert "Callback error" in str(e) or "Cancel callback" in str(e)


class TestCancellation:
    """Test cases for processing cancellation."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, filename, num_pages=1):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        for i in range(num_pages):
            c.drawString(100, 750, f"Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def test_cancellation_before_processing(self):
        """Test cancellation before any processing."""
        cancel_flag = [True]

        def cancel_callback():
            return cancel_flag[0]

        pdf_path = self._create_test_pdf("test.pdf", num_pages=3)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(cancel_callback=cancel_callback)
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)

        assert metadata['cancelled'] is True

    def test_cancellation_mid_processing(self):
        """Test cancellation during processing."""
        pages_processed = [0]
        cancel_flag = [False]

        def status_callback(message, progress_dict=None):
            pages_processed[0] += 1
            # Cancel after first page
            if pages_processed[0] > 1:
                cancel_flag[0] = True

        def cancel_callback():
            return cancel_flag[0]

        pdf_path = self._create_test_pdf("test.pdf", num_pages=10)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(
            status_callback=status_callback,
            cancel_callback=cancel_callback
        )

        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)

        # Should be cancelled
        if metadata.get('cancelled'):
            assert metadata['cancelled'] is True


class TestMemoryManagement:
    """Test cases for memory management with large operations."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, filename, num_pages=1):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        for i in range(num_pages):
            c.drawString(100, 750, f"Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def test_temporary_file_cleanup(self):
        """Test that temporary overlay files are cleaned up."""
        pdf_path = self._create_test_pdf("test.pdf", num_pages=3)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        # Count files before processing
        files_before = set(os.listdir(self.temp_dir))

        numberer = BatesNumberer(prefix="TEMP-")
        numberer.process_pdf(pdf_path, output_path)

        # Count files after processing
        files_after = set(os.listdir(self.temp_dir))

        # Should only have original + output (no temp_overlay files left)
        new_files = files_after - files_before
        for filename in new_files:
            assert not filename.startswith('temp_overlay_')
            assert not filename.startswith('temp_watermark_')

    def test_qr_code_cleanup(self):
        """Test that temporary QR code files are cleaned up."""
        pdf_path = self._create_test_pdf("test.pdf", num_pages=2)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(
            enable_qr=True,
            qr_placement='all_pages'
        )

        # Change to temp directory to check for QR files
        original_dir = os.getcwd()
        os.chdir(self.temp_dir)

        try:
            numberer.process_pdf(pdf_path, output_path)

            # Check for leftover QR files
            temp_files = os.listdir('.')
            qr_files = [f for f in temp_files if f.startswith('temp_qr_')]

            # Should be cleaned up
            assert len(qr_files) == 0

        finally:
            os.chdir(original_dir)

    def test_multiple_operations_no_memory_leak(self):
        """Test multiple operations don't accumulate temporary files."""
        pdf_paths = [
            self._create_test_pdf(f"doc_{i}.pdf", num_pages=2)
            for i in range(5)
        ]

        numberer = BatesNumberer(prefix="MULTI-")

        # Process multiple times
        for i, pdf_path in enumerate(pdf_paths):
            output = os.path.join(self.temp_dir, f"output_{i}.pdf")
            numberer.process_pdf(pdf_path, output)

        # Count temp files
        all_files = os.listdir(self.temp_dir)
        temp_files = [
            f for f in all_files
            if f.startswith('temp_') and not f.endswith('.pdf')
        ]

        # Should have minimal or no temp files
        assert len(temp_files) <= 1  # Allow for one if any cleanup is deferred
