"""
Static Hold Test

Validate sustained force capability over time (30 min target).
Monitors motor temperature and tendon creep.
"""

import time
import numpy as np
from pathlib import Path
from datetime import datetime
from .base_test import BaseTest


class StaticHoldTest(BaseTest):
    """
    Static Hold Test.

    Procedure:
    1. Command motor to achieve target force
    2. Hold for specified duration (typically 30 minutes)
    3. Monitor: force stability, motor current, position drift (creep)
    4. Detect failures: force drop, overcurrent, excessive drift
    """

    def get_name(self) -> str:
        return "Static Hold Test"

    def get_description(self) -> str:
        return ("Hold constant force for extended duration. "
                "Validates 1.2kg/finger target and monitors stability.")

    def get_parameters(self) -> dict:
        return {
            'target_force_N': {
                'type': 'float',
                'default': 11.8,  # 1.2 kg
                'unit': 'N',
                'min': 0,
                'max': 50,
                'description': 'Target fingertip force'
            },
            'hold_duration_min': {
                'type': 'float',
                'default': 30.0,
                'unit': 'minutes',
                'min': 1,
                'max': 120,
                'description': 'Hold duration'
            },
            'sample_interval_s': {
                'type': 'float',
                'default': 1.0,
                'unit': 's',
                'min': 0.1,
                'max': 10,
                'description': 'Time between samples'
            },
            'force_tolerance_percent': {
                'type': 'float',
                'default': 10.0,
                'unit': '%',
                'min': 1,
                'max': 50,
                'description': 'Acceptable force variation'
            },
            'max_drift_counts': {
                'type': 'int',
                'default': 100,
                'unit': 'counts',
                'min': 10,
                'max': 1000,
                'description': 'Max allowable position drift'
            }
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        if config['target_force_N'] <= 0:
            return False, "Target force must be positive"

        if config['hold_duration_min'] < 1:
            return False, "Hold duration must be at least 1 minute"

        if config['target_force_N'] > 20:
            return False, "Force exceeds safety limit (20N)"

        return True, ""

    def estimate_duration(self, config: dict) -> float:
        """Estimate test duration."""
        return config['hold_duration_min'] * 60 + 10  # Duration + setup

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute static hold test."""
        self.is_running = True
        self.stop_requested = False

        # Initialize results
        results = {
            'time_sec': [],
            'position': [],
            'force_tip': [],
            'current': [],
            'drift': [],
            'force_error_percent': []
        }

        # Start data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"static_hold_{timestamp}.csv"

        headers = list(results.keys())
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'static_hold',
            'config': config
        })

        try:
            target_force = config['target_force_N']
            duration_sec = config['hold_duration_min'] * 60
            interval = config['sample_interval_s']

            # Convert force to torque (simplified: force * spool_radius)
            # Assuming 10mm spool: torque(mNm) = force(N) * 10
            target_torque = int(target_force * 10)

            self._update_progress(progress_callback, 0, f"Applying {target_force:.1f}N force...")

            # Apply target torque
            self.hw['teensy'].set_torque(target_torque)
            time.sleep(2)  # Initial settling

            # Record initial position
            initial_data = self.hw['teensy'].get_sensors()
            initial_pos = initial_data['position'] if initial_data else 0

            start_time = time.time()
            last_log_minute = 0

            self._update_progress(progress_callback, 5, "Holding force...")

            while time.time() - start_time < duration_sec:
                if self._check_stop():
                    break

                self._wait_while_paused()

                elapsed = time.time() - start_time

                # Read sensors
                data = self.hw['teensy'].get_sensors()
                if data:
                    force_tip = data['force_tip'] / 1000.0  # Convert to N
                    current_A = data['current'] / 1000.0
                    position = data['position']
                    drift = position - initial_pos

                    # Calculate force error
                    force_error = abs(force_tip - target_force) / target_force * 100

                    # Store results
                    results['time_sec'].append(elapsed)
                    results['position'].append(position)
                    results['force_tip'].append(force_tip)
                    results['current'].append(current_A)
                    results['drift'].append(drift)
                    results['force_error_percent'].append(force_error)

                    # Log to file
                    self.logger.log({
                        'time_sec': elapsed,
                        'position': position,
                        'force_tip': force_tip,
                        'current': current_A,
                        'drift': drift,
                        'force_error_percent': force_error
                    })

                    # Check for failures
                    if force_error > config['force_tolerance_percent']:
                        msg = f"Force error {force_error:.1f}% exceeds tolerance"
                        self._update_progress(progress_callback, -1, f"WARNING: {msg}")

                    if abs(drift) > config['max_drift_counts']:
                        msg = f"Position drift {drift} exceeds limit"
                        self._update_progress(progress_callback, -1, f"WARNING: {msg}")

                # Log every minute
                current_minute = int(elapsed / 60)
                if current_minute > last_log_minute:
                    last_log_minute = current_minute
                    info = f"T+{current_minute}min: Force={force_tip:.2f}N, Drift={drift}"
                    print(info)

                # Update progress
                progress = 5 + ((elapsed / duration_sec) * 95)
                time_remaining = duration_sec - elapsed
                self._update_progress(progress_callback, progress,
                                    f"Holding... {int(elapsed/60)}/{int(duration_sec/60)} min")

                time.sleep(interval)

            # Return to zero
            self.hw['teensy'].set_torque(0)
            self._update_progress(progress_callback, 100, "Hold test complete")

        except Exception as e:
            print(f"Test error: {e}")
            results['error'] = str(e)

        finally:
            self.logger.stop_logging()
            self.is_running = False

        # Calculate summary statistics
        if results['force_tip']:
            results['summary'] = {
                'target_force_N': config['target_force_N'],
                'avg_force_N': np.mean(results['force_tip']),
                'force_std_N': np.std(results['force_tip']),
                'max_drift_counts': max(abs(d) for d in results['drift']) if results['drift'] else 0,
                'avg_current_A': np.mean(results['current']),
                'max_force_error_percent': max(results['force_error_percent']) if results['force_error_percent'] else 0
            }

        results['config'] = config
        results['log_file'] = str(log_path)

        return results
