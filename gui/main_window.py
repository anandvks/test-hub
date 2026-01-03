"""
Main Window

Main application window with tabbed interface.
"""

import tkinter as tk
from tkinter import ttk
from .manual_tab import ManualControlTab
from .status_bar import SafetyStatusBar
from .tendon_testing import TendonTestingTab
from .finger_testing import FingerTestingTab
from .calibration_tab import CalibrationTab
from .library_tab import TestLibraryTab
from .monitor_tab import MonitorTab
from .review_tab import ReviewTab
from protocols.registry import TestRegistry


class MainWindow(tk.Tk):
    """Main application window."""

    def __init__(self, teensy, safety_monitor, data_logger, serial_finder):
        super().__init__()

        self.teensy = teensy
        self.safety = safety_monitor
        self.logger = data_logger
        self.serial_finder = serial_finder

        # Create test registry
        hardware_interface = {'teensy': teensy, 'safety': safety_monitor}
        self.test_registry = TestRegistry(hardware_interface, data_logger)

        self.title("Test Bench Control - Tendon-Driven Hand")
        self.geometry("1400x900")

        self._create_widgets()
        self._setup_safety_callbacks()
        self._start_status_update()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_widgets(self):
        """Create main window widgets."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.manual_tab = ManualControlTab(
            self.notebook, self.teensy, self.safety,
            self.logger, self.serial_finder
        )
        self.notebook.add(self.manual_tab, text="Manual Control")

        # Tendon Testing Tab
        self.tendon_tab = TendonTestingTab(
            self.notebook, self.teensy, self.logger
        )
        self.notebook.add(self.tendon_tab, text="Tendon Testing")

        # Finger Testing Tab
        self.finger_tab = FingerTestingTab(
            self.notebook, self.teensy, self.logger
        )
        self.notebook.add(self.finger_tab, text="Finger Testing")

        # Test Library Tab
        self.library_tab = TestLibraryTab(self.notebook, self.test_registry)
        self.notebook.add(self.library_tab, text="Test Library")

        # Live Monitor Tab
        self.monitor_tab = MonitorTab(self.notebook, self.teensy, self.logger)
        self.notebook.add(self.monitor_tab, text="Live Monitor")

        # Data Review Tab
        self.review_tab = ReviewTab(self.notebook)
        self.notebook.add(self.review_tab, text="Data Review")

        # Calibration Tab
        self.calibration_tab = CalibrationTab(self.notebook, self.teensy)
        self.notebook.add(self.calibration_tab, text="Calibration")

        # Status bar
        self.status_bar = SafetyStatusBar(self)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_safety_callbacks(self):
        """Setup safety violation callbacks."""
        self.safety.register_violation_callback(self._on_safety_violation)

    def _on_safety_violation(self, reason, sensor_data):
        """Handle safety violation."""
        from tkinter import messagebox

        message = f"EMERGENCY STOP\n\n{reason}\n\n"
        if sensor_data:
            message += "Sensor readings at violation:\n"
            message += f"  Current: {sensor_data.get('current', 0) / 1000:.2f} A\n"
            message += f"  Tendon Force: {sensor_data.get('force_tendon', 0) / 1000:.1f} N\n"
            message += f"  Tip Force: {sensor_data.get('force_tip', 0) / 1000:.1f} N\n"
            message += f"  Position: {sensor_data.get('position', 0)} counts\n"

        messagebox.showerror("Safety Violation", message)

    def _update_status_bar(self):
        """Update status bar with current motor and safety status."""
        # Update motor status
        self.status_bar.update_motor_status(
            connected=self.teensy.connected,
            enabled=self.manual_tab.motor_enabled if hasattr(self.manual_tab, 'motor_enabled') else False
        )

        # Update safety status if connected
        if self.teensy.connected:
            try:
                sensor_data = self.teensy.get_sensors()
                if sensor_data:
                    safety_status = self.safety.get_safety_status(sensor_data)
                    self.status_bar.update_safety_status(safety_status)
            except Exception as e:
                pass  # Silently handle errors in status updates

        # Schedule next update
        self.after(100, self._update_status_bar)  # 10 Hz

    def _start_status_update(self):
        """Start status bar update loop."""
        self.after(100, self._update_status_bar)

    def _on_closing(self):
        """Handle window close event."""
        # Stop monitoring and disconnect
        self.safety.stop_monitoring()
        self.logger.stop_logging()
        self.teensy.disconnect()

        # Destroy window
        self.destroy()
