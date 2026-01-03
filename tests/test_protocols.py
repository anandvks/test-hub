"""Unit tests for test protocols."""
import pytest
from protocols.registry import TestRegistry
from hardware.safety import SafetyMonitor


class TestProtocolRegistry:
    """Test the protocol registry."""

    def test_registry_creation(self, mock_controller, data_logger):
        """Test creating test registry."""
        safety = SafetyMonitor(mock_controller)
        hardware = {'controller': mock_controller, 'safety': safety}
        registry = TestRegistry(hardware, data_logger)
        assert registry is not None

    def test_list_tests(self, mock_controller, data_logger):
        """Test listing available tests."""
        safety = SafetyMonitor(mock_controller)
        hardware = {'controller': mock_controller, 'safety': safety}
        registry = TestRegistry(hardware, data_logger)
        tests = registry.get_test_list()
        assert len(tests) > 0
        # Each test should be a tuple of (id, name, description)
        for test in tests:
            assert isinstance(test, tuple)
            assert len(test) == 3

    def test_get_test(self, mock_controller, data_logger):
        """Test retrieving a specific test."""
        safety = SafetyMonitor(mock_controller)
        hardware = {'controller': mock_controller, 'safety': safety}
        registry = TestRegistry(hardware, data_logger)

        # Get first test from the list
        tests = registry.get_test_list()
        if tests:
            test_id = tests[0][0]
            test = registry.get_test(test_id)
            assert test is not None
            assert hasattr(test, 'run')
            assert hasattr(test, 'get_name')
            assert hasattr(test, 'get_parameters')
