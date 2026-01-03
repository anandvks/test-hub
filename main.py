#!/usr/bin/env python3
"""
Test Bench GUI - Main Entry Point

Tendon-driven robotic hand test bench control system.

Supports multiple hardware platforms:
- Teensy 4.1 (Serial/USB)
- IMX8 (Ethernet/TCP)
- Raspberry Pi (SPI/I2C)
- Mock (Simulator for testing without hardware)

Platform selection is configured in config.json.
"""

from hardware import create_controller, list_platforms
from hardware.safety import SafetyMonitor
from data.logger import DataLogger
from data.config_manager import ConfigManager
from utils import serial_finder
from gui.main_window import MainWindow


def main():
    """Main entry point."""
    print("="*60)
    print("Test Bench GUI - Tendon-Driven Robotic Hand")
    print("="*60)

    # Load configuration
    config_manager = ConfigManager()

    # Get platform from config (default: teensy)
    platform = config_manager.get('hardware', 'platform')
    if not platform:
        platform = 'teensy'
        print(f"Warning: No platform specified in config, using default: {platform}")

    print(f"\nPlatform: {platform}")
    print(f"Available platforms: {', '.join(list_platforms())}")

    # Create hardware controller using factory pattern
    print(f"\nCreating {platform} controller...")
    controller = create_controller(platform)

    if controller is None:
        print("\nERROR: Could not create hardware controller")
        print("Please check your configuration and platform availability.")
        print("\nTo change platform, edit config.json:")
        print('  "hardware": {"platform": "teensy|imx8|rpi|mock"}')
        return

    # Print platform info
    info = controller.get_platform_info()
    print(f"\nPlatform Info:")
    print(f"  Name: {info['platform']}")
    print(f"  Version: {info['version']}")
    print(f"  Communication: {info['communication']}")

    # Initialize safety monitor and data logger
    safety_monitor = SafetyMonitor(controller)
    data_logger = DataLogger(buffer_size=10000)

    print("\nStarting GUI...")
    print("-"*60)

    # Create and run GUI
    app = MainWindow(controller, safety_monitor, data_logger, serial_finder)
    app.mainloop()


if __name__ == "__main__":
    main()
