"""
Base Test Class

Abstract base class for all automated test modules.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional
import time


class BaseTest(ABC):
    """
    Abstract base class for test modules.

    All test modules inherit from this class and implement the required methods.
    """

    def __init__(self, hardware_interface, data_logger):
        """
        Initialize test.

        Args:
            hardware_interface: Dict with teensy, safety, etc.
            data_logger: DataLogger instance
        """
        self.hw = hardware_interface
        self.logger = data_logger
        self.config = {}
        self.results = {}
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False

    @abstractmethod
    def get_name(self) -> str:
        """
        Return test name.

        Returns:
            Human-readable test name (e.g., 'Torque & Efficiency Test')
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Return brief description of test goals.

        Returns:
            Description string
        """
        pass

    @abstractmethod
    def get_parameters(self) -> Dict[str, Dict]:
        """
        Return dictionary of configurable parameters with metadata.

        Returns:
            Dict with parameter definitions:
            {
                'param_name': {
                    'type': 'float' | 'int' | 'bool' | 'string',
                    'default': default_value,
                    'unit': 'unit_string' (optional),
                    'min': min_value (optional),
                    'max': max_value (optional),
                    'description': 'description' (optional)
                }
            }

        Example:
            {
                'torque_min': {
                    'type': 'float',
                    'default': 0,
                    'unit': 'mNm',
                    'min': 0,
                    'max': 5000,
                    'description': 'Minimum torque for test'
                }
            }
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict) -> tuple[bool, str]:
        """
        Validate configuration before running test.

        Args:
            config: Configuration dictionary

        Returns:
            (is_valid, error_message) tuple
        """
        pass

    @abstractmethod
    def estimate_duration(self, config: Dict) -> float:
        """
        Estimate test duration.

        Args:
            config: Configuration dictionary

        Returns:
            Estimated duration in seconds
        """
        pass

    @abstractmethod
    def run(self, config: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Execute the test.

        Args:
            config: Test configuration parameters
            progress_callback: Function to call with progress updates
                             callback(percent, message)

        Returns:
            results: Dictionary with test results and analysis
        """
        pass

    # Common Methods (can be overridden if needed)

    def pause(self):
        """Pause test execution (if supported)."""
        self.is_paused = True

    def resume(self):
        """Resume paused test."""
        self.is_paused = False

    def stop(self):
        """Request test stop (graceful)."""
        self.stop_requested = True

    def emergency_stop(self):
        """Emergency stop (immediate)."""
        self.hw['teensy'].emergency_stop()
        self.is_running = False
        self.stop_requested = True

    def _check_stop(self) -> bool:
        """
        Check if test should stop.

        Returns:
            True if stop requested
        """
        return self.stop_requested

    def _wait_while_paused(self):
        """Wait while test is paused."""
        while self.is_paused and not self.stop_requested:
            time.sleep(0.1)

    def _update_progress(self, progress_callback: Optional[Callable],
                        percent: float, message: str = ""):
        """
        Update progress if callback provided.

        Args:
            progress_callback: Progress callback function
            percent: Progress percentage (0-100)
            message: Status message
        """
        if progress_callback:
            try:
                progress_callback(percent, message)
            except Exception as e:
                print(f"Progress callback error: {e}")

    def get_default_config(self) -> Dict:
        """
        Get default configuration based on parameter definitions.

        Returns:
            Dict with default values for all parameters
        """
        params = self.get_parameters()
        config = {}
        for key, metadata in params.items():
            config[key] = metadata.get('default')
        return config

    def format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable form.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "5.2 minutes", "1.5 hours")
        """
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"
