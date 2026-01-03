"""
Encoder Interface

Interface for AS5600 magnetic encoder for absolute joint angle measurement.
"""

from typing import Optional, Dict
from pathlib import Path
import json


class EncoderReader:
    """
    Interface for AS5600 absolute magnetic encoder.

    Encoder connects to Teensy I2C, Teensy reports absolute position.
    This class handles zero position offset and conversion to degrees.
    """

    def __init__(self, sensor_id: str, calibration_file: Optional[Path] = None):
        """
        Initialize encoder reader.

        Args:
            sensor_id: Unique identifier (e.g., "encoder_finger_joint")
            calibration_file: Path to calibration data file
        """
        self.sensor_id = sensor_id
        self.calibration_file = calibration_file or Path(f"data/calibrations/{sensor_id}.json")

        # Calibration parameters
        self.zero_position = 0  # Raw encoder value at zero angle
        self.counts_per_revolution = 4096  # AS5600 is 12-bit
        self.calibration_date = None

        # Load existing calibration if available
        self.load_calibration()

    def load_calibration(self) -> bool:
        """
        Load calibration from file.

        Returns:
            True if calibration loaded successfully
        """
        if not self.calibration_file.exists():
            return False

        try:
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)

            self.zero_position = data.get('zero_position', 0)
            self.counts_per_revolution = data.get('counts_per_revolution', 4096)
            self.calibration_date = data.get('calibration_date')

            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False

    def save_calibration(self):
        """Save calibration to file."""
        self.calibration_file.parent.mkdir(parents=True, exist_ok=True)

        from datetime import datetime

        data = {
            'sensor_id': self.sensor_id,
            'zero_position': self.zero_position,
            'counts_per_revolution': self.counts_per_revolution,
            'calibration_date': datetime.now().isoformat()
        }

        with open(self.calibration_file, 'w') as f:
            json.dump(data, f, indent=2)

    def set_zero(self, raw_value: int):
        """
        Set zero position.

        Args:
            raw_value: Current raw encoder reading at desired zero angle
        """
        self.zero_position = raw_value

    def convert_to_angle(self, raw_value: int) -> float:
        """
        Convert raw encoder value to angle in degrees.

        Args:
            raw_value: Raw encoder reading (0-4095 for AS5600)

        Returns:
            Angle in degrees (0-360)
        """
        # Calculate relative position
        delta_counts = raw_value - self.zero_position

        # Wrap around if negative
        if delta_counts < 0:
            delta_counts += self.counts_per_revolution

        # Convert to degrees
        angle_deg = (delta_counts / self.counts_per_revolution) * 360.0

        return angle_deg

    def is_calibrated(self) -> bool:
        """Check if encoder is calibrated (zero position set)."""
        return self.zero_position != 0

    def get_calibration_info(self) -> Dict:
        """
        Get calibration information.

        Returns:
            Dict with calibration parameters
        """
        return {
            'sensor_id': self.sensor_id,
            'zero_position': self.zero_position,
            'counts_per_revolution': self.counts_per_revolution,
            'calibration_date': self.calibration_date,
            'is_calibrated': self.is_calibrated()
        }

    def test_range(self, raw_value_min: int, raw_value_max: int) -> tuple:
        """
        Test encoder range.

        Args:
            raw_value_min: Raw reading at minimum position
            raw_value_max: Raw reading at maximum position

        Returns:
            (angle_min, angle_max, range_deg) tuple
        """
        angle_min = self.convert_to_angle(raw_value_min)
        angle_max = self.convert_to_angle(raw_value_max)
        range_deg = abs(angle_max - angle_min)

        return angle_min, angle_max, range_deg
