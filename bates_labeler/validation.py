"""PDF pre-flight validation module for Bates-Labeler.

This module provides comprehensive validation of PDF files before processing,
detecting potential issues that could cause failures during Bates numbering.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from pypdf import PdfReader
from pypdf.errors import PdfReadError


# Configure logging
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a PDF."""
    severity: ValidationSeverity
    code: str
    message: str
    details: Optional[Dict] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of the issue."""
        return f"[{self.severity.value.upper()}] {self.code}: {self.message}"


@dataclass
class ValidationResult:
    """Results from PDF validation."""
    file_path: str
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    file_info: Dict = field(default_factory=dict)

    def has_errors(self) -> bool:
        """Check if there are any error or critical issues."""
        return any(
            issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            for issue in self.issues
        )

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return any(
            issue.severity == ValidationSeverity.WARNING
            for issue in self.issues
        )

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        if self.is_valid:
            summary = f"✓ {self.file_path} - VALID"
        else:
            summary = f"✗ {self.file_path} - INVALID"

        error_count = sum(
            1 for i in self.issues
            if i.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
        )
        warning_count = sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

        if error_count > 0:
            summary += f" ({error_count} errors"
        if warning_count > 0:
            if error_count > 0:
                summary += f", {warning_count} warnings)"
            else:
                summary += f" ({warning_count} warnings)"
        elif error_count > 0:
            summary += ")"

        return summary


class PDFValidator:
    """Validates PDF files before Bates numbering processing."""

    def __init__(
        self,
        max_file_size_mb: int = 500,
        max_pages: int = 10000,
        check_encryption: bool = True,
        check_corruption: bool = True,
        check_page_sizes: bool = True
    ):
        """
        Initialize PDF validator.

        Args:
            max_file_size_mb: Maximum file size in megabytes
            max_pages: Maximum number of pages allowed
            check_encryption: Check for encrypted PDFs
            check_corruption: Check for PDF corruption
            check_page_sizes: Validate page sizes
        """
        self.max_file_size_mb = max_file_size_mb
        self.max_pages = max_pages
        self.check_encryption = check_encryption
        self.check_corruption = check_corruption
        self.check_page_sizes = check_page_sizes

    def validate_file(self, file_path: str, password: Optional[str] = None) -> ValidationResult:
        """
        Validate a PDF file for processing.

        Args:
            file_path: Path to the PDF file
            password: Optional password for encrypted PDFs

        Returns:
            ValidationResult object with validation details
        """
        result = ValidationResult(file_path=file_path, is_valid=True)

        # Check file existence
        if not os.path.exists(file_path):
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="FILE_NOT_FOUND",
                message=f"File does not exist: {file_path}"
            ))
            result.is_valid = False
            return result

        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_EXTENSION",
                message="File does not have .pdf extension",
                details={'extension': os.path.splitext(file_path)[1]}
            ))
            result.is_valid = False

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        result.file_info['size_mb'] = round(file_size_mb, 2)

        if file_size_mb > self.max_file_size_mb:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="FILE_TOO_LARGE",
                message=f"File size ({file_size_mb:.2f} MB) exceeds maximum ({self.max_file_size_mb} MB)",
                details={'size_mb': file_size_mb, 'max_size_mb': self.max_file_size_mb}
            ))
            result.is_valid = False
        elif file_size_mb > self.max_file_size_mb * 0.8:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="FILE_SIZE_LARGE",
                message=f"File size ({file_size_mb:.2f} MB) is close to maximum limit",
                details={'size_mb': file_size_mb}
            ))

        # Check file is readable
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="INVALID_PDF_HEADER",
                        message="File does not have valid PDF header",
                        details={'header': str(header)}
                    ))
                    result.is_valid = False
                    return result
        except Exception as e:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="FILE_READ_ERROR",
                message=f"Cannot read file: {str(e)}",
                details={'error': str(e)}
            ))
            result.is_valid = False
            return result

        # Validate PDF structure with pypdf
        try:
            reader = PdfReader(file_path)

            # Check encryption
            if self.check_encryption and reader.is_encrypted:
                if password:
                    try:
                        if not reader.decrypt(password):
                            result.issues.append(ValidationIssue(
                                severity=ValidationSeverity.ERROR,
                                code="INVALID_PASSWORD",
                                message="Provided password is invalid"
                            ))
                            result.is_valid = False
                    except Exception as e:
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            code="DECRYPTION_ERROR",
                            message=f"Error decrypting PDF: {str(e)}",
                            details={'error': str(e)}
                        ))
                        result.is_valid = False
                else:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="PDF_ENCRYPTED",
                        message="PDF is encrypted and requires a password"
                    ))
                    result.file_info['encrypted'] = True

            # Check page count
            num_pages = len(reader.pages)
            result.file_info['page_count'] = num_pages

            if num_pages == 0:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="NO_PAGES",
                    message="PDF has no pages"
                ))
                result.is_valid = False
            elif num_pages > self.max_pages:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="TOO_MANY_PAGES",
                    message=f"PDF has {num_pages} pages, exceeds maximum of {self.max_pages}",
                    details={'page_count': num_pages, 'max_pages': self.max_pages}
                ))
                result.is_valid = False
            elif num_pages > 5000:
                result.issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    code="LARGE_PAGE_COUNT",
                    message=f"PDF has {num_pages} pages, processing may take time"
                ))

            # Check page sizes if enabled
            if self.check_page_sizes and num_pages > 0:
                self._validate_page_sizes(reader, result)

            # Check for corrupted pages
            if self.check_corruption:
                self._check_page_corruption(reader, result)

            # Extract metadata
            if reader.metadata:
                result.file_info['metadata'] = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'creator': reader.metadata.get('/Creator', ''),
                    'producer': reader.metadata.get('/Producer', '')
                }

        except PdfReadError as e:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="PDF_CORRUPTED",
                message=f"PDF file is corrupted or invalid: {str(e)}",
                details={'error': str(e)}
            ))
            result.is_valid = False
        except Exception as e:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="VALIDATION_ERROR",
                message=f"Error validating PDF: {str(e)}",
                details={'error': str(e)}
            ))
            result.is_valid = False

        logger.info(f"Validation complete for {file_path}: {result.get_summary()}")
        return result

    def _validate_page_sizes(self, reader: PdfReader, result: ValidationResult) -> None:
        """
        Validate page sizes and detect unusual dimensions.

        Args:
            reader: PdfReader instance
            result: ValidationResult to append issues to
        """
        try:
            page_sizes = []
            for page_num, page in enumerate(reader.pages):
                try:
                    width = float(page.mediabox.width)
                    height = float(page.mediabox.height)
                    page_sizes.append((width, height))

                    # Check for extremely small pages
                    if width < 72 or height < 72:  # Less than 1 inch
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            code="SMALL_PAGE_SIZE",
                            message=f"Page {page_num + 1} has very small dimensions",
                            details={'page': page_num + 1, 'width': width, 'height': height}
                        ))

                    # Check for extremely large pages
                    if width > 14400 or height > 14400:  # Larger than 200 inches
                        result.issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            code="LARGE_PAGE_SIZE",
                            message=f"Page {page_num + 1} has very large dimensions",
                            details={'page': page_num + 1, 'width': width, 'height': height}
                        ))

                except Exception as e:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        code="PAGE_SIZE_ERROR",
                        message=f"Cannot read size of page {page_num + 1}: {str(e)}",
                        details={'page': page_num + 1, 'error': str(e)}
                    ))

            # Check for mixed page sizes
            if page_sizes:
                unique_sizes = set(page_sizes)
                if len(unique_sizes) > 1:
                    result.issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        code="MIXED_PAGE_SIZES",
                        message=f"PDF contains {len(unique_sizes)} different page sizes",
                        details={'unique_sizes': len(unique_sizes)}
                    ))
                    result.file_info['page_sizes'] = list(unique_sizes)

        except Exception as e:
            logger.warning(f"Error validating page sizes: {str(e)}")

    def _check_page_corruption(self, reader: PdfReader, result: ValidationResult) -> None:
        """
        Check for corrupted or unreadable pages.

        Args:
            reader: PdfReader instance
            result: ValidationResult to append issues to
        """
        corrupted_pages = []

        for page_num, page in enumerate(reader.pages):
            try:
                # Try to access page properties to detect corruption
                _ = page.mediabox
                _ = page.get('/Contents', None)
            except Exception as e:
                corrupted_pages.append(page_num + 1)
                logger.warning(f"Page {page_num + 1} may be corrupted: {str(e)}")

        if corrupted_pages:
            result.issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="CORRUPTED_PAGES",
                message=f"Found {len(corrupted_pages)} potentially corrupted page(s)",
                details={'pages': corrupted_pages}
            ))
            result.is_valid = False

    def validate_batch(
        self,
        file_paths: List[str],
        password: Optional[str] = None,
        stop_on_error: bool = False
    ) -> List[ValidationResult]:
        """
        Validate multiple PDF files.

        Args:
            file_paths: List of PDF file paths
            password: Optional password for encrypted PDFs
            stop_on_error: Stop validation on first error

        Returns:
            List of ValidationResult objects
        """
        results = []

        for file_path in file_paths:
            result = self.validate_file(file_path, password)
            results.append(result)

            if stop_on_error and not result.is_valid:
                logger.warning(f"Stopping validation due to error in {file_path}")
                break

        return results

    def get_batch_summary(self, results: List[ValidationResult]) -> Dict:
        """
        Get summary statistics for batch validation.

        Args:
            results: List of ValidationResult objects

        Returns:
            Dictionary with summary statistics
        """
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        with_errors = sum(1 for r in results if r.has_errors())
        with_warnings = sum(1 for r in results if r.has_warnings())

        total_pages = sum(r.file_info.get('page_count', 0) for r in results)
        total_size_mb = sum(r.file_info.get('size_mb', 0) for r in results)

        return {
            'total_files': total,
            'valid_files': valid,
            'files_with_errors': with_errors,
            'files_with_warnings': with_warnings,
            'total_pages': total_pages,
            'total_size_mb': round(total_size_mb, 2),
            'success_rate': round((valid / total * 100) if total > 0 else 0, 2)
        }
