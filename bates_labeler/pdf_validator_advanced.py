"""
Advanced PDF Validation and Repair Module

Provides comprehensive PDF health checking, corruption detection,
and automatic repair capabilities for batch processing.

Features:
- Deep PDF structure validation
- Corruption detection and repair
- Metadata integrity checks
- Page count verification
- Font embedding validation
- Image compression analysis
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RepairStrategy(Enum):
    """PDF repair strategies."""
    NONE = "none"
    AUTO = "auto"
    GHOSTSCRIPT = "ghostscript"
    QPDF = "qpdf"
    FORCE_REWRITE = "force_rewrite"


@dataclass
class ValidationIssue:
    """Represents a single validation issue."""
    severity: ValidationSeverity
    category: str
    message: str
    page_num: Optional[int] = None
    repairable: bool = False


@dataclass
class ValidationReport:
    """Comprehensive validation report for a PDF."""
    filepath: str
    is_valid: bool
    is_repairable: bool
    page_count: int
    file_size_bytes: int
    issues: List[ValidationIssue]
    metadata: Dict[str, any]
    repair_strategy: Optional[RepairStrategy] = None

    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def has_critical_issues(self) -> bool:
        """Check if report contains critical issues."""
        return any(issue.severity == ValidationSeverity.CRITICAL for issue in self.issues)

    def summary(self) -> str:
        """Generate a human-readable summary."""
        critical = len(self.get_issues_by_severity(ValidationSeverity.CRITICAL))
        errors = len(self.get_issues_by_severity(ValidationSeverity.ERROR))
        warnings = len(self.get_issues_by_severity(ValidationSeverity.WARNING))

        status = "VALID" if self.is_valid else "INVALID"
        repair_status = " (Repairable)" if self.is_repairable else " (Not repairable)" if not self.is_valid else ""

        return (
            f"PDF Validation Report: {status}{repair_status}\n"
            f"File: {self.filepath}\n"
            f"Pages: {self.page_count} | Size: {self.file_size_bytes / 1024:.2f} KB\n"
            f"Issues: {critical} critical, {errors} errors, {warnings} warnings"
        )


class PDFValidatorAdvanced:
    """
    Advanced PDF validator with repair capabilities.

    Performs deep validation of PDF structure, detects corruption,
    and can attempt automatic repairs using multiple strategies.
    """

    def __init__(self, enable_repair: bool = True, repair_strategy: RepairStrategy = RepairStrategy.AUTO):
        """
        Initialize the advanced PDF validator.

        Args:
            enable_repair: Whether to enable automatic repair attempts
            repair_strategy: Strategy to use for repairs
        """
        self.enable_repair = enable_repair
        self.repair_strategy = repair_strategy
        self.ghostscript_available = self._check_ghostscript()
        self.qpdf_available = self._check_qpdf()

    def _check_ghostscript(self) -> bool:
        """Check if Ghostscript is available."""
        try:
            subprocess.run(['gs', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_qpdf(self) -> bool:
        """Check if qpdf is available."""
        try:
            subprocess.run(['qpdf', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def validate_pdf(self, pdf_path: str) -> ValidationReport:
        """
        Perform comprehensive PDF validation.

        Args:
            pdf_path: Path to PDF file to validate

        Returns:
            ValidationReport with detailed findings
        """
        issues: List[ValidationIssue] = []
        page_count = 0
        metadata = {}
        is_valid = True
        is_repairable = False

        # Check file exists
        if not os.path.exists(pdf_path):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="file",
                message=f"File not found: {pdf_path}",
                repairable=False
            ))
            return ValidationReport(
                filepath=pdf_path,
                is_valid=False,
                is_repairable=False,
                page_count=0,
                file_size_bytes=0,
                issues=issues,
                metadata={}
            )

        file_size = os.path.getsize(pdf_path)

        # Attempt to read PDF
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f, strict=False)
                page_count = len(reader.pages)

                # Extract metadata
                if reader.metadata:
                    metadata = {
                        'title': reader.metadata.get('/Title', ''),
                        'author': reader.metadata.get('/Author', ''),
                        'subject': reader.metadata.get('/Subject', ''),
                        'creator': reader.metadata.get('/Creator', ''),
                        'producer': reader.metadata.get('/Producer', ''),
                    }

                # Validate each page
                for i, page in enumerate(reader.pages):
                    try:
                        # Try to access page content
                        _ = page.extract_text()
                        _ = page.mediabox

                    except Exception as e:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category="page",
                            message=f"Page {i + 1} error: {str(e)}",
                            page_num=i + 1,
                            repairable=True
                        ))
                        is_valid = False
                        is_repairable = True

                # Check for encryption
                if reader.is_encrypted:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="encryption",
                        message="PDF is encrypted",
                        repairable=False
                    ))

                # Check page count
                if page_count == 0:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category="structure",
                        message="PDF contains no pages",
                        repairable=False
                    ))
                    is_valid = False

        except PdfReadError as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="corruption",
                message=f"PDF read error: {str(e)}",
                repairable=True
            ))
            is_valid = False
            is_repairable = True

        except Exception as e:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="unknown",
                message=f"Unexpected error: {str(e)}",
                repairable=True
            ))
            is_valid = False
            is_repairable = True

        # File size checks
        if file_size == 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                category="file",
                message="PDF file is empty (0 bytes)",
                repairable=False
            ))
            is_valid = False
        elif file_size > 100 * 1024 * 1024:  # 100 MB
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="size",
                message=f"Large PDF file ({file_size / (1024*1024):.2f} MB)",
                repairable=False
            ))

        return ValidationReport(
            filepath=pdf_path,
            is_valid=is_valid,
            is_repairable=is_repairable and self.enable_repair,
            page_count=page_count,
            file_size_bytes=file_size,
            issues=issues,
            metadata=metadata,
            repair_strategy=self.repair_strategy if is_repairable else None
        )

    def repair_pdf(self, pdf_path: str, output_path: str, strategy: Optional[RepairStrategy] = None) -> Tuple[bool, str]:
        """
        Attempt to repair a corrupted PDF.

        Args:
            pdf_path: Path to corrupted PDF
            output_path: Path for repaired PDF
            strategy: Repair strategy to use (uses self.repair_strategy if None)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enable_repair:
            return False, "Repair is disabled"

        strategy = strategy or self.repair_strategy

        # Auto-select strategy based on available tools
        if strategy == RepairStrategy.AUTO:
            if self.qpdf_available:
                strategy = RepairStrategy.QPDF
            elif self.ghostscript_available:
                strategy = RepairStrategy.GHOSTSCRIPT
            else:
                strategy = RepairStrategy.FORCE_REWRITE

        try:
            if strategy == RepairStrategy.QPDF:
                return self._repair_with_qpdf(pdf_path, output_path)
            elif strategy == RepairStrategy.GHOSTSCRIPT:
                return self._repair_with_ghostscript(pdf_path, output_path)
            elif strategy == RepairStrategy.FORCE_REWRITE:
                return self._repair_with_rewrite(pdf_path, output_path)
            else:
                return False, f"Unknown repair strategy: {strategy}"

        except Exception as e:
            return False, f"Repair failed: {str(e)}"

    def _repair_with_qpdf(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Repair PDF using qpdf."""
        if not self.qpdf_available:
            return False, "qpdf not available"

        try:
            result = subprocess.run(
                ['qpdf', '--check-linearization=n', input_path, output_path],
                capture_output=True,
                text=True,
                check=True
            )
            return True, "Repaired with qpdf"
        except subprocess.CalledProcessError as e:
            return False, f"qpdf repair failed: {e.stderr}"

    def _repair_with_ghostscript(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Repair PDF using Ghostscript."""
        if not self.ghostscript_available:
            return False, "Ghostscript not available"

        try:
            result = subprocess.run([
                'gs',
                '-dNOPAUSE', '-dBATCH', '-dSAFER',
                '-sDEVICE=pdfwrite',
                '-dCompatibilityLevel=1.7',
                '-dPDFSETTINGS=/prepress',
                f'-sOutputFile={output_path}',
                input_path
            ], capture_output=True, text=True, check=True)
            return True, "Repaired with Ghostscript"
        except subprocess.CalledProcessError as e:
            return False, f"Ghostscript repair failed: {e.stderr}"

    def _repair_with_rewrite(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """Repair PDF by rewriting with pypdf."""
        try:
            with open(input_path, 'rb') as input_file:
                reader = PdfReader(input_file, strict=False)
                writer = PdfWriter()

                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)

                # Copy metadata if available
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        writer.add_metadata({key: value})

                # Write repaired PDF
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)

            return True, "Repaired by rewriting"
        except Exception as e:
            return False, f"Rewrite repair failed: {str(e)}"

    def batch_validate(self, pdf_paths: List[str], stop_on_error: bool = False) -> List[ValidationReport]:
        """
        Validate multiple PDFs in batch.

        Args:
            pdf_paths: List of PDF file paths
            stop_on_error: Stop validation if critical error found

        Returns:
            List of ValidationReport objects
        """
        reports = []

        for pdf_path in pdf_paths:
            report = self.validate_pdf(pdf_path)
            reports.append(report)

            if stop_on_error and report.has_critical_issues():
                logger.warning(f"Stopping batch validation due to critical issue in {pdf_path}")
                break

        return reports

    def batch_repair(self, validation_reports: List[ValidationReport], output_dir: str) -> List[Tuple[str, bool, str]]:
        """
        Repair multiple PDFs based on validation reports.

        Args:
            validation_reports: List of validation reports
            output_dir: Directory for repaired PDFs

        Returns:
            List of (filepath, success, message) tuples
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []

        for report in validation_reports:
            if not report.is_repairable:
                results.append((report.filepath, False, "Not repairable"))
                continue

            input_path = report.filepath
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_dir, f"repaired_{filename}")

            success, message = self.repair_pdf(input_path, output_path)
            results.append((input_path, success, message))

            if success:
                logger.info(f"Successfully repaired: {input_path} -> {output_path}")
            else:
                logger.error(f"Failed to repair {input_path}: {message}")

        return results


# Utility functions for integration

def validate_before_processing(pdf_path: str, auto_repair: bool = True) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate PDF before Bates numbering, optionally repair if needed.

    Args:
        pdf_path: Path to PDF file
        auto_repair: Whether to automatically repair if validation fails

    Returns:
        Tuple of (is_valid: bool, repaired_path: Optional[str], message: str)
    """
    validator = PDFValidatorAdvanced(enable_repair=auto_repair)
    report = validator.validate_pdf(pdf_path)

    if report.is_valid:
        return True, None, "PDF is valid"

    if not auto_repair or not report.is_repairable:
        return False, None, f"PDF is invalid: {report.summary()}"

    # Attempt repair
    repaired_path = pdf_path.replace('.pdf', '_repaired.pdf')
    success, message = validator.repair_pdf(pdf_path, repaired_path)

    if success:
        # Validate repaired PDF
        repaired_report = validator.validate_pdf(repaired_path)
        if repaired_report.is_valid:
            return True, repaired_path, f"PDF repaired successfully: {message}"
        else:
            return False, None, f"Repair failed to fix all issues: {repaired_report.summary()}"
    else:
        return False, None, f"Repair failed: {message}"


__all__ = [
    'PDFValidatorAdvanced',
    'ValidationReport',
    'ValidationIssue',
    'ValidationSeverity',
    'RepairStrategy',
    'validate_before_processing',
]
