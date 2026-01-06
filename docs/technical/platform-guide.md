# Platform Porting Guide

Complete guide for adding new hardware platform support to the Test Bench GUI.

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Controller Interface](#hardware-controller-interface)
3. [Supported Platforms](#supported-platforms)
4. [Adding a New Platform](#adding-a-new-platform)
5. [Protocol Examples](#protocol-examples)
6. [Testing Your Controller](#testing-your-controller)
7. [Best Practices](#best-practices)

---

## Overview

The Test Bench GUI uses a **hardware abstraction layer** (HAL) that separates platform-specific communication from the core testing logic. This allows the same GUI and test suite to work with different microcontrollers and communication methods.

### Why Platform Abstraction?

- **Modularity**: Change hardware without modifying tests or GUI
- **Flexibility**: Support multiple platforms simultaneously
- **Testability**: Use mock controllers for development without hardware
- **Maintainability**: Platform-specific code isolated in single files

### Architecture Layers

```
┌─────────────────────────────────────────┐
│         Test Logic Layer                │
│  (Tests, GUI, Data Logging)             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Hardware Controller Interface      │
│      (Abstract Base Class)              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│     Platform-Specific Controllers       │
│ Teensy │ IMX8 │ RPi │ Mock │ YourPlatform │
└─────────────────────────────────────────┘
```

---

## Hardware Controller Interface

All platform controllers must inherit from `HardwareController` and implement its abstract methods.

### Base Class: `hardware/base_controller.py`

```python
from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable

class HardwareController(ABC):
    """Abstract base class for hardware controllers."""

    def __init__(self):
        self.connected = False
        self.enabled = False
```

### Required Methods

#### Connection Management

```python
@abstractmethod
def connect(self, **kwargs) -> bool:
    """
    Connect to hardware controller.

    Args:
        **kwargs: Platform-specific connection parameters
            - Serial: port (str), baudrate (int)
            - Ethernet: host (str), port (int)
            - CAN: interface (str), bitrate (int)
            - SPI/I2C: bus (int), device/address (int)

    Returns:
        True if connection successful, False otherwise
    """
    pass

@abstractmethod
def disconnect(self) -> bool:
    """Disconnect from hardware controller."""
    pass
```

#### Motor Control

```python
@abstractmethod
def enable(self) -> bool:
    """Enable motor driver. Returns True if successful."""
    pass

@abstractmethod
def disable(self) -> bool:
    """Disable motor driver. Returns True if successful."""
    pass

@abstractmethod
def emergency_stop(self) -> bool:
    """Emergency stop - immediately disable motor. Returns True if successful."""
    pass
```

#### Motor Commands

```python
@abstractmethod
def set_position(self, position: int) -> bool:
    """
    Set target position (encoder counts).

    Args:
        position: Target position in encoder counts

    Returns:
        True if command accepted, False if rejected (e.g., limit exceeded)
    """
    pass

@abstractmethod
def set_velocity(self, velocity: int) -> bool:
    """Set target velocity (RPM). Returns True if successful."""
    pass

@abstractmethod
def set_torque(self, torque: int) -> bool:
    """Set target torque (mNm). Returns True if successful."""
    pass

@abstractmethod
def set_current(self, current: int) -> bool:
    """Set motor current (mA). Returns True if successful."""
    pass
```

#### Sensor Reading

```python
@abstractmethod
def get_sensors(self) -> Optional[Dict]:
    """
    Read all sensors.

    Returns:
        Dict with standardized keys (all values in base units):
            'timestamp': int (ms or s, must be consistent)
            'position': int (encoder counts)
            'velocity': int (RPM)
            'current': int (mA)
            'force_tendon': int (mN) - millinewtons
            'force_tip': int (mN)
            'angle_joint': int (encoder counts or angle × 100)

        Returns None if read failed.
    """
    pass
```

**CRITICAL**: The sensor data dict must use these exact keys and units. This standardization allows all tests to work across platforms.

#### Streaming

```python
@abstractmethod
def start_streaming(self, rate_hz: int, callback: Callable) -> bool:
    """
    Start streaming sensor data.

    Args:
        rate_hz: Streaming frequency in Hz (e.g., 100 for 100 Hz)
        callback: Function called with sensor dict for each sample
                  Signature: callback(sensor_data: Dict)

    Returns:
        True if streaming started successfully

    Implementation Notes:
        - Run streaming in background thread
        - Call callback with sensor dict matching get_sensors() format
        - Handle errors gracefully without crashing thread
    """
    pass

@abstractmethod
def stop_streaming(self) -> bool:
    """Stop streaming sensor data. Returns True if successful."""
    pass
```

#### Advanced Control

```python
@abstractmethod
def set_pid_params(self, kp: float, ki: float, kd: float) -> bool:
    """Set PID controller parameters."""
    pass

@abstractmethod
def get_pid_params(self) -> Optional[Dict]:
    """
    Get current PID parameters.

    Returns:
        Dict with keys: 'kp', 'ki', 'kd' (all floats)
        or None if read failed
    """
    pass

@abstractmethod
def set_motion_profile(self, max_velocity: int, max_acceleration: int,
                       max_deceleration: int, jerk: int) -> bool:
    """Set motion profile parameters (all in appropriate units)."""
    pass

@abstractmethod
def get_motion_profile(self) -> Optional[Dict]:
    """
    Get current motion profile.

    Returns:
        Dict with keys: 'max_velocity', 'acceleration',
                       'deceleration', 'jerk_limit'
        or None if read failed
    """
    pass
```

#### Safety and Calibration

```python
@abstractmethod
def set_limit(self, limit_type: str, value: int) -> bool:
    """
    Set safety limit.

    Args:
        limit_type: One of: 'current_max', 'position_min',
                           'position_max', 'force_max'
        value: Limit value in base units (mA, counts, mN)

    Returns:
        True if limit set successfully
    """
    pass

@abstractmethod
def zero_sensors(self) -> bool:
    """
    Zero all sensors (set current readings as zero offset).

    Returns:
        True if zeroing successful
    """
    pass
```

#### Platform Identification

```python
@abstractmethod
def get_platform_name(self) -> str:
    """
    Return platform name.

    Examples: "Teensy", "IMX8", "Raspberry Pi", "Mock"
    """
    pass

@abstractmethod
def get_platform_info(self) -> Dict:
    """
    Return platform-specific information.

    Returns:
        Dict with keys:
            'platform': str (full platform name)
            'version': str (controller version)
            'firmware_version': str
            'communication': str (e.g., "Serial", "Ethernet/TCP")
            'capabilities': list of str (supported features)
            ... other platform-specific fields
    """
    pass
```

---

## Supported Platforms

### 1. Teensy 4.1 (Serial)

**File**: `hardware/teensy_controller.py`

**Communication**: Serial (UART) at 115200 baud

**Protocol**: Text-based, line-delimited ASCII commands

**Example Commands**:
```
>>> PING
<<< ACK PONG

>>> SETPOS 5000
<<< ACK

>>> GETSENSORS
<<< DATA 1000 0 0 50 120 5 0
```

**Use Case**: Direct USB connection, easy debugging, human-readable protocol

---

### 2. IMX8 (Ethernet/TCP)

**File**: `hardware/imx8_controller.py`

**Communication**: Ethernet via TCP sockets (default port 5000)

**Protocol**: JSON over TCP, newline-delimited

**Example Request**:
```json
{"cmd": "SET_POSITION", "data": {"value": 5000}}
```

**Example Response**:
```json
{"status": "ok", "data": {}}
```

**Use Case**: Network-connected systems, remote operation, JSON-friendly systems

**Features**:
- Dual-socket architecture: one for commands, one for streaming
- Robust error handling with status codes
- Supports high-bandwidth streaming

---

### 3. Raspberry Pi (SPI/I2C)

**File**: `hardware/rpi_controller.py`

**Communication**: I2C (default bus 1) for motor control and sensors

**Protocol**: Memory-mapped registers, binary data

**Register Map** (example):
- `0x00`: Control register (enable/disable/estop)
- `0x10`: Position command (4 bytes, little-endian)
- `0x20`: Sensor data start (28 bytes)
- `0x40`: PID parameters (12 bytes)

**Use Case**: Direct hardware access, low-level control, embedded systems

**Requirements**:
```bash
pip install spidev smbus2
```

**I2C Addresses** (configurable):
- Motor controller: `0x60`
- Sensor board: `0x40`

---

### 4. Mock Controller (Simulator)

**File**: `hardware/mock_controller.py`

**Communication**: In-memory (no hardware required)

**Protocol**: N/A (simulated)

**Features**:
- Physics simulation (simplified motor dynamics)
- Realistic sensor noise
- Adjustable simulation parameters
- Perfect for testing without hardware

**Use Case**: Development, testing, tutorials, demonstrations

---

## Adding a New Platform

### Step-by-Step Guide

#### Step 1: Create Controller File

Create `hardware/yourplatform_controller.py`:

```python
"""
YourPlatform Hardware Controller

Brief description of your platform and communication method.
"""

from typing import Optional, Dict, Callable
from .base_controller import HardwareController


class YourPlatformController(HardwareController):
    """Hardware controller for YourPlatform."""

    def __init__(self):
        super().__init__()
        # Initialize platform-specific attributes
        self.your_comm_interface = None

    def connect(self, **kwargs) -> bool:
        """Connect to YourPlatform."""
        # Extract connection parameters
        param1 = kwargs.get('param1', default_value)

        try:
            # Establish connection
            self.your_comm_interface = YourCommLibrary.connect(param1)

            # Verify connection (e.g., ping)
            if self._verify_connection():
                self.connected = True
                print("YourPlatform: Connected successfully")
                return True
            else:
                return False

        except Exception as e:
            print(f"YourPlatform connection failed: {e}")
            return False

    # Implement all other abstract methods...
    # See existing controllers for examples
```

#### Step 2: Add to Factory

The factory (`hardware/__init__.py`) already has graceful imports. Your controller will be automatically imported if the file exists.

Verify it's added to `PLATFORM_MAP`:

```python
# In hardware/__init__.py
try:
    from .yourplatform_controller import YourPlatformController
except ImportError:
    YourPlatformController = None

if YourPlatformController:
    PLATFORM_MAP['yourplatform'] = YourPlatformController
    PLATFORM_MAP['your_alias'] = YourPlatformController  # Optional alias
```

#### Step 3: Add Configuration

Update `data/config_manager.py`:

```python
DEFAULT_CONFIG = {
    'hardware': {
        'platform': 'teensy',  # Default
        # ... existing platforms ...
        'yourplatform': {
            'param1': 'value1',
            'param2': 'value2'
        }
    }
}
```

#### Step 4: Test Connection

Create a simple test script:

```python
from hardware import create_controller

# Create controller
controller = create_controller('yourplatform')

# Connect
if controller.connect(param1='value1'):
    print("Connected!")

    # Test basic operations
    controller.enable()

    # Read sensors
    sensors = controller.get_sensors()
    print(f"Sensors: {sensors}")

    controller.disable()
    controller.disconnect()
else:
    print("Connection failed")
```

#### Step 5: Run Full Tests

Use the mock controller approach - test each method:

1. Connection/disconnection
2. Enable/disable
3. All set commands (position, velocity, torque, current)
4. Sensor reading (verify data format)
5. Streaming (verify callback works, correct rate)
6. PID parameters (set and get)
7. Motion profile (set and get)
8. Safety limits
9. Zero sensors

#### Step 6: Update GUI (Optional)

If your platform needs special connection UI, update `gui/manual_tab.py`:

```python
def _create_connection_panel(self):
    platform = self.controller.get_platform_name()

    if platform == "YourPlatform":
        self._create_yourplatform_connection_ui()
```

---

## Protocol Examples

### Serial Protocol (Teensy-style)

**Characteristics**:
- Human-readable ASCII
- Newline-delimited (`\n`)
- Command-response pairs
- Timeout: 1-2 seconds

**Implementation**:
```python
import serial

class SerialController(HardwareController):
    def connect(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=2.0)

    def _send_command(self, command: str) -> str:
        # Send command with newline
        self.serial.write((command + '\n').encode())

        # Read response
        response = self.serial.readline().decode().strip()
        return response

    def set_position(self, position: int) -> bool:
        response = self._send_command(f"SETPOS {position}")
        return response.startswith("ACK")
```

**Pros**: Easy to debug, human-readable, simple implementation

**Cons**: Parsing overhead, lower bandwidth

---

### JSON over TCP (IMX8-style)

**Characteristics**:
- Structured data (JSON)
- Newline-delimited messages
- Status codes in response
- Supports complex data types

**Implementation**:
```python
import socket
import json

class TCPController(HardwareController):
    def connect(self, host, port=5000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def _send_command(self, cmd: str, data: dict = None) -> dict:
        # Build request
        msg = {"cmd": cmd}
        if data:
            msg["data"] = data

        # Send JSON + newline
        msg_bytes = (json.dumps(msg) + '\n').encode()
        self.socket.sendall(msg_bytes)

        # Receive response
        response_bytes = self.socket.recv(4096)
        response = json.loads(response_bytes.decode())

        return response

    def set_position(self, position: int) -> bool:
        resp = self._send_command("SET_POSITION", {"value": position})
        return resp.get("status") == "ok"
```

**Pros**: Structured data, extensible, error handling built-in

**Cons**: JSON overhead, requires parsing library

---

### Binary Protocol (CAN bus / SPI)

**Characteristics**:
- Compact binary format
- Fixed message sizes
- High bandwidth, low latency
- Requires byte-packing/unpacking

**Implementation**:
```python
import struct

class BinaryController(HardwareController):
    def _pack_command(self, cmd_id: int, data: bytes) -> bytes:
        """Pack command into binary format."""
        # Header: cmd_id (1 byte) + length (1 byte)
        header = struct.pack('BB', cmd_id, len(data))
        return header + data

    def _unpack_response(self, data: bytes) -> tuple:
        """Unpack binary response."""
        cmd_id, length = struct.unpack('BB', data[:2])
        payload = data[2:2+length]
        return cmd_id, payload

    def set_position(self, position: int) -> bool:
        # Pack position as signed 32-bit integer (little-endian)
        data = struct.pack('<i', position)

        # Send command (ID 0x10 for position)
        msg = self._pack_command(0x10, data)
        self.interface.send(msg)

        # Receive response
        response = self.interface.recv()
        cmd_id, payload = self._unpack_response(response)

        # Check if ACK (cmd_id 0x00 = ACK)
        return cmd_id == 0x00
```

**Pros**: High performance, low bandwidth, precise timing

**Cons**: Complex implementation, harder to debug

---

### I2C Register-Based (Raspberry Pi-style)

**Characteristics**:
- Memory-mapped register interface
- Direct hardware access
- Read/write individual registers
- Multi-byte data requires proper handling

**Implementation**:
```python
import smbus2

class I2CController(HardwareController):
    def connect(self, i2c_bus=1, device_addr=0x60):
        self.i2c = smbus2.SMBus(i2c_bus)
        self.addr = device_addr

    def _write_int32(self, reg: int, value: int):
        """Write 32-bit integer to register."""
        bytes_val = value.to_bytes(4, 'little', signed=True)
        self.i2c.write_i2c_block_data(self.addr, reg, list(bytes_val))

    def _read_int32(self, reg: int) -> int:
        """Read 32-bit integer from register."""
        bytes_val = self.i2c.read_i2c_block_data(self.addr, reg, 4)
        return int.from_bytes(bytes_val, 'little', signed=True)

    def set_position(self, position: int) -> bool:
        try:
            self._write_int32(0x10, position)  # Reg 0x10 = position
            return True
        except Exception as e:
            print(f"I2C error: {e}")
            return False

    def get_sensors(self) -> Optional[Dict]:
        try:
            # Read 28-byte sensor block starting at reg 0x20
            data = self.i2c.read_i2c_block_data(self.addr, 0x20, 28)

            # Parse into sensor dict
            return {
                'timestamp': int.from_bytes(data[0:4], 'little'),
                'position': int.from_bytes(data[4:8], 'little', signed=True),
                'velocity': int.from_bytes(data[8:12], 'little', signed=True),
                # ... parse remaining fields ...
            }
        except Exception as e:
            print(f"Sensor read error: {e}")
            return None
```

**Pros**: Direct hardware access, low overhead, fast

**Cons**: Platform-specific, requires hardware expertise

---

## Testing Your Controller

### Unit Test Template

```python
import unittest
from hardware.yourplatform_controller import YourPlatformController

class TestYourPlatformController(unittest.TestCase):
    def setUp(self):
        """Create controller instance before each test."""
        self.controller = YourPlatformController()

    def test_connection(self):
        """Test basic connection."""
        result = self.controller.connect(param1='value1')
        self.assertTrue(result)
        self.assertTrue(self.controller.connected)

    def test_enable_disable(self):
        """Test motor enable/disable."""
        self.controller.connect(param1='value1')

        # Enable
        self.assertTrue(self.controller.enable())
        self.assertTrue(self.controller.enabled)

        # Disable
        self.assertTrue(self.controller.disable())
        self.assertFalse(self.controller.enabled)

    def test_set_position(self):
        """Test position command."""
        self.controller.connect(param1='value1')
        self.controller.enable()

        result = self.controller.set_position(1000)
        self.assertTrue(result)

    def test_get_sensors(self):
        """Test sensor reading."""
        self.controller.connect(param1='value1')

        sensors = self.controller.get_sensors()
        self.assertIsNotNone(sensors)

        # Verify all required keys present
        required_keys = ['timestamp', 'position', 'velocity', 'current',
                        'force_tendon', 'force_tip', 'angle_joint']
        for key in required_keys:
            self.assertIn(key, sensors)

    def test_streaming(self):
        """Test streaming functionality."""
        self.controller.connect(param1='value1')

        # Callback to collect samples
        samples = []
        def callback(data):
            samples.append(data)

        # Start streaming at 10 Hz
        result = self.controller.start_streaming(10, callback)
        self.assertTrue(result)

        # Wait for samples
        import time
        time.sleep(1.0)

        # Stop streaming
        self.controller.stop_streaming()

        # Verify we got approximately 10 samples
        self.assertGreater(len(samples), 8)
        self.assertLess(len(samples), 12)

    def tearDown(self):
        """Cleanup after each test."""
        if self.controller.connected:
            self.controller.disconnect()
```

### Manual Test Script

```python
from hardware import create_controller
import time

def test_platform(platform_name: str, **connect_kwargs):
    """Manual test script for new platform."""

    print(f"\n{'='*60}")
    print(f"Testing Platform: {platform_name}")
    print(f"{'='*60}\n")

    # Create controller
    controller = create_controller(platform_name)
    if not controller:
        print("ERROR: Could not create controller")
        return False

    # Test 1: Connection
    print("Test 1: Connection...")
    if not controller.connect(**connect_kwargs):
        print("  FAIL: Could not connect")
        return False
    print("  PASS: Connected")

    # Test 2: Platform info
    print("\nTest 2: Platform Info...")
    info = controller.get_platform_info()
    print(f"  Platform: {info['platform']}")
    print(f"  Version: {info['version']}")
    print(f"  Communication: {info['communication']}")
    print(f"  Capabilities: {', '.join(info['capabilities'])}")

    # Test 3: Enable
    print("\nTest 3: Enable Motor...")
    if not controller.enable():
        print("  FAIL: Could not enable")
        return False
    print("  PASS: Motor enabled")

    # Test 4: Read sensors
    print("\nTest 4: Read Sensors...")
    sensors = controller.get_sensors()
    if not sensors:
        print("  FAIL: Could not read sensors")
        return False
    print(f"  Position: {sensors['position']}")
    print(f"  Current: {sensors['current']} mA")
    print(f"  Force (tendon): {sensors['force_tendon']} mN")
    print(f"  Force (tip): {sensors['force_tip']} mN")
    print("  PASS: Sensors read successfully")

    # Test 5: Position command
    print("\nTest 5: Position Command...")
    if not controller.set_position(1000):
        print("  FAIL: Could not set position")
        return False
    time.sleep(1.0)
    sensors = controller.get_sensors()
    print(f"  New position: {sensors['position']}")
    print("  PASS: Position command successful")

    # Test 6: Streaming
    print("\nTest 6: Streaming...")
    sample_count = [0]
    def callback(data):
        sample_count[0] += 1

    if not controller.start_streaming(50, callback):
        print("  FAIL: Could not start streaming")
        return False

    time.sleep(2.0)
    controller.stop_streaming()

    print(f"  Received {sample_count[0]} samples in 2 seconds")
    print(f"  Rate: {sample_count[0]/2.0:.1f} Hz")

    if sample_count[0] < 80:  # Expect ~100 samples at 50 Hz
        print("  WARN: Sample rate lower than expected")
    else:
        print("  PASS: Streaming working")

    # Test 7: Disable
    print("\nTest 7: Disable Motor...")
    if not controller.disable():
        print("  FAIL: Could not disable")
        return False
    print("  PASS: Motor disabled")

    # Test 8: Disconnect
    print("\nTest 8: Disconnect...")
    if not controller.disconnect():
        print("  FAIL: Could not disconnect")
        return False
    print("  PASS: Disconnected")

    print(f"\n{'='*60}")
    print("ALL TESTS PASSED")
    print(f"{'='*60}\n")

    return True


# Example usage:
if __name__ == "__main__":
    # Test Teensy
    test_platform('teensy', port='/dev/ttyACM0', baudrate=115200)

    # Test IMX8
    test_platform('imx8', host='192.168.1.100', port=5000)

    # Test Mock (no hardware needed)
    test_platform('mock')
```

---

## Best Practices

### 1. Error Handling

**Do**:
- Return `False` or `None` on errors (don't raise exceptions)
- Print clear error messages with `print(f"Platform: error description")`
- Handle communication timeouts gracefully
- Verify connection before each operation

**Don't**:
- Let exceptions propagate to calling code
- Return incorrect data types
- Block indefinitely on communication errors

### 2. Thread Safety

**Do**:
- Use `threading.Lock()` for serial communication
- Make streaming thread daemon (`daemon=True`)
- Join threads with timeout on stop
- Handle thread exceptions without crashing

**Don't**:
- Access hardware from multiple threads without locks
- Leave threads running after disconnect
- Block forever waiting for thread termination

### 3. Units and Data Format

**Do**:
- Always use standardized units (mA, mN, counts, RPM)
- Return exact dict keys specified in interface
- Convert platform-specific units to standard units
- Document any non-standard units in docstrings

**Don't**:
- Use different units than specified
- Add/remove keys from sensor dict
- Return floats where ints are expected

### 4. Compatibility

**Do**:
- Test with mock controller first (validates interface compliance)
- Run all 5 test protocols (Torque, Hysteresis, Stiffness, Hold, Endurance)
- Verify streaming at different rates (10 Hz, 50 Hz, 100 Hz)
- Test emergency stop immediately halts motor

**Don't**:
- Assume tests will work without running them
- Skip streaming test (many controllers fail here)
- Forget to test disconnect/reconnect cycle

### 5. Documentation

**Do**:
- Add comprehensive docstrings to your controller
- Document required dependencies (e.g., `pip install ...`)
- Provide example connection parameters
- List platform capabilities in `get_platform_info()`

**Don't**:
- Leave methods undocumented
- Assume others know your platform's quirks
- Forget to update this guide with your protocol

---

## Example: Complete Controller Template

See `hardware/mock_controller.py` for a fully-implemented example that can serve as a template for new platforms.

Key sections:
1. Imports and class definition
2. `__init__` with platform-specific attributes
3. `connect()` and `disconnect()`
4. Motor control methods
5. Sensor reading with correct data format
6. Streaming with background thread
7. Advanced control (PID, motion profile)
8. Safety and calibration
9. Platform identification

---

## Troubleshooting

### Issue: Tests fail with "Unknown platform"

**Solution**: Check that:
1. Your controller file is in `hardware/` directory
2. Class name matches import in `hardware/__init__.py`
3. Platform name matches key in `PLATFORM_MAP`

### Issue: Sensors return None

**Solution**:
1. Verify communication is working (test with simple read/write)
2. Check data format matches expected layout
3. Add debug prints to see raw data
4. Ensure proper byte ordering (little vs. big endian)

### Issue: Streaming rate is incorrect

**Solution**:
1. Measure actual callback rate with timestamps
2. Check thread sleep duration calculation
3. Verify communication bandwidth supports rate
4. Consider decimation if platform can't keep up

### Issue: GUI shows connection failed

**Solution**:
1. Test controller with manual script first
2. Check that `connect()` returns `True`
3. Verify `connected` attribute is set correctly
4. Add debug prints in `connect()` method

---

## Support

For questions or issues:

1. Check existing controllers for examples
2. Review the Hardware Controller Interface section
3. Test with mock controller to verify interface compliance
4. Create a minimal test script before integrating with GUI

---

## Summary

Adding a new platform requires:

1. ✅ Create controller file inheriting from `HardwareController`
2. ✅ Implement all abstract methods
3. ✅ Add to factory (automatic with try/except imports)
4. ✅ Add config section to `config_manager.py`
5. ✅ Test with manual script
6. ✅ Run full test suite
7. ✅ Document protocol and dependencies

The hardware abstraction layer makes this process straightforward - focus on platform-specific communication, and the rest just works.

Happy porting! 🚀
