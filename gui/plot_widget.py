"""
Reusable Plot Widget

Matplotlib-based plotting widget for embedding in tkinter GUI.
Provides live updating plots with customizable styling.
"""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from collections import deque
import numpy as np


class PlotWidget:
    """
    Reusable matplotlib plot widget for tkinter.

    Features:
    - Live updating plots
    - Rolling window support
    - Multiple subplots
    - Toolbar for zoom/pan/save
    - Customizable styling
    """

    def __init__(self, parent, num_plots=1, figsize=(8, 4), window_size=1000):
        """
        Initialize plot widget.

        Args:
            parent: Parent tkinter widget
            num_plots: Number of subplots (stacked vertically)
            figsize: Figure size (width, height) in inches
            window_size: Rolling window size (number of samples)
        """
        self.parent = parent
        self.num_plots = num_plots
        self.window_size = window_size

        # Create figure and subplots
        self.figure = Figure(figsize=figsize, dpi=100, facecolor='white')
        self.axes = []

        for i in range(num_plots):
            ax = self.figure.add_subplot(num_plots, 1, i + 1)
            ax.grid(True, alpha=0.3)
            ax.set_facecolor('#f8f9fa')
            self.axes.append(ax)

        self.figure.tight_layout(pad=2.0)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Add toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
        self.toolbar.update()

        # Data storage (rolling buffers)
        self.data_buffers = {}  # {plot_idx: {line_id: deque()}}
        for i in range(num_plots):
            self.data_buffers[i] = {}

        # Line objects for each plot
        self.lines = {}  # {plot_idx: {line_id: Line2D}}
        for i in range(num_plots):
            self.lines[i] = {}

        # Plot configuration
        self.plot_configs = {}  # {plot_idx: {'xlabel': ..., 'ylabel': ..., 'title': ...}}

    def configure_plot(self, plot_idx, xlabel='', ylabel='', title='',
                      xlim=None, ylim=None):
        """
        Configure plot appearance.

        Args:
            plot_idx: Index of subplot (0-based)
            xlabel: X-axis label
            ylabel: Y-axis label
            title: Plot title
            xlim: X-axis limits (tuple: (min, max))
            ylim: Y-axis limits (tuple: (min, max))
        """
        if plot_idx >= self.num_plots:
            return

        ax = self.axes[plot_idx]

        if xlabel:
            ax.set_xlabel(xlabel, fontsize=10)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=10)
        if title:
            ax.set_title(title, fontsize=11, fontweight='bold')
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)

        self.plot_configs[plot_idx] = {
            'xlabel': xlabel,
            'ylabel': ylabel,
            'title': title,
            'xlim': xlim,
            'ylim': ylim
        }

    def add_line(self, plot_idx, line_id, label='', color=None, linewidth=1.5,
                 linestyle='-', marker=''):
        """
        Add a line to a subplot.

        Args:
            plot_idx: Index of subplot
            line_id: Unique identifier for this line
            label: Legend label
            color: Line color
            linewidth: Line width
            linestyle: Line style ('-', '--', ':', '-.')
            marker: Marker style ('o', 's', '^', etc.)
        """
        if plot_idx >= self.num_plots:
            return

        ax = self.axes[plot_idx]

        # Create empty line
        line, = ax.plot([], [], label=label, color=color, linewidth=linewidth,
                       linestyle=linestyle, marker=marker, markersize=4)

        self.lines[plot_idx][line_id] = line
        self.data_buffers[plot_idx][line_id] = deque(maxlen=self.window_size)

        # Update legend if labels exist
        if label:
            ax.legend(loc='upper right', fontsize=9, framealpha=0.9)

    def update_line(self, plot_idx, line_id, x_data, y_data):
        """
        Update line data.

        Args:
            plot_idx: Index of subplot
            line_id: Line identifier
            x_data: X values (single value or list)
            y_data: Y values (single value or list)
        """
        if plot_idx not in self.lines or line_id not in self.lines[plot_idx]:
            return

        # Convert single values to lists
        if not isinstance(x_data, (list, tuple, np.ndarray)):
            x_data = [x_data]
        if not isinstance(y_data, (list, tuple, np.ndarray)):
            y_data = [y_data]

        # Append to buffer
        buffer = self.data_buffers[plot_idx][line_id]
        for x, y in zip(x_data, y_data):
            buffer.append((x, y))

        # Extract x and y arrays
        if len(buffer) > 0:
            x_array, y_array = zip(*buffer)
        else:
            x_array, y_array = [], []

        # Update line
        line = self.lines[plot_idx][line_id]
        line.set_data(x_array, y_array)

        # Auto-scale axes
        ax = self.axes[plot_idx]
        ax.relim()
        ax.autoscale_view()

    def clear_line(self, plot_idx, line_id):
        """Clear data from a specific line."""
        if plot_idx in self.data_buffers and line_id in self.data_buffers[plot_idx]:
            self.data_buffers[plot_idx][line_id].clear()

            if plot_idx in self.lines and line_id in self.lines[plot_idx]:
                self.lines[plot_idx][line_id].set_data([], [])

    def clear_plot(self, plot_idx):
        """Clear all lines in a subplot."""
        if plot_idx in self.data_buffers:
            for line_id in self.data_buffers[plot_idx]:
                self.data_buffers[plot_idx][line_id].clear()

        if plot_idx in self.lines:
            for line_id in self.lines[plot_idx]:
                self.lines[plot_idx][line_id].set_data([], [])

    def clear_all(self):
        """Clear all plots."""
        for plot_idx in range(self.num_plots):
            self.clear_plot(plot_idx)

    def refresh(self):
        """Redraw canvas."""
        self.canvas.draw_idle()

    def save_plot(self, filename):
        """
        Save plot to file.

        Args:
            filename: Output filename (PNG, PDF, SVG supported)
        """
        self.figure.savefig(filename, dpi=150, bbox_inches='tight')

    def set_window_size(self, window_size):
        """
        Change rolling window size.

        Args:
            window_size: New window size (number of samples)
        """
        self.window_size = window_size

        # Update all buffers
        for plot_idx in self.data_buffers:
            for line_id in self.data_buffers[plot_idx]:
                old_buffer = self.data_buffers[plot_idx][line_id]
                new_buffer = deque(old_buffer, maxlen=window_size)
                self.data_buffers[plot_idx][line_id] = new_buffer


class LivePlotWidget(PlotWidget):
    """
    Extended plot widget with automatic refresh for live data.

    Adds auto-refresh capability for real-time monitoring.
    """

    def __init__(self, parent, num_plots=1, figsize=(8, 4), window_size=1000,
                 refresh_interval=100):
        """
        Initialize live plot widget.

        Args:
            parent: Parent tkinter widget
            num_plots: Number of subplots
            figsize: Figure size
            window_size: Rolling window size
            refresh_interval: Auto-refresh interval in milliseconds
        """
        super().__init__(parent, num_plots, figsize, window_size)

        self.refresh_interval = refresh_interval
        self.auto_refresh_enabled = False
        self.refresh_job = None

    def enable_auto_refresh(self, interval=None):
        """
        Enable automatic plot refresh.

        Args:
            interval: Refresh interval in milliseconds (None = use default)
        """
        if interval:
            self.refresh_interval = interval

        self.auto_refresh_enabled = True
        self._schedule_refresh()

    def disable_auto_refresh(self):
        """Disable automatic plot refresh."""
        self.auto_refresh_enabled = False

        if self.refresh_job:
            self.parent.after_cancel(self.refresh_job)
            self.refresh_job = None

    def _schedule_refresh(self):
        """Schedule next refresh (internal)."""
        if not self.auto_refresh_enabled:
            return

        self.refresh()
        self.refresh_job = self.parent.after(self.refresh_interval,
                                            self._schedule_refresh)

    def destroy(self):
        """Clean up widget."""
        self.disable_auto_refresh()
        self.canvas_widget.destroy()


# Convenience function for creating common plot layouts
def create_time_series_plot(parent, num_channels=3, window_seconds=30,
                            sample_rate=100):
    """
    Create a time-series plot widget with multiple channels.

    Args:
        parent: Parent tkinter widget
        num_channels: Number of channels (subplots)
        window_seconds: Time window in seconds
        sample_rate: Expected sample rate (Hz)

    Returns:
        LivePlotWidget configured for time-series data
    """
    window_size = int(window_seconds * sample_rate)

    plot = LivePlotWidget(parent, num_plots=num_channels,
                         figsize=(10, 2.5 * num_channels),
                         window_size=window_size,
                         refresh_interval=100)

    # Configure common time-series settings
    for i in range(num_channels):
        plot.configure_plot(i, xlabel='Time (s)')

    return plot
