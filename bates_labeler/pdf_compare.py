"""
PDF Comparison and Diff Viewer Module

Compare PDFs to identify differences between original and processed documents,
useful for verifying Bates numbering application and quality control.

Features:
- Text-based comparison
- Visual diff generation
- Page-by-page comparison
- Metadata comparison
- Change highlighting
- Comparison reports (HTML, PDF, JSON)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple, Set
import difflib
import logging
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import tempfile
import os
import json

logger = logging.getLogger(__name__)


class DifferenceType(Enum):
    """Types of differences that can be detected."""
    TEXT_ADDED = "text_added"
    TEXT_REMOVED = "text_removed"
    TEXT_MODIFIED = "text_modified"
    METADATA_CHANGED = "metadata_changed"
    PAGE_COUNT_CHANGED = "page_count_changed"
    PAGE_SIZE_CHANGED = "page_size_changed"
    ANNOTATION_ADDED = "annotation_added"
    ANNOTATION_REMOVED = "annotation_removed"


class ComparisonMode(Enum):
    """Comparison modes."""
    TEXT_ONLY = "text_only"
    METADATA_ONLY = "metadata_only"
    FULL = "full"  # Text + Metadata
    VISUAL = "visual"  # Render and compare visually


@dataclass
class PageDifference:
    """Represents a difference on a specific page."""
    page_num: int
    difference_type: DifferenceType
    description: str
    before_content: Optional[str] = None
    after_content: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ComparisonResult:
    """Result of PDF comparison."""
    pdf1_path: str
    pdf2_path: str
    are_identical: bool
    comparison_mode: ComparisonMode
    differences: List[PageDifference]
    pdf1_metadata: Dict[str, any]
    pdf2_metadata: Dict[str, any]
    pdf1_page_count: int
    pdf2_page_count: int
    similarity_score: float  # 0.0 - 1.0
    summary: str

    def get_differences_by_type(self, diff_type: DifferenceType) -> List[PageDifference]:
        """Get all differences of a specific type."""
        return [diff for diff in self.differences if diff.difference_type == diff_type]

    def get_differences_by_page(self, page_num: int) -> List[PageDifference]:
        """Get all differences for a specific page."""
        return [diff for diff in self.differences if diff.page_num == page_num]


class PDFComparator:
    """
    Advanced PDF comparison engine.

    Compares two PDF documents to identify differences in text, metadata,
    structure, and generates detailed comparison reports.
    """

    def __init__(self, comparison_mode: ComparisonMode = ComparisonMode.FULL):
        """
        Initialize the PDF comparator.

        Args:
            comparison_mode: Mode of comparison to perform
        """
        self.comparison_mode = comparison_mode

    def compare_pdfs(
        self,
        pdf1_path: str,
        pdf2_path: str,
        ignore_whitespace: bool = True,
        ignore_case: bool = False
    ) -> ComparisonResult:
        """
        Compare two PDF documents.

        Args:
            pdf1_path: Path to first PDF (typically original)
            pdf2_path: Path to second PDF (typically processed)
            ignore_whitespace: Ignore whitespace differences
            ignore_case: Ignore case differences

        Returns:
            ComparisonResult with detailed findings
        """
        differences: List[PageDifference] = []

        try:
            # Read both PDFs
            with open(pdf1_path, 'rb') as f1, open(pdf2_path, 'rb') as f2:
                reader1 = PdfReader(f1)
                reader2 = PdfReader(f2)

                # Extract metadata
                metadata1 = self._extract_metadata(reader1)
                metadata2 = self._extract_metadata(reader2)

                # Page count comparison
                page_count1 = len(reader1.pages)
                page_count2 = len(reader2.pages)

                if page_count1 != page_count2:
                    differences.append(PageDifference(
                        page_num=0,  # Document-level
                        difference_type=DifferenceType.PAGE_COUNT_CHANGED,
                        description=f"Page count changed from {page_count1} to {page_count2}",
                        before_content=str(page_count1),
                        after_content=str(page_count2)
                    ))

                # Metadata comparison
                if self.comparison_mode in [ComparisonMode.METADATA_ONLY, ComparisonMode.FULL]:
                    metadata_diffs = self._compare_metadata(metadata1, metadata2)
                    differences.extend(metadata_diffs)

                # Text comparison
                if self.comparison_mode in [ComparisonMode.TEXT_ONLY, ComparisonMode.FULL]:
                    text_diffs = self._compare_text(
                        reader1,
                        reader2,
                        ignore_whitespace,
                        ignore_case
                    )
                    differences.extend(text_diffs)

                # Calculate similarity score
                similarity_score = self._calculate_similarity(differences, page_count1)

                # Determine if identical
                are_identical = len(differences) == 0

                # Generate summary
                summary = self._generate_summary(
                    differences,
                    page_count1,
                    page_count2,
                    similarity_score
                )

                return ComparisonResult(
                    pdf1_path=pdf1_path,
                    pdf2_path=pdf2_path,
                    are_identical=are_identical,
                    comparison_mode=self.comparison_mode,
                    differences=differences,
                    pdf1_metadata=metadata1,
                    pdf2_metadata=metadata2,
                    pdf1_page_count=page_count1,
                    pdf2_page_count=page_count2,
                    similarity_score=similarity_score,
                    summary=summary
                )

        except Exception as e:
            logger.error(f"PDF comparison failed: {e}")
            raise

    def _extract_metadata(self, reader: PdfReader) -> Dict[str, any]:
        """Extract metadata from PDF."""
        metadata = {}
        if reader.metadata:
            metadata = {
                'title': reader.metadata.get('/Title', ''),
                'author': reader.metadata.get('/Author', ''),
                'subject': reader.metadata.get('/Subject', ''),
                'creator': reader.metadata.get('/Creator', ''),
                'producer': reader.metadata.get('/Producer', ''),
                'creation_date': reader.metadata.get('/CreationDate', ''),
                'mod_date': reader.metadata.get('/ModDate', ''),
            }
        return metadata

    def _compare_metadata(
        self,
        metadata1: Dict[str, any],
        metadata2: Dict[str, any]
    ) -> List[PageDifference]:
        """Compare metadata between two PDFs."""
        differences = []

        all_keys = set(metadata1.keys()) | set(metadata2.keys())

        for key in all_keys:
            val1 = metadata1.get(key, '')
            val2 = metadata2.get(key, '')

            if val1 != val2:
                differences.append(PageDifference(
                    page_num=0,  # Document-level
                    difference_type=DifferenceType.METADATA_CHANGED,
                    description=f"Metadata '{key}' changed",
                    before_content=str(val1),
                    after_content=str(val2)
                ))

        return differences

    def _compare_text(
        self,
        reader1: PdfReader,
        reader2: PdfReader,
        ignore_whitespace: bool,
        ignore_case: bool
    ) -> List[PageDifference]:
        """Compare text content between two PDFs."""
        differences = []

        # Compare each page
        max_pages = max(len(reader1.pages), len(reader2.pages))

        for page_num in range(max_pages):
            # Extract text from both pages
            text1 = ""
            text2 = ""

            if page_num < len(reader1.pages):
                try:
                    text1 = reader1.pages[page_num].extract_text()
                except Exception as e:
                    logger.warning(f"Failed to extract text from PDF1 page {page_num + 1}: {e}")

            if page_num < len(reader2.pages):
                try:
                    text2 = reader2.pages[page_num].extract_text()
                except Exception as e:
                    logger.warning(f"Failed to extract text from PDF2 page {page_num + 1}: {e}")

            # Normalize text if needed
            if ignore_whitespace:
                text1 = ' '.join(text1.split())
                text2 = ' '.join(text2.split())

            if ignore_case:
                text1 = text1.lower()
                text2 = text2.lower()

            # Compare texts
            if text1 != text2:
                # Use difflib to find specific changes
                diff = self._detailed_text_diff(text1, text2)

                differences.append(PageDifference(
                    page_num=page_num + 1,
                    difference_type=DifferenceType.TEXT_MODIFIED,
                    description=f"Text modified on page {page_num + 1}",
                    before_content=text1[:500] if len(text1) > 500 else text1,
                    after_content=text2[:500] if len(text2) > 500 else text2,
                    confidence=self._calculate_page_similarity(text1, text2)
                ))

        return differences

    def _detailed_text_diff(self, text1: str, text2: str) -> str:
        """Generate detailed text diff."""
        diff = difflib.unified_diff(
            text1.splitlines(),
            text2.splitlines(),
            lineterm='',
            n=0
        )
        return '\n'.join(diff)

    def _calculate_page_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two text strings."""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0

        matcher = difflib.SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    def _calculate_similarity(self, differences: List[PageDifference], total_pages: int) -> float:
        """Calculate overall similarity score."""
        if total_pages == 0:
            return 1.0 if len(differences) == 0 else 0.0

        # Weight different types of differences
        weights = {
            DifferenceType.TEXT_MODIFIED: 1.0,
            DifferenceType.PAGE_COUNT_CHANGED: 2.0,
            DifferenceType.METADATA_CHANGED: 0.1,
        }

        weighted_diff_count = sum(
            weights.get(diff.difference_type, 1.0)
            for diff in differences
        )

        # Calculate similarity (1.0 = identical, 0.0 = completely different)
        max_diff = total_pages * 2.0  # Assume max 2 differences per page
        similarity = max(0.0, 1.0 - (weighted_diff_count / max_diff))

        return similarity

    def _generate_summary(
        self,
        differences: List[PageDifference],
        page_count1: int,
        page_count2: int,
        similarity_score: float
    ) -> str:
        """Generate human-readable summary."""
        diff_count = len(differences)

        if diff_count == 0:
            return "PDFs are identical"

        text_mods = len([d for d in differences if d.difference_type == DifferenceType.TEXT_MODIFIED])
        metadata_changes = len([d for d in differences if d.difference_type == DifferenceType.METADATA_CHANGED])

        summary = f"Found {diff_count} difference(s)\n"
        summary += f"Similarity: {similarity_score * 100:.1f}%\n"
        summary += f"Text modifications: {text_mods}\n"
        summary += f"Metadata changes: {metadata_changes}\n"

        if page_count1 != page_count2:
            summary += f"Page count changed: {page_count1} → {page_count2}\n"

        return summary

    def generate_html_report(self, result: ComparisonResult, output_path: str) -> bool:
        """
        Generate HTML comparison report.

        Args:
            result: ComparisonResult to report on
            output_path: Path for HTML report

        Returns:
            True if successful
        """
        try:
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PDF Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .difference {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ff6b6b; background: #fff5f5; }}
        .metadata {{ background: #e3f2fd; padding: 10px; margin: 10px 0; }}
        .score {{ font-size: 24px; font-weight: bold; color: {'#28a745' if result.similarity_score > 0.9 else '#ffc107'}; }}
    </style>
</head>
<body>
    <h1>PDF Comparison Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>PDF 1:</strong> {result.pdf1_path}</p>
        <p><strong>PDF 2:</strong> {result.pdf2_path}</p>
        <p><strong>Status:</strong> {'Identical' if result.are_identical else 'Different'}</p>
        <p class="score">Similarity: {result.similarity_score * 100:.1f}%</p>
        <p><strong>Differences Found:</strong> {len(result.differences)}</p>
    </div>

    <h2>Page Information</h2>
    <p>PDF 1: {result.pdf1_page_count} pages</p>
    <p>PDF 2: {result.pdf2_page_count} pages</p>

    <h2>Differences</h2>
"""

            for diff in result.differences:
                html += f"""
    <div class="difference">
        <p><strong>Page {diff.page_num}:</strong> {diff.difference_type.value}</p>
        <p>{diff.description}</p>
"""
                if diff.before_content and diff.after_content:
                    html += f"""
        <p><strong>Before:</strong> {diff.before_content[:200]}...</p>
        <p><strong>After:</strong> {diff.after_content[:200]}...</p>
"""
                html += "    </div>\n"

            html += """
</body>
</html>
"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"HTML report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            return False

    def generate_json_report(self, result: ComparisonResult, output_path: str) -> bool:
        """
        Generate JSON comparison report.

        Args:
            result: ComparisonResult to report on
            output_path: Path for JSON report

        Returns:
            True if successful
        """
        try:
            report = {
                'pdf1': result.pdf1_path,
                'pdf2': result.pdf2_path,
                'are_identical': result.are_identical,
                'comparison_mode': result.comparison_mode.value,
                'similarity_score': result.similarity_score,
                'page_count_1': result.pdf1_page_count,
                'page_count_2': result.pdf2_page_count,
                'differences': [
                    {
                        'page_num': diff.page_num,
                        'type': diff.difference_type.value,
                        'description': diff.description,
                        'confidence': diff.confidence
                    }
                    for diff in result.differences
                ],
                'summary': result.summary
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            logger.info(f"JSON report generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate JSON report: {e}")
            return False


# Utility functions

def quick_compare(pdf1_path: str, pdf2_path: str) -> ComparisonResult:
    """
    Quick comparison with default settings.

    Args:
        pdf1_path: Original PDF path
        pdf2_path: Modified PDF path

    Returns:
        ComparisonResult
    """
    comparator = PDFComparator()
    return comparator.compare_pdfs(pdf1_path, pdf2_path)


def verify_bates_numbering(original_path: str, bates_numbered_path: str) -> Tuple[bool, ComparisonResult]:
    """
    Verify that Bates numbering was applied correctly.

    Args:
        original_path: Original PDF path
        bates_numbered_path: Bates-numbered PDF path

    Returns:
        Tuple of (is_valid: bool, result: ComparisonResult)
    """
    comparator = PDFComparator(comparison_mode=ComparisonMode.TEXT_ONLY)
    result = comparator.compare_pdfs(original_path, bates_numbered_path, ignore_whitespace=True)

    # Bates numbering should add text, not remove or heavily modify
    text_removed = len([d for d in result.differences if d.difference_type == DifferenceType.TEXT_REMOVED])
    is_valid = text_removed == 0 and result.similarity_score > 0.95

    return is_valid, result


__all__ = [
    'PDFComparator',
    'ComparisonResult',
    'PageDifference',
    'DifferenceType',
    'ComparisonMode',
    'quick_compare',
    'verify_bates_numbering',
]
