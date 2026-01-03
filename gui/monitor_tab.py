"""
Live Monitor Tab

Real-time monitoring and visualization during automated test execution.
Displays live plots and statistics in a 2x2 grid layout.
"""

import tkinter as tk
from tkinter import ttk
from .plot_widget import create_time_series_plot
from utils.units import format_force, format_current, format_efficiency


class MonitorTab(ttk.Frame):
    """Live monitoring tab for automated tests."""

    def __init__(self, parent, controller, data_logger):
        """
        Initialize monitor tab.

        Args:
            parent: Parent widget
            controller: Hardware controller instance
            data_logger: Data logger instance
        """
        super().__init__(parent)
        self.controller = controller
        self.data_logger = data_logger

        # Test state
        self.test_running = False
        self.current_test = None
        self.test_progress = 0.0

        # Statistics
        self.stats = {
            'samples': 0,
            'duration': 0.0,
            'avg_force': 0.0,
            'avg_current': 0.0,
            'max_force': 0.0,
            'max_current': 0.0
        }

        self._create_widgets()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container with two sections: plots and info
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Plots (2x2 grid)
        plot_frame = ttk.LabelFrame(main_frame, text="Live Plots", padding=10)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self._create_plots(plot_frame)

        # Right: Info panel
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        self._create_info_panel(info_frame)

    def _create_plots(self, parent):
        """Create 2x2 plot grid."""
        # Create notebook for multiple plot views
        self.plot_notebook = ttk.Notebook(parent)
        self.plot_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Time Series (3 channels)
        time_series_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(time_series_frame, text="Time Series")

        self.time_plot = create_time_series_plot(
            time_series_frame,
            num_channels=3,
            window_seconds=30,
            sample_rate=50
        )

        # Configure time series plots
        self.time_plot.configure_plot(0, ylabel='Position (counts)', title='Position vs Time')
        self.time_plot.add_line(0, 'position', label='Position', color='#2563eb')

        self.time_plot.configure_plot(1, ylabel='Force (N)', title='Force vs Time')
        self.time_plot.add_line(1, 'force_tendon', label='Tendon', color='#dc2626')
        self.time_plot.add_line(1, 'force_tip', label='Tip', color='#ea580c')

        self.time_plot.configure_plot(2, ylabel='Current (mA)', title='Current vs Time')
        self.time_plot.add_line(2, 'current', label='Motor Current', color='#16a34a')

        # Tab 2: Force vs Position (hysteresis)
        hysteresis_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(hysteresis_frame, text="Force-Position")

        self.hysteresis_plot = create_time_series_plot(
            hysteresis_frame,
            num_channels=1,
            window_seconds=60,
            sample_rate=50
        )

        self.hysteresis_plot.configure_plot(
            0,
            xlabel='Position (counts)',
            ylabel='Force (N)',
            title='Force vs Position (Hysteresis)'
        )
        self.hysteresis_plot.add_line(0, 'hysteresis', label='', color='#7c3aed',
                                      marker='o')

        # Tab 3: Efficiency
        efficiency_frame = ttk.Frame(self.plot_notebook)
        self.plot_notebook.add(efficiency_frame, text="Efficiency")

        self.efficiency_plot = create_time_series_plot(
            efficiency_frame,
            num_channels=1,
            window_seconds=60,
            sample_rate=10
        )

        self.efficiency_plot.configure_plot(
            0,
            xlabel='Time (s)',
            ylabel='Efficiency (%)',
            title='Transmission Efficiency'
        )
        self.efficiency_plot.add_line(0, 'efficiency', label='Efficiency',
                                      color='#0891b2')

    def _create_info_panel(self, parent):
        """Create information and statistics panel."""
        # Test info section
        test_frame = ttk.LabelFrame(parent, text="Test Information", padding=10)
        test_frame.pack(fill=tk.X, pady=(0, 10))

        # Test name
        ttk.Label(test_frame, text="Test:", font=('', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.test_name_label = ttk.Label(test_frame, text="None")
        self.test_name_label.grid(row=0, column=1, sticky=tk.W, pady=2)

        # Progress bar
        ttk.Label(test_frame, text="Progress:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.progress_bar = ttk.Progressbar(
            test_frame,
            mode='determinate',
            length=200
        )
        self.progress_bar.grid(row=1, column=1, sticky=tk.EW, pady=5)

        self.progress_label = ttk.Label(test_frame, text="0%")
        self.progress_label.grid(row=2, column=1, sticky=tk.W)

        # Statistics section
        stats_frame = ttk.LabelFrame(parent, text="Live Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True)

        # Create stat labels
        self.stat_labels = {}

        stat_definitions = [
            ('Samples:', 'samples', '0'),
            ('Duration:', 'duration', '0.0 s'),
            ('Avg Force:', 'avg_force', '0.0 N'),
            ('Max Force:', 'max_force', '0.0 N'),
            ('Avg Current:', 'avg_current', '0.0 mA'),
            ('Max Current:', 'max_current', '0.0 mA'),
        ]

        for i, (label_text, key, default) in enumerate(stat_definitions):
            ttk.Label(stats_frame, text=label_text, font=('', 9, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=3
            )
            value_label = ttk.Label(stats_frame, text=default, font=('', 9))
            value_label.grid(row=i, column=1, sticky=tk.W, pady=3, padx=(10, 0))
            self.stat_labels[key] = value_label

        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        self.pause_button = ttk.Button(
            control_frame,
            text="Pause",
            command=self.on_pause,
            state=tk.DISABLED
        )
        self.pause_button.pack(fill=tk.X, pady=2)

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Test",
            command=self.on_stop,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=2)

        self.clear_button = ttk.Button(
            control_frame,
            text="Clear Plots",
            command=self.clear_plots
        )
        self.clear_button.pack(fill=tk.X, pady=2)

    def start_monitoring(self, test_name):
        """
        Start monitoring a test.

        Args:
            test_name: Name of the test being run
        """
        self.test_running = True
        self.current_test = test_name
        self.test_progress = 0.0

        # Update UI
        self.test_name_label.config(text=test_name)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="0%")

        self.pause_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

        # Clear plots
        self.clear_plots()

        # Reset statistics
        self.stats = {
            'samples': 0,
            'duration': 0.0,
            'avg_force': 0.0,
            'avg_current': 0.0,
            'max_force': 0.0,
            'max_current': 0.0
        }

        # Enable auto-refresh
        self.time_plot.enable_auto_refresh(100)
        self.hysteresis_plot.enable_auto_refresh(200)
        self.efficiency_plot.enable_auto_refresh(500)

    def stop_monitoring(self):
        """Stop monitoring."""
        self.test_running = False
        self.current_test = None

        # Update UI
        self.pause_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)

        # Disable auto-refresh
        self.time_plot.disable_auto_refresh()
        self.hysteresis_plot.disable_auto_refresh()
        self.efficiency_plot.disable_auto_refresh()

    def update_data(self, sensor_data, timestamp=None):
        """
        Update plots with new sensor data.

        Args:
            sensor_data: Dict with sensor readings
            timestamp: Optional timestamp (uses sensor_data['timestamp'] if None)
        """
        if not self.test_running:
            return

        # Get timestamp
        if timestamp is None:
            timestamp = sensor_data.get('timestamp', 0) / 1000.0  # Convert ms to s

        # Extract values
        position = sensor_data.get('position', 0)
        force_tendon = sensor_data.get('force_tendon', 0) / 1000.0  # mN to N
        force_tip = sensor_data.get('force_tip', 0) / 1000.0  # mN to N
        current = sensor_data.get('current', 0)  # mA

        # Update time series plots
        self.time_plot.update_line(0, 'position', timestamp, position)
        self.time_plot.update_line(1, 'force_tendon', timestamp, force_tendon)
        self.time_plot.update_line(1, 'force_tip', timestamp, force_tip)
        self.time_plot.update_line(2, 'current', timestamp, current)

        # Update hysteresis plot
        self.hysteresis_plot.update_line(0, 'hysteresis', position, force_tip)

        # Update statistics
        self.stats['samples'] += 1
        self.stats['duration'] = timestamp

        # Running averages (exponential moving average)
        alpha = 0.1
        self.stats['avg_force'] = (1 - alpha) * self.stats['avg_force'] + alpha * force_tip
        self.stats['avg_current'] = (1 - alpha) * self.stats['avg_current'] + alpha * current

        # Max values
        self.stats['max_force'] = max(self.stats['max_force'], force_tip)
        self.stats['max_current'] = max(self.stats['max_current'], current)

        # Update stat labels
        self.stat_labels['samples'].config(text=f"{self.stats['samples']}")
        self.stat_labels['duration'].config(text=f"{self.stats['duration']:.1f} s")
        self.stat_labels['avg_force'].config(text=format_force(self.stats['avg_force'] * 1000, 'N'))
        self.stat_labels['max_force'].config(text=format_force(self.stats['max_force'] * 1000, 'N'))
        self.stat_labels['avg_current'].config(text=format_current(self.stats['avg_current'], 'mA'))
        self.stat_labels['max_current'].config(text=format_current(self.stats['max_current'], 'mA'))

    def update_progress(self, progress):
        """
        Update test progress.

        Args:
            progress: Progress as percentage (0-100)
        """
        self.test_progress = progress
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{progress:.1f}%")

    def update_efficiency(self, timestamp, efficiency):
        """
        Update efficiency plot.

        Args:
            timestamp: Time in seconds
            efficiency: Efficiency as decimal (0.0-1.0)
        """
        efficiency_percent = efficiency * 100.0
        self.efficiency_plot.update_line(0, 'efficiency', timestamp, efficiency_percent)

    def clear_plots(self):
        """Clear all plots."""
        self.time_plot.clear_all()
        self.hysteresis_plot.clear_all()
        self.efficiency_plot.clear_all()

    def on_pause(self):
        """Handle pause button click."""
        # To be implemented - pause current test
        pass

    def on_stop(self):
        """Handle stop button click."""
        # To be implemented - stop current test
        pass
