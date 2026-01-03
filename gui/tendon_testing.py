"""
Tendon Testing Tab

Specialized tests for tendon-driven systems: compliance, creep, friction, hysteresis.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import time
from datetime import datetime


class TendonTestingTab(ttk.Frame):
    """Tendon-specific testing interface."""

    def __init__(self, parent, teensy, logger):
        super().__init__(parent)

        self.teensy = teensy
        self.logger = logger

        self.test_running = False
        self.test_thread = None

        self._create_widgets()

    def _create_widgets(self):
        """Create tendon testing widgets."""
        # Main layout
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        results_frame = ttk.Frame(self)
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Test selection
        test_select_frame = ttk.LabelFrame(control_frame, text="Tendon Tests", padding=10)
        test_select_frame.pack(fill=tk.X, pady=5)

        ttk.Button(test_select_frame, text="Compliance Test",
                  command=self._run_compliance_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Creep Test (Long Duration)",
                  command=self._run_creep_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Friction Mapping",
                  command=self._run_friction_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Hysteresis Loop",
                  command=self._run_hysteresis_test, width=25).pack(pady=2)
        ttk.Button(test_select_frame, text="Break-In Cycling",
                  command=self._run_breakin_test, width=25).pack(pady=2)

        # Compliance Test Parameters
        compliance_frame = ttk.LabelFrame(control_frame, text="Compliance Test Config", padding=10)
        compliance_frame.pack(fill=tk.X, pady=5)

        ttk.Label(compliance_frame, text="Test Force (N):").grid(row=0, column=0, sticky=tk.W)
        self.compliance_force = tk.DoubleVar(value=10.0)
        ttk.Entry(compliance_frame, textvariable=self.compliance_force, width=10).grid(row=0, column=1)

        ttk.Label(compliance_frame, text="Measurement Points:").grid(row=1, column=0, sticky=tk.W)
        self.compliance_points = tk.IntVar(value=20)
        ttk.Entry(compliance_frame, textvariable=self.compliance_points, width=10).grid(row=1, column=1)

        # Creep Test Parameters
        creep_frame = ttk.LabelFrame(control_frame, text="Creep Test Config", padding=10)
        creep_frame.pack(fill=tk.X, pady=5)

        ttk.Label(creep_frame, text="Hold Force (N):").grid(row=0, column=0, sticky=tk.W)
        self.creep_force = tk.DoubleVar(value=5.0)
        ttk.Entry(creep_frame, textvariable=self.creep_force, width=10).grid(row=0, column=1)

        ttk.Label(creep_frame, text="Duration (minutes):").grid(row=1, column=0, sticky=tk.W)
        self.creep_duration = tk.IntVar(value=30)
        ttk.Entry(creep_frame, textvariable=self.creep_duration, width=10).grid(row=1, column=1)

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

    # Compliance Test

    def _run_compliance_test(self):
        """
        Compliance Test: Measure tendon elongation under increasing force.

        Tests Young's modulus and validates tendon stiffness.
        """
        if not self._check_connection():
            return

        self._start_test("Compliance Test", self._compliance_test_worker)

    def _compliance_test_worker(self):
        """Execute compliance test."""
        self._log_result("=== COMPLIANCE TEST ===\n")
        self._log_result(f"Test Force: {self.compliance_force.get()} N\n")
        self._log_result(f"Measurement Points: {self.compliance_points.get()}\n\n")

        force_max = self.compliance_force.get()
        points = self.compliance_points.get()

        # Start logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"tendon_compliance_{timestamp}.csv"

        headers = ['force_cmd', 'force_measured', 'position', 'elongation']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'tendon_compliance',
            'force_max': force_max
        })

        initial_pos = self.teensy.get_position()
        self._log_result(f"Initial Position: {initial_pos} counts\n\n")

        for i in range(points + 1):
            if not self.test_running:
                break

            force = (i / points) * force_max
            self._update_status(f"Testing {force:.1f}N", (i / points) * 100)

            # Apply force (convert to motor torque based on spool radius)
            # Assuming 10mm spool radius: Torque(mNm) = Force(N) * 10
            torque_cmd = int(force * 10)
            self.teensy.set_torque(torque_cmd)

            time.sleep(0.5)  # Settling time

            # Measure
            data = self.teensy.get_sensors()
            if data:
                pos = data['position']
                force_meas = data['force_tendon'] / 1000.0  # Convert to N
                elongation = pos - initial_pos

                self.logger.log({
                    'force_cmd': force,
                    'force_measured': force_meas,
                    'position': pos,
                    'elongation': elongation
                })

                self._log_result(f"Force: {force:.1f}N → Position: {pos}, Elongation: {elongation}\n")

        # Return to zero
        self.teensy.set_torque(0)

        self.logger.stop_logging()
        self._log_result(f"\n✓ Test complete! Data saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Creep Test

    def _run_creep_test(self):
        """
        Creep Test: Monitor tendon elongation over time under constant load.

        Validates long-term tendon stability.
        """
        if not self._check_connection():
            return

        duration_min = self.creep_duration.get()
        if messagebox.askyesno("Confirm",
                              f"Creep test will run for {duration_min} minutes.\nContinue?"):
            self._start_test("Creep Test", self._creep_test_worker)

    def _creep_test_worker(self):
        """Execute creep test."""
        self._log_result("=== CREEP TEST ===\n")
        self._log_result(f"Hold Force: {self.creep_force.get()} N\n")
        self._log_result(f"Duration: {self.creep_duration.get()} minutes\n\n")

        force = self.creep_force.get()
        duration_sec = self.creep_duration.get() * 60

        # Start logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"tendon_creep_{timestamp}.csv"

        headers = ['time_sec', 'position', 'force_tendon', 'temperature']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'tendon_creep',
            'hold_force': force,
            'duration_min': duration_sec / 60
        })

        # Apply force
        torque_cmd = int(force * 10)
        self.teensy.set_torque(torque_cmd)

        initial_pos = self.teensy.get_position()
        start_time = time.time()

        self._log_result(f"Applying {force}N force...\n\n")

        while self.test_running:
            elapsed = time.time() - start_time

            if elapsed >= duration_sec:
                break

            # Measure
            data = self.teensy.get_sensors()
            if data:
                pos = data['position']
                force_meas = data['force_tendon'] / 1000.0
                creep = pos - initial_pos

                self.logger.log({
                    'time_sec': elapsed,
                    'position': pos,
                    'force_tendon': force_meas,
                    'temperature': 0  # Placeholder
                })

                if int(elapsed) % 60 == 0:  # Log every minute
                    self._log_result(f"T+{int(elapsed/60)}min: Creep = {creep} counts\n")

            self._update_status(f"Running", (elapsed / duration_sec) * 100,
                               f"Time: {int(elapsed/60)}/{int(duration_sec/60)} min")

            time.sleep(1)  # Sample at 1 Hz

        # Return to zero
        self.teensy.set_torque(0)

        self.logger.stop_logging()
        self._log_result(f"\n✓ Test complete! Data saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Friction Test

    def _run_friction_test(self):
        """
        Friction Mapping: Measure friction at different positions/velocities.

        Identifies routing friction in tendon path.
        """
        if not self._check_connection():
            return

        self._start_test("Friction Test", self._friction_test_worker)

    def _friction_test_worker(self):
        """Execute friction mapping test."""
        self._log_result("=== FRICTION MAPPING TEST ===\n\n")

        velocities = [50, 100, 200, 500]  # RPM

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"tendon_friction_{timestamp}.csv"

        headers = ['velocity_cmd', 'current', 'force_tendon', 'friction_loss']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'tendon_friction'
        })

        for i, vel in enumerate(velocities):
            if not self.test_running:
                break

            self._update_status(f"Testing {vel} RPM", (i / len(velocities)) * 100)
            self._log_result(f"Velocity: {vel} RPM\n")

            self.teensy.set_velocity(vel)
            time.sleep(2)  # Settling

            # Measure current and force
            data = self.teensy.get_sensors()
            if data:
                current = data['current'] / 1000.0
                force = data['force_tendon'] / 1000.0

                # Friction loss estimation (simplified)
                friction = current * 24 - force * vel * 0.001  # Power balance

                self.logger.log({
                    'velocity_cmd': vel,
                    'current': current,
                    'force_tendon': force,
                    'friction_loss': friction
                })

                self._log_result(f"  Current: {current:.2f}A, Force: {force:.1f}N, Friction: {friction:.2f}W\n")

        self.teensy.set_velocity(0)
        self.logger.stop_logging()
        self._log_result(f"\n✓ Test complete! Data saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Hysteresis Test

    def _run_hysteresis_test(self):
        """
        Hysteresis Loop: Measure backlash from approaching position in both directions.
        """
        if not self._check_connection():
            return

        self._start_test("Hysteresis Test", self._hysteresis_test_worker)

    def _hysteresis_test_worker(self):
        """Execute hysteresis test."""
        self._log_result("=== HYSTERESIS LOOP TEST ===\n\n")

        positions = [0, 2500, 5000, 7500, 10000]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = Path("data/sessions") / f"tendon_hysteresis_{timestamp}.csv"

        headers = ['target_pos', 'direction', 'actual_pos', 'backlash']
        self.logger.start_logging(log_path, headers, metadata={
            'test_type': 'tendon_hysteresis'
        })

        for i, target in enumerate(positions):
            if not self.test_running:
                break

            self._update_status(f"Testing position {target}", (i / len(positions) / 2) * 100)

            # Approach from below
            self.teensy.set_position(target - 500)
            time.sleep(1)
            self.teensy.set_position(target)
            time.sleep(1)
            pos_up = self.teensy.get_position()

            # Approach from above
            self.teensy.set_position(target + 500)
            time.sleep(1)
            self.teensy.set_position(target)
            time.sleep(1)
            pos_down = self.teensy.get_position()

            backlash = abs(pos_down - pos_up)

            self.logger.log({'target_pos': target, 'direction': 'up', 'actual_pos': pos_up, 'backlash': backlash})
            self.logger.log({'target_pos': target, 'direction': 'down', 'actual_pos': pos_down, 'backlash': backlash})

            self._log_result(f"Position {target}: Backlash = {backlash} counts\n")

        self.logger.stop_logging()
        self._log_result(f"\n✓ Test complete! Data saved to {log_path}\n")
        self._update_status("Completed", 100)

    # Break-In Test

    def _run_breakin_test(self):
        """
        Break-In Cycling: Run cycles to seat the tendon before validation tests.
        """
        if not self._check_connection():
            return

        if messagebox.askyesno("Confirm", "Run 100 break-in cycles?\n(~5 minutes)"):
            self._start_test("Break-In Test", self._breakin_test_worker)

    def _breakin_test_worker(self):
        """Execute break-in cycling."""
        self._log_result("=== BREAK-IN CYCLING ===\n\n")

        num_cycles = 100

        for cycle in range(num_cycles):
            if not self.test_running:
                break

            self._update_status(f"Cycle {cycle + 1}/{num_cycles}", (cycle / num_cycles) * 100)

            self.teensy.set_position(0)
            time.sleep(0.5)
            self.teensy.set_position(5000)
            time.sleep(0.5)

            if (cycle + 1) % 10 == 0:
                self._log_result(f"Completed {cycle + 1} cycles\n")

        self._log_result("\n✓ Break-in complete!\n")
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
