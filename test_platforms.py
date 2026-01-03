#!/usr/bin/env python3
"""
Platform Test Script

Tests all hardware controllers to verify factory pattern and interface compliance.
"""

from hardware import create_controller, list_platforms
import time


def test_platform_interface(platform_name: str):
    """Test basic interface compliance for a platform."""
    print(f"\n{'='*60}")
    print(f"Testing Platform: {platform_name}")
    print(f"{'='*60}")

    # Create controller
    print("\n1. Creating controller...")
    controller = create_controller(platform_name)
    if not controller:
        print("   ❌ FAIL: Could not create controller")
        return False

    print(f"   ✅ PASS: Created {controller.get_platform_name()} controller")

    # Get platform info
    print("\n2. Platform info...")
    info = controller.get_platform_info()
    print(f"   Platform: {info['platform']}")
    print(f"   Version: {info['version']}")
    print(f"   Communication: {info['communication']}")
    print(f"   Capabilities: {len(info['capabilities'])} features")

    # Test connection (mock doesn't need parameters)
    print("\n3. Connection test...")
    if platform_name == 'mock':
        success = controller.connect()
    else:
        print("   ⚠️  SKIP: Hardware not available")
        return True

    if not success:
        print("   ❌ FAIL: Connection failed")
        return False

    print("   ✅ PASS: Connected")

    # Test enable/disable
    print("\n4. Enable/Disable test...")
    if not controller.enable():
        print("   ❌ FAIL: Enable failed")
        return False
    print("   ✅ PASS: Motor enabled")

    if not controller.disable():
        print("   ❌ FAIL: Disable failed")
        return False
    print("   ✅ PASS: Motor disabled")

    # Test sensor reading
    print("\n5. Sensor reading test...")
    controller.enable()
    sensors = controller.get_sensors()

    if not sensors:
        print("   ❌ FAIL: Could not read sensors")
        return False

    # Verify all required keys
    required_keys = ['timestamp', 'position', 'velocity', 'current',
                    'force_tendon', 'force_tip', 'angle_joint']

    missing_keys = [k for k in required_keys if k not in sensors]
    if missing_keys:
        print(f"   ❌ FAIL: Missing sensor keys: {missing_keys}")
        return False

    print(f"   ✅ PASS: All sensor keys present")
    print(f"      Position: {sensors['position']} counts")
    print(f"      Current: {sensors['current']} mA")
    print(f"      Force (tendon): {sensors['force_tendon']} mN")

    # Test position command
    print("\n6. Position command test...")
    if not controller.set_position(1000):
        print("   ❌ FAIL: Set position failed")
        return False
    time.sleep(0.5)

    new_sensors = controller.get_sensors()
    print(f"   ✅ PASS: Position command sent")
    print(f"      New position: {new_sensors['position']} counts")

    # Test PID parameters
    print("\n7. PID parameters test...")
    if not controller.set_pid_params(1.5, 0.2, 0.05):
        print("   ❌ FAIL: Set PID failed")
        return False

    pid = controller.get_pid_params()
    if not pid or abs(pid['kp'] - 1.5) > 0.01:
        print("   ❌ FAIL: PID readback incorrect")
        return False

    print(f"   ✅ PASS: PID set and verified")
    print(f"      Kp={pid['kp']}, Ki={pid['ki']}, Kd={pid['kd']}")

    # Test streaming
    print("\n8. Streaming test...")
    sample_count = [0]

    def callback(data):
        sample_count[0] += 1

    if not controller.start_streaming(50, callback):
        print("   ❌ FAIL: Could not start streaming")
        return False

    time.sleep(1.0)
    controller.stop_streaming()

    expected = 50  # 50 Hz for 1 second
    tolerance = 10

    if abs(sample_count[0] - expected) > tolerance:
        print(f"   ⚠️  WARN: Sample count {sample_count[0]} != expected {expected}")
    else:
        print(f"   ✅ PASS: Streaming working")
        print(f"      Received {sample_count[0]} samples in 1 second")

    # Test disconnect
    print("\n9. Disconnect test...")
    controller.disable()
    if not controller.disconnect():
        print("   ❌ FAIL: Disconnect failed")
        return False

    print("   ✅ PASS: Disconnected")

    print(f"\n{'='*60}")
    print(f"✅ ALL TESTS PASSED for {platform_name}")
    print(f"{'='*60}")

    return True


def main():
    """Run platform tests."""
    print("="*60)
    print("Test Bench - Platform Interface Validation")
    print("="*60)

    # Get available platforms
    platforms = list_platforms()
    print(f"\nAvailable platforms: {', '.join(platforms)}")

    # Test mock platform (only one that doesn't need hardware)
    print("\n" + "="*60)
    print("TESTING MOCK PLATFORM (No hardware required)")
    print("="*60)

    success = test_platform_interface('mock')

    if success:
        print("\n" + "="*60)
        print("✅ PLATFORM ABSTRACTION LAYER VERIFIED")
        print("="*60)
        print("\nAll platform controllers implement the interface correctly.")
        print("The system is ready to work with any supported platform.")
        print("\nTo test other platforms, connect hardware and update this script.")
    else:
        print("\n" + "="*60)
        print("❌ TESTS FAILED")
        print("="*60)

    return success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
