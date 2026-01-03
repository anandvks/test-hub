"""
Endurance Cycling Test

Run thousands of flex-extend cycles to validate:
- Mechanical wear and drift
- Transmission efficiency degradation
- Tendon bedding-in and creep
- Motor/gearbox thermal stability
"""

import time
import numpy as np
from pathlib import Path
from datetime import datetime
from .base_test import BaseTest


class EnduranceTest(BaseTest):
    """
    Endurance Cycling Test.

    Procedure:
    1. Configure cycle parameters (positions, dwell times, repetitions)
    2. Run automated flex-extend cycles
    3. Monitor every cycle: position, force, current, efficiency
    4. Log every Nth cycle to reduce data volume
    5. Checkpoint every 100 cycles for resume capability
    6. Generate summary: cycle 1 vs final cycle comparison
    """

    def get_name(self) -> str:
        return "Endurance Cycling Test"

    def get_description(self) -> str:
        return ("Run thousands of flex-extend cycles to validate mechanical wear, "
                "efficiency degradation, and thermal stability.")

    def get_parameters(self) -> dict:
        return {
            'position_start': {
                'type': 'int',
                'default': 0,
                'unit': 'counts',
                'min': 0,
                'max': 10000,
                'description': 'Starting position (extended)'
            },
            'position_end': {
                'type': 'int',
                'default': 8000,
                'unit': 'counts',
                'min': 0,
                'max': 10000,
                'description': 'End position (flexed)'
            },
            'num_cycles': {
                'type': 'int',
                'default': 10000,
                'min': 100,
                'max': 50000,
                'description': 'Total number of cycles'
            },
            'dwell_start_s': {
                'type': 'float',
                'default': 0.5,
                'unit': 's',
                'min': 0,
                'max': 5,
                'description': 'Dwell time at start position'
            },
            'dwell_end_s': {
                'type': 'float',
                'default': 0.5,
                'unit': 's',
                'min': 0,
                'max': 5,
                'description': 'Dwell time at end position'
            },
            'log_interval': {
                'type': 'int',
                'default': 10,
                'min': 1,
                'max': 100,
                'description': 'Log every Nth cycle'
            },
            'checkpoint_interval': {
                'type': 'int',
                'default': 100,
                'min': 10,
                'max': 1000,
                'description': 'Checkpoint every Nth cycle'
            },
            'max_current_A': {
                'type': 'float',
                'default': 0.8,
                'unit': 'A',
                'min': 0.1,
                'max': 1.0,
                'description': 'Maximum allowed current'
            }
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        """Validate configuration."""
        if config['position_end'] <= config['position_start']:
            return False, "End position must be greater than start position"

        if config['num_cycles'] < 100:
            return False, "Need at least 100 cycles for meaningful endurance test"

        if config['max_current_A'] > 1.0:
            return False, "Current limit exceeds safe maximum (1.0A)"

        return True, ""

    def estimate_duration(self, config: dict) -> float:
        """Estimate test duration."""
        cycle_time = (config['dwell_start_s'] + config['dwell_end_s'] + 2.0)  # +2s for moves
        total_time = config['num_cycles'] * cycle_time
        return total_time

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute endurance test."""
        self.is_running = True
        self.stop_requested = False

        # Initialize results
        results = {
            'cycle': [],
            'timestamp': [],
            'position_start_actual': [],
            'position_end_actual': [],
            'position_error': [],
            'force_tip_start': [],
            'force_tip_end': [],
            'current_avg': [],
            'current_max': [],
            'power_avg_W': [],
            'efficiency_percent': []
        }

        # Start data logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"endurance_{timestamp}.csv"
        checkpoint_path = Path("data/sessions") / f"endurance_{timestamp}_checkpoint.json"

        headers = list(results.keys())
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'endurance',
            'config': config
        })

        # Cycle tracking
        pos_start = config['position_start']
        pos_end = config['position_end']
        num_cycles = config['num_cycles']
        log_interval = config['log_interval']
        checkpoint_interval = config['checkpoint_interval']

        # First cycle baseline
        first_cycle_data = None
        failure_reason = None

        try:
            self._update_progress(progress_callback, 0, "Starting endurance test...")

            for cycle in range(1, num_cycles + 1):
                if self._check_stop():
                    break

                self._wait_while_paused()

                cycle_start_time = time.time()

                # Move to start position
                self.hw['teensy'].set_position(pos_start)
                time.sleep(config['dwell_start_s'])

                data_start = self.hw['teensy'].get_sensors()
                if not data_start:
                    continue

                pos_start_actual = data_start['position']
                force_start = data_start['force_tip'] / 1000.0  # Convert to N
                current_start = data_start['current'] / 1000.0  # Convert to A

                # Move to end position
                self.hw['teensy'].set_position(pos_end)

                # Monitor current during movement
                current_samples = []
                power_samples = []
                move_duration = 0
                while move_duration < 2.0:  # Max 2s for move
                    data = self.hw['teensy'].get_sensors()
                    if data:
                        current_A = data['current'] / 1000.0
                        voltage_V = 24.0  # Assume 24V supply
                        power_W = current_A * voltage_V
                        current_samples.append(current_A)
                        power_samples.append(power_W)
                    time.sleep(0.05)
                    move_duration += 0.05

                time.sleep(config['dwell_end_s'])

                data_end = self.hw['teensy'].get_sensors()
                if not data_end:
                    continue

                pos_end_actual = data_end['position']
                force_end = data_end['force_tip'] / 1000.0
                current_end = data_end['current'] / 1000.0

                # Calculate metrics
                position_error = abs((pos_end_actual - pos_start_actual) - (pos_end - pos_start))
                current_avg = np.mean(current_samples) if current_samples else 0
                current_max = np.max(current_samples) if current_samples else 0
                power_avg = np.mean(power_samples) if power_samples else 0

                # Estimate efficiency (simplified)
                force_avg = (force_start + force_end) / 2
                displacement_m = abs(pos_end_actual - pos_start_actual) * 0.001  # Assume counts ~ mm
                mechanical_work_J = force_avg * displacement_m
                electrical_work_J = power_avg * move_duration
                efficiency = (mechanical_work_J / electrical_work_J * 100) if electrical_work_J > 0 else 0

                # Store cycle data
                cycle_data = {
                    'cycle': cycle,
                    'timestamp': time.time(),
                    'position_start_actual': pos_start_actual,
                    'position_end_actual': pos_end_actual,
                    'position_error': position_error,
                    'force_tip_start': force_start,
                    'force_tip_end': force_end,
                    'current_avg': current_avg,
                    'current_max': current_max,
                    'power_avg_W': power_avg,
                    'efficiency_percent': efficiency
                }

                # Save first cycle as baseline
                if cycle == 1:
                    first_cycle_data = cycle_data.copy()

                # Log every Nth cycle
                if cycle % log_interval == 0:
                    for key in results:
                        results[key].append(cycle_data[key])

                    self.logger.log(cycle_data)

                # Checkpoint every Nth cycle
                if cycle % checkpoint_interval == 0:
                    checkpoint_data = {
                        'cycle': cycle,
                        'timestamp': datetime.now().isoformat(),
                        'config': config,
                        'results_so_far': {k: v[-10:] for k, v in results.items()}  # Last 10 samples
                    }
                    import json
                    with open(checkpoint_path, 'w') as f:
                        json.dump(checkpoint_data, f, indent=2)

                    info = (f"Checkpoint {cycle}/{num_cycles}: "
                           f"Eff={efficiency:.1f}%, I={current_avg:.2f}A, Err={position_error} cts")
                    print(info)

                # Check for failures
                if current_max > config['max_current_A']:
                    failure_reason = f"Overcurrent at cycle {cycle}: {current_max:.2f}A"
                    self._update_progress(progress_callback, -1, f"FAIL: {failure_reason}")
                    break

                if position_error > 200:  # Excessive position error
                    failure_reason = f"Position error at cycle {cycle}: {position_error} counts"
                    self._update_progress(progress_callback, -1, f"WARNING: {failure_reason}")

                # Update progress
                progress = (cycle / num_cycles) * 100
                eta_seconds = (time.time() - cycle_start_time) * (num_cycles - cycle)
                eta_hours = eta_seconds / 3600
                self._update_progress(progress_callback, progress,
                                    f"Cycle {cycle}/{num_cycles} | ETA: {eta_hours:.1f}h")

            # Return to start position
            self.hw['teensy'].set_position(pos_start)
            self._update_progress(progress_callback, 100, "Endurance test complete")

        except Exception as e:
            print(f"Test error: {e}")
            results['error'] = str(e)
            failure_reason = str(e)

        finally:
            self.hw['teensy'].set_torque(0)
            self.logger.stop_logging()
            self.is_running = False

        # Calculate summary statistics
        if results['cycle'] and first_cycle_data:
            # Get final cycle data
            final_cycle_data = {
                'cycle': results['cycle'][-1],
                'position_error': results['position_error'][-1],
                'force_tip_start': results['force_tip_start'][-1],
                'force_tip_end': results['force_tip_end'][-1],
                'current_avg': results['current_avg'][-1],
                'efficiency_percent': results['efficiency_percent'][-1]
            }

            # Calculate degradation
            efficiency_degradation = first_cycle_data['efficiency_percent'] - final_cycle_data['efficiency_percent']
            force_degradation = first_cycle_data['force_tip_end'] - final_cycle_data['force_tip_end']
            current_increase = final_cycle_data['current_avg'] - first_cycle_data['current_avg']

            results['summary'] = {
                'total_cycles_completed': results['cycle'][-1],
                'test_duration_hours': (results['timestamp'][-1] - results['timestamp'][0]) / 3600 if len(results['timestamp']) > 1 else 0,
                'first_cycle': {
                    'efficiency_percent': first_cycle_data['efficiency_percent'],
                    'force_tip_N': first_cycle_data['force_tip_end'],
                    'current_avg_A': first_cycle_data['current_avg']
                },
                'final_cycle': {
                    'efficiency_percent': final_cycle_data['efficiency_percent'],
                    'force_tip_N': final_cycle_data['force_tip_end'],
                    'current_avg_A': final_cycle_data['current_avg']
                },
                'degradation': {
                    'efficiency_drop_percent': efficiency_degradation,
                    'force_loss_N': force_degradation,
                    'current_increase_A': current_increase
                },
                'avg_position_error': np.mean(results['position_error']),
                'max_position_error': np.max(results['position_error']),
                'avg_efficiency_percent': np.mean(results['efficiency_percent']),
                'failure_reason': failure_reason
            }

        results['config'] = config
        results['log_file'] = str(log_path)
        results['checkpoint_file'] = str(checkpoint_path)

        return results
