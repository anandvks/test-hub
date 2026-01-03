"""
Data Export Utilities

Provides functions for exporting test data in various formats.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np


class DataExporter:
    """Export test data to various formats."""

    @staticmethod
    def export_csv(data: List[Dict], filepath: Path, metadata: Optional[Dict] = None):
        """
        Export data to CSV file with metadata header.

        Args:
            data: List of data dicts (each dict = one row)
            filepath: Output file path
            metadata: Optional metadata to include in header comments
        """
        if not data:
            print("Warning: No data to export")
            return

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', newline='') as f:
            # Write metadata as comments
            if metadata:
                f.write(f"# Export Date: {metadata.get('export_date', 'Unknown')}\n")
                f.write(f"# Test Type: {metadata.get('test_type', 'Unknown')}\n")
                f.write(f"# Session ID: {metadata.get('session_id', 'Unknown')}\n")

                # Write config as JSON comment
                if 'config' in metadata:
                    f.write(f"# Config: {json.dumps(metadata['config'])}\n")

                f.write("#\n")

            # Write CSV data
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        print(f"Exported {len(data)} rows to {filepath}")

    @staticmethod
    def export_json(data: Dict, filepath: Path, indent: int = 2):
        """
        Export data to JSON file.

        Args:
            data: Data dict or list to export
            filepath: Output file path
            indent: JSON indentation level
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent)

        print(f"Exported JSON to {filepath}")

    @staticmethod
    def export_plot(figure, filepath: Path, dpi: int = 150, format: str = 'png'):
        """
        Export matplotlib figure to image file.

        Args:
            figure: Matplotlib Figure object
            filepath: Output file path
            dpi: Resolution in dots per inch
            format: Image format ('png', 'pdf', 'svg')
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Ensure correct extension
        if not filepath.suffix:
            filepath = filepath.with_suffix(f".{format}")

        figure.savefig(filepath, dpi=dpi, bbox_inches='tight', format=format)
        print(f"Exported plot to {filepath}")

    @staticmethod
    def export_summary_report(session_data: Dict, filepath: Path):
        """
        Export session summary as text report.

        Args:
            session_data: Session data dict
            filepath: Output file path
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write("="*60 + "\n")
            f.write("TEST BENCH SESSION REPORT\n")
            f.write("="*60 + "\n\n")

            # Session info
            f.write(f"Session ID: {session_data.get('session_id', 'Unknown')}\n")
            f.write(f"Created: {session_data.get('created', 'Unknown')}\n")
            f.write(f"Platform: {session_data.get('platform', 'Unknown')}\n\n")

            # Hardware info
            if 'hardware' in session_data:
                f.write("Hardware Configuration:\n")
                for key, value in session_data['hardware'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n")

            # Tests summary
            tests = session_data.get('tests', [])
            f.write(f"Total Tests: {len(tests)}\n\n")

            for i, test in enumerate(tests, 1):
                f.write(f"Test {i}: {test.get('test_type', 'Unknown')}\n")
                f.write(f"  ID: {test.get('test_id', 'Unknown')}\n")
                f.write(f"  Time: {test.get('timestamp', 'Unknown')}\n")
                f.write(f"  Status: {test.get('status', 'Unknown')}\n")

                # Test results if available
                if 'results' in test:
                    f.write("  Results:\n")
                    for key, value in test['results'].items():
                        f.write(f"    {key}: {value}\n")

                f.write("\n")

            # Notes
            if session_data.get('notes'):
                f.write("Notes:\n")
                f.write(session_data['notes'])
                f.write("\n\n")

            f.write("="*60 + "\n")
            f.write("End of Report\n")
            f.write("="*60 + "\n")

        print(f"Exported summary report to {filepath}")

    @staticmethod
    def read_csv(filepath: Path) -> tuple:
        """
        Read CSV file with metadata.

        Args:
            filepath: Input CSV file path

        Returns:
            Tuple of (data_list, metadata_dict)
        """
        filepath = Path(filepath)
        metadata = {}
        data = []

        with open(filepath, 'r') as f:
            # Read metadata comments
            for line in f:
                if line.startswith('#'):
                    # Parse metadata
                    line = line.lstrip('#').strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                else:
                    break

            # Reset to start of file
            f.seek(0)

            # Skip comments
            lines = [line for line in f if not line.startswith('#')]

            # Read CSV
            if lines:
                reader = csv.DictReader(lines)
                data = list(reader)

        return data, metadata


class BatchExporter:
    """Export multiple files in batch."""

    def __init__(self, session):
        """
        Initialize batch exporter.

        Args:
            session: Session instance
        """
        self.session = session

    def export_session(self, output_dir: Path, formats: List[str] = ['csv', 'json']):
        """
        Export entire session.

        Args:
            output_dir: Output directory
            formats: List of formats to export ('csv', 'json', 'txt')
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exporter = DataExporter()

        # Export session metadata
        if 'json' in formats:
            exporter.export_json(
                self.session.metadata,
                output_dir / f"{self.session.session_id}_metadata.json"
            )

        # Export summary report
        if 'txt' in formats:
            exporter.export_summary_report(
                self.session.metadata,
                output_dir / f"{self.session.session_id}_report.txt"
            )

        # Copy data files
        if 'csv' in formats:
            for test in self.session.metadata['tests']:
                data_file = test.get('data_file')
                if data_file:
                    src = self.session.session_dir / data_file
                    dst = output_dir / Path(data_file).name

                    if src.exists():
                        import shutil
                        shutil.copy2(src, dst)

        print(f"Exported session to {output_dir}")

    def export_test(self, test_id: str, output_dir: Path,
                   include_plots: bool = True):
        """
        Export individual test.

        Args:
            test_id: Test identifier
            output_dir: Output directory
            include_plots: Whether to include plot files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find test in session
        test = None
        for t in self.session.metadata['tests']:
            if t['test_id'] == test_id:
                test = t
                break

        if not test:
            print(f"Test {test_id} not found in session")
            return

        # Export test data
        data_file = test.get('data_file')
        if data_file:
            src = self.session.session_dir / data_file
            dst = output_dir / Path(data_file).name

            if src.exists():
                import shutil
                shutil.copy2(src, dst)

        # Export plots
        if include_plots:
            for plot_file in test.get('plot_files', []):
                src = self.session.session_dir / plot_file
                dst = output_dir / Path(plot_file).name

                if src.exists():
                    import shutil
                    shutil.copy2(src, dst)

        # Export test config
        exporter = DataExporter()
        exporter.export_json(
            test,
            output_dir / f"{test_id}_config.json"
        )

        print(f"Exported test {test_id} to {output_dir}")


def create_analysis_summary(data: List[Dict], test_type: str) -> Dict:
    """
    Create statistical summary of test data.

    Args:
        data: List of data dicts
        test_type: Type of test

    Returns:
        Summary statistics dict
    """
    if not data:
        return {}

    summary = {
        'test_type': test_type,
        'num_samples': len(data),
        'statistics': {}
    }

    # Convert to numpy for analysis
    numeric_fields = []
    for key in data[0].keys():
        try:
            values = [float(row[key]) for row in data]
            numeric_fields.append((key, values))
        except (ValueError, TypeError):
            continue

    # Calculate statistics for each field
    for field, values in numeric_fields:
        arr = np.array(values)

        summary['statistics'][field] = {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'median': float(np.median(arr))
        }

    return summary
