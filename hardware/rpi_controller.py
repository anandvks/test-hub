"""
Raspberry Pi Hardware Controller

Controller for Raspberry Pi platform using SPI/I2C communication.
Supports direct hardware communication via Linux SPI and I2C interfaces.

Note: Requires spidev and smbus2 packages:
    pip install spidev smbus2
"""

import time
import threading
from typing import Optional, Dict, Callable

try:
    import spidev
    HAS_SPIDEV = True
except ImportError:
    HAS_SPIDEV = False
    print("WARNING: spidev not available. Install with: pip install spidev")

try:
    import smbus2
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False
    print("WARNING: smbus2 not available. Install with: pip install smbus2")

from .base_controller import HardwareController


class RPiController(HardwareController):
    """Hardware controller for Raspberry Pi via SPI/I2C."""

    # I2C register addresses (example - adjust for actual hardware)
    REG_CONTROL = 0x00
    REG_STATUS = 0x01
    REG_POSITION_CMD = 0x10
    REG_VELOCITY_CMD = 0x14
    REG_TORQUE_CMD = 0x18
    REG_CURRENT_CMD = 0x1C
    REG_SENSORS_START = 0x20
    REG_PID_START = 0x40
    REG_PROFILE_START = 0x50
    REG_LIMITS_START = 0x60

    # Control register bits
    CTRL_ENABLE = 0x01
    CTRL_DISABLE = 0x00
    CTRL_ESTOP = 0x80
    CTRL_ZERO_SENSORS = 0x40

    def __init__(self):
        super().__init__()

        # SPI configuration
        self.spi = None
        self.spi_bus = 0
        self.spi_device = 0
        self.spi_speed = 1000000  # 1 MHz

        # I2C configuration
        self.i2c = None
        self.i2c_bus = 1
        self.motor_i2c_addr = 0x60  # Motor controller I2C address
        self.sensor_i2c_addr = 0x40  # Sensor board I2C address

        # Streaming
        self.streaming = False
        self.stream_rate = 0
        self.stream_callback = None
        self.stream_thread = None

    # Connection management

    def connect(self, **kwargs) -> bool:
        """
        Connect to Raspberry Pi GPIO/SPI/I2C.

        Args:
            spi_bus (int): SPI bus number (default 0)
            spi_device (int): SPI device (default 0)
            spi_speed (int): SPI clock speed in Hz (default 1000000)
            i2c_bus (int): I2C bus number (default 1)
            motor_addr (int): Motor controller I2C address (default 0x60)
            sensor_addr (int): Sensor board I2C address (default 0x40)

        Returns:
            True if connection successful
        """
        if not HAS_SPIDEV and not HAS_SMBUS:
            print("RPi controller: Neither SPI nor I2C libraries available")
            return False

        try:
            # Initialize SPI if available
            if HAS_SPIDEV:
                self.spi_bus = kwargs.get('spi_bus', 0)
                self.spi_device = kwargs.get('spi_device', 0)
                self.spi_speed = kwargs.get('spi_speed', 1000000)

                self.spi = spidev.SpiDev()
                self.spi.open(self.spi_bus, self.spi_device)
                self.spi.max_speed_hz = self.spi_speed
                self.spi.mode = 0  # CPOL=0, CPHA=0

                print(f"RPi controller: SPI opened on bus {self.spi_bus}, device {self.spi_device}")

            # Initialize I2C if available
            if HAS_SMBUS:
                self.i2c_bus = kwargs.get('i2c_bus', 1)
                self.motor_i2c_addr = kwargs.get('motor_addr', 0x60)
                self.sensor_i2c_addr = kwargs.get('sensor_addr', 0x40)

                self.i2c = smbus2.SMBus(self.i2c_bus)

                print(f"RPi controller: I2C opened on bus {self.i2c_bus}")
                print(f"  Motor controller at 0x{self.motor_i2c_addr:02X}")
                print(f"  Sensor board at 0x{self.sensor_i2c_addr:02X}")

            # Test communication
            time.sleep(0.1)

            # Try to read status register
            if self.i2c:
                try:
                    status = self.i2c.read_byte_data(self.motor_i2c_addr, self.REG_STATUS)
                    print(f"RPi controller: Motor controller status = 0x{status:02X}")
                except Exception as e:
                    print(f"RPi controller: Warning - could not read motor controller: {e}")

            self.connected = True
            print("RPi controller: Connected successfully")
            return True

        except Exception as e:
            print(f"RPi connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from Raspberry Pi."""
        self.stop_streaming()

        if self.spi:
            try:
                self.spi.close()
            except:
                pass
            self.spi = None

        if self.i2c:
            try:
                self.i2c.close()
            except:
                pass
            self.i2c = None

        self.connected = False
        print("RPi controller: Disconnected")
        return True

    # Internal I2C communication helpers

    def _i2c_write_int32(self, addr: int, reg: int, value: int):
        """Write 32-bit signed integer to I2C register."""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")

        # Convert to 4 bytes (little-endian, signed)
        bytes_val = value.to_bytes(4, byteorder='little', signed=True)
        self.i2c.write_i2c_block_data(addr, reg, list(bytes_val))

    def _i2c_read_int32(self, addr: int, reg: int) -> int:
        """Read 32-bit signed integer from I2C register."""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")

        bytes_val = self.i2c.read_i2c_block_data(addr, reg, 4)
        return int.from_bytes(bytes_val, byteorder='little', signed=True)

    def _i2c_write_uint32(self, addr: int, reg: int, value: int):
        """Write 32-bit unsigned integer to I2C register."""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")

        bytes_val = value.to_bytes(4, byteorder='little', signed=False)
        self.i2c.write_i2c_block_data(addr, reg, list(bytes_val))

    def _i2c_read_uint32(self, addr: int, reg: int) -> int:
        """Read 32-bit unsigned integer from I2C register."""
        if not self.i2c:
            raise RuntimeError("I2C not initialized")

        bytes_val = self.i2c.read_i2c_block_data(addr, reg, 4)
        return int.from_bytes(bytes_val, byteorder='little', signed=False)

    # Motor control

    def enable(self) -> bool:
        """Enable motor driver."""
        if not self.connected or not self.i2c:
            return False

        try:
            self.i2c.write_byte_data(self.motor_i2c_addr, self.REG_CONTROL, self.CTRL_ENABLE)
            self.enabled = True
            print("RPi controller: Motor enabled")
            return True
        except Exception as e:
            print(f"RPi enable error: {e}")
            return False

    def disable(self) -> bool:
        """Disable motor driver."""
        if not self.connected or not self.i2c:
            return False

        try:
            self.i2c.write_byte_data(self.motor_i2c_addr, self.REG_CONTROL, self.CTRL_DISABLE)
            self.enabled = False
            print("RPi controller: Motor disabled")
            return True
        except Exception as e:
            print(f"RPi disable error: {e}")
            return False

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately disable motor."""
        if not self.connected or not self.i2c:
            return False

        try:
            self.i2c.write_byte_data(self.motor_i2c_addr, self.REG_CONTROL, self.CTRL_ESTOP)
            self.enabled = False
            print("RPi controller: EMERGENCY STOP")
            return True
        except Exception as e:
            print(f"RPi e-stop error: {e}")
            return False

    # Motor commands

    def set_position(self, position: int) -> bool:
        """Set target position (encoder counts)."""
        if not self.connected or not self.i2c:
            return False

        try:
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_POSITION_CMD, position)
            return True
        except Exception as e:
            print(f"RPi set position error: {e}")
            return False

    def set_velocity(self, velocity: int) -> bool:
        """Set target velocity (RPM)."""
        if not self.connected or not self.i2c:
            return False

        try:
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_VELOCITY_CMD, velocity)
            return True
        except Exception as e:
            print(f"RPi set velocity error: {e}")
            return False

    def set_torque(self, torque: int) -> bool:
        """Set target torque (mNm)."""
        if not self.connected or not self.i2c:
            return False

        try:
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_TORQUE_CMD, torque)
            return True
        except Exception as e:
            print(f"RPi set torque error: {e}")
            return False

    def set_current(self, current: int) -> bool:
        """Set motor current (mA)."""
        if not self.connected or not self.i2c:
            return False

        try:
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_CURRENT_CMD, current)
            return True
        except Exception as e:
            print(f"RPi set current error: {e}")
            return False

    # Sensor reading

    def get_position(self) -> Optional[int]:
        """Read motor position (encoder counts)."""
        sensors = self.get_sensors()
        return sensors['position'] if sensors else None

    def get_velocity(self) -> Optional[int]:
        """Read motor velocity (RPM)."""
        sensors = self.get_sensors()
        return sensors['velocity'] if sensors else None

    def get_current(self) -> Optional[int]:
        """Read motor current (mA)."""
        sensors = self.get_sensors()
        return sensors['current'] if sensors else None

    def get_sensors(self) -> Optional[Dict]:
        """
        Read all sensors via I2C.

        Sensor data layout (28 bytes starting at REG_SENSORS_START):
            Offset 0-3:   timestamp (uint32, ms)
            Offset 4-7:   position (int32, counts)
            Offset 8-11:  velocity (int32, RPM)
            Offset 12-15: current (uint32, mA)
            Offset 16-19: force_tendon (uint32, mN)
            Offset 20-23: force_tip (uint32, mN)
            Offset 24-27: angle_joint (int32, counts)

        Returns:
            Dict with standardized keys or None on error
        """
        if not self.connected or not self.i2c:
            return None

        try:
            # Read 28 bytes from sensor register block
            data = self.i2c.read_i2c_block_data(
                self.sensor_i2c_addr,
                self.REG_SENSORS_START,
                28
            )

            # Parse bytes to sensor values
            timestamp = int.from_bytes(data[0:4], byteorder='little', signed=False)
            position = int.from_bytes(data[4:8], byteorder='little', signed=True)
            velocity = int.from_bytes(data[8:12], byteorder='little', signed=True)
            current = int.from_bytes(data[12:16], byteorder='little', signed=False)
            force_tendon = int.from_bytes(data[16:20], byteorder='little', signed=False)
            force_tip = int.from_bytes(data[20:24], byteorder='little', signed=False)
            angle_joint = int.from_bytes(data[24:28], byteorder='little', signed=True)

            return {
                'timestamp': timestamp,
                'position': position,
                'velocity': velocity,
                'current': current,
                'force_tendon': force_tendon,
                'force_tip': force_tip,
                'angle_joint': angle_joint
            }

        except Exception as e:
            print(f"RPi read sensors error: {e}")
            return None

    # Streaming

    def start_streaming(self, rate_hz: int, callback: Callable) -> bool:
        """
        Start streaming sensor data.

        Args:
            rate_hz: Streaming frequency (Hz)
            callback: Function called with sensor dict for each sample

        Returns:
            True if streaming started successfully
        """
        if not self.connected or self.streaming:
            return False

        self.streaming = True
        self.stream_rate = rate_hz
        self.stream_callback = callback

        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()

        print(f"RPi controller: Streaming started at {rate_hz} Hz")
        return True

    def stop_streaming(self) -> bool:
        """Stop streaming sensor data."""
        if not self.streaming:
            return True

        self.streaming = False

        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)

        print("RPi controller: Streaming stopped")
        return True

    def _stream_loop(self):
        """Background thread for polling sensor data."""
        interval = 1.0 / self.stream_rate if self.stream_rate > 0 else 0.1

        while self.streaming:
            try:
                sensor_data = self.get_sensors()
                if sensor_data and self.stream_callback:
                    self.stream_callback(sensor_data)

                time.sleep(interval)

            except Exception as e:
                print(f"RPi stream error: {e}")
                break

    # Advanced control

    def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID controller parameters."""
        if not self.connected or not self.i2c:
            return False

        try:
            # Convert floats to fixed-point (scale by 1000)
            kp_int = int(kp * 1000)
            ki_int = int(ki * 1000)
            kd_int = int(kd * 1000)

            self._i2c_write_int32(self.motor_i2c_addr, self.REG_PID_START, kp_int)
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_PID_START + 4, ki_int)
            self._i2c_write_int32(self.motor_i2c_addr, self.REG_PID_START + 8, kd_int)

            print(f"RPi controller: PID set to Kp={kp}, Ki={ki}, Kd={kd}")
            return True

        except Exception as e:
            print(f"RPi set PID error: {e}")
            return False

    def get_pid_params(self) -> Optional[Dict]:
        """Get current PID parameters."""
        if not self.connected or not self.i2c:
            return None

        try:
            kp_int = self._i2c_read_int32(self.motor_i2c_addr, self.REG_PID_START)
            ki_int = self._i2c_read_int32(self.motor_i2c_addr, self.REG_PID_START + 4)
            kd_int = self._i2c_read_int32(self.motor_i2c_addr, self.REG_PID_START + 8)

            return {
                'kp': kp_int / 1000.0,
                'ki': ki_int / 1000.0,
                'kd': kd_int / 1000.0
            }

        except Exception as e:
            print(f"RPi get PID error: {e}")
            return None

    def set_motion_profile(self, max_velocity: int, max_acceleration: int,
                          max_deceleration: int, jerk: int) -> bool:
        """Set motion profile parameters."""
        if not self.connected or not self.i2c:
            return False

        try:
            self._i2c_write_uint32(self.motor_i2c_addr, self.REG_PROFILE_START, max_velocity)
            self._i2c_write_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 4, max_acceleration)
            self._i2c_write_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 8, max_deceleration)
            self._i2c_write_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 12, jerk)

            print("RPi controller: Motion profile updated")
            return True

        except Exception as e:
            print(f"RPi set profile error: {e}")
            return False

    def get_motion_profile(self) -> Optional[Dict]:
        """Get current motion profile."""
        if not self.connected or not self.i2c:
            return None

        try:
            max_vel = self._i2c_read_uint32(self.motor_i2c_addr, self.REG_PROFILE_START)
            max_accel = self._i2c_read_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 4)
            max_decel = self._i2c_read_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 8)
            jerk = self._i2c_read_uint32(self.motor_i2c_addr, self.REG_PROFILE_START + 12)

            return {
                'max_velocity': max_vel,
                'acceleration': max_accel,
                'deceleration': max_decel,
                'jerk_limit': jerk
            }

        except Exception as e:
            print(f"RPi get profile error: {e}")
            return None

    # Safety and calibration

    def set_limit(self, limit_type: str, value: int) -> bool:
        """
        Set safety limit.

        Args:
            limit_type: 'current_max', 'position_min', 'position_max', 'force_max'
            value: Limit value in base units
        """
        if not self.connected or not self.i2c:
            return False

        # Map limit type to register offset
        limit_map = {
            'current_max': 0,
            'position_min': 4,
            'position_max': 8,
            'force_max': 12
        }

        if limit_type not in limit_map:
            print(f"RPi controller: Unknown limit type '{limit_type}'")
            return False

        try:
            offset = limit_map[limit_type]
            self._i2c_write_uint32(self.motor_i2c_addr, self.REG_LIMITS_START + offset, value)
            print(f"RPi controller: Limit {limit_type} set to {value}")
            return True

        except Exception as e:
            print(f"RPi set limit error: {e}")
            return False

    def zero_sensors(self) -> bool:
        """Zero all sensors."""
        if not self.connected or not self.i2c:
            return False

        try:
            self.i2c.write_byte_data(self.motor_i2c_addr, self.REG_CONTROL, self.CTRL_ZERO_SENSORS)
            time.sleep(0.1)  # Wait for zeroing to complete
            print("RPi controller: Sensors zeroed")
            return True

        except Exception as e:
            print(f"RPi zero sensors error: {e}")
            return False

    # Platform identification

    def get_platform_name(self) -> str:
        """Return platform name."""
        return "Raspberry Pi"

    def get_platform_info(self) -> Dict:
        """Return platform-specific info."""
        return {
            'platform': 'Raspberry Pi',
            'version': '1.0',
            'firmware_version': 'Hardware-dependent',
            'communication': 'SPI/I2C',
            'i2c_bus': self.i2c_bus,
            'motor_i2c_addr': f'0x{self.motor_i2c_addr:02X}',
            'sensor_i2c_addr': f'0x{self.sensor_i2c_addr:02X}',
            'spi_bus': self.spi_bus,
            'spi_device': self.spi_device,
            'spi_speed': self.spi_speed,
            'capabilities': [
                'position_control',
                'velocity_control',
                'torque_control',
                'current_control',
                'pid_tuning',
                'motion_profiles',
                'streaming',
                'safety_limits',
                'direct_hardware_access'
            ],
            'notes': 'Raspberry Pi controller using I2C for motor control and sensor reading. '
                    'Requires spidev and smbus2 Python packages. '
                    'I2C addresses and register map are hardware-dependent.'
        }
