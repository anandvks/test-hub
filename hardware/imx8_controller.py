"""
IMX8 Hardware Controller

Controller for IMX8 platform using Ethernet/TCP communication.
Uses JSON protocol over TCP sockets for command/response.
"""

import socket
import json
import threading
import time
from typing import Optional, Dict, Callable
from .base_controller import HardwareController


class IMX8Controller(HardwareController):
    """Hardware controller for IMX8 platform via Ethernet/TCP."""

    def __init__(self):
        super().__init__()
        self.socket = None
        self.host = None
        self.port = None
        self.lock = threading.Lock()
        self.streaming_thread = None
        self.streaming_active = False
        self.streaming_callback = None
        self.streaming_rate = 0

    # Connection management

    def connect(self, **kwargs) -> bool:
        """
        Connect to IMX8 via TCP socket.

        Args:
            host (str): IP address (e.g., '192.168.1.100')
            port (int): TCP port (e.g., 5000)

        Returns:
            True if connection successful
        """
        self.host = kwargs.get('host', '192.168.1.100')
        self.port = kwargs.get('port', 5000)

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(2.0)
            self.socket.connect((self.host, self.port))

            print(f"IMX8 controller: Connected to {self.host}:{self.port}")

            # Verify connection with ping
            response = self._send_command('PING')
            if response and response.get('status') == 'ok':
                self.connected = True
                return True
            else:
                self.disconnect()
                return False

        except Exception as e:
            print(f"IMX8 connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from IMX8."""
        self.stop_streaming()

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.connected = False
        print("IMX8 controller: Disconnected")
        return True

    # Internal communication

    def _send_command(self, command: str, data: dict = None) -> Optional[dict]:
        """
        Send JSON command to IMX8.

        Protocol:
            Request:  {"cmd": "COMMAND", "data": {...}}
            Response: {"status": "ok"/"error", "data": {...}, "error": "message"}

        Args:
            command: Command name
            data: Optional command parameters

        Returns:
            Response dict or None on error
        """
        if not self.connected or not self.socket:
            print("IMX8 controller: Not connected")
            return None

        with self.lock:
            try:
                # Build request
                msg = {"cmd": command}
                if data:
                    msg["data"] = data

                # Send JSON + newline delimiter
                msg_bytes = (json.dumps(msg) + '\n').encode('utf-8')
                self.socket.sendall(msg_bytes)

                # Receive response (up to 4KB)
                response_bytes = self.socket.recv(4096)
                if not response_bytes:
                    print("IMX8 controller: Connection closed by remote")
                    return None

                response = json.loads(response_bytes.decode('utf-8'))

                if response.get('status') != 'ok':
                    error_msg = response.get('error', 'Unknown error')
                    print(f"IMX8 command error: {error_msg}")

                return response

            except socket.timeout:
                print("IMX8 controller: Communication timeout")
                return None
            except Exception as e:
                print(f"IMX8 communication error: {e}")
                return None

    # Motor control

    def enable(self) -> bool:
        """Enable motor driver."""
        response = self._send_command('ENABLE')
        if response and response.get('status') == 'ok':
            self.enabled = True
            print("IMX8 controller: Motor enabled")
            return True
        return False

    def disable(self) -> bool:
        """Disable motor driver."""
        response = self._send_command('DISABLE')
        if response and response.get('status') == 'ok':
            self.enabled = False
            print("IMX8 controller: Motor disabled")
            return True
        return False

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately disable motor."""
        response = self._send_command('ESTOP')
        if response and response.get('status') == 'ok':
            self.enabled = False
            print("IMX8 controller: EMERGENCY STOP")
            return True
        return False

    # Motor commands

    def set_position(self, position: int) -> bool:
        """Set target position (encoder counts)."""
        response = self._send_command('SET_POSITION', {'value': position})
        return response and response.get('status') == 'ok'

    def set_velocity(self, velocity: int) -> bool:
        """Set target velocity (RPM)."""
        response = self._send_command('SET_VELOCITY', {'value': velocity})
        return response and response.get('status') == 'ok'

    def set_torque(self, torque: int) -> bool:
        """Set target torque (mNm)."""
        response = self._send_command('SET_TORQUE', {'value': torque})
        return response and response.get('status') == 'ok'

    def set_current(self, current: int) -> bool:
        """Set motor current (mA)."""
        response = self._send_command('SET_CURRENT', {'value': current})
        return response and response.get('status') == 'ok'

    # Sensor reading

    def get_position(self) -> Optional[int]:
        """Read motor position (encoder counts)."""
        response = self._send_command('GET_POSITION')
        if response and response.get('status') == 'ok':
            return response.get('data', {}).get('position')
        return None

    def get_velocity(self) -> Optional[int]:
        """Read motor velocity (RPM)."""
        response = self._send_command('GET_VELOCITY')
        if response and response.get('status') == 'ok':
            return response.get('data', {}).get('velocity')
        return None

    def get_current(self) -> Optional[int]:
        """Read motor current (mA)."""
        response = self._send_command('GET_CURRENT')
        if response and response.get('status') == 'ok':
            return response.get('data', {}).get('current')
        return None

    def get_sensors(self) -> Optional[Dict]:
        """
        Read all sensors via JSON protocol.

        Returns:
            Dict with keys: timestamp, position, velocity, current,
                           force_tendon, force_tip, angle_joint
        """
        response = self._send_command('GET_SENSORS')

        if response and response.get('status') == 'ok':
            data = response.get('data', {})

            # Convert from platform-specific format to standardized dict
            return {
                'timestamp': data.get('timestamp', 0),
                'position': data.get('position', 0),
                'velocity': data.get('velocity', 0),
                'current': data.get('current', 0),
                'force_tendon': data.get('force_tendon', 0),
                'force_tip': data.get('force_tip', 0),
                'angle_joint': data.get('angle_joint', 0)
            }

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
        if not self.connected or self.streaming_active:
            return False

        response = self._send_command('START_STREAM', {'rate': rate_hz})

        if response and response.get('status') == 'ok':
            self.streaming_active = True
            self.streaming_rate = rate_hz
            self.streaming_callback = callback

            # Start background thread to receive stream
            self.streaming_thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.streaming_thread.start()

            print(f"IMX8 controller: Streaming started at {rate_hz} Hz")
            return True

        return False

    def stop_streaming(self) -> bool:
        """Stop streaming sensor data."""
        if not self.streaming_active:
            return True

        self.streaming_active = False

        # Send stop command
        self._send_command('STOP_STREAM')

        # Wait for thread to finish
        if self.streaming_thread:
            self.streaming_thread.join(timeout=2.0)

        print("IMX8 controller: Streaming stopped")
        return True

    def _stream_loop(self):
        """Background thread for receiving streaming data."""
        # Create separate socket for streaming to avoid blocking commands
        stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stream_socket.settimeout(1.0)

        try:
            # Connect to streaming port (command port + 1)
            stream_socket.connect((self.host, self.port + 1))

            while self.streaming_active:
                try:
                    # Receive JSON line
                    data_bytes = stream_socket.recv(4096)
                    if not data_bytes:
                        break

                    # Parse JSON (may contain multiple lines)
                    lines = data_bytes.decode('utf-8').strip().split('\n')
                    for line in lines:
                        if not line:
                            continue

                        data = json.loads(line)

                        # Convert to standardized format
                        sensor_data = {
                            'timestamp': data.get('timestamp', 0),
                            'position': data.get('position', 0),
                            'velocity': data.get('velocity', 0),
                            'current': data.get('current', 0),
                            'force_tendon': data.get('force_tendon', 0),
                            'force_tip': data.get('force_tip', 0),
                            'angle_joint': data.get('angle_joint', 0)
                        }

                        # Call user callback
                        if self.streaming_callback:
                            self.streaming_callback(sensor_data)

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"IMX8 stream error: {e}")
                    break

        except Exception as e:
            print(f"IMX8 stream connection error: {e}")

        finally:
            stream_socket.close()

    # Advanced control

    def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID controller parameters."""
        response = self._send_command('SET_PID', {'kp': kp, 'ki': ki, 'kd': kd})
        return response and response.get('status') == 'ok'

    def get_pid_params(self) -> Optional[Dict]:
        """Get current PID parameters."""
        response = self._send_command('GET_PID')
        if response and response.get('status') == 'ok':
            data = response.get('data', {})
            return {
                'kp': data.get('kp', 0.0),
                'ki': data.get('ki', 0.0),
                'kd': data.get('kd', 0.0)
            }
        return None

    def set_motion_profile(self, max_velocity: int, max_acceleration: int,
                          max_deceleration: int, jerk: int) -> bool:
        """Set motion profile parameters."""
        response = self._send_command('SET_PROFILE', {
            'max_velocity': max_velocity,
            'max_acceleration': max_acceleration,
            'max_deceleration': max_deceleration,
            'jerk': jerk
        })
        return response and response.get('status') == 'ok'

    def get_motion_profile(self) -> Optional[Dict]:
        """Get current motion profile."""
        response = self._send_command('GET_PROFILE')
        if response and response.get('status') == 'ok':
            data = response.get('data', {})
            return {
                'max_velocity': data.get('max_velocity', 0),
                'acceleration': data.get('max_acceleration', 0),
                'deceleration': data.get('max_deceleration', 0),
                'jerk_limit': data.get('jerk', 0)
            }
        return None

    # Safety and calibration

    def set_limit(self, limit_type: str, value: int) -> bool:
        """
        Set safety limit.

        Args:
            limit_type: 'current_max', 'position_min', 'position_max', 'force_max'
            value: Limit value in base units
        """
        response = self._send_command('SET_LIMIT', {
            'type': limit_type,
            'value': value
        })
        return response and response.get('status') == 'ok'

    def zero_sensors(self) -> bool:
        """Zero all sensors."""
        response = self._send_command('ZERO_SENSORS')
        if response and response.get('status') == 'ok':
            print("IMX8 controller: Sensors zeroed")
            return True
        return False

    # Platform identification

    def get_platform_name(self) -> str:
        """Return platform name."""
        return "IMX8"

    def get_platform_info(self) -> Dict:
        """
        Return platform-specific info.

        Returns:
            Dict with firmware version and capabilities
        """
        # Try to query firmware info from device
        response = self._send_command('GET_INFO')

        if response and response.get('status') == 'ok':
            data = response.get('data', {})
            firmware_version = data.get('firmware_version', 'Unknown')
        else:
            firmware_version = 'Unknown'

        return {
            'platform': 'IMX8',
            'version': '1.0',
            'firmware_version': firmware_version,
            'communication': 'Ethernet/TCP',
            'protocol': 'JSON',
            'host': self.host,
            'port': self.port,
            'capabilities': [
                'position_control',
                'velocity_control',
                'torque_control',
                'current_control',
                'pid_tuning',
                'motion_profiles',
                'streaming',
                'safety_limits',
                'network_communication'
            ],
            'notes': 'Ethernet/TCP communication with JSON protocol. '
                    'Supports dual-socket streaming for low-latency data acquisition.'
        }
