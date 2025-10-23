"""Integration tests for PDF processing workflows."""

import pytest
import os
import tempfile
import shutil
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from bates_labeler import BatesNumberer


class TestPDFProcessing:
    """Integration tests for PDF document processing."""

    def setup_method(self):
        """Create temporary directory and test PDFs."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_pdf = self._create_test_pdf("test_document.pdf", num_pages=3)
        self.test_pdf_encrypted = self._create_encrypted_pdf("test_encrypted.pdf", "password123")

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, filename, num_pages=1, page_size=letter):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=page_size)

        for i in range(num_pages):
            c.drawString(100, 750, f"Test Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def _create_encrypted_pdf(self, filename, password):
        """Helper to create a password-protected PDF."""
        # First create a regular PDF
        temp_pdf = self._create_test_pdf("temp_encrypted.pdf", num_pages=2)

        # Encrypt it
        reader = PdfReader(temp_pdf)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Add password protection
        writer.encrypt(password)

        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'wb') as output_file:
            writer.write(output_file)

        os.remove(temp_pdf)
        return filepath

    def test_process_simple_pdf(self):
        """Test processing a simple PDF document."""
        numberer = BatesNumberer(prefix="TEST-")
        output_path = os.path.join(self.temp_dir, "output.pdf")

        success = numberer.process_pdf(self.test_pdf, output_path)

        assert success is True
        assert os.path.exists(output_path)

        # Verify output has same number of pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 3

    def test_process_with_separator_page(self):
        """Test processing PDF with separator page."""
        numberer = BatesNumberer(prefix="DOC-")
        output_path = os.path.join(self.temp_dir, "output_separator.pdf")

        success = numberer.process_pdf(self.test_pdf, output_path, add_separator=True)

        assert success is True
        assert os.path.exists(output_path)

        # Should have original pages + 1 separator
        reader = PdfReader(output_path)
        assert len(reader.pages) == 4  # 3 original + 1 separator

    def test_process_with_metadata_return(self):
        """Test processing with metadata return."""
        numberer = BatesNumberer(prefix="CASE-", start_number=100, padding=4)
        output_path = os.path.join(self.temp_dir, "output_meta.pdf")

        result = numberer.process_pdf(
            self.test_pdf,
            output_path,
            return_metadata=True
        )

        assert result['success'] is True
        assert result['first_bates'] == "CASE-0100"
        assert result['last_bates'] == "CASE-0102"
        assert result['page_count'] == 3
        assert 'original_filename' in result

    def test_process_encrypted_pdf_with_password(self):
        """Test processing encrypted PDF with correct password."""
        numberer = BatesNumberer(prefix="SEC-")
        output_path = os.path.join(self.temp_dir, "output_encrypted.pdf")

        success = numberer.process_pdf(
            self.test_pdf_encrypted,
            output_path,
            password="password123"
        )

        assert success is True
        assert os.path.exists(output_path)

    def test_process_encrypted_pdf_wrong_password(self):
        """Test processing encrypted PDF with wrong password."""
        numberer = BatesNumberer(prefix="SEC-")
        output_path = os.path.join(self.temp_dir, "output_failed.pdf")

        success = numberer.process_pdf(
            self.test_pdf_encrypted,
            output_path,
            password="wrongpassword"
        )

        assert success is False

    def test_continuous_numbering_across_pdfs(self):
        """Test that Bates numbers continue across multiple PDFs."""
        pdf1 = self._create_test_pdf("doc1.pdf", num_pages=2)
        pdf2 = self._create_test_pdf("doc2.pdf", num_pages=3)

        numberer = BatesNumberer(prefix="CONT-", start_number=1)

        # Process first PDF
        output1 = os.path.join(self.temp_dir, "out1.pdf")
        metadata1 = numberer.process_pdf(pdf1, output1, return_metadata=True)

        # Process second PDF with same numberer
        output2 = os.path.join(self.temp_dir, "out2.pdf")
        metadata2 = numberer.process_pdf(pdf2, output2, return_metadata=True)

        # Verify continuous numbering
        assert metadata1['first_bates'] == "CONT-0001"
        assert metadata1['last_bates'] == "CONT-0002"
        assert metadata2['first_bates'] == "CONT-0003"
        assert metadata2['last_bates'] == "CONT-0005"

    def test_different_page_sizes(self):
        """Test processing PDFs with different page sizes."""
        from reportlab.lib.pagesizes import A4, legal

        pdf_letter = self._create_test_pdf("letter.pdf", page_size=letter)
        pdf_a4 = self._create_test_pdf("a4.pdf", page_size=A4)
        pdf_legal = self._create_test_pdf("legal.pdf", page_size=legal)

        numberer = BatesNumberer(prefix="SIZE-")

        for pdf_path in [pdf_letter, pdf_a4, pdf_legal]:
            output = os.path.join(
                self.temp_dir,
                f"out_{os.path.basename(pdf_path)}"
            )
            success = numberer.process_pdf(pdf_path, output)
            assert success is True
            assert os.path.exists(output)


class TestBatchProcessing:
    """Test cases for batch PDF processing."""

    def setup_method(self):
        """Create temporary directory and multiple test PDFs."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir)

        # Create multiple test PDFs
        self.test_pdfs = []
        for i in range(3):
            pdf_path = self._create_test_pdf(f"batch_{i+1}.pdf", num_pages=2)
            self.test_pdfs.append(pdf_path)

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

    def test_batch_processing_basic(self):
        """Test basic batch processing of multiple PDFs."""
        numberer = BatesNumberer(prefix="BATCH-")
        numberer.process_batch(self.test_pdfs, self.output_dir)

        # Verify output files exist
        for original_path in self.test_pdfs:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_name = f"{base_name}_bates.pdf"
            output_path = os.path.join(self.output_dir, output_name)
            assert os.path.exists(output_path)

    def test_batch_with_separator_pages(self):
        """Test batch processing with separator pages."""
        numberer = BatesNumberer(prefix="BSEP-")
        numberer.process_batch(self.test_pdfs, self.output_dir, add_separator=True)

        # Each output should have separator page
        for original_path in self.test_pdfs:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            output_name = f"{base_name}_bates.pdf"
            output_path = os.path.join(self.output_dir, output_name)

            reader = PdfReader(output_path)
            # 2 original pages + 1 separator = 3 pages
            assert len(reader.pages) == 3

    def test_batch_continuous_numbering(self):
        """Test that batch processing maintains continuous numbering."""
        numberer = BatesNumberer(prefix="CONT-", start_number=1)

        # Track which numberer instance is used
        results = []
        for pdf_path in self.test_pdfs:
            output_path = os.path.join(
                self.output_dir,
                os.path.basename(pdf_path).replace('.pdf', '_bates.pdf')
            )
            metadata = numberer.process_pdf(pdf_path, output_path, return_metadata=True)
            results.append(metadata)

        # Verify continuous numbering across all files
        assert results[0]['first_bates'] == "CONT-0001"
        assert results[0]['last_bates'] == "CONT-0002"
        assert results[1]['first_bates'] == "CONT-0003"
        assert results[1]['last_bates'] == "CONT-0004"
        assert results[2]['first_bates'] == "CONT-0005"
        assert results[2]['last_bates'] == "CONT-0006"


class TestPDFCombination:
    """Test cases for combining multiple PDFs."""

    def setup_method(self):
        """Create temporary directory and test PDFs."""
        self.temp_dir = tempfile.mkdtemp()

        # Create multiple test PDFs
        self.test_pdfs = []
        for i in range(3):
            pdf_path = self._create_test_pdf(f"combine_{i+1}.pdf", num_pages=2)
            self.test_pdfs.append(pdf_path)

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_test_pdf(self, filename, num_pages=1):
        """Helper to create a test PDF file."""
        filepath = os.path.join(self.temp_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        for i in range(num_pages):
            c.drawString(100, 750, f"Document: {filename}, Page {i + 1}")
            c.showPage()

        c.save()
        return filepath

    def test_combine_pdfs_basic(self):
        """Test combining multiple PDFs into one."""
        numberer = BatesNumberer(prefix="CMB-")
        output_path = os.path.join(self.temp_dir, "combined.pdf")

        result = numberer.combine_and_process_pdfs(
            self.test_pdfs,
            output_path
        )

        assert result['success'] is True
        assert os.path.exists(output_path)

        # Verify combined file has all pages (3 PDFs * 2 pages each = 6 pages)
        reader = PdfReader(output_path)
        assert len(reader.pages) == 6

        # Verify metadata
        assert len(result['documents']) == 3
        assert result['total_pages'] == 6

    def test_combine_with_document_separators(self):
        """Test combining PDFs with separator pages between documents."""
        numberer = BatesNumberer(prefix="SEP-")
        output_path = os.path.join(self.temp_dir, "combined_sep.pdf")

        result = numberer.combine_and_process_pdfs(
            self.test_pdfs,
            output_path,
            add_document_separators=True
        )

        assert result['success'] is True
        assert os.path.exists(output_path)

        # 3 PDFs * 2 pages + 3 separators = 9 pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 9

    def test_combine_with_index_page(self):
        """Test combining PDFs with index page."""
        numberer = BatesNumberer(prefix="IDX-")
        output_path = os.path.join(self.temp_dir, "combined_idx.pdf")

        result = numberer.combine_and_process_pdfs(
            self.test_pdfs,
            output_path,
            add_index_page=True
        )

        assert result['success'] is True
        assert os.path.exists(output_path)

        # 1 index page + 3 PDFs * 2 pages = 7 pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 7

    def test_combine_with_separators_and_index(self):
        """Test combining with both separators and index page."""
        numberer = BatesNumberer(prefix="FULL-")
        output_path = os.path.join(self.temp_dir, "combined_full.pdf")

        result = numberer.combine_and_process_pdfs(
            self.test_pdfs,
            output_path,
            add_document_separators=True,
            add_index_page=True
        )

        assert result['success'] is True

        # 1 index + 3 separators + 3 PDFs * 2 pages = 10 pages
        reader = PdfReader(output_path)
        assert len(reader.pages) == 10

    def test_combine_metadata_tracking(self):
        """Test that document metadata is correctly tracked."""
        numberer = BatesNumberer(prefix="META-", start_number=100)
        output_path = os.path.join(self.temp_dir, "combined_meta.pdf")

        result = numberer.combine_and_process_pdfs(
            self.test_pdfs,
            output_path
        )

        assert result['success'] is True
        assert len(result['documents']) == 3

        # Check first document metadata
        doc1 = result['documents'][0]
        assert doc1['first_bates'] == "META-0100"
        assert doc1['last_bates'] == "META-0101"
        assert doc1['page_count'] == 2

        # Check continuous numbering
        doc2 = result['documents'][1]
        assert doc2['first_bates'] == "META-0102"
        assert doc2['last_bates'] == "META-0103"

        doc3 = result['documents'][2]
        assert doc3['first_bates'] == "META-0104"
        assert doc3['last_bates'] == "META-0105"


class TestFilenameMappingGeneration:
    """Test cases for filename mapping CSV and PDF generation."""

    def setup_method(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_csv_mapping(self):
        """Test CSV mapping file generation."""
        numberer = BatesNumberer()
        mappings = [
            {
                'original_filename': 'doc1.pdf',
                'new_filename': 'CASE-0001.pdf',
                'first_bates': 'CASE-0001',
                'last_bates': 'CASE-0005',
                'page_count': 5
            },
            {
                'original_filename': 'doc2.pdf',
                'new_filename': 'CASE-0006.pdf',
                'first_bates': 'CASE-0006',
                'last_bates': 'CASE-0010',
                'page_count': 5
            }
        ]

        csv_path = os.path.join(self.temp_dir, "mapping.csv")
        success = numberer.generate_filename_mapping_csv(mappings, csv_path)

        assert success is True
        assert os.path.exists(csv_path)

        # Verify CSV content
        with open(csv_path, 'r') as f:
            content = f.read()
            assert 'Original Filename' in content
            assert 'doc1.pdf' in content
            assert 'CASE-0001' in content

    def test_generate_pdf_mapping(self):
        """Test PDF mapping file generation."""
        numberer = BatesNumberer()
        mappings = [
            {
                'original_filename': 'evidence.pdf',
                'new_filename': 'BATCH-0001.pdf',
                'first_bates': 'BATCH-0001',
                'last_bates': 'BATCH-0003',
                'page_count': 3
            }
        ]

        pdf_path = os.path.join(self.temp_dir, "mapping.pdf")
        success = numberer.generate_filename_mapping_pdf(mappings, pdf_path)

        assert success is True
        assert os.path.exists(pdf_path)

        # Verify it's a valid PDF
        reader = PdfReader(pdf_path)
        assert len(reader.pages) >= 1
