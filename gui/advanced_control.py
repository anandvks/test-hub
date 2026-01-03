"""
Advanced Motor Control Panel

PID tuning, motion profiles, and automated cycle testing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import time
import threading


class AdvancedControlPanel(ttk.LabelFrame):
    """Advanced motor control features."""

    def __init__(self, parent, teensy, logger):
        super().__init__(parent, text="Advanced Controls", padding=10)

        self.teensy = teensy
        self.logger = logger

        self.pid_params = {
            'kp': tk.DoubleVar(value=1.0),
            'ki': tk.DoubleVar(value=0.1),
            'kd': tk.DoubleVar(value=0.01)
        }

        self.motion_params = {
            'max_velocity': tk.IntVar(value=500),       # RPM
            'acceleration': tk.IntVar(value=1000),      # RPM/s
            'deceleration': tk.IntVar(value=1000),      # RPM/s
            'jerk_limit': tk.IntVar(value=5000)         # RPM/s²
        }

        self.cycle_params = {
            'num_cycles': tk.IntVar(value=10),
            'pos_start': tk.IntVar(value=0),
            'pos_end': tk.IntVar(value=5000),
            'dwell_start': tk.DoubleVar(value=0.5),     # seconds
            'dwell_end': tk.DoubleVar(value=0.5),       # seconds
            'cycle_delay': tk.DoubleVar(value=0.1)      # seconds between cycles
        }

        self.cycle_running = False
        self.cycle_thread = None

        self._create_widgets()

    def _create_widgets(self):
        """Create advanced control widgets."""
        # Create notebook for sub-sections
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # PID Tuning Tab
        self._create_pid_tab()

        # Motion Profile Tab
        self._create_motion_tab()

        # Cycle Test Tab
        self._create_cycle_tab()

    def _create_pid_tab(self):
        """Create PID tuning controls."""
        pid_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(pid_frame, text="PID Tuning")

        # PID Parameters
        params_frame = ttk.LabelFrame(pid_frame, text="PID Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=5)

        # Kp
        ttk.Label(params_frame, text="Kp (Proportional):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.pid_params['kp'], width=10).grid(row=0, column=1, padx=5)
        ttk.Scale(params_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                 variable=self.pid_params['kp']).grid(row=0, column=2, sticky=tk.EW, padx=5)

        # Ki
        ttk.Label(params_frame, text="Ki (Integral):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.pid_params['ki'], width=10).grid(row=1, column=1, padx=5)
        ttk.Scale(params_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                 variable=self.pid_params['ki']).grid(row=1, column=2, sticky=tk.EW, padx=5)

        # Kd
        ttk.Label(params_frame, text="Kd (Derivative):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.pid_params['kd'], width=10).grid(row=2, column=1, padx=5)
        ttk.Scale(params_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                 variable=self.pid_params['kd']).grid(row=2, column=2, sticky=tk.EW, padx=5)

        params_frame.columnconfigure(2, weight=1)

        # Preset buttons
        preset_frame = ttk.LabelFrame(pid_frame, text="Presets", padding=10)
        preset_frame.pack(fill=tk.X, pady=5)

        ttk.Button(preset_frame, text="Conservative",
                  command=lambda: self._apply_pid_preset(1.0, 0.05, 0.01)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Moderate",
                  command=lambda: self._apply_pid_preset(2.0, 0.1, 0.05)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Aggressive",
                  command=lambda: self._apply_pid_preset(5.0, 0.5, 0.1)).pack(side=tk.LEFT, padx=2)

        # Control buttons
        control_frame = ttk.Frame(pid_frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(control_frame, text="Apply to Teensy",
                  command=self._apply_pid).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Read from Teensy",
                  command=self._read_pid).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Preset",
                  command=self._save_pid_preset).pack(side=tk.LEFT, padx=5)

        # Info
        info_text = (
            "PID Controller Tuning:\n\n"
            "• Kp: Proportional gain - higher = faster response, may overshoot\n"
            "• Ki: Integral gain - eliminates steady-state error\n"
            "• Kd: Derivative gain - dampens oscillations\n\n"
            "Start with conservative values and increase gradually."
        )
        info_label = ttk.Label(pid_frame, text=info_text, justify=tk.LEFT,
                              foreground="gray", font=("Arial", 9))
        info_label.pack(fill=tk.X, pady=10)

    def _create_motion_tab(self):
        """Create motion profile controls."""
        motion_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(motion_frame, text="Motion Profile")

        # Motion parameters
        params_frame = ttk.LabelFrame(motion_frame, text="Motion Limits", padding=10)
        params_frame.pack(fill=tk.X, pady=5)

        # Max Velocity
        ttk.Label(params_frame, text="Max Velocity (RPM):").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.motion_params['max_velocity'], width=10).grid(row=0, column=1, padx=5)
        ttk.Scale(params_frame, from_=0, to=1000, orient=tk.HORIZONTAL,
                 variable=self.motion_params['max_velocity']).grid(row=0, column=2, sticky=tk.EW, padx=5)

        # Acceleration
        ttk.Label(params_frame, text="Acceleration (RPM/s):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.motion_params['acceleration'], width=10).grid(row=1, column=1, padx=5)
        ttk.Scale(params_frame, from_=100, to=5000, orient=tk.HORIZONTAL,
                 variable=self.motion_params['acceleration']).grid(row=1, column=2, sticky=tk.EW, padx=5)

        # Deceleration
        ttk.Label(params_frame, text="Deceleration (RPM/s):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.motion_params['deceleration'], width=10).grid(row=2, column=1, padx=5)
        ttk.Scale(params_frame, from_=100, to=5000, orient=tk.HORIZONTAL,
                 variable=self.motion_params['deceleration']).grid(row=2, column=2, sticky=tk.EW, padx=5)

        # Jerk Limit
        ttk.Label(params_frame, text="Jerk Limit (RPM/s²):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.motion_params['jerk_limit'], width=10).grid(row=3, column=1, padx=5)
        ttk.Scale(params_frame, from_=1000, to=10000, orient=tk.HORIZONTAL,
                 variable=self.motion_params['jerk_limit']).grid(row=3, column=2, sticky=tk.EW, padx=5)

        params_frame.columnconfigure(2, weight=1)

        # Control buttons
        control_frame = ttk.Frame(motion_frame)
        control_frame.pack(fill=tk.X, pady=10)

        ttk.Button(control_frame, text="Apply Motion Profile",
                  command=self._apply_motion_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Read Current Profile",
                  command=self._read_motion_profile).pack(side=tk.LEFT, padx=5)

        # Profile visualization (placeholder)
        viz_frame = ttk.LabelFrame(motion_frame, text="Profile Preview", padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(viz_frame, text="Velocity profile visualization\n(Coming soon)",
                 foreground="gray").pack(expand=True)

    def _create_cycle_tab(self):
        """Create cycle test controls."""
        cycle_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(cycle_frame, text="Cycle Test")

        # Cycle parameters
        params_frame = ttk.LabelFrame(cycle_frame, text="Cycle Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=5)

        # Number of cycles
        ttk.Label(params_frame, text="Number of Cycles:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['num_cycles'], width=10).grid(row=0, column=1, padx=5)

        # Start position
        ttk.Label(params_frame, text="Start Position (counts):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['pos_start'], width=10).grid(row=1, column=1, padx=5)

        # End position
        ttk.Label(params_frame, text="End Position (counts):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['pos_end'], width=10).grid(row=2, column=1, padx=5)

        # Dwell at start
        ttk.Label(params_frame, text="Dwell at Start (s):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['dwell_start'], width=10).grid(row=3, column=1, padx=5)

        # Dwell at end
        ttk.Label(params_frame, text="Dwell at End (s):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['dwell_end'], width=10).grid(row=4, column=1, padx=5)

        # Cycle delay
        ttk.Label(params_frame, text="Inter-Cycle Delay (s):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(params_frame, textvariable=self.cycle_params['cycle_delay'], width=10).grid(row=5, column=1, padx=5)

        # Status
        status_frame = ttk.LabelFrame(cycle_frame, text="Cycle Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        self.cycle_status_label = ttk.Label(status_frame, text="Ready", foreground="green")
        self.cycle_status_label.pack()

        self.cycle_progress = ttk.Progressbar(status_frame, mode='determinate')
        self.cycle_progress.pack(fill=tk.X, pady=5)

        self.cycle_info_label = ttk.Label(status_frame, text="", foreground="gray")
        self.cycle_info_label.pack()

        # Control buttons
        control_frame = ttk.Frame(cycle_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.start_cycle_btn = ttk.Button(control_frame, text="▶ Start Cycle Test",
                                         command=self._start_cycle_test)
        self.start_cycle_btn.pack(side=tk.LEFT, padx=5)

        self.stop_cycle_btn = ttk.Button(control_frame, text="⏹ Stop",
                                        command=self._stop_cycle_test, state=tk.DISABLED)
        self.stop_cycle_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Save Config",
                  command=self._save_cycle_config).pack(side=tk.LEFT, padx=5)

    # PID Control Methods

    def _apply_pid_preset(self, kp, ki, kd):
        """Apply PID preset values."""
        self.pid_params['kp'].set(kp)
        self.pid_params['ki'].set(ki)
        self.pid_params['kd'].set(kd)

    def _apply_pid(self):
        """Send PID parameters to Teensy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            kp = self.pid_params['kp'].get()
            ki = self.pid_params['ki'].get()
            kd = self.pid_params['kd'].get()

            # Send PID parameters (Teensy firmware needs to implement this)
            success = self.teensy.set_pid_params(kp, ki, kd)

            if success:
                messagebox.showinfo("Success", f"PID parameters applied:\nKp={kp}, Ki={ki}, Kd={kd}")
            else:
                messagebox.showerror("Error", "Failed to apply PID parameters")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply PID: {str(e)}")

    def _read_pid(self):
        """Read PID parameters from Teensy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            params = self.teensy.get_pid_params()
            if params:
                self.pid_params['kp'].set(params['kp'])
                self.pid_params['ki'].set(params['ki'])
                self.pid_params['kd'].set(params['kd'])
                messagebox.showinfo("Success", "PID parameters read from Teensy")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read PID: {str(e)}")

    def _save_pid_preset(self):
        """Save current PID parameters to file."""
        import json
        preset = {
            'kp': self.pid_params['kp'].get(),
            'ki': self.pid_params['ki'].get(),
            'kd': self.pid_params['kd'].get()
        }

        preset_file = Path("data/pid_preset.json")
        preset_file.parent.mkdir(parents=True, exist_ok=True)

        with open(preset_file, 'w') as f:
            json.dump(preset, f, indent=2)

        messagebox.showinfo("Saved", f"PID preset saved to {preset_file}")

    # Motion Profile Methods

    def _apply_motion_profile(self):
        """Send motion profile to Teensy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            profile = {
                'max_velocity': self.motion_params['max_velocity'].get(),
                'acceleration': self.motion_params['acceleration'].get(),
                'deceleration': self.motion_params['deceleration'].get(),
                'jerk_limit': self.motion_params['jerk_limit'].get()
            }

            success = self.teensy.set_motion_profile(profile)

            if success:
                messagebox.showinfo("Success", "Motion profile applied")
            else:
                messagebox.showerror("Error", "Failed to apply motion profile")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply profile: {str(e)}")

    def _read_motion_profile(self):
        """Read motion profile from Teensy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            profile = self.teensy.get_motion_profile()
            if profile:
                self.motion_params['max_velocity'].set(profile['max_velocity'])
                self.motion_params['acceleration'].set(profile['acceleration'])
                self.motion_params['deceleration'].set(profile['deceleration'])
                self.motion_params['jerk_limit'].set(profile['jerk_limit'])
                messagebox.showinfo("Success", "Motion profile read from Teensy")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read profile: {str(e)}")

    # Cycle Test Methods

    def _start_cycle_test(self):
        """Start automated cycle test."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        if self.cycle_running:
            messagebox.showwarning("Warning", "Cycle test already running")
            return

        # Validate parameters
        num_cycles = self.cycle_params['num_cycles'].get()
        if num_cycles < 1:
            messagebox.showerror("Error", "Number of cycles must be >= 1")
            return

        # Start cycle test in background thread
        self.cycle_running = True
        self.start_cycle_btn.config(state=tk.DISABLED)
        self.stop_cycle_btn.config(state=tk.NORMAL)

        self.cycle_thread = threading.Thread(target=self._run_cycle_test)
        self.cycle_thread.daemon = True
        self.cycle_thread.start()

    def _stop_cycle_test(self):
        """Stop cycle test."""
        self.cycle_running = False
        self.cycle_status_label.config(text="Stopping...", foreground="orange")

    def _run_cycle_test(self):
        """Execute cycle test (runs in background thread)."""
        try:
            num_cycles = self.cycle_params['num_cycles'].get()
            pos_start = self.cycle_params['pos_start'].get()
            pos_end = self.cycle_params['pos_end'].get()
            dwell_start = self.cycle_params['dwell_start'].get()
            dwell_end = self.cycle_params['dwell_end'].get()
            cycle_delay = self.cycle_params['cycle_delay'].get()

            # Start data logging
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = Path("data/sessions") / f"cycle_test_{timestamp}.csv"

            headers = ['cycle', 'timestamp', 'position', 'velocity', 'current',
                      'force_tendon', 'force_tip', 'angle_joint']
            self.logger.start_logging(log_path, headers, metadata={
                'test_type': 'cycle_test',
                'num_cycles': num_cycles,
                'pos_start': pos_start,
                'pos_end': pos_end
            })

            for cycle in range(num_cycles):
                if not self.cycle_running:
                    break

                # Update status
                self._update_cycle_status(
                    f"Cycle {cycle + 1}/{num_cycles}",
                    (cycle / num_cycles) * 100,
                    f"Moving to start position..."
                )

                # Move to start position
                self.teensy.set_position(pos_start)
                time.sleep(dwell_start)

                # Log data
                data = self.teensy.get_sensors()
                if data:
                    data['cycle'] = cycle
                    self.logger.log(data)

                # Move to end position
                self._update_cycle_status(
                    f"Cycle {cycle + 1}/{num_cycles}",
                    ((cycle + 0.5) / num_cycles) * 100,
                    f"Moving to end position..."
                )

                self.teensy.set_position(pos_end)
                time.sleep(dwell_end)

                # Log data
                data = self.teensy.get_sensors()
                if data:
                    data['cycle'] = cycle
                    self.logger.log(data)

                # Inter-cycle delay
                time.sleep(cycle_delay)

            # Finish
            self.logger.stop_logging()
            self._update_cycle_status("Completed", 100, f"{num_cycles} cycles finished")
            messagebox.showinfo("Success", f"Cycle test completed!\nData saved to {log_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Cycle test failed: {str(e)}")
            self._update_cycle_status("Error", 0, str(e))

        finally:
            self.cycle_running = False
            self.start_cycle_btn.config(state=tk.NORMAL)
            self.stop_cycle_btn.config(state=tk.DISABLED)

    def _update_cycle_status(self, status, progress, info):
        """Update cycle test status (thread-safe)."""
        self.cycle_status_label.config(text=status)
        self.cycle_progress['value'] = progress
        self.cycle_info_label.config(text=info)

    def _save_cycle_config(self):
        """Save cycle test configuration."""
        import json
        config = {
            'num_cycles': self.cycle_params['num_cycles'].get(),
            'pos_start': self.cycle_params['pos_start'].get(),
            'pos_end': self.cycle_params['pos_end'].get(),
            'dwell_start': self.cycle_params['dwell_start'].get(),
            'dwell_end': self.cycle_params['dwell_end'].get(),
            'cycle_delay': self.cycle_params['cycle_delay'].get()
        }

        config_file = Path("data/cycle_config.json")
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        messagebox.showinfo("Saved", f"Cycle config saved to {config_file}")
