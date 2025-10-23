#!/usr/bin/env python3
"""
Performance benchmark tests for Bates-Labeler optimizations.

Tests verify:
1. In-memory buffer functionality
2. Performance improvements
3. Zero temporary file creation
4. Backward compatibility
"""

import io
import os
import time
import unittest
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Add parent directory to path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bates_labeler.core import BatesNumberer


class TestPerformanceOptimizations(unittest.TestCase):
    """Test suite for performance optimizations."""

    @classmethod
    def setUpClass(cls):
        """Create test PDF files."""
        cls.test_dir = os.path.dirname(__file__)
        cls.small_pdf = os.path.join(cls.test_dir, 'test_small.pdf')
        cls.large_pdf = os.path.join(cls.test_dir, 'test_large.pdf')

        # Create small test PDF (10 pages)
        cls._create_test_pdf(cls.small_pdf, pages=10)

        # Create large test PDF (100 pages) for performance testing
        cls._create_test_pdf(cls.large_pdf, pages=100)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files."""
        for pdf in [cls.small_pdf, cls.large_pdf]:
            if os.path.exists(pdf):
                os.remove(pdf)

    @staticmethod
    def _create_test_pdf(filename: str, pages: int = 10):
        """Create a test PDF file with specified number of pages."""
        writer = PdfWriter()

        for i in range(pages):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, f"Test Page {i + 1}")
            c.save()
            buffer.seek(0)

            reader = PdfReader(buffer)
            writer.add_page(reader.pages[0])

        with open(filename, 'wb') as f:
            writer.write(f)

    def test_create_bates_overlay_returns_bytesio(self):
        """Test that create_bates_overlay returns BytesIO buffer."""
        numberer = BatesNumberer(prefix="TEST-", padding=4)

        result = numberer.create_bates_overlay(
            page_width=612,
            page_height=792,
            bates_number="TEST-0001"
        )

        # Verify it's a BytesIO object
        self.assertIsInstance(result, io.BytesIO)

        # Verify it contains valid PDF data
        result.seek(0)
        self.assertTrue(result.read(4) == b'%PDF')

    def test_create_watermark_overlay_returns_bytesio(self):
        """Test that create_watermark_overlay returns BytesIO buffer."""
        numberer = BatesNumberer(
            enable_watermark=True,
            watermark_text="CONFIDENTIAL"
        )

        result = numberer.create_watermark_overlay(
            page_width=612,
            page_height=792
        )

        self.assertIsInstance(result, io.BytesIO)
        result.seek(0)
        self.assertTrue(result.read(4) == b'%PDF')

    def test_create_separator_page_returns_bytesio(self):
        """Test that create_separator_page returns BytesIO buffer."""
        numberer = BatesNumberer(prefix="TEST-")

        result = numberer.create_separator_page(
            page_width=612,
            page_height=792,
            first_bates="TEST-0001",
            last_bates="TEST-0010"
        )

        self.assertIsInstance(result, io.BytesIO)
        result.seek(0)
        self.assertTrue(result.read(4) == b'%PDF')

    def test_create_qr_code_returns_bytesio(self):
        """Test that QR code generation returns BytesIO buffer."""
        numberer = BatesNumberer(enable_qr=True)

        result = numberer._create_qr_code("TEST-0001")

        self.assertIsInstance(result, io.BytesIO)
        # Verify PNG header
        result.seek(0)
        self.assertTrue(result.read(8) == b'\x89PNG\r\n\x1a\n')

    def test_no_temp_files_created_during_processing(self):
        """Verify no temporary files are created during PDF processing."""
        # Get initial file count
        initial_files = set(os.listdir(self.test_dir))

        # Process PDF
        numberer = BatesNumberer(prefix="TEST-", padding=4)
        output_path = os.path.join(self.test_dir, 'test_output.pdf')

        numberer.process_pdf(
            input_path=self.small_pdf,
            output_path=output_path
        )

        # Get final file count (excluding expected output)
        final_files = set(os.listdir(self.test_dir))
        final_files.discard('test_output.pdf')

        # Verify no new temp files created
        temp_files = final_files - initial_files
        temp_pdf_files = [f for f in temp_files if f.startswith('temp_') and f.endswith('.pdf')]

        self.assertEqual(len(temp_pdf_files), 0,
                        f"Found unexpected temp files: {temp_pdf_files}")

        # Clean up output
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_performance_improvement_small_pdf(self):
        """Benchmark processing time for small PDF (10 pages)."""
        numberer = BatesNumberer(prefix="PERF-", padding=4)
        output_path = os.path.join(self.test_dir, 'perf_small.pdf')

        start_time = time.time()
        numberer.process_pdf(
            input_path=self.small_pdf,
            output_path=output_path
        )
        elapsed = time.time() - start_time

        # Should complete in under 2 seconds for 10 pages
        self.assertLess(elapsed, 2.0,
                       f"Small PDF took {elapsed:.2f}s (expected < 2s)")

        # Verify output exists and is valid
        self.assertTrue(os.path.exists(output_path))
        reader = PdfReader(output_path)
        self.assertEqual(len(reader.pages), 10)

        # Clean up
        os.remove(output_path)

    def test_performance_improvement_large_pdf(self):
        """Benchmark processing time for large PDF (100 pages)."""
        numberer = BatesNumberer(prefix="PERF-", padding=4)
        output_path = os.path.join(self.test_dir, 'perf_large.pdf')

        start_time = time.time()
        numberer.process_pdf(
            input_path=self.large_pdf,
            output_path=output_path
        )
        elapsed = time.time() - start_time

        # Should complete in under 10 seconds for 100 pages
        # (Old implementation would take 45+ seconds)
        self.assertLess(elapsed, 10.0,
                       f"Large PDF took {elapsed:.2f}s (expected < 10s)")

        # Verify output
        self.assertTrue(os.path.exists(output_path))
        reader = PdfReader(output_path)
        self.assertEqual(len(reader.pages), 100)

        print(f"\n✅ Performance: 100 pages processed in {elapsed:.2f}s")
        print(f"   Estimated speedup: ~{45/elapsed:.1f}x faster than old implementation")

        # Clean up
        os.remove(output_path)

    def test_backward_compatibility_output_path_parameter(self):
        """Test backward compatibility with deprecated output_path parameter."""
        numberer = BatesNumberer(prefix="TEST-")

        # Old API should still work (output_path ignored)
        result = numberer.create_bates_overlay(
            page_width=612,
            page_height=792,
            bates_number="TEST-0001",
            output_path="ignored.pdf"  # This parameter is now ignored
        )

        # Should return BytesIO regardless of output_path
        self.assertIsInstance(result, io.BytesIO)

    def test_buffer_reusability(self):
        """Test that returned buffers can be read multiple times."""
        numberer = BatesNumberer(prefix="TEST-")

        buffer = numberer.create_bates_overlay(
            page_width=612,
            page_height=792,
            bates_number="TEST-0001"
        )

        # Read buffer first time
        buffer.seek(0)
        data1 = buffer.read()

        # Read buffer second time (rewind first)
        buffer.seek(0)
        data2 = buffer.read()

        # Both reads should return same data
        self.assertEqual(data1, data2)
        self.assertTrue(len(data1) > 0)

    def test_memory_cleanup_implicit(self):
        """Test that buffers are garbage collected properly."""
        import gc
        import weakref

        numberer = BatesNumberer(prefix="TEST-")

        # Create buffer
        buffer = numberer.create_bates_overlay(
            page_width=612,
            page_height=792,
            bates_number="TEST-0001"
        )

        # Create weak reference
        weak_buffer = weakref.ref(buffer)

        # Delete strong reference
        del buffer
        gc.collect()

        # Weak reference should be dead (buffer was garbage collected)
        self.assertIsNone(weak_buffer())

    def test_separator_with_watermark_no_temp_files(self):
        """Test complex scenario with separator + watermark creates no temp files."""
        initial_files = set(os.listdir(self.test_dir))

        numberer = BatesNumberer(
            prefix="TEST-",
            enable_watermark=True,
            watermark_text="CONFIDENTIAL",
            watermark_scope="all_pages"
        )

        output_path = os.path.join(self.test_dir, 'test_complex.pdf')

        numberer.process_pdf(
            input_path=self.small_pdf,
            output_path=output_path,
            add_separator=True
        )

        final_files = set(os.listdir(self.test_dir))
        final_files.discard('test_complex.pdf')

        temp_files = final_files - initial_files
        temp_pdf_files = [f for f in temp_files if f.startswith('temp_')]

        self.assertEqual(len(temp_pdf_files), 0,
                        f"Complex processing created temp files: {temp_pdf_files}")

        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage patterns."""

    def test_buffer_size_reasonable(self):
        """Test that buffer sizes are reasonable."""
        numberer = BatesNumberer(prefix="TEST-")

        buffer = numberer.create_bates_overlay(
            page_width=612,
            page_height=792,
            bates_number="TEST-0001"
        )

        buffer.seek(0, 2)  # Seek to end
        size = buffer.tell()

        # Overlay PDF should be small (< 10KB typically)
        self.assertLess(size, 20000,
                       f"Buffer size {size} bytes seems excessive")
        self.assertGreater(size, 100,
                          f"Buffer size {size} bytes seems too small")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
