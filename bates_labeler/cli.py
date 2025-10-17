#!/usr/bin/env python3
"""
PDF Bates Numbering Script - CLI Interface
Command-line interface for adding Bates numbers to PDF documents.

Author: Adam Blackington
Version: 1.1.0
"""

import argparse
import sys
import os

from bates_labeler.core import BatesNumberer
from bates_labeler.__version__ import __version__


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Add Bates numbers to PDF documents for legal document management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic usage:
    bates --input evidence.pdf --bates-prefix "CASE123-"
  
  Custom position and font:
    bates --input evidence.pdf --bates-prefix "SMITH-" --position top-right --font-size 14
  
  With separator page:
    bates --input evidence.pdf --bates-prefix "DOC-" --add-separator
  
  Without background (for clean documents):
    bates --input clean.pdf --bates-prefix "EXHIBIT-" --no-background
  
  With date stamp:
    bates --input evidence.pdf --bates-prefix "DOC-" --include-date --date-format "%Y/%m/%d"
  
  Batch processing:
    bates --batch file1.pdf file2.pdf file3.pdf --bates-prefix "BATCH-" --add-separator
        """
    )
    
    # Version
    parser.add_argument('--version', action='version', version=f'bates-labeler {__version__}')
    
    # Input/Output arguments
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', type=str, help='Input PDF file path')
    input_group.add_argument('--batch', '-b', nargs='+', help='Batch process multiple PDFs')
    
    parser.add_argument('--output', '-o', type=str, help='Output PDF file path (default: input_bates.pdf)')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch processing')
    
    # Bates numbering arguments
    parser.add_argument('--bates-prefix', type=str, default='', help='Prefix for Bates number (e.g., "CASE123-")')
    parser.add_argument('--bates-suffix', type=str, default='', help='Suffix for Bates number')
    parser.add_argument('--start-number', type=int, default=1, help='Starting number (default: 1)')
    parser.add_argument('--padding', type=int, default=4, help='Number padding width (default: 4)')
    
    # Position arguments
    parser.add_argument('--position', type=str, default='bottom-left',
                       choices=['top-left', 'top-center', 'top-right', 
                               'bottom-left', 'bottom-center', 'bottom-right', 'center'],
                       help='Position of Bates number on page (default: bottom-left)')
    
    # Font arguments
    parser.add_argument('--font-name', type=str, default='Helvetica',
                       choices=['Helvetica', 'Times-Roman', 'Courier'],
                       help='Font family (default: Helvetica)')
    parser.add_argument('--font-size', type=int, default=12, help='Font size (default: 12)')
    parser.add_argument('--font-color', type=str, default='black', 
                       help='Font color name or hex (default: black)')
    parser.add_argument('--bold', action='store_true', default=True, help='Use bold font (default: True)')
    parser.add_argument('--no-bold', dest='bold', action='store_false', help='Do not use bold font')
    parser.add_argument('--italic', action='store_true', help='Use italic font')
    
    # Date/time arguments
    parser.add_argument('--include-date', action='store_true', help='Include date/time stamp')
    parser.add_argument('--date-format', type=str, default='%Y-%m-%d',
                       help='Date format string (default: %%Y-%%m-%%d)')
    
    # Separator page arguments
    parser.add_argument('--add-separator', action='store_true',
                       help='Add separator page at the beginning with Bates range')
    
    # Background arguments  
    parser.add_argument('--no-background', dest='add_background', action='store_false',
                       default=True, help='Do not add white background behind text')
    parser.add_argument('--background-padding', type=int, default=3,
                       help='Padding around text background in pixels (default: 3)')
    
    # Other arguments
    parser.add_argument('--password', type=str, help='Password for encrypted PDFs')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.input and not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    if args.batch:
        for file_path in args.batch:
            if not os.path.exists(file_path):
                print(f"Warning: File not found in batch: {file_path}")
    
    # Create BatesNumberer instance
    bates_numberer = BatesNumberer(
        prefix=args.bates_prefix,
        start_number=args.start_number,
        padding=args.padding,
        suffix=args.bates_suffix,
        position=args.position,
        font_name=args.font_name,
        font_size=args.font_size,
        font_color=args.font_color,
        bold=args.bold,
        italic=args.italic,
        include_date=args.include_date,
        date_format=args.date_format,
        add_background=args.add_background,
        background_padding=args.background_padding
    )
    
    # Process based on mode
    if args.input:
        # Single file mode
        output_path = args.output
        if not output_path:
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            output_path = f"{base_name}_bates.pdf"
        
        success = bates_numberer.process_pdf(args.input, output_path, args.password, 
                                            add_separator=args.add_separator)
        sys.exit(0 if success else 1)
    
    else:
        # Batch mode
        bates_numberer.process_batch(args.batch, args.output_dir, 
                                   add_separator=args.add_separator)


if __name__ == "__main__":
    main()
