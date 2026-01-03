"""
Load Cell Interface

Interface for load cells connected via HX711/ADS1256 ADCs.
Handles calibration and conversion to engineering units.
"""

from typing import Optional, Dict
from pathlib import Path
import json


class LoadCellReader:
    """
    Interface for load cell measurements.

    Load cells connect to Teensy ADC (HX711 or ADS1256),
    Teensy reports raw values which are converted here.
    """

    def __init__(self, sensor_id: str, calibration_file: Optional[Path] = None):
        """
        Initialize load cell reader.

        Args:
            sensor_id: Unique identifier (e.g., "load_cell_tendon")
            calibration_file: Path to calibration data file
        """
        self.sensor_id = sensor_id
        self.calibration_file = calibration_file or Path(f"data/calibrations/{sensor_id}.json")

        # Calibration parameters
        self.zero_offset = 0  # Raw ADC value at zero load
        self.calibration_factor = 1.0  # N per ADC count
        self.calibration_date = None
        self.calibration_weight_kg = None

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

            self.zero_offset = data.get('zero_offset', 0)
            self.calibration_factor = data.get('calibration_factor', 1.0)
            self.calibration_date = data.get('calibration_date')
            self.calibration_weight_kg = data.get('calibration_weight_kg')

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
            'zero_offset': self.zero_offset,
            'calibration_factor': self.calibration_factor,
            'calibration_date': datetime.now().isoformat(),
            'calibration_weight_kg': self.calibration_weight_kg
        }

        with open(self.calibration_file, 'w') as f:
            json.dump(data, f, indent=2)

    def zero(self, raw_value: int):
        """
        Set zero offset.

        Args:
            raw_value: Current raw ADC reading (with no load)
        """
        self.zero_offset = raw_value

    def calibrate(self, raw_value: int, known_weight_kg: float):
        """
        Calibrate using known weight.

        Args:
            raw_value: Raw ADC reading with known weight applied
            known_weight_kg: Known calibration weight in kg
        """
        known_force_N = known_weight_kg * 9.81  # Convert to Newtons

        # Calculate calibration factor
        delta_counts = raw_value - self.zero_offset

        if delta_counts != 0:
            self.calibration_factor = known_force_N / delta_counts
            self.calibration_weight_kg = known_weight_kg
        else:
            raise ValueError("No change in reading - check load cell connection")

    def convert_to_force(self, raw_value: int) -> float:
        """
        Convert raw ADC value to force in Newtons.

        Args:
            raw_value: Raw ADC reading

        Returns:
            Force in Newtons
        """
        delta_counts = raw_value - self.zero_offset
        force_N = delta_counts * self.calibration_factor
        return force_N

    def is_calibrated(self) -> bool:
        """Check if sensor is calibrated."""
        return self.calibration_factor != 1.0 and self.zero_offset != 0

    def get_calibration_info(self) -> Dict:
        """
        Get calibration information.

        Returns:
            Dict with calibration parameters
        """
        return {
            'sensor_id': self.sensor_id,
            'zero_offset': self.zero_offset,
            'calibration_factor': self.calibration_factor,
            'calibration_date': self.calibration_date,
            'calibration_weight_kg': self.calibration_weight_kg,
            'is_calibrated': self.is_calibrated()
        }

    def test_calibration(self, raw_value: int, expected_weight_kg: float) -> tuple:
        """
        Test calibration accuracy with known weight.

        Args:
            raw_value: Raw ADC reading
            expected_weight_kg: Expected weight

        Returns:
            (measured_kg, error_percent) tuple
        """
        force_N = self.convert_to_force(raw_value)
        measured_kg = force_N / 9.81

        error_percent = abs(measured_kg - expected_weight_kg) / expected_weight_kg * 100

        return measured_kg, error_percent
