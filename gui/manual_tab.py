"""
Manual Control Tab

Interface for manual motor control and live sensor monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque
from pathlib import Path
from .advanced_control import AdvancedControlPanel


class ManualControlTab(ttk.Frame):
    """Manual motor control with live plotting."""

    def __init__(self, parent, teensy, safety_monitor, data_logger, serial_finder):
        super().__init__(parent)

        self.teensy = teensy
        self.safety = safety_monitor
        self.logger = data_logger
        self.serial_finder = serial_finder

        self.connected = False
        self.motor_enabled = False
        self.control_mode = tk.StringVar(value="position")
        self.target_value = tk.DoubleVar(value=0)

        # Plot data buffers (30 seconds at 10Hz = 300 points)
        self.plot_buffer_size = 300
        self.time_data = deque(maxlen=self.plot_buffer_size)
        self.position_data = deque(maxlen=self.plot_buffer_size)
        self.force_tendon_data = deque(maxlen=self.plot_buffer_size)
        self.force_tip_data = deque(maxlen=self.plot_buffer_size)
        self.current_data = deque(maxlen=self.plot_buffer_size)
        self.plot_start_time = 0

        self._create_widgets()
        self._setup_plots()
        self._start_update_loop()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main layout: left controls + right plots
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Connection panel
        conn_frame = ttk.LabelFrame(control_frame, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            conn_frame, textvariable=self.port_var, width=20
        )
        self.port_combo.grid(row=0, column=1, padx=5)

        ttk.Button(
            conn_frame, text="Refresh", command=self._refresh_ports
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            conn_frame, text="Connect", command=self._connect
        ).grid(row=1, column=0, columnspan=3, pady=5, sticky=tk.EW)

        # Motor control panel
        motor_frame = ttk.LabelFrame(control_frame, text="Motor Control", padding=10)
        motor_frame.pack(fill=tk.X, pady=5)

        ttk.Label(motor_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W)
        modes = [
            ("Position", "position"),
            ("Velocity", "velocity"),
            ("Torque", "torque"),
            ("Current", "current")
        ]
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(
                motor_frame, text=text, variable=self.control_mode,
                value=value, command=self._update_control_mode
            ).grid(row=i, column=1, sticky=tk.W)

        ttk.Label(motor_frame, text="Target:").grid(row=4, column=0, sticky=tk.W)
        self.target_entry = ttk.Entry(motor_frame, textvariable=self.target_value, width=10)
        self.target_entry.grid(row=4, column=1, padx=5)

        self.unit_label = ttk.Label(motor_frame, text="counts")
        self.unit_label.grid(row=4, column=2, sticky=tk.W)

        self.target_slider = ttk.Scale(
            motor_frame, from_=0, to=10000, orient=tk.HORIZONTAL,
            variable=self.target_value, command=self._slider_changed
        )
        self.target_slider.grid(row=5, column=0, columnspan=3, sticky=tk.EW, pady=5)

        ttk.Button(
            motor_frame, text="Enable Motor", command=self._enable_motor
        ).grid(row=6, column=0, columnspan=2, pady=5, sticky=tk.EW)

        ttk.Button(
            motor_frame, text="Disable Motor", command=self._disable_motor
        ).grid(row=7, column=0, columnspan=2, pady=5, sticky=tk.EW)

        ttk.Button(
            motor_frame, text="🛑 EMERGENCY STOP", command=self._emergency_stop,
            style="Danger.TButton"
        ).grid(row=8, column=0, columnspan=3, pady=10, sticky=tk.EW)

        # Live sensor readings
        sensor_frame = ttk.LabelFrame(control_frame, text="Live Sensors", padding=10)
        sensor_frame.pack(fill=tk.X, pady=5)

        self.sensor_labels = {}
        sensors = [
            ('position', 'Position:', 'counts'),
            ('velocity', 'Velocity:', 'RPM'),
            ('current', 'Current:', 'A'),
            ('force_tendon', 'Tendon Force:', 'N'),
            ('force_tip', 'Tip Force:', 'N'),
            ('angle', 'Joint Angle:', '°')
        ]

        for i, (key, label, unit) in enumerate(sensors):
            ttk.Label(sensor_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            self.sensor_labels[key] = ttk.Label(sensor_frame, text=f"0 {unit}")
            self.sensor_labels[key].grid(row=i, column=1, sticky=tk.W, padx=5)

        # Logging controls
        log_frame = ttk.LabelFrame(control_frame, text="Data Logging", padding=10)
        log_frame.pack(fill=tk.X, pady=5)

        self.log_button = ttk.Button(
            log_frame, text="Start Logging", command=self._toggle_logging
        )
        self.log_button.pack(fill=tk.X)

        # Advanced controls
        self.advanced_panel = AdvancedControlPanel(control_frame, self.teensy, self.logger)
        self.advanced_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        # Store plot frame reference
        self.plot_container = plot_frame

    def _setup_plots(self):
        """Setup matplotlib plots."""
        self.fig = Figure(figsize=(8, 6))

        # Three stacked subplots
        self.ax_position = self.fig.add_subplot(311)
        self.ax_force = self.fig.add_subplot(312)
        self.ax_current = self.fig.add_subplot(313)

        # Position plot
        self.ax_position.set_ylabel('Position (counts)')
        self.ax_position.grid(True, alpha=0.3)
        self.line_position, = self.ax_position.plot([], [], 'b-', label='Motor')

        # Force plot
        self.ax_force.set_ylabel('Force (N)')
        self.ax_force.grid(True, alpha=0.3)
        self.line_force_tendon, = self.ax_force.plot([], [], 'r-', label='Tendon')
        self.line_force_tip, = self.ax_force.plot([], [], 'g-', label='Tip')
        self.ax_force.legend(loc='upper right')

        # Current plot
        self.ax_current.set_xlabel('Time (s)')
        self.ax_current.set_ylabel('Current (A)')
        self.ax_current.grid(True, alpha=0.3)
        self.line_current, = self.ax_current.plot([], [], 'orange')

        self.fig.tight_layout()

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _refresh_ports(self):
        """Refresh available serial ports."""
        ports = self.serial_finder.find_serial_ports()
        port_list = [f"{port} - {desc}" for port, desc in ports]
        self.port_combo['values'] = port_list

        # Auto-select Teensy if found
        teensy_port = self.serial_finder.find_teensy_port()
        if teensy_port:
            for item in port_list:
                if teensy_port in item:
                    self.port_var.set(item)
                    break

    def _connect(self):
        """Connect to Teensy."""
        if self.connected:
            self.teensy.disconnect()
            self.connected = False
            messagebox.showinfo("Disconnected", "Disconnected from Teensy")
            return

        port_str = self.port_var.get()
        if not port_str:
            messagebox.showerror("Error", "Please select a port")
            return

        # Extract port from "PORT - Description" format
        port = port_str.split(' - ')[0]

        if self.teensy.connect(port):
            self.connected = True
            self.safety.start_monitoring()
            messagebox.showinfo("Connected", f"Connected to {port}")
        else:
            messagebox.showerror("Error", "Failed to connect to Teensy")

    def _update_control_mode(self):
        """Update UI when control mode changes."""
        mode = self.control_mode.get()

        if mode == "position":
            self.unit_label.config(text="counts")
            self.target_slider.config(from_=0, to=10000)
        elif mode == "velocity":
            self.unit_label.config(text="RPM")
            self.target_slider.config(from_=-1000, to=1000)
        elif mode == "torque":
            self.unit_label.config(text="mNm")
            self.target_slider.config(from_=0, to=3000)
        elif mode == "current":
            self.unit_label.config(text="mA")
            self.target_slider.config(from_=0, to=1000)

    def _slider_changed(self, value):
        """Handle slider movement."""
        if not self.motor_enabled:
            return

        self._send_motor_command()

    def _send_motor_command(self):
        """Send motor command based on current mode and target."""
        if not self.connected or not self.motor_enabled:
            return

        mode = self.control_mode.get()
        value = int(self.target_value.get())

        try:
            if mode == "position":
                self.teensy.set_position(value)
            elif mode == "velocity":
                self.teensy.set_velocity(value)
            elif mode == "torque":
                self.teensy.set_torque(value)
            elif mode == "current":
                self.teensy.set_current(value)
        except ValueError as e:
            messagebox.showerror("Safety Limit", str(e))

    def _enable_motor(self):
        """Enable motor driver."""
        if not self.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        if self.teensy.enable():
            self.motor_enabled = True
            messagebox.showinfo("Motor Enabled", "Motor driver enabled")
        else:
            messagebox.showerror("Error", "Failed to enable motor")

    def _disable_motor(self):
        """Disable motor driver."""
        if self.teensy.disable():
            self.motor_enabled = False
            messagebox.showinfo("Motor Disabled", "Motor driver disabled")

    def _emergency_stop(self):
        """Trigger emergency stop."""
        if self.teensy.emergency_stop():
            self.motor_enabled = False
            messagebox.showwarning("Emergency Stop", "Motor stopped immediately")

    def _toggle_logging(self):
        """Start/stop data logging."""
        if self.logger.is_active():
            self.logger.stop_logging()
            self.log_button.config(text="Start Logging")
        else:
            # Create log file
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = Path("data/sessions") / f"manual_{timestamp}.csv"

            headers = [
                'timestamp', 'position', 'velocity', 'current',
                'force_tendon', 'force_tip', 'angle_joint'
            ]

            self.logger.start_logging(log_path, headers)
            self.log_button.config(text="Stop Logging")

    def _update_loop(self):
        """Update loop for reading sensors and updating plots."""
        if self.connected:
            try:
                # Read sensors
                data = self.teensy.get_sensors()

                if data:
                    # Update sensor labels
                    self.sensor_labels['position'].config(
                        text=f"{data['position']} counts"
                    )
                    self.sensor_labels['velocity'].config(
                        text=f"{data['velocity']} RPM"
                    )
                    self.sensor_labels['current'].config(
                        text=f"{data['current'] / 1000:.2f} A"
                    )
                    self.sensor_labels['force_tendon'].config(
                        text=f"{data['force_tendon'] / 1000:.1f} N"
                    )
                    self.sensor_labels['force_tip'].config(
                        text=f"{data['force_tip'] / 1000:.1f} N"
                    )
                    self.sensor_labels['angle'].config(
                        text=f"{data['angle_joint'] / 100:.1f}°"
                    )

                    # Log data
                    if self.logger.is_active():
                        self.logger.log(data)

                    # Update plot buffers
                    import time
                    if not self.time_data:
                        self.plot_start_time = time.time()

                    self.time_data.append(time.time() - self.plot_start_time)
                    self.position_data.append(data['position'])
                    self.force_tendon_data.append(data['force_tendon'] / 1000)
                    self.force_tip_data.append(data['force_tip'] / 1000)
                    self.current_data.append(data['current'] / 1000)

                    # Update plots
                    self._update_plots()

            except Exception as e:
                print(f"Update error: {e}")

        # Schedule next update
        self.after(100, self._update_loop)  # 10 Hz

    def _update_plots(self):
        """Update live plots."""
        if not self.time_data:
            return

        time_array = np.array(self.time_data)

        # Update position plot
        self.line_position.set_data(time_array, np.array(self.position_data))
        self.ax_position.relim()
        self.ax_position.autoscale_view()

        # Update force plot
        self.line_force_tendon.set_data(time_array, np.array(self.force_tendon_data))
        self.line_force_tip.set_data(time_array, np.array(self.force_tip_data))
        self.ax_force.relim()
        self.ax_force.autoscale_view()

        # Update current plot
        self.line_current.set_data(time_array, np.array(self.current_data))
        self.ax_current.relim()
        self.ax_current.autoscale_view()

        self.canvas.draw_idle()

    def _start_update_loop(self):
        """Start the update loop."""
        # Populate ports on startup
        self._refresh_ports()

        # Start update loop
        self.after(100, self._update_loop)
