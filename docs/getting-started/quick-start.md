# Quick Start

Get up and running with Test Bench GUI in 30 minutes.

---

## Prerequisites

- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Python**: 3.8 or later
- **Hardware**: USB port (Teensy), Ethernet (IMX8), or GPIO (Raspberry Pi)

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/anandvks/test-hub.git
cd test-hub
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core dependencies:**

- numpy >= 1.24.0
- scipy >= 1.10.0
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- pyserial >= 3.5 (for Teensy)

---

## Configuration

### Select Platform

Edit `config.json` to choose your hardware platform:

```json
{
  "hardware": {
    "platform": "teensy"
  }
}
```

**Available platforms:**

- `teensy` - Teensy 4.1 (Serial/USB)
- `imx8` - IMX8 processor (Ethernet/TCP)
- `rpi` - Raspberry Pi (SPI/I2C)
- `mock` - Simulator (no hardware needed)

---

## First Test

### 1. Launch GUI

```bash
python3 main.py
```

### 2. Connect Hardware

1. Go to **Manual Control** tab
2. Click **Refresh** to detect available ports
3. Select your device from the dropdown
4. Click **Connect**

### 3. Calibrate Sensors

1. Navigate to **Calibration** tab
2. Follow the calibration wizard:
   - Load cell calibration (apply known weights)
   - Encoder calibration (home position)

### 4. Run Static Hold Test

1. Navigate to **Test Library** tab
2. Select **Static Hold Test** from the list
3. Configure parameters:
   - **Target force**: 11.8 N (1.2 kg fingertip force)
   - **Duration**: 5 minutes
   - **Ramp rate**: 100 mN/s
4. Click **Run Test**
5. Monitor progress in **Live Monitor** tab

### 5. Review Results

1. Navigate to **Data Review** tab
2. Select your test session from the tree view
3. View real-time plots:
   - Force vs. Time
   - Position vs. Time
   - Current vs. Time
4. Export data as CSV/JSON/PNG

---

## Next Steps

- Read the [Tutorial](../user-guide/tutorial.md) for detailed usage
- Learn about [Test Protocols](../technical/test-protocols.md)
- Explore [Hardware Setup](../user-guide/hardware-setup.md) for wiring diagrams

---

## Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to Teensy"

**Solutions:**

- Check USB cable connection
- Verify correct port selected (click Refresh)
- Linux: Add user to dialout group: `sudo usermod -a -G dialout $USER`
- Check Teensy firmware is loaded

### Motor Not Moving

**Problem**: Motor enabled but doesn't move

**Solutions:**

- Check 24V power supply to motor driver
- Verify motor driver enable signal
- Check current limit not set too low
- Review safety limits (position, force)
- Verify PID parameters configured

---

## Support

For more help, see:

- [Tutorial](../user-guide/tutorial.md) - Complete user guide with detailed troubleshooting
- [GUI Overview](../user-guide/gui-overview.md) - Interface guide
- [GitHub Issues](https://github.com/anandvks/test-hub/issues) - Report bugs
