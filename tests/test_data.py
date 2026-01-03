"""Unit tests for data management."""
import pytest
from data.config_manager import ConfigManager
from data.logger import DataLogger


class TestConfigManager:
    """Test configuration manager."""

    def test_creation(self, config_manager):
        """Test creating config manager."""
        assert config_manager is not None
        assert config_manager.config is not None

    def test_has_default_config(self, config_manager):
        """Test config has default hardware section."""
        assert 'hardware' in config_manager.config
        assert 'platform' in config_manager.config['hardware']


class TestDataLogger:
    """Test data logger."""

    def test_logger_creation(self, data_logger):
        """Test creating a data logger."""
        assert data_logger is not None
        assert data_logger.buffer is not None

    @pytest.mark.unit
    def test_log_data(self, data_logger):
        """Test logging data point to buffer."""
        data_point = {
            'timestamp': 1234567890.0,
            'force_tendon': 1000,
            'force_tip': 800,
            'position': 5000,
            'current': 150
        }
        # Log to buffer
        data_logger.buffer.append(data_point)
        assert len(data_logger.buffer) == 1

    def test_buffer_size(self):
        """Test logger buffer size."""
        logger = DataLogger(buffer_size=100)
        assert logger is not None
        assert logger.buffer.maxlen == 100
