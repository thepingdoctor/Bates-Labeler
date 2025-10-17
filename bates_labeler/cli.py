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
    
    # Combine PDFs arguments
    parser.add_argument('--combine', action='store_true',
                       help='Combine all batch files into a single PDF with continuous Bates numbering')
    parser.add_argument('--document-separators', action='store_true',
                       help='Add separator pages between documents (only with --combine)')
    parser.add_argument('--add-index', action='store_true',
                       help='Add index page at the beginning listing all documents (only with --combine)')
    
    # Bates filename arguments
    parser.add_argument('--bates-filenames', action='store_true',
                       help='Use first Bates number as output filename (e.g., CASE-0001.pdf)')
    parser.add_argument('--mapping-prefix', type=str, default='bates_mapping',
                       help='Prefix for mapping files (default: bates_mapping)')
    
    # Custom font argument
    parser.add_argument('--custom-font', type=str,
                       help='Path to custom TrueType (.ttf) or OpenType (.otf) font file')
    
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
        background_padding=args.background_padding,
        custom_font_path=args.custom_font
    )
    
    # Process based on mode
    if args.input:
        # Single file mode
        output_path = args.output
        if not output_path:
            if args.bates_filenames:
                # Need to process to get first Bates number
                metadata = bates_numberer.process_pdf(
                    args.input, 
                    "temp_output.pdf",
                    args.password,
                    add_separator=args.add_separator,
                    return_metadata=True
                )
                if metadata['success']:
                    output_path = f"{metadata['first_bates']}.pdf"
                    os.rename("temp_output.pdf", output_path)
                    
                    # Generate mapping files
                    if args.bates_filenames:
                        mappings = [{
                            'original_filename': os.path.basename(args.input),
                            'new_filename': output_path,
                            'first_bates': metadata['first_bates'],
                            'last_bates': metadata['last_bates'],
                            'page_count': metadata['page_count']
                        }]
                        bates_numberer.generate_filename_mapping_csv(
                            mappings, f"{args.mapping_prefix}.csv"
                        )
                        bates_numberer.generate_filename_mapping_pdf(
                            mappings, f"{args.mapping_prefix}.pdf"
                        )
                    sys.exit(0)
                else:
                    sys.exit(1)
            else:
                base_name = os.path.splitext(os.path.basename(args.input))[0]
                output_path = f"{base_name}_bates.pdf"
                success = bates_numberer.process_pdf(
                    args.input, output_path, args.password,
                    add_separator=args.add_separator
                )
                sys.exit(0 if success else 1)
        else:
            success = bates_numberer.process_pdf(
                args.input, output_path, args.password,
                add_separator=args.add_separator
            )
            sys.exit(0 if success else 1)
    
    else:
        # Batch mode
        if args.combine:
            # Combine all PDFs into single file
            output_path = args.output if args.output else "combined_bates.pdf"
            if args.output_dir:
                output_path = os.path.join(args.output_dir, os.path.basename(output_path))
            
            result = bates_numberer.combine_and_process_pdfs(
                args.batch,
                output_path,
                add_document_separators=args.document_separators,
                add_index_page=args.add_index,
                password=args.password
            )
            
            if result['success']:
                # Optionally rename with Bates range
                if args.bates_filenames and result['documents']:
                    first_bates = result['documents'][0]['first_bates']
                    last_bates = result['documents'][-1]['last_bates']
                    new_output_path = f"{first_bates}_to_{last_bates}.pdf"
                    if args.output_dir:
                        new_output_path = os.path.join(args.output_dir, new_output_path)
                    os.rename(output_path, new_output_path)
                    output_path = new_output_path
                    
                    # Generate mapping files
                    bates_numberer.generate_filename_mapping_csv(
                        result['documents'], f"{args.mapping_prefix}.csv"
                    )
                    bates_numberer.generate_filename_mapping_pdf(
                        result['documents'], f"{args.mapping_prefix}.pdf"
                    )
                
                print(f"\nCombined PDF saved to: {output_path}")
                sys.exit(0)
            else:
                sys.exit(1)
        
        elif args.bates_filenames:
            # Process with Bates number filenames
            successful = 0
            failed = 0
            mappings = []
            
            for input_path in args.batch:
                if not os.path.exists(input_path):
                    print(f"Warning: File not found: {input_path}")
                    failed += 1
                    continue
                
                # Process with metadata
                metadata = bates_numberer.process_pdf(
                    input_path,
                    "temp_output.pdf",
                    args.password,
                    add_separator=args.add_separator,
                    return_metadata=True
                )
                
                if metadata['success']:
                    # Generate new filename
                    output_name = f"{metadata['first_bates']}.pdf"
                    if args.output_dir:
                        output_path = os.path.join(args.output_dir, output_name)
                    else:
                        output_path = output_name
                    
                    os.rename("temp_output.pdf", output_path)
                    
                    # Track mapping
                    mappings.append({
                        'original_filename': os.path.basename(input_path),
                        'new_filename': output_name,
                        'first_bates': metadata['first_bates'],
                        'last_bates': metadata['last_bates'],
                        'page_count': metadata['page_count']
                    })
                    
                    successful += 1
                else:
                    failed += 1
            
            # Generate mapping files
            if mappings:
                mapping_csv = f"{args.mapping_prefix}.csv"
                mapping_pdf = f"{args.mapping_prefix}.pdf"
                if args.output_dir:
                    mapping_csv = os.path.join(args.output_dir, os.path.basename(mapping_csv))
                    mapping_pdf = os.path.join(args.output_dir, os.path.basename(mapping_pdf))
                
                bates_numberer.generate_filename_mapping_csv(mappings, mapping_csv)
                bates_numberer.generate_filename_mapping_pdf(mappings, mapping_pdf)
            
            print(f"\nBatch processing complete: {successful} successful, {failed} failed")
            print(f"Mapping files saved: {mapping_csv}, {mapping_pdf}")
            sys.exit(0 if failed == 0 else 1)
        
        else:
            # Standard batch processing
            bates_numberer.process_batch(
                args.batch, args.output_dir,
                add_separator=args.add_separator
            )


if __name__ == "__main__":
    main()
