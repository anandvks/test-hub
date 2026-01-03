#!/usr/bin/env python3
"""
System Validation Script

Comprehensive validation of the Test Bench GUI system.
Tests all major components without requiring hardware (uses Mock controller).

Usage:
    python validate_system.py              # Run all tests
    python validate_system.py --platform teensy  # Test with specific platform
    python validate_system.py --quick      # Quick validation (subset of tests)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime


class SystemValidator:
    """Comprehensive system validation."""

    def __init__(self, platform='mock', quick=False):
        """
        Initialize validator.

        Args:
            platform: Platform to test ('teensy', 'imx8', 'rpi', 'mock')
            quick: If True, run quick subset of tests
        """
        self.platform = platform
        self.quick = quick
        self.passed = 0
        self.failed = 0
        self.warnings = []
        self.errors = []

    def log(self, message, level='INFO'):
        """Log message with color coding."""
        colors = {
            'INFO': '\033[94m',   # Blue
            'PASS': '\033[92m',   # Green
            'FAIL': '\033[91m',   # Red
            'WARN': '\033[93m',   # Yellow
            'RESET': '\033[0m'
        }

        color = colors.get(level, colors['INFO'])
        reset = colors['RESET']
        print(f"{color}[{level}]{reset} {message}")

    def test_imports(self):
        """Test 1: Verify all modules can be imported."""
        self.log("Test 1: Module Imports", 'INFO')

        modules = [
            ('hardware', 'create_controller'),
            ('hardware', 'list_platforms'),
            ('hardware.base_controller', 'HardwareController'),
            ('hardware.mock_controller', 'MockController'),
            ('hardware.safety', 'SafetyMonitor'),
            ('protocols.registry', 'TestRegistry'),
            ('protocols.base_test', 'BaseTest'),
            ('data.logger', 'DataLogger'),
            ('data.exporter', 'DataExporter'),
            ('data.session', 'Session', 'SessionManager'),
            ('data.config_manager', 'ConfigManager'),
            ('utils.serial_finder', 'find_serial_ports'),
            ('utils.units', 'UnitConverter'),
        ]

        for module_parts in modules:
            module_name = module_parts[0]
            try:
                if len(module_parts) == 2:
                    exec(f"from {module_name} import {module_parts[1]}")
                else:
                    imports = ', '.join(module_parts[1:])
                    exec(f"from {module_name} import {imports}")
                self.log(f"  ✓ {module_name}", 'PASS')
                self.passed += 1
            except Exception as e:
                self.log(f"  ✗ {module_name}: {e}", 'FAIL')
                self.errors.append(f"Import error in {module_name}: {e}")
                self.failed += 1

    def test_hardware_factory(self):
        """Test 2: Hardware controller factory pattern."""
        self.log("\nTest 2: Hardware Controller Factory", 'INFO')

        from hardware import create_controller, list_platforms

        # Test list_platforms
        try:
            platforms = list_platforms()
            self.log(f"  ✓ list_platforms() returned {len(platforms)} platforms", 'PASS')
            self.passed += 1
        except Exception as e:
            self.log(f"  ✗ list_platforms() failed: {e}", 'FAIL')
            self.errors.append(f"list_platforms() error: {e}")
            self.failed += 1

        # Test controller creation
        controller = create_controller(self.platform)
        if controller is None:
            self.log(f"  ✗ Failed to create {self.platform} controller", 'FAIL')
            self.errors.append(f"create_controller('{self.platform}') returned None")
            self.failed += 1
            return None
        else:
            self.log(f"  ✓ Created {self.platform} controller", 'PASS')
            self.passed += 1

        # Test platform info
        try:
            info = controller.get_platform_info()
            required_keys = ['platform', 'version', 'communication']
            for key in required_keys:
                if key not in info:
                    self.log(f"  ✗ Missing key '{key}' in platform_info", 'FAIL')
                    self.errors.append(f"Platform info missing key: {key}")
                    self.failed += 1
                else:
                    self.log(f"  ✓ Platform info contains '{key}': {info[key]}", 'PASS')
                    self.passed += 1
        except Exception as e:
            self.log(f"  ✗ get_platform_info() failed: {e}", 'FAIL')
            self.errors.append(f"get_platform_info() error: {e}")
            self.failed += 1

        return controller

    def test_hardware_interface(self, controller):
        """Test 3: Hardware controller interface compliance."""
        if controller is None:
            self.log("\nTest 3: Hardware Interface - SKIPPED (no controller)", 'WARN')
            return

        self.log("\nTest 3: Hardware Controller Interface", 'INFO')

        # Test connection
        try:
            success = controller.connect()
            if success:
                self.log(f"  ✓ connect() succeeded", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ connect() returned False", 'FAIL')
                self.failed += 1
        except Exception as e:
            self.log(f"  ✗ connect() raised exception: {e}", 'FAIL')
            self.errors.append(f"connect() error: {e}")
            self.failed += 1
            return

        # Test enable/disable
        try:
            controller.enable()
            self.log(f"  ✓ enable() succeeded", 'PASS')
            self.passed += 1

            controller.disable()
            self.log(f"  ✓ disable() succeeded", 'PASS')
            self.passed += 1
        except Exception as e:
            self.log(f"  ✗ enable/disable error: {e}", 'FAIL')
            self.errors.append(f"Enable/disable error: {e}")
            self.failed += 1

        # Test sensor reading
        try:
            sensors = controller.get_sensors()
            if sensors is None:
                self.log(f"  ✗ get_sensors() returned None", 'FAIL')
                self.failed += 1
            else:
                required_keys = ['timestamp', 'position', 'velocity', 'current',
                                'force_tendon', 'force_tip', 'angle_joint']
                for key in required_keys:
                    if key not in sensors:
                        self.log(f"  ✗ Sensor data missing key: {key}", 'FAIL')
                        self.errors.append(f"Sensor data missing: {key}")
                        self.failed += 1
                    else:
                        self.log(f"  ✓ Sensor '{key}': {sensors[key]}", 'PASS')
                        self.passed += 1
        except Exception as e:
            self.log(f"  ✗ get_sensors() error: {e}", 'FAIL')
            self.errors.append(f"get_sensors() error: {e}")
            self.failed += 1

        # Test motor commands
        try:
            controller.set_position(1000)
            self.log(f"  ✓ set_position(1000) succeeded", 'PASS')
            self.passed += 1

            controller.set_velocity(100)
            self.log(f"  ✓ set_velocity(100) succeeded", 'PASS')
            self.passed += 1

            controller.set_torque(500)
            self.log(f"  ✓ set_torque(500) succeeded", 'PASS')
            self.passed += 1

            controller.set_current(200)
            self.log(f"  ✓ set_current(200) succeeded", 'PASS')
            self.passed += 1
        except Exception as e:
            self.log(f"  ✗ Motor command error: {e}", 'FAIL')
            self.errors.append(f"Motor command error: {e}")
            self.failed += 1

        # Test disconnect
        try:
            controller.disconnect()
            self.log(f"  ✓ disconnect() succeeded", 'PASS')
            self.passed += 1
        except Exception as e:
            self.log(f"  ✗ disconnect() error: {e}", 'FAIL')
            self.errors.append(f"disconnect() error: {e}")
            self.failed += 1

    def test_registry(self):
        """Test 4: Test registry and test discovery."""
        self.log("\nTest 4: Test Registry", 'INFO')

        try:
            from tests.registry import TestRegistry
            from hardware import create_controller
            from data.logger import DataLogger

            # Create test dependencies
            controller = create_controller('mock')
            controller.connect()
            logger = DataLogger()

            hardware_interface = {'controller': controller, 'safety': None}
            registry = TestRegistry(hardware_interface, logger)

            self.log(f"  ✓ TestRegistry initialized", 'PASS')
            self.passed += 1

            # Get all tests
            tests = registry.get_all_tests()
            self.log(f"  ✓ Found {len(tests)} tests", 'PASS')
            self.passed += 1

            # Verify expected tests exist
            expected = ['torque', 'hysteresis', 'stiffness', 'hold', 'endurance']
            for test_id in expected:
                test = registry.get_test(test_id)
                if test is None:
                    self.log(f"  ✗ Test '{test_id}' not found", 'FAIL')
                    self.errors.append(f"Missing test: {test_id}")
                    self.failed += 1
                else:
                    name = test.get_name()
                    params = test.get_parameters()
                    self.log(f"  ✓ Test '{test_id}': {name} ({len(params)} params)", 'PASS')
                    self.passed += 1

        except Exception as e:
            self.log(f"  ✗ TestRegistry error: {e}", 'FAIL')
            self.errors.append(f"TestRegistry error: {e}")
            self.failed += 1

    def test_data_management(self):
        """Test 5: Data logging and export."""
        self.log("\nTest 5: Data Management", 'INFO')

        # Test DataLogger
        try:
            from data.logger import DataLogger

            logger = DataLogger(buffer_size=100)
            self.log(f"  ✓ DataLogger created", 'PASS')
            self.passed += 1

            # Test logging
            test_file = Path("data/sessions/test_validation.csv")
            test_file.parent.mkdir(parents=True, exist_ok=True)

            headers = ['timestamp', 'position', 'force']
            logger.start_logging(test_file, headers)
            self.log(f"  ✓ Logging started", 'PASS')
            self.passed += 1

            # Log some data
            for i in range(10):
                logger.log({'timestamp': i, 'position': i*100, 'force': i*10})

            logger.stop_logging()
            self.log(f"  ✓ Logged 10 samples", 'PASS')
            self.passed += 1

            # Verify file exists
            if test_file.exists():
                self.log(f"  ✓ CSV file created: {test_file}", 'PASS')
                self.passed += 1
                test_file.unlink()  # Clean up
            else:
                self.log(f"  ✗ CSV file not created", 'FAIL')
                self.failed += 1

        except Exception as e:
            self.log(f"  ✗ DataLogger error: {e}", 'FAIL')
            self.errors.append(f"DataLogger error: {e}")
            self.failed += 1

        # Test Session Management
        try:
            from data.session import SessionManager

            sm = SessionManager()
            session = sm.create_session(prefix='validation_test', platform='mock')
            self.log(f"  ✓ Session created: {session.session_id}", 'PASS')
            self.passed += 1

            # Verify directory structure
            if session.session_dir.exists():
                self.log(f"  ✓ Session directory created", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ Session directory not created", 'FAIL')
                self.failed += 1

            # Add a test
            session.add_test(
                test_id='test_001',
                test_type='validation',
                config={'param': 'value'},
                data_file='data/test.csv',
                plot_files=[]
            )
            self.log(f"  ✓ Test added to session", 'PASS')
            self.passed += 1

            # Clean up
            session.delete()

        except Exception as e:
            self.log(f"  ✗ SessionManager error: {e}", 'FAIL')
            self.errors.append(f"SessionManager error: {e}")
            self.failed += 1

    def test_unit_conversions(self):
        """Test 6: Unit conversion utilities."""
        self.log("\nTest 6: Unit Conversions", 'INFO')

        try:
            from utils.units import UnitConverter

            # Test force conversions
            force_n = UnitConverter.mn_to_newtons(1000)
            if abs(force_n - 1.0) < 0.001:
                self.log(f"  ✓ mN to N conversion: 1000 mN = {force_n:.3f} N", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ mN to N conversion incorrect: {force_n}", 'FAIL')
                self.failed += 1

            force_kg = UnitConverter.newtons_to_kg(9.81)
            if abs(force_kg - 1.0) < 0.01:
                self.log(f"  ✓ N to kg conversion: 9.81 N ≈ {force_kg:.3f} kg", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ N to kg conversion incorrect: {force_kg}", 'FAIL')
                self.failed += 1

            # Test angle conversions
            degrees = UnitConverter.counts_to_degrees(250, counts_per_rev=1000)
            if abs(degrees - 90.0) < 0.1:
                self.log(f"  ✓ Counts to degrees: 250/1000 rev = {degrees:.1f}°", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ Counts to degrees incorrect: {degrees}", 'FAIL')
                self.failed += 1

            # Test velocity conversions
            rad_per_sec = UnitConverter.rpm_to_rad_per_sec(60)
            import math
            expected = 2 * math.pi
            if abs(rad_per_sec - expected) < 0.01:
                self.log(f"  ✓ RPM to rad/s: 60 RPM = {rad_per_sec:.3f} rad/s", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ RPM to rad/s incorrect: {rad_per_sec}", 'FAIL')
                self.failed += 1

        except Exception as e:
            self.log(f"  ✗ Unit conversion error: {e}", 'FAIL')
            self.errors.append(f"Unit conversion error: {e}")
            self.failed += 1

    def test_config_manager(self):
        """Test 7: Configuration management."""
        self.log("\nTest 7: Configuration Management", 'INFO')

        try:
            from data.config_manager import ConfigManager

            cm = ConfigManager()
            self.log(f"  ✓ ConfigManager initialized", 'PASS')
            self.passed += 1

            # Test get
            platform = cm.get('hardware', 'platform')
            self.log(f"  ✓ get('hardware', 'platform') = {platform}", 'PASS')
            self.passed += 1

            # Test set and save
            cm.set('test', 'validation', True)
            cm.save()
            self.log(f"  ✓ set/save configuration", 'PASS')
            self.passed += 1

            # Reload and verify
            cm2 = ConfigManager()
            value = cm2.get('test', 'validation')
            if value == True:
                self.log(f"  ✓ Configuration persisted correctly", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ Configuration not persisted", 'FAIL')
                self.failed += 1

        except Exception as e:
            self.log(f"  ✗ ConfigManager error: {e}", 'FAIL')
            self.errors.append(f"ConfigManager error: {e}")
            self.failed += 1

    def test_documentation(self):
        """Test 8: Documentation files exist."""
        self.log("\nTest 8: Documentation", 'INFO')

        docs = [
            'README.md',
            'docs/THEORY.md',
            'docs/TUTORIAL.md',
            'docs/PLATFORM_GUIDE.md',
            'docs/index.html'
        ]

        for doc_file in docs:
            path = Path(doc_file)
            if path.exists():
                size = path.stat().st_size
                self.log(f"  ✓ {doc_file} exists ({size} bytes)", 'PASS')
                self.passed += 1
            else:
                self.log(f"  ✗ {doc_file} missing", 'FAIL')
                self.errors.append(f"Missing documentation: {doc_file}")
                self.failed += 1

    def print_summary(self):
        """Print validation summary."""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0

        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        print(f"Platform: {self.platform}")
        print(f"Mode: {'Quick' if self.quick else 'Full'}")
        print(f"\nTests Passed: {self.passed}")
        print(f"Tests Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                self.log(f"  {warning}", 'WARN')

        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                self.log(f"  {error}", 'FAIL')

        print("="*60)

        if self.failed == 0:
            self.log("\n✅ ALL TESTS PASSED - System is ready for use!", 'PASS')
            return 0
        else:
            self.log(f"\n❌ {self.failed} TESTS FAILED - Please review errors above", 'FAIL')
            return 1

    def run_all(self):
        """Run all validation tests."""
        self.log("="*60, 'INFO')
        self.log("Test Bench GUI - System Validation", 'INFO')
        self.log("="*60, 'INFO')
        self.log(f"Platform: {self.platform}", 'INFO')
        self.log(f"Mode: {'Quick' if self.quick else 'Full'}", 'INFO')
        self.log(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'INFO')
        self.log("="*60 + "\n", 'INFO')

        # Run tests
        self.test_imports()

        controller = self.test_hardware_factory()

        self.test_hardware_interface(controller)

        if not self.quick:
            self.test_registry()
            self.test_data_management()
            self.test_unit_conversions()
            self.test_config_manager()
            self.test_documentation()

        return self.print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Bench GUI System Validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_system.py                    # Full validation with mock
  python validate_system.py --platform teensy  # Test Teensy platform
  python validate_system.py --quick            # Quick validation
  python validate_system.py --help             # Show this help
        """
    )

    parser.add_argument(
        '--platform',
        default='mock',
        choices=['teensy', 'imx8', 'rpi', 'mock'],
        help='Platform to test (default: mock)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick validation (subset of tests)'
    )

    args = parser.parse_args()

    # Run validation
    validator = SystemValidator(platform=args.platform, quick=args.quick)
    exit_code = validator.run_all()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
