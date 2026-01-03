"""
Hysteresis Loop Test

Measure backlash by approaching target positions from both directions.
Quantifies combined gearbox and tendon stretch/creep.
"""

import time
import numpy as np
from pathlib import Path
from datetime import datetime
from .base_test import BaseTest


class HysteresisTest(BaseTest):
    """
    Hysteresis Loop Test.

    Procedure:
    1. For each target position:
        a. Approach from below (lower position first)
        b. Measure actual position
        c. Approach from above (higher position first)
        d. Measure actual position
    2. Calculate backlash (difference between approaches)
    3. Generate hysteresis plot
    """

    def get_name(self) -> str:
        return "Hysteresis Loop Test"

    def get_description(self) -> str:
        return ("Measure backlash by approaching positions from both directions. "
                "Quantifies gearbox backlash + tendon stretch/creep.")

    def get_parameters(self) -> dict:
        return {
            'position_min': {
                'type': 'int',
                'default': 0,
                'unit': 'counts',
                'min': 0,
                'max': 10000,
                'description': 'Minimum test position'
            },
            'position_max': {
                'type': 'int',
                'default': 10000,
                'unit': 'counts',
                'min': 0,
                'max': 10000,
                'description': 'Maximum test position'
            },
            'test_points': {
                'type': 'int',
                'default': 10,
                'min': 3,
                'max': 50,
                'description': 'Number of positions to test'
            },
            'approach_offset': {
                'type': 'int',
                'default': 500,
                'unit': 'counts',
                'min': 100,
                'max': 2000,
                'description': 'Distance to approach from'
            },
            'settling_time_s': {
                'type': 'float',
                'default': 1.0,
                'unit': 's',
                'min': 0.5,
                'max': 5,
                'description': 'Settling time at each position'
            }
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        if config['position_max'] <= config['position_min']:
            return False, "Max position must be greater than min position"

        if config['test_points'] < 3:
            return False, "Need at least 3 test points"

        if config['approach_offset'] <= 0:
            return False, "Approach offset must be positive"

        return True, ""

    def estimate_duration(self, config: dict) -> float:
        """Estimate test duration."""
        points = config['test_points']
        settling = config['settling_time_s']

        # Each point: approach from below + settle + approach from above + settle
        duration = points * (settling * 3)  # 2 approaches + 1 return

        return duration

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute hysteresis test."""
        self.is_running = True
        self.stop_requested = False

        # Initialize results
        results = {
            'target_position': [],
            'position_from_below': [],
            'position_from_above': [],
            'backlash': [],
            'force_tendon': [],
            'timestamp': []
        }

        # Start data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"hysteresis_{timestamp}.csv"

        headers = list(results.keys())
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'hysteresis',
            'config': config
        })

        try:
            # Generate test positions
            positions = np.linspace(
                config['position_min'],
                config['position_max'],
                config['test_points'],
                dtype=int
            )

            offset = config['approach_offset']
            settling = config['settling_time_s']

            self._update_progress(progress_callback, 0, "Starting hysteresis test...")

            for i, target in enumerate(positions):
                if self._check_stop():
                    break

                self._wait_while_paused()

                # Approach from below
                approach_low = max(0, target - offset)
                self.hw['teensy'].set_position(approach_low)
                time.sleep(settling)

                self.hw['teensy'].set_position(target)
                time.sleep(settling)

                data_low = self.hw['teensy'].get_sensors()
                pos_from_below = data_low['position'] if data_low else 0

                # Approach from above
                approach_high = min(10000, target + offset)
                self.hw['teensy'].set_position(approach_high)
                time.sleep(settling)

                self.hw['teensy'].set_position(target)
                time.sleep(settling)

                data_high = self.hw['teensy'].get_sensors()
                pos_from_above = data_high['position'] if data_high else 0

                # Calculate backlash
                backlash = abs(pos_from_above - pos_from_below)

                # Store results
                results['target_position'].append(target)
                results['position_from_below'].append(pos_from_below)
                results['position_from_above'].append(pos_from_above)
                results['backlash'].append(backlash)
                results['force_tendon'].append(data_high['force_tendon'] / 1000.0 if data_high else 0)
                results['timestamp'].append(time.time())

                # Log to file
                self.logger.log({
                    'target_position': target,
                    'position_from_below': pos_from_below,
                    'position_from_above': pos_from_above,
                    'backlash': backlash,
                    'force_tendon': data_high['force_tendon'] / 1000.0 if data_high else 0
                })

                # Update progress
                progress = ((i + 1) / len(positions)) * 100
                self._update_progress(progress_callback, progress,
                                    f"Position {i+1}/{len(positions)}: Backlash = {backlash} counts")

            # Return to start
            self.hw['teensy'].set_position(config['position_min'])
            self._update_progress(progress_callback, 100, "Test complete")

        except Exception as e:
            print(f"Test error: {e}")
            results['error'] = str(e)

        finally:
            self.logger.stop_logging()
            self.is_running = False

        # Add summary
        if results['backlash']:
            results['summary'] = {
                'avg_backlash': np.mean(results['backlash']),
                'max_backlash': np.max(results['backlash']),
                'min_backlash': np.min(results['backlash'])
            }

        results['config'] = config
        results['log_file'] = str(log_path)

        return results
