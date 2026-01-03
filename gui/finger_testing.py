"""
Finger Testing Tab

Specialized tests for robotic finger mechanisms: range of motion, grip force, precision.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time
from datetime import datetime


class FingerTestingTab(ttk.Frame):
    """Finger-specific testing interface."""

    def __init__(self, parent, teensy, logger):
        super().__init__(parent)

        self.teensy = teensy
        self.logger = logger

        self.test_running = False
        self.test_thread = None

        # Finger configuration
        self.finger_config = {
            'num_joints': tk.IntVar(value=3),
            'tendon_routing': tk.StringVar(value="direct"),  # direct, force-doubling
            'spool_radius': tk.DoubleVar(value=10.0)  # mm
        }

        self._create_widgets()

    def _create_widgets(self):
        """Create finger testing widgets."""
        # Main layout
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        results_frame = ttk.Frame(self)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Finger Configuration
        config_frame = ttk.LabelFrame(control_frame, text="Finger Configuration", padding=10)
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="Number of Joints:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(config_frame, textvariable=self.finger_config['num_joints'],
                    values=[1, 2, 3, 4], width=8, state='readonly').grid(row=0, column=1)

        ttk.Label(config_frame, text="Routing Type:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(config_frame, textvariable=self.finger_config['tendon_routing'],
                    values=["direct", "force-doubling", "differential"], width=15,
                    state='readonly').grid(row=1, column=1)

        ttk.Label(config_frame, text="Spool Radius (mm):").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(config_frame, textvariable=self.finger_config['spool_radius'],
                 width=10).grid(row=2, column=1)

        # Test selection
        test_select_frame = ttk.LabelFrame(control_frame, text="Finger Tests", padding=10)
        test_select_frame.pack(fill=tk.X, pady=5)

        ttk.Button(test_select_frame, text="Range of Motion Test",
                  command=self._run_rom_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Fingertip Force Test",
                  command=self._run_force_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Grip Strength Test",
                  command=self._run_grip_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Precision Grasp Test",
                  command=self._run_precision_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Power Grasp Test",
                  command=self._run_power_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Repeatability Test",
                  command=self._run_repeatability_test, width=25).pack(pady=2)

        # Test Parameters
        params_frame = ttk.LabelFrame(control_frame, text="Test Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=5)

        ttk.Label(params_frame, text="Target Force (N):").grid(row=0, column=0, sticky=tk.W)
        self.target_force = tk.DoubleVar(value=5.0)
        ttk.Entry(params_frame, textvariable=self.target_force, width=10).grid(row=0, column=1)

        ttk.Label(params_frame, text="Test Repetitions:").grid(row=1, column=0, sticky=tk.W)
        self.test_reps = tk.IntVar(value=10)
        ttk.Entry(params_frame, textvariable=self.test_reps, width=10).grid(row=1, column=1)

        # Test Status
        status_frame = ttk.LabelFrame(control_frame, text="Test Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.status_label.pack()

        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.info_label = ttk.Label(status_frame, text="", foreground="gray")
        self.info_label.pack()

        self.stop_btn = ttk.Button(status_frame, text="⏹ Stop Test",
                                   command=self._stop_test, state=tk.DISABLED)
        self.stop_btn.pack(pady=5)

        # Results display
        results_text_frame = ttk.LabelFrame(results_frame, text="Test Results", padding=10)
        results_text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = tk.Text(results_text_frame, height=25, width=60)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(results_text_frame, command=self.results_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)

    # Range of Motion Test

    def _run_rom_test(self):
        """
        Range of Motion Test: Measure full flexion/extension range.

        Validates mechanical limits and encoder calibration.
        """
        if not self._check_connection():
            return

        self._start_test("Range of Motion Test", self._rom_test_worker)

    def _rom_test_worker(self):
        """Execute ROM test."""
        self._log_result("=== RANGE OF MOTION TEST ===\n\n")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"finger_rom_{timestamp}.csv"

        headers = ['direction', 'position', 'angle_joint', 'force_tendon']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'finger_rom',
            'num_joints': self.finger_config['num_joints'].get()
        })

        # Extend fully
        self._update_status("Extending to limit", 25)
        self._log_result("Extending finger to full extension...\n")

        self.teensy.set_position(0)
        time.sleep(2)

        data = self.teensy.get_sensors()
        if data:
            pos_extended = data['position']
            angle_extended = data['angle_joint'] / 100.0  # Convert to degrees
            self._log_result(f"  Extended position: {pos_extended} counts, Angle: {angle_extended:.1f}°\n")

            self.logger.log({
                'direction': 'extended',
                'position': pos_extended,
                'angle_joint': angle_extended,
                'force_tendon': data['force_tendon'] / 1000.0
            })

        # Flex fully (with force limit)
        self._update_status("Flexing to limit", 75)
        self._log_result("\nFlexing finger to full flexion...\n")

        self.teensy.set_torque(2000)  # Apply torque until limit
        time.sleep(3)

        data = self.teensy.get_sensors()
        if data:
            pos_flexed = data['position']
            angle_flexed = data['angle_joint'] / 100.0
            self._log_result(f"  Flexed position: {pos_flexed} counts, Angle: {angle_flexed:.1f}°\n")

            self.logger.log({
                'direction': 'flexed',
                'position': pos_flexed,
                'angle_joint': angle_flexed,
                'force_tendon': data['force_tendon'] / 1000.0
            })

        # Calculate ROM
        rom = abs(pos_flexed - pos_extended)
        angle_rom = abs(angle_flexed - angle_extended)

        self._log_result(f"\n✓ Range of Motion:\n")
        self._log_result(f"  Motor: {rom} counts\n")
        self._log_result(f"  Joint: {angle_rom:.1f}°\n")

        self.teensy.set_torque(0)
        self.logger.stop_logging()
        self._log_result(f"\nData saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Fingertip Force Test

    def _run_force_test(self):
        """
        Fingertip Force Test: Measure maximum achievable tip force.

        Validates 1.2kg per-finger target.
        """
        if not self._check_connection():
            return

        self._start_test("Fingertip Force Test", self._force_test_worker)

    def _force_test_worker(self):
        """Execute force test."""
        self._log_result("=== FINGERTIP FORCE TEST ===\n")
        self._log_result(f"Target: {self.target_force.get()} N (1.2 kg = 11.8 N)\n\n")

        target = self.target_force.get()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"finger_force_{timestamp}.csv"

        headers = ['torque_cmd', 'current', 'force_tip', 'efficiency']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'finger_force',
            'target_force': target
        })

        # Ramp up torque until target force reached
        max_torque = 3000  # mNm
        steps = 20

        for i in range(steps + 1):
            if not self.test_running:
                break

            torque = int((i / steps) * max_torque)
            self._update_status(f"Applying {torque} mNm", (i / steps) * 100)

            self.teensy.set_torque(torque)
            time.sleep(0.5)

            data = self.teensy.get_sensors()
            if data:
                current = data['current'] / 1000.0
                force_tip = data['force_tip'] / 1000.0

                # Calculate efficiency
                power_elec = current * 24  # V * A
                power_mech = force_tip * 0.001  # Simplified
                efficiency = (power_mech / power_elec * 100) if power_elec > 0 else 0

                self.logger.log({
                    'torque_cmd': torque,
                    'current': current,
                    'force_tip': force_tip,
                    'efficiency': efficiency
                })

                self._log_result(f"Torque: {torque} mNm → Force: {force_tip:.2f} N, Current: {current:.2f} A\n")

                if force_tip >= target:
                    self._log_result(f"\n✓ Target force {target}N achieved!\n")
                    break

        self.teensy.set_torque(0)
        self.logger.stop_logging()
        self._log_result(f"\nData saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Grip Strength Test

    def _run_grip_test(self):
        """
        Grip Strength Test: Measure sustained grip force.
        """
        if not self._check_connection():
            return

        self._start_test("Grip Strength Test", self._grip_test_worker)

    def _grip_test_worker(self):
        """Execute grip test."""
        self._log_result("=== GRIP STRENGTH TEST ===\n\n")

        force = self.target_force.get()
        duration = 30  # seconds

        self._log_result(f"Target Force: {force} N\n")
        self._log_result(f"Duration: {duration} seconds\n\n")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"finger_grip_{timestamp}.csv"

        headers = ['time_sec', 'force_tip', 'current', 'position']
        self.logger.start_logging(log_path, headers)

        # Apply grip force
        torque_cmd = int(force * 10)  # Convert to torque
        self.teensy.set_torque(torque_cmd)

        start_time = time.time()
        self._log_result("Applying grip force...\n\n")

        while self.test_running:
            elapsed = time.time() - start_time
            if elapsed >= duration:
                break

            data = self.teensy.get_sensors()
            if data:
                force_tip = data['force_tip'] / 1000.0
                current = data['current'] / 1000.0

                self.logger.log({
                    'time_sec': elapsed,
                    'force_tip': force_tip,
                    'current': current,
                    'position': data['position']
                })

                if int(elapsed) % 5 == 0:
                    self._log_result(f"T+{int(elapsed)}s: Force = {force_tip:.2f} N\n")

            self._update_status("Holding grip", (elapsed / duration) * 100)
            time.sleep(0.1)

        self.teensy.set_torque(0)
        self.logger.stop_logging()
        self._log_result(f"\n✓ Grip test complete!\nData saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Precision Grasp Test

    def _run_precision_test(self):
        """
        Precision Grasp Test: Test low-force controlled grasping.
        """
        if not self._check_connection():
            return

        self._start_test("Precision Grasp Test", self._precision_test_worker)

    def _precision_test_worker(self):
        """Execute precision grasp test."""
        self._log_result("=== PRECISION GRASP TEST ===\n\n")
        self._log_result("Testing controlled low-force grasping (0.5 - 2.0 N)\n\n")

        forces = [0.5, 1.0, 1.5, 2.0]  # N

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"finger_precision_{timestamp}.csv"

        headers = ['target_force', 'achieved_force', 'error', 'overshoot']
        self.logger.start_logging(log_path, headers)

        for i, target in enumerate(forces):
            if not self.test_running:
                break

            self._update_status(f"Testing {target}N", (i / len(forces)) * 100)
            self._log_result(f"Target: {target} N\n")

            torque = int(target * 10)
            self.teensy.set_torque(torque)
            time.sleep(1)

            data = self.teensy.get_sensors()
            if data:
                achieved = data['force_tip'] / 1000.0
                error = abs(achieved - target)
                overshoot = max(0, achieved - target)

                self.logger.log({
                    'target_force': target,
                    'achieved_force': achieved,
                    'error': error,
                    'overshoot': overshoot
                })

                self._log_result(f"  Achieved: {achieved:.2f} N, Error: {error:.2f} N\n")

        self.teensy.set_torque(0)
        self.logger.stop_logging()
        self._log_result(f"\n✓ Test complete!\nData saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Power Grasp Test

    def _run_power_test(self):
        """
        Power Grasp Test: Test maximum force grasping.
        """
        if not self._check_connection():
            return

        self._start_test("Power Grasp Test", self._power_test_worker)

    def _power_test_worker(self):
        """Execute power grasp test."""
        self._log_result("=== POWER GRASP TEST ===\n\n")
        self._log_result("Testing maximum force capability\n\n")

        # Ramp to max force
        max_torque = 3000
        self.teensy.set_torque(max_torque)

        time.sleep(2)

        data = self.teensy.get_sensors()
        if data:
            max_force = data['force_tip'] / 1000.0
            current = data['current'] / 1000.0

            self._log_result(f"Maximum Force: {max_force:.2f} N ({max_force/9.81:.2f} kg)\n")
            self._log_result(f"Current Draw: {current:.2f} A\n")

            if max_force >= 11.8:  # 1.2 kg target
                self._log_result(f"\n✓ PASS: Exceeds 1.2kg target!\n")
            else:
                self._log_result(f"\n⚠ FAIL: Below 1.2kg target\n")

        self.teensy.set_torque(0)
        self._update_status("Completed", 100)

    # Repeatability Test

    def _run_repeatability_test(self):
        """
        Repeatability Test: Measure position/force consistency over multiple trials.
        """
        if not self._check_connection():
            return

        self._start_test("Repeatability Test", self._repeatability_test_worker)

    def _repeatability_test_worker(self):
        """Execute repeatability test."""
        self._log_result("=== REPEATABILITY TEST ===\n\n")

        reps = self.test_reps.get()
        target_pos = 5000

        self._log_result(f"Repetitions: {reps}\n")
        self._log_result(f"Target Position: {target_pos} counts\n\n")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"finger_repeatability_{timestamp}.csv"

        headers = ['trial', 'target_pos', 'actual_pos', 'error']
        self.logger.start_logging(log_path, headers)

        positions = []

        for i in range(reps):
            if not self.test_running:
                break

            self._update_status(f"Trial {i+1}/{reps}", (i / reps) * 100)

            # Reset
            self.teensy.set_position(0)
            time.sleep(0.5)

            # Move to target
            self.teensy.set_position(target_pos)
            time.sleep(1)

            data = self.teensy.get_sensors()
            if data:
                actual = data['position']
                error = abs(actual - target_pos)
                positions.append(actual)

                self.logger.log({
                    'trial': i + 1,
                    'target_pos': target_pos,
                    'actual_pos': actual,
                    'error': error
                })

                self._log_result(f"Trial {i+1}: {actual} counts (error: {error})\n")

        # Calculate statistics
        if positions:
            import statistics
            mean = statistics.mean(positions)
            stdev = statistics.stdev(positions) if len(positions) > 1 else 0

            self._log_result(f"\n--- Statistics ---\n")
            self._log_result(f"Mean: {mean:.1f} counts\n")
            self._log_result(f"Std Dev: {stdev:.1f} counts\n")
            self._log_result(f"Repeatability: ±{stdev:.1f} counts\n")

        self.teensy.set_position(0)
        self.logger.stop_logging()
        self._log_result(f"\nData saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Helper Methods

    def _check_connection(self):
        """Check if connected to Teensy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return False
        return True

    def _start_test(self, name, worker_func):
        """Start a test in background thread."""
        if self.test_running:
            messagebox.showwarning("Warning", "Test already running")
            return

        self.test_running = True
        self.stop_btn.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)

        self.test_thread = threading.Thread(target=worker_func)
        self.test_thread.daemon = True
        self.test_thread.start()

    def _stop_test(self):
        """Stop running test."""
        self.test_running = False
        self.status_label.config(text="Stopping...", foreground="orange")

    def _update_status(self, status, progress=0, info=""):
        """Update test status display."""
        self.status_label.config(text=status)
        self.progress['value'] = progress
        self.info_label.config(text=info)

        if not self.test_running:
            self.stop_btn.config(state=tk.DISABLED)

    def _log_result(self, text):
        """Append text to results display."""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
