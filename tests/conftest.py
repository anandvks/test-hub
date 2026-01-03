"""Pytest configuration and shared fixtures."""
import pytest
from hardware import create_controller
from data.logger import DataLogger
from data.config_manager import ConfigManager


@pytest.fixture
def mock_controller():
    """Fixture providing a mock hardware controller."""
    controller = create_controller('mock')
    controller.connect()
    yield controller
    controller.disconnect()


@pytest.fixture
def data_logger():
    """Fixture providing a data logger."""
    logger = DataLogger(buffer_size=1000)
    yield logger
    if logger.is_logging:
        logger.stop_logging()


@pytest.fixture
def config_manager(tmp_path):
    """Fixture providing a config manager with temp config."""
    from pathlib import Path
    config_path = tmp_path / "config.json"
    cm = ConfigManager(config_file=Path(config_path))
    yield cm
