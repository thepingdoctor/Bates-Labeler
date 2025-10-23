"""Batch export module for Bates-Labeler metadata.

Provides comprehensive export functionality for Bates numbering metadata
in multiple formats (JSON, CSV, Excel, XML).
"""

import json
import csv
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path


logger = logging.getLogger(__name__)


class MetadataExporter:
    """Exports Bates numbering metadata to various formats."""

    def __init__(self):
        """Initialize metadata exporter."""
        self.export_timestamp = datetime.now()

    def export_to_json(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str,
        indent: int = 2,
        include_summary: bool = True
    ) -> bool:
        """
        Export metadata to JSON format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output JSON file
            indent: JSON indentation (default: 2)
            include_summary: Include summary statistics

        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'export_timestamp': self.export_timestamp.isoformat(),
                'export_format': 'json',
                'version': '1.0',
                'documents': metadata
            }

            if include_summary:
                export_data['summary'] = self._generate_summary(metadata)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=indent, ensure_ascii=False)

            logger.info(f"JSON export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False

    def export_to_csv(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str,
        delimiter: str = ',',
        include_header: bool = True
    ) -> bool:
        """
        Export metadata to CSV format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output CSV file
            delimiter: CSV delimiter (default: ',')
            include_header: Include header row

        Returns:
            True if successful, False otherwise
        """
        try:
            if not metadata:
                logger.warning("No metadata to export")
                return False

            # Determine fieldnames from first record
            fieldnames = list(metadata[0].keys())

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)

                if include_header:
                    writer.writeheader()

                for row in metadata:
                    writer.writerow(row)

            logger.info(f"CSV export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return False

    def export_to_tsv(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str
    ) -> bool:
        """
        Export metadata to TSV (Tab-Separated Values) format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output TSV file

        Returns:
            True if successful, False otherwise
        """
        return self.export_to_csv(metadata, output_path, delimiter='\t')

    def export_to_xml(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str,
        root_element: str = 'bates_export',
        record_element: str = 'document'
    ) -> bool:
        """
        Export metadata to XML format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output XML file
            root_element: Name of root XML element
            record_element: Name of record XML element

        Returns:
            True if successful, False otherwise
        """
        try:
            import xml.etree.ElementTree as ET
            from xml.dom import minidom

            root = ET.Element(root_element)
            root.set('timestamp', self.export_timestamp.isoformat())
            root.set('version', '1.0')

            # Add summary
            summary = ET.SubElement(root, 'summary')
            summary_data = self._generate_summary(metadata)
            for key, value in summary_data.items():
                elem = ET.SubElement(summary, key)
                elem.text = str(value)

            # Add documents
            documents = ET.SubElement(root, 'documents')
            for record in metadata:
                doc = ET.SubElement(documents, record_element)
                for key, value in record.items():
                    elem = ET.SubElement(doc, key.replace(' ', '_').lower())
                    elem.text = str(value) if value is not None else ''

            # Pretty print XML
            xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            logger.info(f"XML export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to XML: {str(e)}")
            return False

    def export_to_markdown(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str,
        include_summary: bool = True,
        table_format: str = 'grid'
    ) -> bool:
        """
        Export metadata to Markdown format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output Markdown file
            include_summary: Include summary section
            table_format: Table format ('grid' or 'simple')

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("# Bates Numbering Export Report\n\n")
                f.write(f"**Generated:** {self.export_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Summary
                if include_summary:
                    summary = self._generate_summary(metadata)
                    f.write("## Summary\n\n")
                    for key, value in summary.items():
                        f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                    f.write("\n")

                # Documents table
                f.write("## Documents\n\n")

                if metadata:
                    # Get headers
                    headers = list(metadata[0].keys())

                    # Write table header
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

                    # Write rows
                    for record in metadata:
                        row = [str(record.get(h, '')) for h in headers]
                        f.write("| " + " | ".join(row) + " |\n")

            logger.info(f"Markdown export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to Markdown: {str(e)}")
            return False

    def export_to_html(
        self,
        metadata: List[Dict[str, Any]],
        output_path: str,
        include_summary: bool = True,
        title: str = "Bates Numbering Export"
    ) -> bool:
        """
        Export metadata to HTML format.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_path: Path for output HTML file
            include_summary: Include summary section
            title: HTML page title

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # HTML header
                f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #1f77b4; }}
        h2 {{ color: #666; border-bottom: 2px solid #1f77b4; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th {{ background-color: #1f77b4; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .summary {{ background-color: #f0f2f6; padding: 15px; border-radius: 5px; }}
        .summary p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p><strong>Generated:</strong> {self.export_timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
""")

                # Summary
                if include_summary:
                    summary = self._generate_summary(metadata)
                    f.write("    <h2>Summary</h2>\n")
                    f.write("    <div class='summary'>\n")
                    for key, value in summary.items():
                        f.write(f"        <p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>\n")
                    f.write("    </div>\n")

                # Documents table
                f.write("    <h2>Documents</h2>\n")
                f.write("    <table>\n")

                if metadata:
                    # Table header
                    headers = list(metadata[0].keys())
                    f.write("        <thead>\n            <tr>\n")
                    for header in headers:
                        f.write(f"                <th>{header}</th>\n")
                    f.write("            </tr>\n        </thead>\n")

                    # Table body
                    f.write("        <tbody>\n")
                    for record in metadata:
                        f.write("            <tr>\n")
                        for header in headers:
                            value = record.get(header, '')
                            f.write(f"                <td>{value}</td>\n")
                        f.write("            </tr>\n")
                    f.write("        </tbody>\n")

                f.write("    </table>\n")
                f.write("</body>\n</html>")

            logger.info(f"HTML export successful: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to HTML: {str(e)}")
            return False

    def export_all_formats(
        self,
        metadata: List[Dict[str, Any]],
        output_dir: str,
        base_filename: str = "bates_export"
    ) -> Dict[str, bool]:
        """
        Export metadata to all supported formats.

        Args:
            metadata: List of dictionaries containing Bates metadata
            output_dir: Directory for output files
            base_filename: Base filename for exports

        Returns:
            Dictionary mapping format to success status
        """
        os.makedirs(output_dir, exist_ok=True)

        results = {}

        # JSON
        results['json'] = self.export_to_json(
            metadata,
            os.path.join(output_dir, f"{base_filename}.json")
        )

        # CSV
        results['csv'] = self.export_to_csv(
            metadata,
            os.path.join(output_dir, f"{base_filename}.csv")
        )

        # TSV
        results['tsv'] = self.export_to_tsv(
            metadata,
            os.path.join(output_dir, f"{base_filename}.tsv")
        )

        # XML
        results['xml'] = self.export_to_xml(
            metadata,
            os.path.join(output_dir, f"{base_filename}.xml")
        )

        # Markdown
        results['markdown'] = self.export_to_markdown(
            metadata,
            os.path.join(output_dir, f"{base_filename}.md")
        )

        # HTML
        results['html'] = self.export_to_html(
            metadata,
            os.path.join(output_dir, f"{base_filename}.html")
        )

        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Exported to {success_count}/{len(results)} formats successfully")

        return results

    def _generate_summary(self, metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics from metadata.

        Args:
            metadata: List of dictionaries containing Bates metadata

        Returns:
            Dictionary with summary statistics
        """
        if not metadata:
            return {}

        total_documents = len(metadata)
        total_pages = sum(m.get('page_count', 0) for m in metadata)

        # Extract Bates range
        first_bates = metadata[0].get('first_bates', '')
        last_bates = metadata[-1].get('last_bates', '')

        return {
            'total_documents': total_documents,
            'total_pages': total_pages,
            'first_bates_number': first_bates,
            'last_bates_number': last_bates,
            'export_timestamp': self.export_timestamp.isoformat()
        }
