"""Performance tests for Bates-Labeler."""

import pytest
import os
import tempfile
import shutil
import time
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from bates_labeler import BatesNumberer


class TestPerformance:
    """Performance benchmarks and stress tests."""

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
            c.drawString(100, 750, f"Test Page {i + 1}")
            c.drawString(100, 700, f"Document: {filename}")
            c.showPage()

        c.save()
        return filepath

    @pytest.mark.slow
    def test_process_100_page_document(self):
        """Test processing a 100-page document."""
        pdf_path = self._create_test_pdf("large_doc.pdf", num_pages=100)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        numberer = BatesNumberer(prefix="PERF-")

        start_time = time.time()
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)
        elapsed = time.time() - start_time

        assert metadata['success'] is True
        assert metadata['page_count'] == 100

        # Performance assertion: Should process in reasonable time
        # Adjust threshold based on your requirements
        assert elapsed < 60.0, f"Processing took {elapsed:.2f}s, expected < 60s"

        print(f"\n100-page document processed in {elapsed:.2f} seconds")
        print(f"Average: {elapsed / 100:.3f} seconds per page")

    @pytest.mark.slow
    def test_process_500_page_document(self):
        """Test processing a very large 500-page document."""
        pdf_path = self._create_test_pdf("very_large.pdf", num_pages=500)
        output_path = os.path.join(self.temp_dir, "output_large.pdf")

        numberer = BatesNumberer(prefix="BIG-")

        start_time = time.time()
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)
        elapsed = time.time() - start_time

        assert metadata['success'] is True
        assert metadata['page_count'] == 500

        # Should complete in reasonable time (adjust as needed)
        assert elapsed < 300.0, f"Processing took {elapsed:.2f}s, expected < 300s"

        print(f"\n500-page document processed in {elapsed:.2f} seconds")
        print(f"Average: {elapsed / 500:.3f} seconds per page")

    def test_batch_processing_speed(self):
        """Test batch processing performance."""
        # Create 20 PDFs with 10 pages each
        pdf_paths = [
            self._create_test_pdf(f"batch_{i}.pdf", num_pages=10)
            for i in range(20)
        ]

        numberer = BatesNumberer(prefix="BATCH-")

        start_time = time.time()
        numberer.process_batch(pdf_paths, self.temp_dir)
        elapsed = time.time() - start_time

        # Should process 20 files in reasonable time
        assert elapsed < 120.0, f"Batch processing took {elapsed:.2f}s, expected < 120s"

        print(f"\n20 files (10 pages each) processed in {elapsed:.2f} seconds")
        print(f"Average: {elapsed / 20:.3f} seconds per file")

    def test_combine_many_pdfs_performance(self):
        """Test combining many PDFs performance."""
        # Create 50 small PDFs
        pdf_paths = [
            self._create_test_pdf(f"combine_{i}.pdf", num_pages=2)
            for i in range(50)
        ]

        numberer = BatesNumberer(prefix="CMB-")
        output_path = os.path.join(self.temp_dir, "combined.pdf")

        start_time = time.time()
        result = numberer.combine_and_process_pdfs(pdf_paths, output_path)
        elapsed = time.time() - start_time

        assert result['success'] is True
        assert result['total_pages'] == 100  # 50 files * 2 pages

        print(f"\n50 PDFs combined in {elapsed:.2f} seconds")
        print(f"Total pages: {result['total_pages']}")

    def test_memory_usage_large_document(self):
        """Test memory efficiency with large documents."""
        import tracemalloc

        pdf_path = self._create_test_pdf("memory_test.pdf", num_pages=100)
        output_path = os.path.join(self.temp_dir, "output.pdf")

        tracemalloc.start()

        numberer = BatesNumberer(prefix="MEM-")
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert metadata['success'] is True

        # Convert to MB for readability
        peak_mb = peak / (1024 * 1024)

        print(f"\nPeak memory usage: {peak_mb:.2f} MB")

        # Memory should be reasonable (adjust threshold as needed)
        assert peak_mb < 500, f"Peak memory {peak_mb:.2f}MB exceeds threshold"

    def test_sequential_numbering_performance(self):
        """Test performance of generating many Bates numbers."""
        numberer = BatesNumberer(prefix="SEQ-")

        start_time = time.time()

        # Generate 10,000 Bates numbers
        numbers = [numberer.get_next_bates_number() for _ in range(10000)]

        elapsed = time.time() - start_time

        assert len(numbers) == 10000
        assert numbers[0] == "SEQ-0001"
        assert numbers[-1] == "SEQ-10000"

        # Should be very fast
        assert elapsed < 1.0, f"Generating 10k numbers took {elapsed:.2f}s"

        print(f"\n10,000 Bates numbers generated in {elapsed:.4f} seconds")
        print(f"Average: {(elapsed / 10000) * 1000:.3f} milliseconds per number")

    def test_overlay_creation_performance(self):
        """Test performance of creating PDF overlays."""
        numberer = BatesNumberer(prefix="OVR-")

        overlays = []
        start_time = time.time()

        # Create 100 overlays
        for i in range(100):
            overlay_path = os.path.join(self.temp_dir, f"overlay_{i}.pdf")
            numberer.create_bates_overlay(
                612, 792,  # Letter size
                f"OVR-{i:04d}",
                overlay_path
            )
            overlays.append(overlay_path)

        elapsed = time.time() - start_time

        # Verify all created
        assert len(overlays) == 100
        for overlay in overlays:
            assert os.path.exists(overlay)

        print(f"\n100 overlays created in {elapsed:.2f} seconds")
        print(f"Average: {(elapsed / 100) * 1000:.1f} milliseconds per overlay")

    def test_qr_code_generation_performance(self):
        """Test performance of QR code generation."""
        numberer = BatesNumberer(enable_qr=True)

        qr_codes = []
        start_time = time.time()

        # Generate 100 QR codes
        for i in range(100):
            qr_path = numberer._create_qr_code(f"TEST-{i:04d}")
            if qr_path:
                qr_codes.append(qr_path)

        elapsed = time.time() - start_time

        assert len(qr_codes) == 100

        # Clean up
        for qr_path in qr_codes:
            if os.path.exists(qr_path):
                os.remove(qr_path)

        print(f"\n100 QR codes generated in {elapsed:.2f} seconds")
        print(f"Average: {(elapsed / 100) * 1000:.1f} milliseconds per QR code")

    @pytest.mark.slow
    def test_complex_features_performance(self):
        """Test performance with all features enabled."""
        # Create test logo
        from PIL import Image
        logo_path = os.path.join(self.temp_dir, "logo.png")
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(logo_path)

        pdf_path = self._create_test_pdf("complex.pdf", num_pages=50)
        output_path = os.path.join(self.temp_dir, "output_complex.pdf")

        numberer = BatesNumberer(
            prefix="COMPLEX-",
            position="bottom-right",
            include_date=True,
            logo_path=logo_path,
            enable_qr=True,
            qr_placement='all_pages',
            enable_watermark=True,
            watermark_text="CONFIDENTIAL"
        )

        start_time = time.time()
        metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)
        elapsed = time.time() - start_time

        assert metadata['success'] is True
        assert metadata['page_count'] == 50

        print(f"\n50-page document with all features processed in {elapsed:.2f} seconds")
        print(f"Average: {elapsed / 50:.3f} seconds per page")

        # Should still be reasonable even with all features
        assert elapsed < 180.0, f"Processing took {elapsed:.2f}s, expected < 180s"


class TestScalability:
    """Tests for scalability with varying loads."""

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

    def test_scalability_increasing_pages(self):
        """Test scalability with increasing page counts."""
        page_counts = [10, 50, 100, 200]
        times = []

        for page_count in page_counts:
            pdf_path = self._create_test_pdf(f"scale_{page_count}.pdf", num_pages=page_count)
            output_path = os.path.join(self.temp_dir, f"output_{page_count}.pdf")

            numberer = BatesNumberer(prefix=f"P{page_count}-")

            start_time = time.time()
            metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)
            elapsed = time.time() - start_time

            assert metadata['success'] is True
            times.append(elapsed)

            print(f"{page_count} pages: {elapsed:.2f}s ({elapsed/page_count:.4f}s per page)")

        # Time should scale roughly linearly
        # (not exponentially - no page_count^2 behavior)
        time_per_page = [t/p for t, p in zip(times, page_counts)]

        # Variance should be reasonable
        import statistics
        variance = statistics.variance(time_per_page) if len(time_per_page) > 1 else 0

        print(f"\nTime per page variance: {variance:.6f}")
        print(f"Average time per page: {statistics.mean(time_per_page):.4f}s")

    def test_concurrent_numberer_instances(self):
        """Test multiple BatesNumberer instances don't interfere."""
        pdf_path = self._create_test_pdf("concurrent.pdf", num_pages=5)

        # Create multiple numberers with different configs
        numberers = [
            BatesNumberer(prefix=f"INST{i}-", start_number=i*100)
            for i in range(5)
        ]

        # Process with each
        for i, numberer in enumerate(numberers):
            output = os.path.join(self.temp_dir, f"output_{i}.pdf")
            metadata = numberer.process_pdf(pdf_path, output, return_metadata=True)

            assert metadata['success'] is True
            # Each should have correct prefix and numbering
            expected_first = f"INST{i}-{i*100:04d}"
            assert metadata['first_bates'] == expected_first
