"""
Hardware Controller Base Class

Abstract base class defining the hardware controller interface.
All platform-specific controllers must inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable


class HardwareController(ABC):
    """Abstract base class for hardware controllers."""

    def __init__(self):
        self.connected = False
        self.enabled = False

    # Connection management
    @abstractmethod
    def connect(self, **kwargs) -> bool:
        """
        Connect to hardware controller.

        Args:
            **kwargs: Platform-specific connection parameters
                - Serial: port (str), baudrate (int)
                - Ethernet: host (str), port (int)
                - CAN: interface (str), bitrate (int)

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from hardware controller."""
        pass

    # Motor control
    @abstractmethod
    def enable(self) -> bool:
        """Enable motor driver."""
        pass

    @abstractmethod
    def disable(self) -> bool:
        """Disable motor driver."""
        pass

    @abstractmethod
    def emergency_stop(self) -> bool:
        """Trigger emergency stop."""
        pass

    @abstractmethod
    def set_position(self, position: int) -> bool:
        """Set target position (encoder counts)."""
        pass

    @abstractmethod
    def set_velocity(self, velocity: int) -> bool:
        """Set target velocity (RPM)."""
        pass

    @abstractmethod
    def set_torque(self, torque: int) -> bool:
        """Set target torque (mNm)."""
        pass

    @abstractmethod
    def set_current(self, current: int) -> bool:
        """Set target current (mA)."""
        pass

    # Sensor reading
    @abstractmethod
    def get_sensors(self) -> Optional[Dict]:
        """
        Read all sensors.

        Returns:
            Dict with keys (all values in base units):
                'timestamp': int (ms or s, consistent per platform)
                'position': int (encoder counts)
                'velocity': int (RPM)
                'current': int (mA)
                'force_tendon': int (mN)
                'force_tip': int (mN)
                'angle_joint': int (raw encoder counts)
            or None if read failed
        """
        pass

    @abstractmethod
    def start_streaming(self, rate_hz: int, callback: Callable) -> bool:
        """
        Start streaming sensor data.

        Args:
            rate_hz: Streaming frequency (Hz)
            callback: Function called with sensor dict

        Returns:
            True if streaming started successfully, False otherwise
        """
        pass

    @abstractmethod
    def stop_streaming(self) -> bool:
        """Stop streaming sensor data."""
        pass

    # Advanced control
    @abstractmethod
    def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
        """
        Set PID parameters.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_pid_params(self) -> Optional[Dict]:
        """
        Get current PID parameters.

        Returns:
            Dict with keys: 'kp', 'ki', 'kd' or None if failed
        """
        pass

    @abstractmethod
    def set_motion_profile(self, max_velocity: int, max_acceleration: int,
                          max_deceleration: int, jerk: int) -> bool:
        """
        Set motion profile parameters.

        Args:
            max_velocity: Maximum velocity (RPM)
            max_acceleration: Maximum acceleration (RPM/s)
            max_deceleration: Maximum deceleration (RPM/s)
            jerk: Jerk limit (RPM/s²)

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_motion_profile(self) -> Optional[Dict]:
        """
        Get current motion profile.

        Returns:
            Dict with keys: 'max_velocity', 'max_acceleration',
                          'max_deceleration', 'jerk' or None if failed
        """
        pass

    # Safety and calibration
    @abstractmethod
    def set_limit(self, limit_type: str, value: int) -> bool:
        """
        Set safety limit.

        Args:
            limit_type: 'current', 'position_min', 'position_max', 'force'
            value: Limit value in base units

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def zero_sensors(self) -> bool:
        """Zero all sensors."""
        pass

    # Platform identification
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name (e.g., 'Teensy', 'IMX8', 'RPi')."""
        pass

    @abstractmethod
    def get_platform_info(self) -> Dict:
        """
        Return platform-specific info.

        Returns:
            Dict with keys: 'version', 'firmware_version', 'capabilities', etc.
        """
        pass
