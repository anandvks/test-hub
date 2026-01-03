"""
Mock Hardware Controller

Simulated controller for testing without real hardware.
Provides realistic sensor data with noise and simple physics simulation.
"""

import time
import random
import threading
from typing import Optional, Dict, Callable
from .base_controller import HardwareController


class MockController(HardwareController):
    """Mock hardware controller for testing without real hardware."""

    def __init__(self):
        super().__init__()
        # Control targets
        self.target_position = 0
        self.target_velocity = 0
        self.target_torque = 0
        self.target_current = 0

        # Current state
        self.current_position = 0
        self.current_velocity = 0
        self.current_current = 0

        # PID parameters
        self.pid = {'kp': 1.0, 'ki': 0.1, 'kd': 0.05}

        # Motion profile
        self.motion_profile = {
            'max_velocity': 3000,      # RPM
            'acceleration': 1000,       # RPM/s
            'deceleration': 1000,       # RPM/s
            'jerk_limit': 5000         # RPM/s²
        }

        # Safety limits
        self.limits = {
            'current_max': 1000,        # mA
            'position_min': 0,
            'position_max': 10000,
            'force_max': 60000          # mN (60 N)
        }

        # Simulation state
        self.start_time = time.time()
        self.last_update = time.time()

        # Streaming
        self.streaming = False
        self.stream_rate = 0
        self.stream_callback = None
        self.stream_thread = None

        # Sensor zero offsets
        self.zero_offsets = {
            'force_tendon': 0,
            'force_tip': 0,
            'angle_joint': 0
        }

    # Connection management

    def connect(self, **kwargs) -> bool:
        """Simulate connection (always succeeds)."""
        print("Mock controller: Connecting...")
        time.sleep(0.2)  # Simulate connection delay
        self.connected = True
        print("Mock controller: Connected successfully")
        return True

    def disconnect(self) -> bool:
        """Disconnect from mock controller."""
        self.stop_streaming()
        self.connected = False
        print("Mock controller: Disconnected")
        return True

    # Motor control

    def enable(self) -> bool:
        """Enable motor driver."""
        if not self.connected:
            return False
        print("Mock controller: Motor enabled")
        self.enabled = True
        return True

    def disable(self) -> bool:
        """Disable motor driver."""
        print("Mock controller: Motor disabled")
        self.enabled = False
        self.target_position = self.current_position
        self.target_velocity = 0
        self.target_torque = 0
        self.target_current = 0
        return True

    def emergency_stop(self) -> bool:
        """Emergency stop - immediately disable motor."""
        print("Mock controller: EMERGENCY STOP")
        self.enabled = False
        self.current_velocity = 0
        self.target_position = self.current_position
        self.target_velocity = 0
        self.target_torque = 0
        self.target_current = 0
        return True

    # Motor commands

    def set_position(self, position: int) -> bool:
        """Set target position (encoder counts)."""
        if not self.connected:
            return False

        # Check limits
        if position < self.limits['position_min'] or position > self.limits['position_max']:
            print(f"Mock controller: Position {position} exceeds limits")
            return False

        self.target_position = position
        return True

    def set_velocity(self, velocity: int) -> bool:
        """Set target velocity (RPM)."""
        if not self.connected:
            return False

        self.target_velocity = velocity
        return True

    def set_torque(self, torque: int) -> bool:
        """Set target torque (mNm)."""
        if not self.connected:
            return False

        self.target_torque = torque
        # Estimate current from torque (simplified: 1 Nm ≈ 1 A for typical motor)
        self.target_current = abs(torque)  # mNm ≈ mA
        return True

    def set_current(self, current: int) -> bool:
        """Set motor current (mA)."""
        if not self.connected:
            return False

        # Check limits
        if abs(current) > self.limits['current_max']:
            print(f"Mock controller: Current {current} mA exceeds limit")
            return False

        self.target_current = current
        return True

    # Sensor reading

    def get_position(self) -> Optional[int]:
        """Read motor position (encoder counts)."""
        if not self.connected:
            return None
        self._update_simulation()
        return self.current_position

    def get_velocity(self) -> Optional[int]:
        """Read motor velocity (RPM)."""
        if not self.connected:
            return None
        self._update_simulation()
        return int(self.current_velocity)

    def get_current(self) -> Optional[int]:
        """Read motor current (mA)."""
        if not self.connected:
            return None
        self._update_simulation()
        return int(self.current_current)

    def get_sensors(self) -> Optional[Dict]:
        """
        Read all sensors with simulated physics.

        Returns:
            Dict with keys: timestamp, position, velocity, current,
                           force_tendon, force_tip, angle_joint
        """
        if not self.connected:
            return None

        self._update_simulation()

        # Simulate forces based on current
        # Simplified model: Force proportional to current
        # Typical: 1A current → ~10N force at fingertip (via gearbox)
        force_tendon = int(self.current_current * 15 + random.gauss(0, 50))  # mN
        force_tip = int(force_tendon * 0.7 + random.gauss(0, 30))  # mN (mechanical advantage ~0.7)

        # Apply zero offsets
        force_tendon -= self.zero_offsets['force_tendon']
        force_tip -= self.zero_offsets['force_tip']

        # Simulate joint angle from position (gear ratio ~230:1, encoder 1000 counts/rev)
        # Joint angle in raw counts (could be mapped to degrees)
        angle_joint = int(self.current_position / 230 * 1000) - self.zero_offsets['angle_joint']

        return {
            'timestamp': int((time.time() - self.start_time) * 1000),  # ms
            'position': self.current_position + random.randint(-2, 2),  # Add encoder noise
            'velocity': int(self.current_velocity + random.gauss(0, 5)),  # RPM
            'current': int(self.current_current + random.gauss(0, 3)),  # mA
            'force_tendon': max(0, force_tendon),  # mN
            'force_tip': max(0, force_tip),  # mN
            'angle_joint': angle_joint  # counts
        }

    # Streaming

    def start_streaming(self, rate_hz: int, callback: Callable) -> bool:
        """Start streaming sensor data."""
        if not self.connected or self.streaming:
            return False

        self.streaming = True
        self.stream_rate = rate_hz
        self.stream_callback = callback

        self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()

        print(f"Mock controller: Streaming started at {rate_hz} Hz")
        return True

    def stop_streaming(self) -> bool:
        """Stop streaming sensor data."""
        if not self.streaming:
            return True

        self.streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=2.0)

        print("Mock controller: Streaming stopped")
        return True

    # Advanced control

    def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
        """Set PID controller parameters."""
        if not self.connected:
            return False

        self.pid = {'kp': kp, 'ki': ki, 'kd': kd}
        print(f"Mock controller: PID set to Kp={kp}, Ki={ki}, Kd={kd}")
        return True

    def get_pid_params(self) -> Optional[Dict]:
        """Get current PID parameters."""
        if not self.connected:
            return None
        return self.pid.copy()

    def set_motion_profile(self, max_velocity: int, max_acceleration: int,
                          max_deceleration: int, jerk: int) -> bool:
        """Set motion profile parameters."""
        if not self.connected:
            return False

        self.motion_profile = {
            'max_velocity': max_velocity,
            'acceleration': max_acceleration,
            'deceleration': max_deceleration,
            'jerk_limit': jerk
        }
        print(f"Mock controller: Motion profile updated")
        return True

    def get_motion_profile(self) -> Optional[Dict]:
        """Get current motion profile."""
        if not self.connected:
            return None
        return self.motion_profile.copy()

    # Safety and calibration

    def set_limit(self, limit_type: str, value: int) -> bool:
        """Set safety limit."""
        if not self.connected:
            return False

        if limit_type in ['current_max', 'position_min', 'position_max', 'force_max']:
            self.limits[limit_type] = value
            print(f"Mock controller: Limit {limit_type} set to {value}")
            return True

        return False

    def zero_sensors(self) -> bool:
        """Zero all sensors."""
        if not self.connected:
            return False

        # Read current values and store as offsets
        sensors = self.get_sensors()
        if sensors:
            self.zero_offsets['force_tendon'] = sensors['force_tendon']
            self.zero_offsets['force_tip'] = sensors['force_tip']
            self.zero_offsets['angle_joint'] = sensors['angle_joint']
            print("Mock controller: Sensors zeroed")
            return True

        return False

    # Platform identification

    def get_platform_name(self) -> str:
        """Return platform name."""
        return "Mock"

    def get_platform_info(self) -> Dict:
        """Return platform-specific info."""
        return {
            'platform': 'Mock Controller (Simulator)',
            'version': '1.0',
            'firmware_version': 'Simulated',
            'communication': 'In-memory',
            'baudrate': None,
            'capabilities': [
                'position_control',
                'velocity_control',
                'torque_control',
                'current_control',
                'pid_tuning',
                'motion_profiles',
                'streaming',
                'safety_limits',
                'physics_simulation'
            ],
            'notes': 'Simulated controller for testing without hardware. '
                    'Provides realistic sensor data with noise and simple physics.'
        }

    # Internal simulation methods

    def _update_simulation(self):
        """Update simulated motor state based on physics."""
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        if not self.enabled:
            # Motor disabled - coast to stop with friction
            self.current_velocity *= 0.9  # Decay velocity
            self.current_current = 0
            return

        # Position control mode (simplified)
        position_error = self.target_position - self.current_position

        # Simple proportional control for simulation
        # Velocity proportional to position error
        desired_velocity = position_error * 0.5  # Proportional gain

        # Limit velocity to max
        max_vel = self.motion_profile['max_velocity']
        desired_velocity = max(-max_vel, min(max_vel, desired_velocity))

        # Update velocity (with acceleration limit)
        velocity_error = desired_velocity - self.current_velocity
        max_accel = self.motion_profile['acceleration'] * dt
        velocity_change = max(-max_accel, min(max_accel, velocity_error))
        self.current_velocity += velocity_change

        # Update position (velocity is in RPM, need to convert to counts)
        # Assuming 1000 counts/rev encoder
        counts_per_minute = self.current_velocity * 1000
        counts_per_second = counts_per_minute / 60
        position_change = int(counts_per_second * dt)
        self.current_position += position_change

        # Clamp position to limits
        self.current_position = max(
            self.limits['position_min'],
            min(self.limits['position_max'], self.current_position)
        )

        # Simulate current based on load
        # Higher current when accelerating or far from target
        base_current = abs(position_error) * 0.05  # Proportional to error
        accel_current = abs(velocity_change) * 10  # Additional current when accelerating
        friction_current = 20  # Baseline friction

        self.current_current = base_current + accel_current + friction_current

        # Limit current
        self.current_current = min(self.current_current, self.limits['current_max'])

        # Add some noise
        self.current_current += random.gauss(0, 2)

    def _stream_loop(self):
        """Background thread for streaming sensor data."""
        interval = 1.0 / self.stream_rate if self.stream_rate > 0 else 0.1

        while self.streaming:
            try:
                sensor_data = self.get_sensors()
                if sensor_data and self.stream_callback:
                    self.stream_callback(sensor_data)

                time.sleep(interval)
            except Exception as e:
                print(f"Mock controller stream error: {e}")
                break
