"""Unit tests for hardware controllers."""
import pytest
from hardware import create_controller, list_platforms


class TestHardwareFactory:
    """Test hardware controller factory."""

    def test_list_platforms(self):
        """Test platform listing."""
        platforms = list_platforms()
        assert 'mock' in platforms
        assert isinstance(platforms, list)
        assert len(platforms) >= 1

    def test_create_mock_controller(self):
        """Test creating mock controller."""
        controller = create_controller('mock')
        assert controller is not None
        info = controller.get_platform_info()
        assert 'platform' in info
        assert 'Mock' in info['platform']

    def test_invalid_platform(self):
        """Test creating invalid platform returns None."""
        controller = create_controller('invalid_platform_xyz')
        assert controller is None


class TestMockController:
    """Test mock controller functionality."""

    def test_connect(self, mock_controller):
        """Test connection succeeds."""
        assert mock_controller.connected

    def test_read_sensors(self, mock_controller):
        """Test reading sensor data."""
        data = mock_controller.get_sensors()
        assert data is not None
        assert 'force_tendon' in data
        assert 'force_tip' in data
        assert 'position' in data
        assert 'current' in data

        # Check types
        assert isinstance(data['force_tendon'], (int, float))
        assert isinstance(data['force_tip'], (int, float))
        assert isinstance(data['position'], (int, float))
        assert isinstance(data['current'], (int, float))

    @pytest.mark.unit
    def test_set_torque(self, mock_controller):
        """Test setting torque command."""
        mock_controller.set_torque(1500)
        # Mock should accept command without error
        data = mock_controller.get_sensors()
        assert data is not None

    def test_platform_info(self, mock_controller):
        """Test getting platform information."""
        info = mock_controller.get_platform_info()
        assert 'platform' in info
        assert 'version' in info
        assert 'communication' in info
        assert 'Mock' in info['platform']
