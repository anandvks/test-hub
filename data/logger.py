"""
Data Logger

Real-time data logging with buffering for live plots.
"""

import csv
import time
from collections import deque
from pathlib import Path
import threading
from typing import Dict, List, Optional


class DataLogger:
    """
    Real-time data logging with ring buffer for live plotting.
    """

    def __init__(self, buffer_size: int = 10000):
        self.buffer = deque(maxlen=buffer_size)  # Ring buffer for live plots
        self.csv_file: Optional[Path] = None
        self.csv_writer = None
        self.file_handle = None
        self.is_logging = False
        self.lock = threading.Lock()
        self.headers: List[str] = []
        self.sample_count = 0
        self.flush_interval = 100  # Flush every N samples

    def start_logging(self, filepath: Path, headers: List[str], metadata: Dict = None):
        """
        Start logging to CSV file.

        Args:
            filepath: Path to CSV file
            headers: List of column headers
            metadata: Optional metadata to write as comments at start of file
        """
        with self.lock:
            self.csv_file = Path(filepath)
            self.csv_file.parent.mkdir(parents=True, exist_ok=True)

            self.file_handle = open(self.csv_file, 'w', newline='')

            # Write metadata as comments
            if metadata:
                for key, value in metadata.items():
                    self.file_handle.write(f"# {key}: {value}\n")

            # Write headers
            self.csv_writer = csv.DictWriter(self.file_handle, fieldnames=headers)
            self.csv_writer.writeheader()

            self.headers = headers
            self.is_logging = True
            self.buffer.clear()
            self.sample_count = 0

    def log(self, data_dict: Dict):
        """
        Log a single data point.

        Args:
            data_dict: Dictionary with sensor readings
        """
        if not self.is_logging:
            return

        # Add timestamp if not present
        if 'timestamp' not in data_dict:
            data_dict['timestamp'] = time.time()

        with self.lock:
            # Add to ring buffer (for live plotting)
            self.buffer.append(data_dict.copy())

            # Write to CSV
            if self.csv_writer:
                self.csv_writer.writerow(data_dict)
                self.sample_count += 1

                # Periodic flush for safety
                if self.sample_count % self.flush_interval == 0:
                    self.file_handle.flush()

    def get_recent_data(self, n: int = 1000) -> List[Dict]:
        """
        Get most recent n data points for live plotting.

        Args:
            n: Number of recent samples to return

        Returns:
            List of data dictionaries
        """
        with self.lock:
            return list(self.buffer)[-n:]

    def get_buffer_data(self) -> List[Dict]:
        """Get all buffered data."""
        with self.lock:
            return list(self.buffer)

    def stop_logging(self):
        """Stop logging and close file."""
        with self.lock:
            if self.file_handle:
                self.file_handle.flush()
                self.file_handle.close()
                self.file_handle = None
                self.csv_writer = None

            self.is_logging = False
            print(f"Logged {self.sample_count} samples to {self.csv_file}")

    def clear_buffer(self):
        """Clear the ring buffer."""
        with self.lock:
            self.buffer.clear()

    def is_active(self) -> bool:
        """Check if logging is active."""
        return self.is_logging

    def get_sample_count(self) -> int:
        """Get total number of samples logged."""
        return self.sample_count
