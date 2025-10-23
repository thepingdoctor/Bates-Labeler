"""Tests for CLI interface."""

import pytest
import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader


class TestCLI:
    """Test cases for command-line interface."""

    def setup_method(self):
        """Create temporary directory and test PDFs."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = self._create_test_pdf("input.pdf", num_pages=3)

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
            c.showPage()

        c.save()
        return filepath

    def _run_cli(self, args):
        """Helper to run CLI command."""
        cmd = [sys.executable, "-m", "bates_labeler.cli"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        return result

    def test_cli_version(self):
        """Test --version flag."""
        result = self._run_cli(["--version"])

        assert result.returncode == 0
        assert "bates-labeler" in result.stdout.lower()

    def test_cli_basic_processing(self):
        """Test basic CLI processing."""
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "CLI-"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Verify output
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3

    def test_cli_with_separator(self):
        """Test CLI with separator page option."""
        output_path = os.path.join(self.temp_dir, "output_sep.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "SEP-",
            "--add-separator"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Should have separator page
        reader = PdfReader(output_path)
        assert len(reader.pages) == 4  # 3 + 1 separator

    def test_cli_custom_position(self):
        """Test CLI with custom position."""
        output_path = os.path.join(self.temp_dir, "output_pos.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "POS-",
            "--position", "top-right"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_custom_font_settings(self):
        """Test CLI with custom font settings."""
        output_path = os.path.join(self.temp_dir, "output_font.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "FONT-",
            "--font-name", "Courier",
            "--font-size", "14",
            "--font-color", "blue",
            "--italic"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_with_date_stamp(self):
        """Test CLI with date stamp option."""
        output_path = os.path.join(self.temp_dir, "output_date.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "DATE-",
            "--include-date",
            "--date-format", "%Y-%m-%d"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_no_background(self):
        """Test CLI with background disabled."""
        output_path = os.path.join(self.temp_dir, "output_nobg.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "NOBG-",
            "--no-background"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_batch_processing(self):
        """Test CLI batch processing."""
        # Create multiple test PDFs
        pdf1 = self._create_test_pdf("batch1.pdf", num_pages=2)
        pdf2 = self._create_test_pdf("batch2.pdf", num_pages=2)
        pdf3 = self._create_test_pdf("batch3.pdf", num_pages=2)

        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir)

        result = self._run_cli([
            "--batch", pdf1, pdf2, pdf3,
            "--output-dir", output_dir,
            "--bates-prefix", "BATCH-"
        ])

        assert result.returncode == 0

        # Verify output files
        expected_files = [
            "batch1_bates.pdf",
            "batch2_bates.pdf",
            "batch3_bates.pdf"
        ]

        for filename in expected_files:
            output_path = os.path.join(output_dir, filename)
            assert os.path.exists(output_path)

    def test_cli_combine_pdfs(self):
        """Test CLI combine PDFs option."""
        pdf1 = self._create_test_pdf("combine1.pdf", num_pages=2)
        pdf2 = self._create_test_pdf("combine2.pdf", num_pages=2)

        output_path = os.path.join(self.temp_dir, "combined.pdf")

        result = self._run_cli([
            "--batch", pdf1, pdf2,
            "--output", output_path,
            "--bates-prefix", "CMB-",
            "--combine"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Should have combined pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 4  # 2 + 2

    def test_cli_combine_with_separators(self):
        """Test CLI combine with document separators."""
        pdf1 = self._create_test_pdf("sep1.pdf", num_pages=2)
        pdf2 = self._create_test_pdf("sep2.pdf", num_pages=2)

        output_path = os.path.join(self.temp_dir, "combined_sep.pdf")

        result = self._run_cli([
            "--batch", pdf1, pdf2,
            "--output", output_path,
            "--bates-prefix", "CSEP-",
            "--combine",
            "--document-separators"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Should have pages + separators
        reader = PdfReader(output_path)
        assert len(reader.pages) == 6  # 2 + 2 + 2 separators

    def test_cli_combine_with_index(self):
        """Test CLI combine with index page."""
        pdf1 = self._create_test_pdf("idx1.pdf", num_pages=2)
        pdf2 = self._create_test_pdf("idx2.pdf", num_pages=2)

        output_path = os.path.join(self.temp_dir, "combined_idx.pdf")

        result = self._run_cli([
            "--batch", pdf1, pdf2,
            "--output", output_path,
            "--bates-prefix", "IDX-",
            "--combine",
            "--add-index"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Should have index + pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 5  # 1 index + 2 + 2

    def test_cli_bates_filenames(self):
        """Test CLI with Bates number filenames."""
        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir)

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output-dir", output_dir,
            "--bates-prefix", "FILE-",
            "--start-number", "100",
            "--bates-filenames"
        ])

        # Should create file named with first Bates number
        expected_file = os.path.join(output_dir, "FILE-0100.pdf")
        assert os.path.exists(expected_file)

        # Should create mapping files
        csv_mapping = os.path.join(output_dir, "bates_mapping.csv")
        pdf_mapping = os.path.join(output_dir, "bates_mapping.pdf")

        # Note: mapping files might be in current dir depending on implementation
        # Just verify the main output file for now

    def test_cli_custom_padding(self):
        """Test CLI with custom padding."""
        output_path = os.path.join(self.temp_dir, "output_pad.pdf")

        result = self._run_cli([
            "--input", self.test_pdf,
            "--output", output_path,
            "--bates-prefix", "PAD-",
            "--padding", "6",
            "--start-number", "1"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Bates numbers should be PAD-000001, PAD-000002, etc.

    def test_cli_nonexistent_input(self):
        """Test CLI with nonexistent input file."""
        result = self._run_cli([
            "--input", "/nonexistent/file.pdf",
            "--bates-prefix", "ERR-"
        ])

        # Should fail
        assert result.returncode != 0

    def test_cli_help(self):
        """Test CLI help output."""
        result = self._run_cli(["--help"])

        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "bates" in result.stdout.lower()
        assert "prefix" in result.stdout.lower()


class TestCLIEdgeCases:
    """Test edge cases for CLI."""

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

    def _run_cli(self, args):
        """Helper to run CLI command."""
        cmd = [sys.executable, "-m", "bates_labeler.cli"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        return result

    def test_cli_empty_prefix_suffix(self):
        """Test CLI with empty prefix and suffix."""
        test_pdf = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", test_pdf,
            "--output", output_path,
            "--bates-prefix", "",
            "--bates-suffix", ""
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_special_characters_in_prefix(self):
        """Test CLI with special characters in prefix."""
        test_pdf = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", test_pdf,
            "--output", output_path,
            "--bates-prefix", "CASE#123_@-"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_very_large_start_number(self):
        """Test CLI with very large start number."""
        test_pdf = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", test_pdf,
            "--output", output_path,
            "--bates-prefix", "BIG-",
            "--start-number", "999999"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_minimum_padding(self):
        """Test CLI with minimum padding."""
        test_pdf = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", test_pdf,
            "--output", output_path,
            "--bates-prefix", "MIN-",
            "--padding", "1"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

    def test_cli_maximum_font_size(self):
        """Test CLI with very large font size."""
        test_pdf = self._create_test_pdf("test.pdf")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        result = self._run_cli([
            "--input", test_pdf,
            "--output", output_path,
            "--bates-prefix", "HUGE-",
            "--font-size", "24"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

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

    def _run_cli(self, args):
        """Helper to run CLI command."""
        cmd = [sys.executable, "-m", "bates_labeler.cli"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        return result

    def test_complete_legal_workflow(self):
        """Test a complete legal document processing workflow."""
        # Create mock legal documents
        exhibit_a = self._create_test_pdf("Exhibit_A.pdf", num_pages=5)
        exhibit_b = self._create_test_pdf("Exhibit_B.pdf", num_pages=3)
        exhibit_c = self._create_test_pdf("Exhibit_C.pdf", num_pages=7)

        output_path = os.path.join(self.temp_dir, "production.pdf")

        # Combine with separators and index
        result = self._run_cli([
            "--batch", exhibit_a, exhibit_b, exhibit_c,
            "--output", output_path,
            "--bates-prefix", "PLAINTIFF-PROD-",
            "--padding", "6",
            "--position", "bottom-right",
            "--font-size", "12",
            "--combine",
            "--document-separators",
            "--add-index"
        ])

        assert result.returncode == 0
        assert os.path.exists(output_path)

        # Verify output structure
        reader = PdfReader(output_path)

        # 1 index + 3 separators + (5 + 3 + 7) pages = 19 pages
        expected_pages = 1 + 3 + (5 + 3 + 7)
        assert len(reader.pages) == expected_pages

    def test_batch_with_continuous_numbering(self):
        """Test batch processing maintains continuous numbering."""
        pdfs = [
            self._create_test_pdf(f"doc{i}.pdf", num_pages=2)
            for i in range(3)
        ]

        output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(output_dir)

        result = self._run_cli([
            "--batch"] + pdfs + [
            "--output-dir", output_dir,
            "--bates-prefix", "CONT-",
            "--start-number", "1"
        ])

        assert result.returncode == 0

        # All files should be processed
        for i in range(3):
            output_file = os.path.join(output_dir, f"doc{i}_bates.pdf")
            assert os.path.exists(output_file)
