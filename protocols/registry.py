"""
Test Registry

Central registry of all available test modules.
"""

from .torque_test import TorqueEfficiencyTest
from .hysteresis_test import HysteresisTest
from .stiffness_test import StiffnessTest
from .hold_test import StaticHoldTest
from .endurance_test import EnduranceTest


class TestRegistry:
    """Registry of all available test modules."""

    def __init__(self, hardware_interface, data_logger):
        """
        Initialize test registry.

        Args:
            hardware_interface: Dict with teensy, safety, etc.
            data_logger: DataLogger instance
        """
        self.hw = hardware_interface
        self.logger = data_logger

        # Register all tests
        self.tests = {
            'torque_efficiency': TorqueEfficiencyTest(self.hw, self.logger),
            'hysteresis': HysteresisTest(self.hw, self.logger),
            'stiffness': StiffnessTest(self.hw, self.logger),
            'static_hold': StaticHoldTest(self.hw, self.logger),
            'endurance': EnduranceTest(self.hw, self.logger),
        }

    def get_test(self, test_id: str):
        """
        Get test module by ID.

        Args:
            test_id: Test identifier

        Returns:
            Test module instance or None
        """
        return self.tests.get(test_id)

    def get_all_tests(self) -> dict:
        """
        Get all registered tests.

        Returns:
            Dict of test_id -> test_instance
        """
        return self.tests

    def get_test_list(self) -> list:
        """
        Get list of tests for GUI.

        Returns:
            List of (test_id, name, description) tuples
        """
        test_list = []
        for test_id, test in self.tests.items():
            test_list.append((
                test_id,
                test.get_name(),
                test.get_description()
            ))
        return test_list

    def run_test(self, test_id: str, config: dict, progress_callback=None) -> dict:
        """
        Run a test by ID.

        Args:
            test_id: Test identifier
            config: Test configuration
            progress_callback: Progress update callback

        Returns:
            Test results dictionary
        """
        test = self.get_test(test_id)
        if not test:
            raise ValueError(f"Unknown test: {test_id}")

        # Validate configuration
        valid, error = test.validate_config(config)
        if not valid:
            raise ValueError(f"Invalid configuration: {error}")

        # Run test
        return test.run(config, progress_callback)
