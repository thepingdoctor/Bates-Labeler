"""
Bates Labeler - Professional Bates numbering for legal documents.

A comprehensive Python tool for adding Bates numbers to PDF documents,
commonly used in legal document management and discovery processes.
"""

from bates_labeler.__version__ import __version__, __author__, __license__
from bates_labeler.core import BatesNumberer, POSITION_COORDINATES

__all__ = [
    '__version__',
    '__author__',
    '__license__',
    'BatesNumberer',
    'POSITION_COORDINATES',
]
