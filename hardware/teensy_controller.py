"""
Teensy 4.1 Controller Interface

Handles serial communication with Teensy microcontroller for motor control.
"""

import serial
import time
import threading
from typing import Optional, Dict, Tuple
from . import protocol as proto
from .base_controller import HardwareController


class TeensyController(HardwareController):
    """Serial interface to Teensy 4.1 motor controller."""

    def __init__(self):
        super().__init__()
        self.serial_port: Optional[serial.Serial] = None
        self.streaming = False
        self.stream_callback = None
        self.stream_thread = None
        self.lock = threading.Lock()

    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """
        Connect to Teensy via serial port.

        Args:
            port: Serial port (e.g., '/dev/ttyACM0' or 'COM3')
            baudrate: Baud rate (default 115200)

        Returns:
            True if connection successful
        """
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=proto.RESPONSE_TIMEOUT
            )
            time.sleep(0.5)  # Wait for connection to stabilize

            # Verify connection with PING
            response = self.ping()
            if response == "PONG":
                self.connected = True
                return True
            else:
                self.disconnect()
                return False

        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from Teensy."""
        self.stop_streaming()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connected = False

    def _send_command(self, command: str) -> str:
        """
        Send command and wait for response.

        Args:
            command: Command string (without line terminator)

        Returns:
            Response string (without terminator)
        """
        if not self.connected or not self.serial_port:
            raise RuntimeError("Not connected to Teensy")

        with self.lock:
            # Clear input buffer
            self.serial_port.reset_input_buffer()

            # Send command
            cmd_bytes = (command + proto.LINE_TERMINATOR).encode('utf-8')
            self.serial_port.write(cmd_bytes)

            # Read response
            response = self.serial_port.readline().decode('utf-8').strip()
            return response

    def _parse_response(self, response: str) -> Tuple[str, str]:
        """
        Parse response into type and data.

        Args:
            response: Raw response string

        Returns:
            (response_type, data) tuple
        """
        parts = response.split(' ', 1)
        resp_type = parts[0]
        data = parts[1] if len(parts) > 1 else ""
        return resp_type, data

    # Basic commands

    def ping(self) -> str:
        """Test connection. Returns 'PONG' if successful."""
        response = self._send_command(proto.CMD_PING)
        resp_type, data = self._parse_response(response)
        return data if resp_type == proto.RESP_ACK else None

    def enable(self) -> bool:
        """Enable motor driver."""
        response = self._send_command(proto.CMD_ENABLE)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    def disable(self) -> bool:
        """Disable motor driver."""
        response = self._send_command(proto.CMD_DISABLE)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately disable motor."""
        response = self._send_command(proto.CMD_ESTOP)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    # Motor control commands

    def set_position(self, position: int) -> bool:
        """Set target position (encoder counts)."""
        command = f"{proto.CMD_SETPOS} {position}"
        response = self._send_command(command)
        resp_type, data = self._parse_response(response)
        if resp_type == proto.RESP_NACK and data == proto.ERR_LIMIT:
            raise ValueError("Position would exceed safety limits")
        return resp_type == proto.RESP_ACK

    def set_velocity(self, velocity: int) -> bool:
        """Set target velocity (RPM)."""
        command = f"{proto.CMD_SETVEL} {velocity}"
        response = self._send_command(command)
        resp_type, data = self._parse_response(response)
        if resp_type == proto.RESP_NACK and data == proto.ERR_LIMIT:
            raise ValueError("Velocity would exceed safety limits")
        return resp_type == proto.RESP_ACK

    def set_torque(self, torque: int) -> bool:
        """Set target torque (mNm)."""
        command = f"{proto.CMD_SETTORQ} {torque}"
        response = self._send_command(command)
        resp_type, data = self._parse_response(response)
        if resp_type == proto.RESP_NACK and data == proto.ERR_LIMIT:
            raise ValueError("Torque would exceed safety limits")
        return resp_type == proto.RESP_ACK

    def set_current(self, current: int) -> bool:
        """Set motor current (mA)."""
        command = f"{proto.CMD_SETCURR} {current}"
        response = self._send_command(command)
        resp_type, data = self._parse_response(response)
        if resp_type == proto.RESP_NACK and data == proto.ERR_LIMIT:
            raise ValueError("Current would exceed safety limits")
        return resp_type == proto.RESP_ACK

    # Sensor reading commands

    def get_position(self) -> Optional[int]:
        """Read motor position (encoder counts)."""
        response = self._send_command(proto.CMD_GETPOS)
        resp_type, data = self._parse_response(response)
        return int(data) if resp_type == proto.RESP_ACK else None

    def get_velocity(self) -> Optional[int]:
        """Read motor velocity (RPM)."""
        response = self._send_command(proto.CMD_GETVEL)
        resp_type, data = self._parse_response(response)
        return int(data) if resp_type == proto.RESP_ACK else None

    def get_current(self) -> Optional[int]:
        """Read motor current (mA)."""
        response = self._send_command(proto.CMD_GETCURR)
        resp_type, data = self._parse_response(response)
        return int(data) if resp_type == proto.RESP_ACK else None

    def get_sensors(self) -> Optional[Dict]:
        """
        Read all sensors.

        Returns:
            Dict with keys: timestamp, position, velocity, current,
                           force_tendon, force_tip, angle_joint
        """
        response = self._send_command(proto.CMD_GETSENSORS)
        resp_type, data = self._parse_response(response)

        if resp_type == proto.RESP_DATA:
            values = data.split()
            if len(values) >= 7:
                return {
                    'timestamp': int(values[0]),
                    'position': int(values[1]),
                    'velocity': int(values[2]),
                    'current': int(values[3]),
                    'force_tendon': int(values[4]),
                    'force_tip': int(values[5]),
                    'angle_joint': int(values[6])
                }
        return None

    # Safety limit commands

    def set_limit(self, limit_type: str, value: int) -> bool:
        """Set safety limit."""
        command = f"{proto.CMD_SETLIMIT} {limit_type} {value}"
        response = self._send_command(command)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    def zero_sensors(self) -> bool:
        """Zero all sensors."""
        response = self._send_command(proto.CMD_ZERO)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    # Streaming mode

    def start_streaming(self, rate_hz: int, callback):
        """
        Start streaming sensor data.

        Args:
            rate_hz: Streaming rate in Hz
            callback: Function called with sensor dict for each sample
        """
        if self.streaming:
            return

        command = f"{proto.CMD_STREAM} {rate_hz}"
        response = self._send_command(command)
        resp_type, _ = self._parse_response(response)

        if resp_type == proto.RESP_ACK:
            self.streaming = True
            self.stream_callback = callback
            self.stream_thread = threading.Thread(target=self._stream_loop)
            self.stream_thread.daemon = True
            self.stream_thread.start()

    def stop_streaming(self):
        """Stop streaming sensor data."""
        if not self.streaming:
            return

        self.streaming = False
        response = self._send_command(f"{proto.CMD_STREAM} 0")

        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)

    # Advanced control commands

    def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
        """
        Set PID controller parameters.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain

        Returns:
            True if successful
        """
        command = f"{proto.CMD_SETPID} {kp} {ki} {kd}"
        response = self._send_command(command)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    def get_pid_params(self) -> Optional[Dict]:
        """
        Read PID controller parameters from Teensy.

        Returns:
            Dict with keys: kp, ki, kd
        """
        response = self._send_command(proto.CMD_GETPID)
        resp_type, data = self._parse_response(response)

        if resp_type == proto.RESP_ACK:
            values = data.split()
            if len(values) >= 3:
                return {
                    'kp': float(values[0]),
                    'ki': float(values[1]),
                    'kd': float(values[2])
                }
        return None

    def set_motion_profile(self, profile: Dict) -> bool:
        """
        Set motion profile parameters.

        Args:
            profile: Dict with keys: max_velocity, acceleration, deceleration, jerk_limit

        Returns:
            True if successful
        """
        command = f"{proto.CMD_SETPROFILE} {profile['max_velocity']} " \
                 f"{profile['acceleration']} {profile['deceleration']} {profile['jerk_limit']}"
        response = self._send_command(command)
        resp_type, _ = self._parse_response(response)
        return resp_type == proto.RESP_ACK

    def get_motion_profile(self) -> Optional[Dict]:
        """
        Read motion profile parameters from Teensy.

        Returns:
            Dict with keys: max_velocity, acceleration, deceleration, jerk_limit
        """
        response = self._send_command(proto.CMD_GETPROFILE)
        resp_type, data = self._parse_response(response)

        if resp_type == proto.RESP_ACK:
            values = data.split()
            if len(values) >= 4:
                return {
                    'max_velocity': int(values[0]),
                    'acceleration': int(values[1]),
                    'deceleration': int(values[2]),
                    'jerk_limit': int(values[3])
                }
        return None

    def _stream_loop(self):
        """Background thread for reading streaming data."""
        while self.streaming and self.serial_port:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                resp_type, data = self._parse_response(line)

                if resp_type == proto.RESP_DATA:
                    values = data.split()
                    if len(values) >= 7 and self.stream_callback:
                        sensor_data = {
                            'timestamp': int(values[0]),
                            'position': int(values[1]),
                            'velocity': int(values[2]),
                            'current': int(values[3]),
                            'force_tendon': int(values[4]),
                            'force_tip': int(values[5]),
                            'angle_joint': int(values[6])
                        }
                        self.stream_callback(sensor_data)
            except Exception as e:
                print(f"Stream error: {e}")
                break

    # Platform identification methods (required by HardwareController)
    def get_platform_name(self) -> str:
        """Return platform name."""
        return "Teensy"

    def get_platform_info(self) -> Dict:
        """
        Return platform-specific info.

        Returns:
            Dict with firmware version and capabilities
        """
        return {
            'platform': 'Teensy 4.1',
            'version': '1.0',
            'firmware_version': 'Unknown',  # Could query from Teensy if implemented
            'communication': 'Serial',
            'baudrate': 115200,
            'capabilities': [
                'position_control',
                'velocity_control',
                'torque_control',
                'current_control',
                'pid_tuning',
                'motion_profiles',
                'streaming',
                'safety_limits'
            ]
        }
