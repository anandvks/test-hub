"""
Calibration Tab

Sensor calibration workflows for load cells and encoders.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from hardware.load_cell import LoadCellReader
from hardware.encoder import EncoderReader


class CalibrationTab(ttk.Frame):
    """Calibration interface for all sensors."""

    def __init__(self, parent, teensy):
        super().__init__(parent)

        self.teensy = teensy

        # Create load cell readers
        self.load_cell_tendon = LoadCellReader("load_cell_tendon")
        self.load_cell_tip = LoadCellReader("load_cell_tip")

        # Create encoder reader
        self.encoder_joint = EncoderReader("encoder_finger_joint")

        self._create_widgets()
        self._update_displays()

    def _create_widgets(self):
        """Create calibration widgets."""
        # Main layout: left tendon, middle tip, right encoder
        tendon_frame = ttk.Frame(self)
        tendon_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tip_frame = ttk.Frame(self)
        tip_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        encoder_frame = ttk.Frame(self)
        encoder_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tendon Load Cell
        self._create_load_cell_panel(
            tendon_frame, "Tendon Load Cell", self.load_cell_tendon,
            "tendon_status", "tendon_reading"
        )

        # Tip Load Cell
        self._create_load_cell_panel(
            tip_frame, "Fingertip Load Cell", self.load_cell_tip,
            "tip_status", "tip_reading"
        )

        # Joint Encoder
        self._create_encoder_panel(encoder_frame)

    def _create_load_cell_panel(self, parent, title, load_cell, status_key, reading_key):
        """Create load cell calibration panel."""
        panel = ttk.LabelFrame(parent, text=title, padding=10)
        panel.pack(fill=tk.BOTH, expand=True)

        # Status display
        status_frame = ttk.LabelFrame(panel, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        info = load_cell.get_calibration_info()

        if info['is_calibrated']:
            status_text = f"✓ Calibrated"
            status_color = "green"
        else:
            status_text = "⚠ Not Calibrated"
            status_color = "orange"

        status_label = ttk.Label(status_frame, text=status_text, foreground=status_color,
                                font=("Arial", 12, "bold"))
        status_label.pack()

        # Store reference for updates
        setattr(self, status_key, status_label)

        # Calibration info
        info_text = f"Zero Offset: {info['zero_offset']} counts\n"
        info_text += f"Factor: {info['calibration_factor']:.6f} N/count\n"
        if info['calibration_date']:
            info_text += f"Date: {info['calibration_date'][:10]}"

        ttk.Label(status_frame, text=info_text, justify=tk.LEFT).pack(pady=5)

        # Current reading
        reading_frame = ttk.LabelFrame(panel, text="Current Reading", padding=10)
        reading_frame.pack(fill=tk.X, pady=5)

        reading_label = ttk.Label(reading_frame, text="0.00 N", font=("Arial", 14))
        reading_label.pack()

        # Store reference for updates
        setattr(self, reading_key, reading_label)

        # Calibration procedure
        proc_frame = ttk.LabelFrame(panel, text="Calibration Procedure", padding=10)
        proc_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(proc_frame, text="Step 1: Remove all load", justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Button(proc_frame, text="Zero Sensor",
                  command=lambda: self._zero_load_cell(load_cell, reading_key)).pack(fill=tk.X, pady=2)

        ttk.Separator(proc_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(proc_frame, text="Step 2: Apply known weight", justify=tk.LEFT).pack(anchor=tk.W)

        weight_frame = ttk.Frame(proc_frame)
        weight_frame.pack(fill=tk.X, pady=2)

        ttk.Label(weight_frame, text="Weight (kg):").pack(side=tk.LEFT)
        weight_var = tk.DoubleVar(value=1.0)
        ttk.Entry(weight_frame, textvariable=weight_var, width=10).pack(side=tk.LEFT, padx=5)

        # Store weight variable
        setattr(self, f"{status_key}_weight", weight_var)

        ttk.Button(proc_frame, text="Calibrate with Known Weight",
                  command=lambda: self._calibrate_load_cell(load_cell, weight_var, status_key)).pack(fill=tk.X, pady=2)

        ttk.Separator(proc_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(proc_frame, text="Step 3: Test accuracy", justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Button(proc_frame, text="Test with Known Weight",
                  command=lambda: self._test_load_cell(load_cell, weight_var)).pack(fill=tk.X, pady=2)

    def _create_encoder_panel(self, parent):
        """Create encoder calibration panel."""
        panel = ttk.LabelFrame(parent, text="Joint Encoder (AS5600)", padding=10)
        panel.pack(fill=tk.BOTH, expand=True)

        # Status display
        status_frame = ttk.LabelFrame(panel, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)

        info = self.encoder_joint.get_calibration_info()

        if info['is_calibrated']:
            status_text = f"✓ Calibrated"
            status_color = "green"
        else:
            status_text = "⚠ Not Calibrated"
            status_color = "orange"

        self.encoder_status = ttk.Label(status_frame, text=status_text, foreground=status_color,
                                       font=("Arial", 12, "bold"))
        self.encoder_status.pack()

        info_text = f"Zero Position: {info['zero_position']} counts\n"
        info_text += f"Resolution: {info['counts_per_revolution']} counts/rev\n"
        if info['calibration_date']:
            info_text += f"Date: {info['calibration_date'][:10]}"

        ttk.Label(status_frame, text=info_text, justify=tk.LEFT).pack(pady=5)

        # Current reading
        reading_frame = ttk.LabelFrame(panel, text="Current Reading", padding=10)
        reading_frame.pack(fill=tk.X, pady=5)

        self.encoder_reading = ttk.Label(reading_frame, text="0.0°", font=("Arial", 14))
        self.encoder_reading.pack()

        # Calibration procedure
        proc_frame = ttk.LabelFrame(panel, text="Calibration Procedure", padding=10)
        proc_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(proc_frame,
                 text="Move finger to reference position\n(e.g., fully extended)",
                 justify=tk.LEFT).pack(anchor=tk.W, pady=5)

        ttk.Button(proc_frame, text="Set Zero Position",
                  command=self._zero_encoder).pack(fill=tk.X, pady=2)

        ttk.Separator(proc_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(proc_frame, text="Test full range:", justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Button(proc_frame, text="Test Range of Motion",
                  command=self._test_encoder_range).pack(fill=tk.X, pady=2)

    # Load Cell Methods

    def _zero_load_cell(self, load_cell, reading_key):
        """Zero load cell."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            # Read current sensor value
            data = self.teensy.get_sensors()
            if data:
                # Determine which sensor
                if load_cell.sensor_id == "load_cell_tendon":
                    raw_value = data['force_tendon']
                else:
                    raw_value = data['force_tip']

                # Set zero
                load_cell.zero(raw_value)
                load_cell.save_calibration()

                messagebox.showinfo("Success", f"Zero offset set to {raw_value} counts")
                self._update_displays()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to zero sensor: {str(e)}")

    def _calibrate_load_cell(self, load_cell, weight_var, status_key):
        """Calibrate load cell with known weight."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        weight_kg = weight_var.get()
        if weight_kg <= 0:
            messagebox.showerror("Error", "Weight must be positive")
            return

        try:
            # Read current sensor value
            data = self.teensy.get_sensors()
            if data:
                # Determine which sensor
                if load_cell.sensor_id == "load_cell_tendon":
                    raw_value = data['force_tendon']
                else:
                    raw_value = data['force_tip']

                # Calibrate
                load_cell.calibrate(raw_value, weight_kg)
                load_cell.save_calibration()

                messagebox.showinfo("Success",
                                  f"Calibrated with {weight_kg} kg\n"
                                  f"Factor: {load_cell.calibration_factor:.6f} N/count")
                self._update_displays()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Calibration failed: {str(e)}")

    def _test_load_cell(self, load_cell, weight_var):
        """Test load cell accuracy."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        if not load_cell.is_calibrated():
            messagebox.showerror("Error", "Sensor not calibrated")
            return

        weight_kg = weight_var.get()
        if weight_kg <= 0:
            messagebox.showerror("Error", "Weight must be positive")
            return

        try:
            # Read current sensor value
            data = self.teensy.get_sensors()
            if data:
                # Determine which sensor
                if load_cell.sensor_id == "load_cell_tendon":
                    raw_value = data['force_tendon']
                else:
                    raw_value = data['force_tip']

                # Test
                measured_kg, error_percent = load_cell.test_calibration(raw_value, weight_kg)

                result = f"Expected: {weight_kg:.2f} kg\n"
                result += f"Measured: {measured_kg:.2f} kg\n"
                result += f"Error: {error_percent:.1f}%\n\n"

                if error_percent < 5:
                    result += "✓ Calibration OK (< 5% error)"
                    messagebox.showinfo("Test Result", result)
                else:
                    result += "⚠ High error - consider recalibration"
                    messagebox.showwarning("Test Result", result)

        except Exception as e:
            messagebox.showerror("Error", f"Test failed: {str(e)}")

    # Encoder Methods

    def _zero_encoder(self):
        """Set encoder zero position."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        try:
            # Read current encoder value
            data = self.teensy.get_sensors()
            if data:
                raw_value = data['angle_joint']

                # Set zero
                self.encoder_joint.set_zero(raw_value)
                self.encoder_joint.save_calibration()

                messagebox.showinfo("Success", f"Zero position set to {raw_value} counts")
                self._update_displays()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to set zero: {str(e)}")

    def _test_encoder_range(self):
        """Test encoder range of motion."""
        if not self.teensy.connected:
            messagebox.showerror("Error", "Not connected to Teensy")
            return

        if not self.encoder_joint.is_calibrated():
            messagebox.showerror("Error", "Encoder not calibrated")
            return

        result = messagebox.askquestion("Range Test",
                                       "Move finger through full range.\n"
                                       "Click Yes when at minimum position.")

        if result != 'yes':
            return

        # Read minimum
        data_min = self.teensy.get_sensors()
        if not data_min:
            return

        result = messagebox.askquestion("Range Test",
                                       "Now move to maximum position.\n"
                                       "Click Yes when ready.")

        if result != 'yes':
            return

        # Read maximum
        data_max = self.teensy.get_sensors()
        if not data_max:
            return

        # Calculate range
        angle_min, angle_max, range_deg = self.encoder_joint.test_range(
            data_min['angle_joint'], data_max['angle_joint']
        )

        result = f"Minimum: {angle_min:.1f}°\n"
        result += f"Maximum: {angle_max:.1f}°\n"
        result += f"Range: {range_deg:.1f}°\n"

        messagebox.showinfo("Range Test Result", result)

    # Update Methods

    def _update_displays(self):
        """Update all status displays."""
        # Tendon load cell
        info = self.load_cell_tendon.get_calibration_info()
        if info['is_calibrated']:
            self.tendon_status.config(text="✓ Calibrated", foreground="green")
        else:
            self.tendon_status.config(text="⚠ Not Calibrated", foreground="orange")

        # Tip load cell
        info = self.load_cell_tip.get_calibration_info()
        if info['is_calibrated']:
            self.tip_status.config(text="✓ Calibrated", foreground="green")
        else:
            self.tip_status.config(text="⚠ Not Calibrated", foreground="orange")

        # Encoder
        info = self.encoder_joint.get_calibration_info()
        if info['is_calibrated']:
            self.encoder_status.config(text="✓ Calibrated", foreground="green")
        else:
            self.encoder_status.config(text="⚠ Not Calibrated", foreground="orange")

        # Start live reading updates
        self._update_readings()

    def _update_readings(self):
        """Update live sensor readings."""
        if self.teensy.connected:
            try:
                data = self.teensy.get_sensors()
                if data:
                    # Tendon force
                    force_tendon = self.load_cell_tendon.convert_to_force(data['force_tendon'])
                    self.tendon_reading.config(text=f"{force_tendon:.2f} N")

                    # Tip force
                    force_tip = self.load_cell_tip.convert_to_force(data['force_tip'])
                    self.tip_reading.config(text=f"{force_tip:.2f} N")

                    # Joint angle
                    angle = self.encoder_joint.convert_to_angle(data['angle_joint'])
                    self.encoder_reading.config(text=f"{angle:.1f}°")

            except Exception as e:
                pass  # Silently handle errors

        # Schedule next update
        self.after(100, self._update_readings)  # 10 Hz
