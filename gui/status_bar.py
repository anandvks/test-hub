"""
Safety Status Bar

Visual indicators for motor status and safety limits.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional


class SafetyStatusBar(ttk.Frame):
    """
    Status bar showing motor state and safety status.
    """

    def __init__(self, parent):
        super().__init__(parent, relief=tk.SUNKEN)

        self.status_labels = {}
        self.indicators = {}

        self._create_widgets()

    def _create_widgets(self):
        """Create status bar widgets."""
        # Motor status
        ttk.Label(self, text="Motor:").pack(side=tk.LEFT, padx=5)
        self.status_labels['motor'] = ttk.Label(
            self, text="DISCONNECTED", foreground="gray"
        )
        self.status_labels['motor'].pack(side=tk.LEFT, padx=5)

        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        # Current
        ttk.Label(self, text="Current:").pack(side=tk.LEFT, padx=5)
        self.status_labels['current'] = ttk.Label(self, text="0.00A / 1.00A")
        self.status_labels['current'].pack(side=tk.LEFT, padx=5)

        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        # Force
        ttk.Label(self, text="Force:").pack(side=tk.LEFT, padx=5)
        self.status_labels['force'] = ttk.Label(self, text="0.0N / 20.0N")
        self.status_labels['force'].pack(side=tk.LEFT, padx=5)

        ttk.Separator(self, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        # Overall status indicator
        self.indicators['status'] = tk.Canvas(
            self, width=20, height=20, highlightthickness=0
        )
        self.indicators['status'].pack(side=tk.LEFT, padx=5)

        self.status_labels['overall'] = ttk.Label(
            self, text="SAFE", foreground="green"
        )
        self.status_labels['overall'].pack(side=tk.LEFT, padx=5)

        # Draw initial indicator (green circle)
        self._update_indicator('safe')

    def _update_indicator(self, status: str):
        """
        Update status indicator circle.

        Args:
            status: 'safe', 'warning', or 'danger'
        """
        color_map = {
            'safe': 'green',
            'warning': 'yellow',
            'danger': 'red',
            'disconnected': 'gray'
        }

        color = color_map.get(status, 'gray')
        canvas = self.indicators['status']
        canvas.delete("all")
        canvas.create_oval(2, 2, 18, 18, fill=color, outline=color)

    def update_motor_status(self, connected: bool, enabled: bool):
        """
        Update motor status display.

        Args:
            connected: True if connected to Teensy
            enabled: True if motor driver is enabled
        """
        if not connected:
            self.status_labels['motor'].config(
                text="DISCONNECTED", foreground="gray"
            )
            self._update_indicator('disconnected')
        elif enabled:
            self.status_labels['motor'].config(
                text="ENABLED", foreground="green"
            )
        else:
            self.status_labels['motor'].config(
                text="DISABLED", foreground="orange"
            )

    def update_safety_status(self, safety_status: Dict):
        """
        Update safety indicators.

        Args:
            safety_status: Dict from SafetyMonitor.get_safety_status()
        """
        # Update current
        curr = safety_status['current']
        self.status_labels['current'].config(
            text=f"{curr['value']:.2f}A / {curr['limit']:.2f}A"
        )

        # Update force (use tip force)
        force = safety_status['force_tip']
        self.status_labels['force'].config(
            text=f"{force['value']:.1f}N / {force['limit']:.1f}N"
        )

        # Determine overall status
        statuses = [
            curr['status'],
            safety_status['force_tendon']['status'],
            force['status'],
            safety_status['position']['status']
        ]

        if 'danger' in statuses:
            overall = 'danger'
            text = "DANGER"
            color = "red"
        elif 'warning' in statuses:
            overall = 'warning'
            text = "WARNING"
            color = "orange"
        else:
            overall = 'safe'
            text = "SAFE"
            color = "green"

        self.status_labels['overall'].config(text=text, foreground=color)
        self._update_indicator(overall)

    def reset(self):
        """Reset status bar to initial state."""
        self.status_labels['motor'].config(
            text="DISCONNECTED", foreground="gray"
        )
        self.status_labels['current'].config(text="0.00A / 1.00A")
        self.status_labels['force'].config(text="0.0N / 20.0N")
        self.status_labels['overall'].config(text="SAFE", foreground="green")
        self._update_indicator('disconnected')
