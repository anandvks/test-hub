"""
Serial Port Finder

Auto-detect available serial ports for Teensy connection.
"""

import serial.tools.list_ports
from typing import List, Tuple


def find_serial_ports() -> List[Tuple[str, str]]:
    """
    Find all available serial ports.

    Returns:
        List of (port, description) tuples
    """
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append((port.device, port.description))
    return ports


def find_teensy_port() -> str:
    """
    Try to auto-detect Teensy port.

    Returns:
        Port device string or empty string if not found
    """
    for port in serial.tools.list_ports.comports():
        # Teensy typically shows up with these identifiers
        if 'teensy' in port.description.lower() or \
           'usb serial' in port.description.lower():
            return port.device

    # If no Teensy-specific port found, return first available
    ports = find_serial_ports()
    if ports:
        return ports[0][0]

    return ""


def get_port_info(port_device: str) -> dict:
    """
    Get detailed information about a serial port.

    Args:
        port_device: Port device string (e.g., '/dev/ttyACM0')

    Returns:
        Dict with port information
    """
    for port in serial.tools.list_ports.comports():
        if port.device == port_device:
            return {
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid,
                'serial_number': port.serial_number,
                'manufacturer': port.manufacturer,
                'product': port.product
            }
    return {}
