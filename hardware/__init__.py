"""
Hardware Interface Layer

Factory pattern for creating platform-specific controllers.
"""

from typing import Optional
from .base_controller import HardwareController

# Platform-specific controller imports
# (These will be created in subsequent steps)
try:
    from .teensy_controller import TeensyController
except ImportError:
    TeensyController = None

try:
    from .imx8_controller import IMX8Controller
except ImportError:
    IMX8Controller = None

try:
    from .rpi_controller import RPiController
except ImportError:
    RPiController = None

try:
    from .mock_controller import MockController
except ImportError:
    MockController = None


# Platform mapping
PLATFORM_MAP = {}

if TeensyController:
    PLATFORM_MAP['teensy'] = TeensyController

if IMX8Controller:
    PLATFORM_MAP['imx8'] = IMX8Controller

if RPiController:
    PLATFORM_MAP['rpi'] = RPiController
    PLATFORM_MAP['raspberry_pi'] = RPiController  # Alias

if MockController:
    PLATFORM_MAP['mock'] = MockController
    PLATFORM_MAP['simulator'] = MockController  # Alias


def create_controller(platform: str) -> Optional[HardwareController]:
    """
    Create hardware controller for specified platform.

    Args:
        platform: Platform name ('teensy', 'imx8', 'rpi', 'mock')

    Returns:
        HardwareController instance or None if platform unknown
    """
    platform = platform.lower()

    if platform not in PLATFORM_MAP:
        available = ', '.join(sorted(PLATFORM_MAP.keys()))
        print(f"ERROR: Unknown platform '{platform}'")
        if available:
            print(f"Available platforms: {available}")
        else:
            print("No platform controllers available. Install platform-specific modules.")
        return None

    controller_class = PLATFORM_MAP[platform]
    return controller_class()


def list_platforms() -> list:
    """Return list of supported platform names."""
    return sorted(PLATFORM_MAP.keys())
