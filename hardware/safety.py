"""
Safety Monitor

Real-time monitoring of safety limits for motor control system.
"""

import threading
import time
from typing import Dict, Callable, List


class SafetyMonitor:
    """
    Monitors sensor data against safety limits.
    Triggers emergency stop if limits exceeded.
    """

    def __init__(self, teensy_controller):
        self.teensy = teensy_controller
        self.limits = {
            'current_max': 1.0,        # Amps (gearbox protection)
            'force_tendon_max': 200.0,  # Newtons
            'force_tip_max': 20.0,      # Newtons
            'position_min': 0,          # Encoder counts
            'position_max': 10000,      # Encoder counts
        }

        self.monitoring = False
        self.monitor_thread = None
        self.violation_callbacks: List[Callable] = []
        self.last_violation = None
        self.check_interval = 0.1  # 10 Hz

    def set_limits(self, limits: Dict):
        """Update safety limits."""
        self.limits.update(limits)

    def get_limits(self) -> Dict:
        """Get current safety limits."""
        return self.limits.copy()

    def register_violation_callback(self, callback: Callable):
        """
        Register callback for safety violations.

        Args:
            callback: Function called with (reason, sensor_data) on violation
        """
        self.violation_callbacks.append(callback)

    def start_monitoring(self):
        """Start safety monitoring in background thread."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop safety monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def check_safety(self, sensor_data: Dict) -> tuple[bool, str]:
        """
        Check if sensor data is within safety limits.

        Args:
            sensor_data: Dictionary with sensor readings

        Returns:
            (is_safe, reason) tuple
        """
        # Convert mA to A for current check
        current_A = sensor_data.get('current', 0) / 1000.0

        if current_A > self.limits['current_max']:
            return False, f"Current limit exceeded: {current_A:.2f}A > {self.limits['current_max']:.2f}A"

        # Convert raw ADC values to Newtons (assuming calibration applied in Teensy)
        force_tendon = sensor_data.get('force_tendon', 0) / 1000.0  # Assuming mN to N
        if force_tendon > self.limits['force_tendon_max']:
            return False, f"Tendon force limit exceeded: {force_tendon:.1f}N > {self.limits['force_tendon_max']:.1f}N"

        force_tip = sensor_data.get('force_tip', 0) / 1000.0  # Assuming mN to N
        if force_tip > self.limits['force_tip_max']:
            return False, f"Tip force limit exceeded: {force_tip:.1f}N > {self.limits['force_tip_max']:.1f}N"

        position = sensor_data.get('position', 0)
        if position < self.limits['position_min']:
            return False, f"Position below minimum: {position} < {self.limits['position_min']}"

        if position > self.limits['position_max']:
            return False, f"Position above maximum: {position} > {self.limits['position_max']}"

        return True, ""

    def trigger_estop(self, reason: str, sensor_data: Dict = None):
        """
        Trigger emergency stop.

        Args:
            reason: Description of why e-stop was triggered
            sensor_data: Optional sensor data at time of violation
        """
        print(f"EMERGENCY STOP: {reason}")

        # Send e-stop to Teensy
        try:
            self.teensy.emergency_stop()
        except Exception as e:
            print(f"Error sending e-stop: {e}")

        # Record violation
        self.last_violation = {
            'reason': reason,
            'timestamp': time.time(),
            'sensor_data': sensor_data
        }

        # Notify all registered callbacks
        for callback in self.violation_callbacks:
            try:
                callback(reason, sensor_data)
            except Exception as e:
                print(f"Error in violation callback: {e}")

    def _monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring:
            try:
                # Read sensors
                sensor_data = self.teensy.get_sensors()

                if sensor_data:
                    # Check safety
                    is_safe, reason = self.check_safety(sensor_data)

                    if not is_safe:
                        self.trigger_estop(reason, sensor_data)
                        break  # Stop monitoring after e-stop

                time.sleep(self.check_interval)

            except Exception as e:
                print(f"Safety monitor error: {e}")
                time.sleep(self.check_interval)

    def get_safety_status(self, sensor_data: Dict) -> Dict:
        """
        Get detailed safety status for display.

        Args:
            sensor_data: Current sensor readings

        Returns:
            Dict with status for each limit
        """
        current_A = sensor_data.get('current', 0) / 1000.0
        force_tendon_N = sensor_data.get('force_tendon', 0) / 1000.0
        force_tip_N = sensor_data.get('force_tip', 0) / 1000.0
        position = sensor_data.get('position', 0)

        def get_status_level(value, limit, is_max=True):
            """Return 'safe', 'warning', or 'danger' based on proximity to limit."""
            if is_max:
                ratio = value / limit if limit > 0 else 0
            else:
                ratio = (limit - value) / limit if limit > 0 else 0

            if ratio < 0.8:
                return 'safe'
            elif ratio < 1.0:
                return 'warning'
            else:
                return 'danger'

        return {
            'current': {
                'value': current_A,
                'limit': self.limits['current_max'],
                'status': get_status_level(current_A, self.limits['current_max'])
            },
            'force_tendon': {
                'value': force_tendon_N,
                'limit': self.limits['force_tendon_max'],
                'status': get_status_level(force_tendon_N, self.limits['force_tendon_max'])
            },
            'force_tip': {
                'value': force_tip_N,
                'limit': self.limits['force_tip_max'],
                'status': get_status_level(force_tip_N, self.limits['force_tip_max'])
            },
            'position': {
                'value': position,
                'min': self.limits['position_min'],
                'max': self.limits['position_max'],
                'status': 'safe' if self.limits['position_min'] <= position <= self.limits['position_max'] else 'danger'
            }
        }
