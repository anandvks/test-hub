# Installation

Complete installation guide for Test Bench GUI.

## System Requirements

### Operating System
- **Linux**: Ubuntu 20.04+ (recommended)
- **macOS**: 10.14+
- **Windows**: 10 or 11

### Hardware Requirements
- **CPU**: Dual-core 2.0 GHz or higher
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free space
- **Connectivity**:
  - USB port for Teensy 4.1
  - Ethernet for IMX8
  - GPIO for Raspberry Pi

### Software Requirements
- **Python**: 3.8, 3.9, 3.10, or 3.11
- **Git**: For cloning repository
- **Tkinter**: Usually pre-installed with Python

## Installation Steps

### 1. Install Python

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10
```

#### Windows
Download and install from [python.org](https://www.python.org/downloads/)

### 2. Clone Repository

```bash
git clone https://github.com/anandvks/test-hub.git
cd test-hub
```

### 3. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

This installs:
- **numpy** - Array operations
- **scipy** - Signal processing
- **pandas** - Data analysis
- **matplotlib** - Plotting
- **pyserial** - Serial communication
- **pytest** - Testing framework (optional)

### 4. Platform-Specific Setup

#### Teensy 4.1 (Serial/USB)

**Linux**: Add user to dialout group
```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

**Windows**: Install Teensy drivers from [pjrc.com](https://www.pjrc.com/teensy/loader.html)

#### Raspberry Pi (SPI/I2C)

Install additional dependencies:
```bash
pip3 install spidev smbus2
```

Enable SPI and I2C:
```bash
sudo raspi-config
# Navigate to Interface Options → Enable SPI and I2C
```

#### IMX8 (Ethernet/TCP)

No additional setup needed - uses standard Python socket library.

### 5. Verify Installation

```bash
# Run system validation
python3 validate_system.py

# Expected output: All checks passing
```

### 6. Run Application

```bash
python3 main.py
```

## Optional: Development Tools

For contributing or running tests:

```bash
# Install development dependencies
pip3 install pytest pytest-cov pytest-mock

# Run unit tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Configuration

### Edit config.json

```json
{
  "hardware": {
    "platform": "teensy",
    "motor": {
      "model": "Maxon ECX TORQUE 22 L",
      "gearbox": "GPX 22 HP 231:1"
    }
  },
  "safety": {
    "max_current": 2000,
    "max_force": 60000,
    "position_limits": [-10000, 10000]
  }
}
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'numpy'`

**Solution**: Reinstall dependencies
```bash
pip3 install -r requirements.txt
```

### Permission Denied (Linux)

**Problem**: `Permission denied: '/dev/ttyACM0'`

**Solution**: Add user to dialout group
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Tkinter Not Found

**Problem**: `No module named '_tkinter'`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# macOS
brew install python-tk
```

## Next Steps

- [Quick Start Guide](quick-start.md) - Run your first test
- [Hardware Setup](../user-guide/hardware-setup.md) - Wiring diagrams
- [Tutorial](../user-guide/tutorial.md) - Complete user guide
