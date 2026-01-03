"""
Torque & Efficiency Test

Measure motor torque-current relationship and system efficiency.
"""

import time
import numpy as np
from pathlib import Path
from datetime import datetime
from .base_test import BaseTest


class TorqueEfficiencyTest(BaseTest):
    """
    Torque & Efficiency Test.

    Procedure:
    1. Ramp motor torque from min to max in steps
    2. At each step, hold for settling time and measure sensors
    3. Calculate mechanical power, electrical power, and efficiency
    4. Optionally ramp back down to measure hysteresis
    5. Generate torque curve and efficiency plots
    """

    def get_name(self) -> str:
        return "Torque & Efficiency Test"

    def get_description(self) -> str:
        return ("Measure motor torque-current curve and calculate system efficiency. "
                "Validates power transmission from motor to fingertip.")

    def get_parameters(self) -> dict:
        return {
            'torque_min_mNm': {
                'type': 'float',
                'default': 0,
                'unit': 'mNm',
                'min': 0,
                'max': 5000,
                'description': 'Minimum torque'
            },
            'torque_max_mNm': {
                'type': 'float',
                'default': 3000,
                'unit': 'mNm',
                'min': 0,
                'max': 5000,
                'description': 'Maximum torque'
            },
            'steps': {
                'type': 'int',
                'default': 20,
                'min': 5,
                'max': 100,
                'description': 'Number of measurement points'
            },
            'hold_duration_s': {
                'type': 'float',
                'default': 2.0,
                'unit': 's',
                'min': 0.5,
                'max': 10,
                'description': 'Hold time at each torque level'
            },
            'settling_time_s': {
                'type': 'float',
                'default': 0.5,
                'unit': 's',
                'min': 0.1,
                'max': 5,
                'description': 'Settling time before measurement'
            },
            'measure_efficiency': {
                'type': 'bool',
                'default': True,
                'description': 'Calculate system efficiency'
            },
            'plot_hysteresis': {
                'type': 'bool',
                'default': True,
                'description': 'Ramp down to measure hysteresis'
            }
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        if config['torque_max_mNm'] <= config['torque_min_mNm']:
            return False, "Max torque must be greater than min torque"

        if config['steps'] < 2:
            return False, "Need at least 2 steps"

        if config['torque_max_mNm'] > 3300:
            return False, "Torque exceeds gearbox limit (3.3 Nm)"

        return True, ""

    def estimate_duration(self, config: dict) -> float:
        """Estimate test duration."""
        steps = config['steps']
        hold = config['hold_duration_s']
        settling = config['settling_time_s']

        duration = steps * (hold + settling)

        # Double if measuring hysteresis
        if config['plot_hysteresis']:
            duration *= 2

        return duration

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute torque & efficiency test."""
        self.is_running = True
        self.stop_requested = False

        # Initialize results
        results = {
            'torque_commanded': [],
            'torque_measured': [],
            'current': [],
            'voltage': [],
            'force_tendon': [],
            'force_tip': [],
            'position': [],
            'velocity': [],
            'power_electrical': [],
            'power_mechanical': [],
            'efficiency': [],
            'timestamp': [],
            'direction': []  # 'up' or 'down'
        }

        # Start data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"torque_efficiency_{timestamp}.csv"

        headers = list(results.keys())
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'torque_efficiency',
            'config': config
        })

        try:
            # Generate torque profile
            torques = np.linspace(
                config['torque_min_mNm'],
                config['torque_max_mNm'],
                config['steps']
            )

            total_steps = len(torques)
            if config['plot_hysteresis']:
                total_steps *= 2

            step_count = 0

            # Ramp up
            self._update_progress(progress_callback, 0, "Starting ramp up...")

            for i, torque in enumerate(torques):
                if self._check_stop():
                    break

                self._wait_while_paused()

                # Command torque
                self.hw['teensy'].set_torque(int(torque))

                # Settling time
                time.sleep(config['settling_time_s'])

                # Hold and measure
                t_start = time.time()
                samples = []

                while time.time() - t_start < config['hold_duration_s']:
                    if self._check_stop():
                        break

                    data = self.hw['teensy'].get_sensors()
                    if data:
                        samples.append(data)
                    time.sleep(0.01)  # 100Hz sampling

                # Average samples for this torque level
                if samples:
                    avg_data = self._average_samples(samples)

                    # Calculate efficiency
                    efficiency = 0
                    if config['measure_efficiency']:
                        efficiency = self._calculate_efficiency(avg_data, torque)

                    # Store results
                    self._store_result(results, torque, avg_data, efficiency, 'up')

                    # Log to file
                    self.logger.log({
                        'torque_commanded': torque,
                        'current': avg_data['current'] / 1000.0,
                        'force_tendon': avg_data['force_tendon'] / 1000.0,
                        'force_tip': avg_data['force_tip'] / 1000.0,
                        'efficiency': efficiency,
                        'direction': 'up'
                    })

                # Update progress
                step_count += 1
                progress = (step_count / total_steps) * 100
                self._update_progress(progress_callback, progress,
                                    f"Ramp up: {torque:.0f} mNm ({i+1}/{len(torques)})")

            # Ramp down (if hysteresis enabled)
            if config['plot_hysteresis'] and not self._check_stop():
                self._update_progress(progress_callback, 50, "Starting ramp down...")

                for i, torque in enumerate(reversed(torques)):
                    if self._check_stop():
                        break

                    self._wait_while_paused()

                    # Command torque
                    self.hw['teensy'].set_torque(int(torque))

                    # Settling time
                    time.sleep(config['settling_time_s'])

                    # Hold and measure
                    t_start = time.time()
                    samples = []

                    while time.time() - t_start < config['hold_duration_s']:
                        if self._check_stop():
                            break

                        data = self.hw['teensy'].get_sensors()
                        if data:
                            samples.append(data)
                        time.sleep(0.01)

                    # Average samples
                    if samples:
                        avg_data = self._average_samples(samples)
                        efficiency = 0
                        if config['measure_efficiency']:
                            efficiency = self._calculate_efficiency(avg_data, torque)

                        self._store_result(results, torque, avg_data, efficiency, 'down')

                        self.logger.log({
                            'torque_commanded': torque,
                            'current': avg_data['current'] / 1000.0,
                            'force_tendon': avg_data['force_tendon'] / 1000.0,
                            'force_tip': avg_data['force_tip'] / 1000.0,
                            'efficiency': efficiency,
                            'direction': 'down'
                        })

                    # Update progress
                    step_count += 1
                    progress = (step_count / total_steps) * 100
                    self._update_progress(progress_callback, progress,
                                        f"Ramp down: {torque:.0f} mNm ({i+1}/{len(torques)})")

            # Return to zero
            self.hw['teensy'].set_torque(0)
            self._update_progress(progress_callback, 100, "Test complete")

        except Exception as e:
            print(f"Test error: {e}")
            results['error'] = str(e)

        finally:
            self.logger.stop_logging()
            self.is_running = False

        # Add summary statistics
        results['summary'] = self._calculate_summary(results)
        results['config'] = config
        results['log_file'] = str(log_path)

        return results

    def _average_samples(self, samples: list) -> dict:
        """Average sensor samples."""
        if not samples:
            return {}

        avg = {
            'position': int(np.mean([s['position'] for s in samples])),
            'velocity': int(np.mean([s['velocity'] for s in samples])),
            'current': int(np.mean([s['current'] for s in samples])),
            'force_tendon': int(np.mean([s['force_tendon'] for s in samples])),
            'force_tip': int(np.mean([s['force_tip'] for s in samples])),
            'angle_joint': int(np.mean([s['angle_joint'] for s in samples]))
        }
        return avg

    def _calculate_efficiency(self, data: dict, torque_cmd: float) -> float:
        """
        Calculate system efficiency.

        η = P_mech / P_elec
        """
        try:
            # Electrical power (assuming 24V supply)
            voltage = 24.0  # V
            current_A = data['current'] / 1000.0  # Convert mA to A
            power_elec = voltage * current_A  # W

            # Mechanical power at fingertip
            force_tip_N = data['force_tip'] / 1000.0  # Convert mN to N
            velocity_RPM = data['velocity']
            velocity_rad_s = velocity_RPM * 2 * np.pi / 60  # Convert to rad/s

            # Simplified: assume tip velocity proportional to motor velocity
            # In reality, need to account for gearbox ratio and tendon routing
            # For now, use force as proxy for mechanical power
            power_mech = force_tip_N * 0.01  # Simplified (force * velocity_factor)

            # Calculate efficiency
            if power_elec > 0:
                efficiency = (power_mech / power_elec) * 100  # Percentage
                efficiency = max(0, min(100, efficiency))  # Clamp to 0-100%
            else:
                efficiency = 0

            return efficiency

        except Exception as e:
            print(f"Efficiency calculation error: {e}")
            return 0

    def _store_result(self, results: dict, torque: float, data: dict,
                     efficiency: float, direction: str):
        """Store measurement in results dictionary."""
        results['torque_commanded'].append(torque)
        results['torque_measured'].append(torque)  # Assuming accurate control
        results['current'].append(data['current'] / 1000.0)
        results['voltage'].append(24.0)
        results['force_tendon'].append(data['force_tendon'] / 1000.0)
        results['force_tip'].append(data['force_tip'] / 1000.0)
        results['position'].append(data['position'])
        results['velocity'].append(data['velocity'])
        results['efficiency'].append(efficiency)
        results['timestamp'].append(time.time())
        results['direction'].append(direction)

    def _calculate_summary(self, results: dict) -> dict:
        """Calculate summary statistics."""
        summary = {}

        if results['efficiency']:
            summary['avg_efficiency'] = np.mean(results['efficiency'])
            summary['max_efficiency'] = np.max(results['efficiency'])

        if results['force_tip']:
            summary['max_force_tip'] = np.max(results['force_tip'])
            summary['max_force_tip_kg'] = np.max(results['force_tip']) / 9.81

        if results['current']:
            summary['max_current'] = np.max(results['current'])

        return summary
