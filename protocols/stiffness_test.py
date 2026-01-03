"""
Stiffness Test

Measure tendon compliance by locking motor and applying external force.
Validates tendon Young's modulus and "bedding-in" behavior.
"""

import time
import numpy as np
from pathlib import Path
from datetime import datetime
from .base_test import BaseTest


class StiffnessTest(BaseTest):
    """
    Stiffness Mapping Test.

    Procedure:
    1. Lock motor at test position
    2. Apply external force to finger (user applies or automated)
    3. Measure position displacement
    4. Calculate stiffness (force / displacement)
    5. Repeat at multiple positions
    """

    def get_name(self) -> str:
        return "Stiffness Mapping Test"

    def get_description(self) -> str:
        return ("Lock motor and measure position change under external force. "
                "Validates tendon stiffness and compliance.")

    def get_parameters(self) -> dict:
        return {
            'test_position': {
                'type': 'int',
                'default': 5000,
                'unit': 'counts',
                'min': 0,
                'max': 10000,
                'description': 'Position to lock motor'
            },
            'hold_time_s': {
                'type': 'float',
                'default': 10.0,
                'unit': 's',
                'min': 5,
                'max': 60,
                'description': 'Time to hold position while measuring'
            },
            'sample_rate_hz': {
                'type': 'int',
                'default': 10,
                'unit': 'Hz',
                'min': 1,
                'max': 100,
                'description': 'Sampling rate'
            },
            'expected_force_N': {
                'type': 'float',
                'default': 5.0,
                'unit': 'N',
                'min': 0,
                'max': 50,
                'description': 'Expected external force (for info)'
            }
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        if config['hold_time_s'] < 5:
            return False, "Hold time must be at least 5 seconds"

        if config['sample_rate_hz'] < 1:
            return False, "Sample rate must be at least 1 Hz"

        return True, ""

    def estimate_duration(self, config: dict) -> float:
        """Estimate test duration."""
        return config['hold_time_s'] + 5  # Hold time + setup

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute stiffness test."""
        self.is_running = True
        self.stop_requested = False

        # Initialize results
        results = {
            'time': [],
            'position': [],
            'force_tendon': [],
            'force_tip': [],
            'displacement': []
        }

        # Start data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"stiffness_{timestamp}.csv"

        headers = list(results.keys())
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'stiffness',
            'config': config
        })

        try:
            # Move to test position
            target_pos = config['test_position']
            self._update_progress(progress_callback, 0, f"Moving to position {target_pos}...")

            self.hw['teensy'].set_position(target_pos)
            time.sleep(2)  # Allow settling

            # Record initial position
            initial_data = self.hw['teensy'].get_sensors()
            initial_pos = initial_data['position'] if initial_data else target_pos

            self._update_progress(progress_callback, 10,
                                f"Position locked. Apply external force now...")

            # Hold and measure
            hold_time = config['hold_time_s']
            sample_period = 1.0 / config['sample_rate_hz']
            start_time = time.time()

            while time.time() - start_time < hold_time:
                if self._check_stop():
                    break

                self._wait_while_paused()

                # Maintain position command (motor tries to hold)
                self.hw['teensy'].set_position(target_pos)

                # Read sensors
                data = self.hw['teensy'].get_sensors()
                if data:
                    current_time = time.time() - start_time
                    displacement = data['position'] - initial_pos

                    results['time'].append(current_time)
                    results['position'].append(data['position'])
                    results['force_tendon'].append(data['force_tendon'] / 1000.0)
                    results['force_tip'].append(data['force_tip'] / 1000.0)
                    results['displacement'].append(displacement)

                    # Log to file
                    self.logger.log({
                        'time': current_time,
                        'position': data['position'],
                        'force_tendon': data['force_tendon'] / 1000.0,
                        'force_tip': data['force_tip'] / 1000.0,
                        'displacement': displacement
                    })

                # Update progress
                progress = 10 + ((time.time() - start_time) / hold_time) * 90
                self._update_progress(progress_callback, progress,
                                    f"Measuring... {current_time:.1f}/{hold_time:.1f}s")

                time.sleep(sample_period)

            self._update_progress(progress_callback, 100, "Test complete")

        except Exception as e:
            print(f"Test error: {e}")
            results['error'] = str(e)

        finally:
            # Release position hold
            self.hw['teensy'].set_torque(0)
            self.logger.stop_logging()
            self.is_running = False

        # Calculate stiffness
        if results['force_tip'] and results['displacement']:
            # Find max displacement
            max_disp = max(abs(d) for d in results['displacement'])
            avg_force = np.mean([f for f in results['force_tip'] if f > 0.5])

            if max_disp > 0 and avg_force > 0:
                stiffness = avg_force / (max_disp * 0.001)  # N/mm (assuming counts ~ mm)
                results['summary'] = {
                    'max_displacement_counts': max_disp,
                    'avg_force_N': avg_force,
                    'stiffness_N_per_mm': stiffness
                }

        results['config'] = config
        results['log_file'] = str(log_path)

        return results
