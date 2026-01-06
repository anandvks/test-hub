# GUI Overview

Complete guide to the Test Bench GUI interface.

---

## Main Window

The application features a tabbed interface with 7 functional tabs:

1. **Manual Control** - Direct motor control and testing
2. **Test Library** - Automated test protocols
3. **Live Monitor** - Real-time data visualization
4. **Data Review** - Historical data analysis
5. **Calibration** - Sensor calibration workflows
6. **Tendon Testing** - Specialized tendon tests
7. **Finger Testing** - Complete finger validation

---

## Tab 1: Manual Control

### Features

- **Control Modes**: Position, Velocity, Torque, Current
- **Real-time Feedback**: Live sensor readings at 50-100 Hz
- **Safety Controls**: Emergency stop, enable/disable
- **Connection Management**: Platform selection and connection

### Controls

- **Position Control**: Set target position in encoder counts
- **Velocity Control**: Set target velocity in counts/sec
- **Torque Control**: Set target torque in mNm
- **Current Control**: Set target current in mA

---

## Tab 2: Test Library

### Available Tests

1. **Torque Efficiency Test**
2. **Hysteresis Test**
3. **Stiffness Test**
4. **Static Hold Test**
5. **Endurance Test**

### Workflow

1. Select test from list
2. Configure parameters (sliders/inputs)
3. Review estimated duration
4. Click "Run Test"
5. Monitor progress
6. View results summary

---

## Tab 3: Live Monitor

### Real-Time Plots

- Force vs. Time (both load cells)
- Position vs. Time
- Current vs. Time
- Velocity vs. Time

### Statistics

- Mean, RMS, Peak values
- Sample rate indicator
- Data quality metrics

---

## Tab 4: Data Review

### Features

- Session browser (tree view)
- Plot multiple variables
- Export capabilities (CSV, JSON, PNG)
- Session comparison

### Usage

1. Select session from tree
2. Choose variables to plot
3. Apply filters (time range, decimation)
4. Export or analyze

---

## Tab 5: Calibration

### Calibration Workflows

**Load Cell Calibration:**

1. Zero reading (no load)
2. Apply known weight
3. Record ADC value
4. Calculate scale factor
5. Verify with test weight

**Encoder Calibration:**

1. Home to reference position
2. Set zero point
3. Verify counts per revolution
4. Test motion

---

## Safety Features

### Hardware Protection

- Emergency stop button
- Current limit monitoring
- Position limits
- Timeout detection

### Software Protection

- Velocity limit checking
- Force threshold monitoring
- Watchdog timer
- Automatic disable on error

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quit application |
| `Space` | Emergency stop |
| `E` | Enable motor |
| `D` | Disable motor |
| `R` | Refresh ports |

---

## Status Bar

Bottom status bar shows:

- Connection status
- Motor enable state
- Safety system status
- Current limits
- Last error message

---

## Next Steps

- [Tutorial](tutorial.md) - Step-by-step guide
- [Quick Start](../getting-started/quick-start.md) - Get started quickly
- [Test Protocols](../technical/test-protocols.md) - Learn about tests
