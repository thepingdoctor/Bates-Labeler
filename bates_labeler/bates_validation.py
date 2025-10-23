"""Bates number validation and conflict detection module.

Provides functionality to validate Bates numbers, detect conflicts,
and ensure sequential numbering integrity across document sets.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict


logger = logging.getLogger(__name__)


@dataclass
class BatesRange:
    """Represents a range of Bates numbers."""
    first: str
    last: str
    count: int
    prefix: str = ""
    suffix: str = ""
    first_number: int = 0
    last_number: int = 0

    def __post_init__(self):
        """Extract numeric parts from Bates numbers."""
        if not self.first_number:
            self.first_number = self._extract_number(self.first)
        if not self.last_number:
            self.last_number = self._extract_number(self.last)

    @staticmethod
    def _extract_number(bates: str) -> int:
        """Extract numeric portion from Bates number."""
        match = re.search(r'\d+', bates)
        return int(match.group()) if match else 0

    def overlaps_with(self, other: 'BatesRange') -> bool:
        """Check if this range overlaps with another."""
        if self.prefix != other.prefix or self.suffix != other.suffix:
            return False

        return not (self.last_number < other.first_number or
                   other.last_number < self.first_number)

    def contains(self, bates: str) -> bool:
        """Check if a Bates number falls within this range."""
        number = self._extract_number(bates)
        return self.first_number <= number <= self.last_number

    def is_sequential(self) -> bool:
        """Check if the range is sequential."""
        expected_count = self.last_number - self.first_number + 1
        return self.count == expected_count


@dataclass
class BatesConflict:
    """Represents a Bates numbering conflict."""
    conflict_type: str  # 'duplicate', 'overlap', 'gap', 'out_of_sequence'
    description: str
    affected_ranges: List[BatesRange] = field(default_factory=list)
    affected_numbers: List[str] = field(default_factory=list)
    severity: str = "warning"  # 'info', 'warning', 'error'

    def __str__(self) -> str:
        """String representation of the conflict."""
        return f"[{self.severity.upper()}] {self.conflict_type}: {self.description}"


class BatesValidator:
    """Validates Bates numbers and detects conflicts."""

    def __init__(self):
        """Initialize Bates validator."""
        self.ranges: List[BatesRange] = []
        self.all_numbers: Set[str] = set()

    def add_range(
        self,
        first_bates: str,
        last_bates: str,
        page_count: int,
        prefix: str = "",
        suffix: str = ""
    ) -> None:
        """
        Add a Bates range for validation.

        Args:
            first_bates: First Bates number in range
            last_bates: Last Bates number in range
            page_count: Number of pages in range
            prefix: Bates number prefix
            suffix: Bates number suffix
        """
        bates_range = BatesRange(
            first=first_bates,
            last=last_bates,
            count=page_count,
            prefix=prefix,
            suffix=suffix
        )
        self.ranges.append(bates_range)

        # Track all individual numbers
        for i in range(page_count):
            num = bates_range.first_number + i
            bates_num = f"{prefix}{str(num).zfill(len(str(bates_range.first_number)))}{suffix}"
            self.all_numbers.add(bates_num)

    def validate(self) -> List[BatesConflict]:
        """
        Validate all Bates ranges and detect conflicts.

        Returns:
            List of detected conflicts
        """
        conflicts = []

        # Check for overlapping ranges
        conflicts.extend(self._check_overlaps())

        # Check for duplicates
        conflicts.extend(self._check_duplicates())

        # Check for gaps
        conflicts.extend(self._check_gaps())

        # Check sequential integrity
        conflicts.extend(self._check_sequential())

        logger.info(f"Validation complete: {len(conflicts)} conflict(s) found")
        return conflicts

    def _check_overlaps(self) -> List[BatesConflict]:
        """Check for overlapping Bates ranges."""
        conflicts = []

        for i, range1 in enumerate(self.ranges):
            for range2 in self.ranges[i + 1:]:
                if range1.overlaps_with(range2):
                    conflict = BatesConflict(
                        conflict_type='overlap',
                        description=f"Bates ranges overlap: {range1.first}-{range1.last} and {range2.first}-{range2.last}",
                        affected_ranges=[range1, range2],
                        severity='error'
                    )
                    conflicts.append(conflict)
                    logger.warning(f"Overlap detected: {conflict.description}")

        return conflicts

    def _check_duplicates(self) -> List[BatesConflict]:
        """Check for duplicate Bates numbers."""
        conflicts = []
        number_counts = defaultdict(int)

        # Count occurrences of each number
        for bates_range in self.ranges:
            for i in range(bates_range.count):
                num = bates_range.first_number + i
                padding = len(str(bates_range.first_number))
                bates_num = f"{bates_range.prefix}{str(num).zfill(padding)}{bates_range.suffix}"
                number_counts[bates_num] += 1

        # Find duplicates
        duplicates = [num for num, count in number_counts.items() if count > 1]

        if duplicates:
            conflict = BatesConflict(
                conflict_type='duplicate',
                description=f"Found {len(duplicates)} duplicate Bates number(s)",
                affected_numbers=duplicates,
                severity='error'
            )
            conflicts.append(conflict)
            logger.warning(f"Duplicates found: {duplicates[:5]}..." if len(duplicates) > 5 else f"Duplicates: {duplicates}")

        return conflicts

    def _check_gaps(self) -> List[BatesConflict]:
        """Check for gaps in Bates numbering sequence."""
        conflicts = []

        if len(self.ranges) < 2:
            return conflicts

        # Sort ranges by first number
        sorted_ranges = sorted(self.ranges, key=lambda r: r.first_number)

        for i in range(len(sorted_ranges) - 1):
            current = sorted_ranges[i]
            next_range = sorted_ranges[i + 1]

            # Check if ranges have the same prefix/suffix
            if current.prefix == next_range.prefix and current.suffix == next_range.suffix:
                expected_next = current.last_number + 1
                actual_next = next_range.first_number

                if actual_next > expected_next:
                    gap_size = actual_next - expected_next
                    conflict = BatesConflict(
                        conflict_type='gap',
                        description=f"Gap of {gap_size} number(s) between {current.last} and {next_range.first}",
                        affected_ranges=[current, next_range],
                        severity='warning'
                    )
                    conflicts.append(conflict)
                    logger.info(f"Gap detected: {conflict.description}")

        return conflicts

    def _check_sequential(self) -> List[BatesConflict]:
        """Check if each range is internally sequential."""
        conflicts = []

        for bates_range in self.ranges:
            if not bates_range.is_sequential():
                expected = bates_range.last_number - bates_range.first_number + 1
                actual = bates_range.count

                conflict = BatesConflict(
                    conflict_type='out_of_sequence',
                    description=f"Range {bates_range.first}-{bates_range.last} has {actual} pages but should have {expected}",
                    affected_ranges=[bates_range],
                    severity='error'
                )
                conflicts.append(conflict)
                logger.warning(f"Sequential error: {conflict.description}")

        return conflicts

    def validate_format(self, bates_number: str, pattern: Optional[str] = None) -> bool:
        """
        Validate Bates number format.

        Args:
            bates_number: Bates number to validate
            pattern: Optional regex pattern to match

        Returns:
            True if valid, False otherwise
        """
        if not bates_number:
            return False

        # Check if contains at least one digit
        if not re.search(r'\d', bates_number):
            logger.warning(f"Invalid Bates number (no digits): {bates_number}")
            return False

        # If pattern provided, match against it
        if pattern:
            if not re.match(pattern, bates_number):
                logger.warning(f"Bates number doesn't match pattern: {bates_number}")
                return False

        return True

    def suggest_next_range(
        self,
        prefix: str = "",
        suffix: str = "",
        page_count: int = 1
    ) -> Tuple[str, str]:
        """
        Suggest the next Bates range based on existing ranges.

        Args:
            prefix: Bates number prefix
            suffix: Bates number suffix
            page_count: Number of pages needed

        Returns:
            Tuple of (first_bates, last_bates)
        """
        # Find the highest last number for matching prefix/suffix
        max_number = 0
        padding = 4  # Default padding

        for bates_range in self.ranges:
            if bates_range.prefix == prefix and bates_range.suffix == suffix:
                if bates_range.last_number > max_number:
                    max_number = bates_range.last_number
                    padding = len(str(bates_range.last_number))

        # Next range starts after the highest
        first_num = max_number + 1
        last_num = first_num + page_count - 1

        first_bates = f"{prefix}{str(first_num).zfill(padding)}{suffix}"
        last_bates = f"{prefix}{str(last_num).zfill(padding)}{suffix}"

        return first_bates, last_bates

    def get_summary(self) -> Dict[str, any]:
        """
        Get summary of all Bates ranges.

        Returns:
            Dictionary with summary statistics
        """
        if not self.ranges:
            return {'total_ranges': 0}

        total_pages = sum(r.count for r in self.ranges)
        all_numbers = sorted([r.first_number for r in self.ranges] +
                           [r.last_number for r in self.ranges])

        return {
            'total_ranges': len(self.ranges),
            'total_pages': total_pages,
            'lowest_number': all_numbers[0] if all_numbers else 0,
            'highest_number': all_numbers[-1] if all_numbers else 0,
            'unique_prefixes': len(set(r.prefix for r in self.ranges)),
            'unique_suffixes': len(set(r.suffix for r in self.ranges))
        }

    def clear(self) -> None:
        """Clear all ranges and reset validator."""
        self.ranges.clear()
        self.all_numbers.clear()
        logger.debug("Validator cleared")


def validate_bates_pattern(pattern: str) -> bool:
    """
    Validate a Bates numbering pattern.

    Args:
        pattern: Bates pattern (e.g., "ABC-{0000}-XYZ")

    Returns:
        True if valid, False otherwise
    """
    if not pattern:
        return False

    # Check for numeric placeholder
    if not re.search(r'\{0+\}|\d', pattern):
        logger.warning(f"Invalid pattern (no numeric placeholder): {pattern}")
        return False

    return True


def parse_bates_number(
    bates: str
) -> Tuple[str, int, str]:
    """
    Parse a Bates number into components.

    Args:
        bates: Bates number to parse

    Returns:
        Tuple of (prefix, number, suffix)
    """
    # Find the numeric portion
    match = re.search(r'(\D*)(\d+)(\D*)', bates)

    if match:
        prefix = match.group(1)
        number = int(match.group(2))
        suffix = match.group(3)
        return prefix, number, suffix

    return "", 0, ""


def generate_bates_number(
    number: int,
    prefix: str = "",
    suffix: str = "",
    padding: int = 4
) -> str:
    """
    Generate a Bates number.

    Args:
        number: Numeric portion
        prefix: Prefix text
        suffix: Suffix text
        padding: Number of digits (with zero padding)

    Returns:
        Formatted Bates number
    """
    num_str = str(number).zfill(padding)
    return f"{prefix}{num_str}{suffix}"
