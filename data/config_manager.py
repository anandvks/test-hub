"""
Configuration Manager

Handles saving and loading of system configuration.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class ConfigManager:
    """Manage system configuration and calibration data."""

    def __init__(self, config_file: Path = Path("config.json")):
        """
        Initialize config manager.

        Args:
            config_file: Path to main configuration file
        """
        self.config_file = config_file
        self.config = self._load_default_config()

        # Load existing config if available
        if self.config_file.exists():
            self.load()

    def _load_default_config(self) -> Dict:
        """Load default configuration."""
        return {
            'hardware': {
                'platform': 'teensy',  # Default platform: teensy, imx8, rpi, mock
                'motor': {
                    'model': 'Maxon ECX TORQUE 22 L',
                    'gearbox': 'GPX 22 HP 231:1',
                    'driver': 'ESCON 24/2'
                },
                'teensy': {
                    'port': '',  # Auto-detect (empty string)
                    'baudrate': 115200
                },
                'imx8': {
                    'host': '192.168.1.100',
                    'port': 5000
                },
                'rpi': {
                    'spi_bus': 0,
                    'spi_device': 0,
                    'i2c_bus': 1,
                    'motor_addr': 0x60,
                    'sensor_addr': 0x40
                },
                'mock': {
                    # No connection parameters needed for simulator
                },
                'sensors': {
                    'load_cell_tendon': {
                        'type': 'S-Type',
                        'max_force_N': 200
                    },
                    'load_cell_tip': {
                        'type': 'Button',
                        'max_force_N': 50
                    },
                    'encoder_joint': {
                        'type': 'AS5600',
                        'resolution': 4096
                    }
                }
            },
            'safety_limits': {
                'current_max_A': 1.0,
                'force_tendon_max_N': 200.0,
                'force_tip_max_N': 20.0,
                'position_min': 0,
                'position_max': 10000
            },
            'pid': {
                'kp': 1.0,
                'ki': 0.1,
                'kd': 0.01
            },
            'motion_profile': {
                'max_velocity': 500,
                'acceleration': 1000,
                'deceleration': 1000,
                'jerk_limit': 5000
            },
            'last_modified': datetime.now().isoformat()
        }

    def load(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if successful
        """
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)

            # Merge with defaults (in case new keys were added)
            self._merge_config(self.config, loaded_config)

            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save(self):
        """Save configuration to file."""
        self.config['last_modified'] = datetime.now().isoformat()

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _merge_config(self, default: Dict, loaded: Dict):
        """Recursively merge loaded config into default config."""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def get(self, *keys) -> Optional:
        """
        Get configuration value by key path.

        Args:
            *keys: Key path (e.g., 'hardware', 'teensy', 'port')

        Returns:
            Configuration value or None
        """
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def set(self, *keys, value):
        """
        Set configuration value by key path.

        Args:
            *keys: Key path (e.g., 'hardware', 'teensy', 'port')
            value: Value to set
        """
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def get_safety_limits(self) -> Dict:
        """Get safety limits configuration."""
        return self.config.get('safety_limits', {})

    def set_safety_limits(self, limits: Dict):
        """Set safety limits configuration."""
        self.config['safety_limits'].update(limits)

    def get_pid_params(self) -> Dict:
        """Get PID parameters."""
        return self.config.get('pid', {})

    def set_pid_params(self, params: Dict):
        """Set PID parameters."""
        self.config['pid'].update(params)

    def get_motion_profile(self) -> Dict:
        """Get motion profile."""
        return self.config.get('motion_profile', {})

    def set_motion_profile(self, profile: Dict):
        """Set motion profile."""
        self.config['motion_profile'].update(profile)

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._load_default_config()
