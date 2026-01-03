# Test Bench GUI

**Comprehensive validation platform for tendon-driven mechatronic systems**

---

## 🎯 Project Overview

This is a professional test bench control system for validating tendon-driven mechanisms. It provides:

- **Platform-agnostic architecture** - Supports Teensy 4.1, IMX8, Raspberry Pi, and simulation
- **5 automated test protocols** - Torque, Hysteresis, Stiffness, Static Hold, Endurance
- **Real-time visualization** - Live plotting at 50-100 Hz sample rates
- **Comprehensive data management** - Session-based organization with CSV/JSON export
- **Multi-layer safety system** - Hardware, firmware, and software protection

### Key Features

✅ **Manual Control** - Position, velocity, torque, and current control modes
✅ **Automated Testing** - 5 validation protocols with configurable parameters
✅ **Live Monitoring** - Real-time plots and statistics during test execution
✅ **Data Review** - Browse historical sessions, export results
✅ **Sensor Calibration** - Load cell and encoder calibration workflows
✅ **Safety First** - Emergency stop, current limits, position limits

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Hardware Setup](#-hardware-setup)
- [Platform Support](#-platform-support)
- [User Guide](#-user-guide)
- [Test Protocols](#-test-protocols)
- [Data Format](#-data-format)
- [Architecture](#-architecture)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [References](#-references)

---

## 🚀 Quick Start

**30-minute workflow to run your first static hold test:**

### 1. Install Dependencies

```bash
# Clone repository
cd test-gui

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Platform

Edit `config.json` to select your hardware platform:

```json
{
  "hardware": {
    "platform": "teensy"
  }
}
```

Options: `"teensy"`, `"imx8"`, `"rpi"`, `"mock"` (simulator)

### 3. Launch GUI

```bash
python main.py
```

### 4. Connect and Calibrate

1. Go to **Manual Control** tab
2. Click **Refresh** to detect ports
3. Click **Connect**
4. Navigate to **Calibration** tab
5. Follow calibration workflow (load cells → encoder)

### 5. Run Static Hold Test

1. Navigate to **Test Library** tab
2. Select **Static Hold Test**
3. Configure:
   - Target force: 11.8 N (1.2 kg fingertip force)
   - Duration: 5 minutes
4. Click **Run Test**
5. Monitor progress in **Live Monitor** tab

### 6. Review Results

1. Navigate to **Data Review** tab
2. Select your session from tree view
3. View plots and statistics
4. Export as CSV/JSON/PNG

**Complete tutorial:** See `docs/TUTORIAL.md`

---

## 📦 Installation

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, Windows 10+
- **Python**: 3.8 or later
- **Hardware**: USB port (Teensy), Ethernet (IMX8), GPIO (Raspberry Pi)

### Python Dependencies

```bash
pip install -r requirements.txt
```

**Core dependencies:**
- numpy >= 1.24.0
- scipy >= 1.10.0
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- pyserial >= 3.5 (for Teensy)

**Optional (platform-specific):**
- spidev >= 3.5 (for Raspberry Pi SPI)
- smbus2 >= 0.4.1 (for Raspberry Pi I2C)

### Documentation

View engineering documentation:

**Online (works offline):**
```bash
# Simply open docs/index.html in your browser
open docs/index.html        # macOS
xdg-open docs/index.html    # Linux
start docs/index.html       # Windows
```

The documentation site works without an HTTP server and includes links to all guides.

---

## 🔧 Hardware Setup

### System Requirements

**Motor System:**
- DC motor with gearbox (suitable for tendon-driven applications)
- Motor controller/driver
- Position feedback (encoder)

**Sensors:**
- Load cells for force measurement (tendon and fingertip)
- ADC interface for sensor data acquisition

**Control Platform** (choose one):
- **Teensy 4.1** (Serial/USB) - Recommended for development
- **IMX8** (Ethernet/TCP) - For production systems
- **Raspberry Pi** (SPI/I2C) - For embedded applications
- **Mock** (Simulator) - For testing without hardware

**Power:**
- Appropriate DC power supply for motor driver
- 5V power for microcontroller

### Basic Architecture

```
Power Supply → Motor Driver → DC Motor
                    ↕              ↓
            Microcontroller ← Sensors (Force, Position)
                    ↓
              PC (Test Bench GUI)
```

### Safety Considerations

Implement appropriate safety measures:
- Current limiting
- Position limits
- Force thresholds
- Emergency stop functionality
- Watchdog timers

For detailed hardware setup, see the [Hardware Setup Guide](https://anandvks.github.io/test-hub/user-guide/hardware-setup/).

---

## 🖥️ Platform Support

### Teensy 4.1 (Serial/USB)

**Communication**: Text-based serial protocol at 115200 baud

**Connection:**
```python
# Automatic in GUI (Manual Control → Connect)
# Or programmatically:
from hardware import create_controller
controller = create_controller('teensy')
controller.connect(port='/dev/ttyACM0', baudrate=115200)
```

**Firmware**: See `firmware/teensy/` for Arduino sketch

### IMX8 (Ethernet/TCP)

**Communication**: JSON over TCP sockets

**Connection:**
```python
controller = create_controller('imx8')
controller.connect(host='192.168.1.100', port=5000)
```

**Configuration**: Edit `config.json`:
```json
"imx8": {
  "host": "192.168.1.100",
  "port": 5000
}
```

### Raspberry Pi (SPI/I2C)

**Communication**: Binary protocol over I2C

**Connection:**
```python
controller = create_controller('rpi')
controller.connect(spi_bus=0, spi_device=0, i2c_bus=1)
```

**Requirements**: Enable SPI/I2C in `raspi-config`

### Mock (Simulator)

**No hardware required** - Physics simulation for testing

**Connection:**
```python
controller = create_controller('mock')
controller.connect()  # Always succeeds
```

**Use cases:**
- GUI development without hardware
- Tutorial walkthroughs
- Continuous integration testing

### Adding New Platforms

See `docs/PLATFORM_GUIDE.md` for complete porting guide.

---

## 📖 User Guide

### Tab 1: Manual Control

**Purpose**: Manual motor operation and live sensor monitoring

**Workflow:**
1. **Connect**: Select port/IP → Click Connect
2. **Enable Motor**: Click "Enable Motor"
3. **Select Mode**: Position / Velocity / Torque / Current
4. **Set Target**: Use slider or enter value
5. **Monitor**: View live plots (position, force, current)

**Controls:**
- **Position Mode**: Encoder counts (0-10000)
- **Velocity Mode**: RPM (-1000 to +1000)
- **Torque Mode**: mNm (0-3000)
- **Current Mode**: mA (0-1000)

**Live Plots**: Rolling 30-second window at 10 Hz

### Tab 2: Tendon Testing

**Purpose**: Specialized tests for tendon characterization

**Tests:**
- Tendon stiffness measurement
- Break-in cycles
- Creep analysis

### Tab 3: Finger Testing

**Purpose**: Complete finger mechanism validation

**Tests:**
- Fingertip force characterization
- Grip strength measurement
- Range of motion tests

### Tab 4: Test Library

**Purpose**: Automated validation test protocols

**Workflow:**
1. **Select Test**: Choose from 5 protocols
2. **Configure**: Set test parameters
3. **Review**: Check estimated duration
4. **Run**: Click "Run Test"
5. **Monitor**: Switch to Live Monitor tab

**Available Tests:**
- **Torque/Efficiency Test**: Measure η across torque range
- **Hysteresis Test**: Bidirectional backlash measurement
- **Stiffness Test**: System compliance (N/mm)
- **Static Hold Test**: 30-minute force stability
- **Endurance Test**: 10,000 flex-extend cycles

### Tab 5: Live Monitor

**Purpose**: Real-time visualization during automated tests

**Features:**
- 3 time-series plots (position, force, current)
- Force-position hysteresis plot
- Efficiency plot
- Live statistics panel
- Progress bar
- Pause/Stop controls

### Tab 6: Data Review

**Purpose**: Browse and export historical test data

**Features:**
- Session tree view (sessions → tests)
- 4-tab detail view:
  - **Information**: Session/test metadata
  - **Data**: CSV table (first 1000 rows)
  - **Plots**: Matplotlib figures
  - **Export**: CSV/JSON/PNG export
- Batch export entire sessions
- Delete old sessions

### Tab 7: Calibration

**Purpose**: Sensor calibration workflows

**Calibration Procedures:**

**1. Tendon Load Cell:**
- Zero: Remove all load → Click "Zero"
- Calibrate: Apply 1 kg weight → Enter 1.0 kg → Click "Calibrate"

**2. Tip Load Cell:**
- Zero: Remove all load → Click "Zero"
- Calibrate: Apply known weight → Enter value → Click "Calibrate"

**3. Joint Encoder:**
- Zero: Move finger to neutral position → Click "Set Zero"

**Save**: Calibration data saved to `data/calibrations/`

---

## 🧪 Test Protocols

### 1. Torque/Efficiency Test

**Purpose**: Measure transmission efficiency across torque range

**Theory**:
- Efficiency η = (F_tip × v_tip) / (V_motor × I_motor)
- Expected: 40-60% for planetary gearbox

**Parameters:**
- Torque range: 0-3000 mNm
- Steps: 10-50
- Hold duration: 2-5 seconds per step

**Output:**
- Torque vs. Force plot
- Efficiency vs. Torque plot
- CSV data

**Validation Criteria**: η > 40% at nominal torque

### 2. Hysteresis Test

**Purpose**: Measure backlash from bidirectional positioning

**Theory**:
- Backlash = |pos_approach_from_below - pos_approach_from_above|
- Sources: Gear tooth clearance + tendon stretch

**Parameters:**
- Position range: Full ROM
- Number of cycles: 5-10
- Approach velocity: Slow (minimize inertia)

**Output:**
- Hysteresis loop plot
- Backlash value (encoder counts)

**Validation Criteria**: Backlash < 200 counts (< 5° joint angle)

### 3. Stiffness Test

**Purpose**: Measure system compliance (tendon + mechanism)

**Theory**:
- Stiffness k = F / Δx (N/mm)
- Young's modulus: E = (F × L) / (A × ΔL)

**Parameters:**
- Force range: 0-50 N
- Force increment: 5 N
- Hold time: 2 seconds

**Output:**
- Force vs. Displacement plot
- Stiffness value (N/mm)

**Validation Criteria**: k > 10 N/mm

### 4. Static Hold Test

**Purpose**: Validate force stability over extended period

**Theory**:
- Creep: Force decay due to tendon stress relaxation
- Drift: Position change under constant load

**Parameters:**
- Target force: 11.8 N (1.2 kg fingertip, 50-60 N tendon)
- Duration: 30 minutes (configurable)
- Sample interval: 1 second
- Force tolerance: ±10%

**Output:**
- Force vs. Time plot
- Position vs. Time plot
- Statistics: mean force, std dev, max drift

**Validation Criteria**:
- Force error < 10%
- Creep < 2% over 30 min
- Position drift < 100 counts

### 5. Endurance Test

**Purpose**: Long-term wear and efficiency degradation

**Theory**:
- Mechanical wear in gearbox and tendon routing
- Efficiency loss over repeated cycles

**Parameters:**
- Number of cycles: 10,000
- Velocity: Moderate (100 RPM)
- ROM: Full range or partial
- Checkpoint interval: 100 cycles

**Output:**
- Efficiency vs. Cycle plot
- Position error vs. Cycle plot
- Checkpointed CSV data

**Validation Criteria**: Efficiency loss < 10% over 10k cycles

---

## 📊 Data Format

### Session Directory Structure

```
data/sessions/20251228_143022_session/
├── session.json              # Metadata
├── data/
│   ├── torque_test_001.csv
│   ├── hold_test_001.csv
│   └── endurance_test_001.csv
├── plots/
│   ├── torque_curve.png
│   ├── hysteresis.png
│   └── efficiency.png
└── config/
    └── test_config_001.json
```

### CSV Data Format

```csv
# Test Type: Static Hold Test
# Date: 2025-12-28T14:30:22
# Config: {"target_force": 11800, "duration": 1800, ...}
timestamp,torque_cmd,current,force_tendon,force_tip,position,angle
1703761815.123,0,50,100,80,0,0
1703761816.123,1500,150,11500,11800,5000,500
...
```

**Column Definitions:**
- `timestamp`: Unix time (seconds.milliseconds)
- `torque_cmd`: Commanded torque (mNm)
- `current`: Motor current (mA)
- `force_tendon`: Tendon force (mN)
- `force_tip`: Fingertip force (mN)
- `position`: Motor encoder (counts)
- `angle`: Joint angle (raw counts × 100)

### Session Metadata (JSON)

```json
{
  "session_id": "20251228_143022_session",
  "created": "2025-12-28T14:30:22",
  "platform": "teensy",
  "hardware": {
    "motor": "Maxon ECX TORQUE 22 L",
    "gearbox": "GPX 22 HP 231:1",
    "load_cell_tendon": "50kg HX711",
    "load_cell_tip": "5kg HX711",
    "encoder": "AS5600 12-bit"
  },
  "tests": [
    {
      "test_id": "torque_001",
      "test_type": "torque",
      "timestamp": "2025-12-28T14:32:15",
      "config": {...},
      "data_file": "data/torque_test_001.csv",
      "plot_files": ["plots/torque_curve.png"],
      "results": {
        "max_efficiency": 0.52,
        "avg_efficiency": 0.47,
        "max_force": 58.2
      }
    }
  ],
  "notes": "Baseline characterization of new tendon routing"
}
```

---

## 🏗️ Architecture

### Modular Design

```
┌─────────────────────────────────────┐
│         GUI Layer (tkinter)         │
│  Manual | Library | Monitor | Review │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Test Logic Layer (tests/)      │
│  Torque | Hysteresis | Stiffness... │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Hardware Layer (hardware/)        │
│  Teensy | IMX8 | RPi | Mock         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Data Layer (data/)             │
│  Logger | Exporter | Session        │
└─────────────────────────────────────┘
```

### File Structure

```
test-gui/
├── main.py                   # Entry point
├── config.json               # Runtime configuration
├── requirements.txt
│
├── hardware/                 # Hardware abstraction
│   ├── base_controller.py   # Abstract interface
│   ├── teensy_controller.py
│   ├── imx8_controller.py
│   ├── rpi_controller.py
│   ├── mock_controller.py
│   ├── safety.py            # Safety monitoring
│   └── protocol.py          # Command definitions
│
├── tests/                    # Test protocols
│   ├── base_test.py         # Abstract base
│   ├── torque_test.py
│   ├── hysteresis_test.py
│   ├── stiffness_test.py
│   ├── hold_test.py
│   ├── endurance_test.py
│   └── registry.py          # Test catalog
│
├── gui/                      # User interface
│   ├── main_window.py
│   ├── manual_tab.py
│   ├── library_tab.py
│   ├── monitor_tab.py       # NEW - Live monitoring
│   ├── review_tab.py        # NEW - Data review
│   ├── calibration_tab.py
│   ├── status_bar.py
│   └── plot_widget.py       # NEW - Reusable plots
│
├── data/                     # Data management
│   ├── logger.py            # Real-time logging
│   ├── exporter.py          # NEW - CSV/JSON export
│   ├── session.py           # NEW - Session organization
│   └── config_manager.py    # Config save/load
│
├── utils/
│   ├── serial_finder.py     # Auto-detect ports
│   └── units.py             # NEW - Unit conversions
│
├── docs/                     # Documentation
│   ├── index.html           # Web portal
│   ├── THEORY.md            # Engineering theory
│   ├── TUTORIAL.md          # Quick start guide
│   └── PLATFORM_GUIDE.md    # Porting guide
│
└── data/                     # Output (created at runtime)
    ├── sessions/
    └── calibrations/
```

**Design Principles:**
- Small files (< 300 lines each)
- Clear separation of concerns
- Platform-independent tests
- Reusable components

---

## 💻 Development

### Adding a New Test Protocol

**1. Create test file** (`protocols/my_test.py`):

```python
from .base_test import BaseTest

class MyTest(BaseTest):
    def get_name(self) -> str:
        return "My Custom Test"

    def get_parameters(self) -> dict:
        return {
            'param1': {'type': 'float', 'default': 0.0, 'min': 0, 'max': 100},
            'param2': {'type': 'int', 'default': 10, 'min': 1, 'max': 50}
        }

    def run(self, config, progress_callback=None):
        # Test implementation
        pass
```

**2. Add to registry** (`protocols/registry.py`):

```python
from .my_test import MyTest

class TestRegistry:
    def __init__(self, hardware, logger):
        self.tests = {
            # ... existing tests
            'my_test': MyTest(hardware, logger)
        }
```

**3. Done!** GUI automatically detects and displays the new test.

### Adding a New Platform

See `docs/PLATFORM_GUIDE.md` for complete guide.

**Summary:**

1. Create `hardware/yourplatform_controller.py`
2. Inherit from `HardwareController`
3. Implement all abstract methods
4. Add to factory in `hardware/__init__.py`
5. Update `config.json` with platform config

### Running Tests

**Unit Tests (pytest)**

Run all unit tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage
```

Run specific test file:
```bash
pytest tests/test_hardware.py -v
```

**System Validation**

Run comprehensive system validation:
```bash
# Full validation (all 52 checks)
python validate_system.py

# Quick validation (subset)
python validate_system.py --quick

# Test specific platform
python validate_system.py --platform teensy
```

**Platform Testing**

```bash
# Test platform abstraction
python test_platforms.py mock

# Test specific controller
python -c "from hardware import create_controller; c = create_controller('teensy'); print(c.get_platform_info())"
```

### Code Style

- Follow PEP 8
- Docstrings for all public methods
- Type hints encouraged
- Keep files < 300 lines

---

## 🐛 Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to Teensy"

**Solutions:**
- Check USB cable connection
- Verify correct port selected (use Refresh button)
- Linux: Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Check Teensy firmware is loaded

**Problem**: "Platform 'imx8' not available"

**Solutions:**
- Install socket library (should be built-in)
- Check network connectivity: `ping 192.168.1.100`
- Verify IMX8 firmware listening on port 5000

### Motor Not Moving

**Problem**: Motor enabled but doesn't move

**Solutions:**
- Check motor driver power supply (24V)
- Verify motor driver enable signal
- Check current limit not set too low
- Review safety limits (position, force)
- Check PID parameters configured

### Data Logging Errors

**Problem**: "Permission denied" when logging

**Solutions:**
- Ensure `data/sessions/` directory exists
- Check write permissions: `chmod 755 data/`
- Close any programs with files open (Excel, etc.)

### Plot Performance Issues

**Problem**: GUI lags during high-speed tests

**Solutions:**
- Reduce plot refresh rate (100ms → 200ms)
- Decrease plot window size (30s → 15s)
- Use data decimation (plot every 10th point)
- Disable live plots, review post-test

### Calibration Issues

**Problem**: Load cell readings unstable

**Solutions:**
- Check ADC connections (HX711/ADS1256)
- Verify power supply stable (5V regulation)
- Zero load cell with nothing attached
- Apply known weight slowly (avoid impact)
- Repeat calibration 2-3 times, average

---

## 📚 References

### Engineering Theory

See `docs/THEORY.md` for comprehensive theory:
- Tendon mechanics and force transmission
- Material properties (Young's modulus, creep, hysteresis)
- Gearbox efficiency and backlash
- Motor control (PID, motion profiles)
- Test methodology and validation criteria

### Tutorials

- **Quick Start**: `docs/TUTORIAL.md`
- **Platform Porting**: `docs/PLATFORM_GUIDE.md`
- **Web Documentation**: `docs/index.html` (works offline, open in any browser)

### Historical Documentation

Archived planning documents and status reports can be found in `docs/archive/`:
- `PROJECT_STATUS.md` - Original project status (now in README)
- `PHASE_7_SUMMARY.md` - Phase 7 completion report
- Development planning documents

### External Resources

**Motor & Gearbox:**
- [Maxon ECX TORQUE 22 L Datasheet](https://www.maxongroup.com)
- [GPX 22 HP Gearbox Specs](https://www.maxongroup.com)

**Sensors:**
- [HX711 Load Cell Amplifier](https://github.com/bogde/HX711)
- [AS5600 Magnetic Encoder](https://ams.com/as5600)

**Protocols:**
- [Teensy 4.1 Documentation](https://www.pjrc.com/teensy/)
- [I2C Protocol Specification](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)

### Scientific Literature

- Salisbury, J. K. (1982). "Kinematic and Force Analysis of Articulated Hands"
- Bicchi, A. (2000). "Hands for Dexterous Manipulation and Robust Grasping"
- Dollar, A. M. (2014). "Principles of Human and Robotic Hand Design"

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Open Pull Request

**Development guidelines:**
- Keep files < 300 lines
- Add tests for new features
- Update documentation
- Follow existing code style

---

## ✨ Acknowledgments

- Maxon Motor AG for motor/gearbox specifications
- Open-source community for Python libraries (numpy, matplotlib, pandas)
- Teensy/PJRC for versatile microcontroller platform

---

## 📊 Project Status

**Current Version**: 1.0.0 (Phase 7 - Polish & Integration)

**Completed Phases:**
- ✅ Phase 1: Foundation (Connection, Manual Control, Safety)
- ✅ Phase 2: Calibration Workflows
- ✅ Phase 3: Test Framework + Torque Test
- ✅ Phase 4: Complete Test Suite (5 protocols)
- ✅ Phase 4.5: Documentation + Platform Abstraction
- ✅ Phase 5: Visualization (Live Monitoring)
- ✅ Phase 6: Data Review & Export
- 🔄 Phase 7: Polish & Integration (In Progress)
- ⏳ Phase 8: Platform Testing (Pending)

**Metrics:**
- **Files**: 36+
- **Lines of Code**: ~10,000+
- **Test Protocols**: 5 automated + 11 specialized
- **Supported Platforms**: 4 (Teensy, IMX8, RPi, Mock)
- **Documentation Pages**: 4 (Theory, Tutorial, Platform Guide, Web Portal)

---

**Last Updated**: 2025-12-28
