# Test Bench Quick Start Tutorial

**Get up and running in 30 minutes**

This tutorial guides you through the complete workflow: calibration → static hold test → results review.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [First Run - Connection and Calibration](#2-first-run---connection-and-calibration)
3. [Manual Control - Verify System](#3-manual-control---verify-system)
4. [Automated Test - Static Hold Validation](#4-automated-test---static-hold-validation)
5. [Review Results](#5-review-results)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Prerequisites

### Hardware Requirements

Ensure you have the following components connected:

**Motor Assembly**:
- [ ] Maxon ECX TORQUE 22 L motor
- [ ] Maxon GPX 22 HP gearbox (231:1)
- [ ] Maxon ESCON 24/2 motor driver
- [ ] 24V power supply (2-3A minimum)

**Sensors**:
- [ ] Tendon load cell (0-200 N range) connected to ADC
- [ ] Fingertip load cell (0-20 N range) connected to ADC
- [ ] AS5600 magnetic encoder for joint angle (optional)

**Controller**:
- [ ] Teensy 4.1 microcontroller (or IMX8, Raspberry Pi, Mock for simulation)
- [ ] USB cable for serial communication

**Physical Setup**:
- [ ] Tendon routed through pulleys/guides
- [ ] Tendon attached to motor spool (10 mm radius recommended)
- [ ] Fingertip force measurement point established
- [ ] Safety: Clear workspace, e-stop accessible

### Software Installation

**Python Dependencies**:

```bash
# Navigate to project directory
cd /path/to/test-gui

# Install required packages
pip install -r requirements.txt
```

**Requirements include**:
- `numpy` >= 1.24.0 (numerical computing)
- `scipy` >= 1.10.0 (signal processing)
- `pandas` >= 2.0.0 (data analysis)
- `matplotlib` >= 3.7.0 (plotting)
- `pyserial` >= 3.5 (serial communication)

**Firmware** (if using Teensy):
- Upload firmware to Teensy 4.1 that implements serial protocol
- Verify connection with serial monitor (115200 baud)
- Test `PING` command returns `ACK PONG`

### Connection Diagram

```
┌─────────────┐
│   24V PSU   │
└──────┬──────┘
       │
       v
┌─────────────┐      USB        ┌──────────────┐
│ ESCON Driver├─────────────────>│  Teensy 4.1  │
└──────┬──────┘                  └──────┬───────┘
       │                                │
       │ Motor Cables                   │ Sensor Wires
       │                                │
       v                                v
┌─────────────┐                  ┌─────────────┐
│  ECX Motor  │                  │ Load Cells  │
│  + Gearbox  │                  │  + Encoder  │
└──────┬──────┘                  └─────────────┘
       │
       │ Tendon
       │
       v
  [ Finger Mechanism ]
```

### Safety Precautions

⚠️ **IMPORTANT SAFETY WARNINGS**:

- **Current Limit**: Set to 1.0 A max (protects gearbox)
- **Force Limit**: Keep fingertip force < 20 N during setup
- **E-Stop**: Keep emergency stop button accessible at all times
- **Moving Parts**: Keep hands clear of pinch points when motor is enabled
- **Power**: Verify 24V supply polarity before connecting
- **First Run**: Start with low gains and slow speeds

---

## 2. First Run - Connection and Calibration

### Step 2.1: Launch the GUI

Open a terminal and navigate to the project directory:

```bash
cd /path/to/test-gui
python3 main.py
```

The GUI window should appear (1400×900 resolution):

```
┌────────────────────────────────────────────────────┐
│  Test Bench Control - Tendon-Driven Hand          │
├────────────────────────────────────────────────────┤
│  [Manual] [Tendon] [Finger] [Library] [Monitor]   │
│  [Review] [Calibration]                            │
│ ┌──────────────────────────────────────────────────┤
│ │                                                  │
│ │         Tab Content Area                         │
│ │                                                  │
│ └──────────────────────────────────────────────────┤
├────────────────────────────────────────────────────┤
│ Motor: OFF │ Curr: 0.0A │ Force: 0N │ 🟢 Safe    │
└────────────────────────────────────────────────────┘
```

### Step 2.2: Select Platform and Connect

**Platform Selection** (in config.json or GUI):

The system supports multiple hardware platforms. For this tutorial:
- **Teensy**: Serial USB connection (most common)
- **Mock**: Simulated hardware (no physical setup needed)
- **IMX8**: Ethernet connection
- **Raspberry Pi**: SPI/I2C connection

To select platform, edit `data/config.json`:

```json
{
  "hardware": {
    "platform": "teensy"  // Change to "mock" for simulation
  }
}
```

**For Teensy (Serial)**:

1. Navigate to **Manual Control** tab
2. In the **Connection** panel:
   - **Port**: Select from dropdown (auto-detects `/dev/ttyACM0` or `COM3`)
   - **Baudrate**: 115200 (default)
3. Click **Connect**
4. Status bar should show: `Motor: CONNECTED | 🟢 Safe`

**For Mock (Simulation)**:

1. Set platform to `"mock"` in config
2. Click **Connect** (succeeds immediately, no port selection needed)
3. GUI will simulate sensor data for testing without hardware

### Step 2.3: Navigate to Calibration Tab

Click the **Calibration** tab. You'll see three columns:

```
┌──────────────┬──────────────┬──────────────┐
│ Tendon Load  │  Tip Load    │   Joint      │
│    Cell      │    Cell      │   Encoder    │
├──────────────┼──────────────┼──────────────┤
│ Raw: 12543   │ Raw: 8421    │ Raw: 2048    │
│ Force: 0.0 N │ Force: 0.0 N │ Angle: 0.0°  │
│              │              │              │
│ [Zero]       │ [Zero]       │ [Zero]       │
│ [Calibrate]  │ [Calibrate]  │ [Calibrate]  │
│ [Test]       │ [Test]       │ [Test]       │
│              │              │              │
│ Status:      │ Status:      │ Status:      │
│ ⚠ Not Cal.  │ ⚠ Not Cal.  │ ⚠ Not Cal.  │
└──────────────┴──────────────┴──────────────┘
```

### Step 2.4: Calibrate Tendon Load Cell

**Zero Offset**:
1. Ensure **no tension** on tendon (motor disabled, finger relaxed)
2. Click **[Zero]** under Tendon Load Cell
3. Raw value is saved as zero offset
4. Force display should now read `0.0 N`

**Calibration**:
1. Hang a known weight on the tendon (e.g., **1.0 kg** = **9.81 N**)
   - Use a calibrated weight or water bottle
   - Ensure weight is fully supported by tendon
2. Enter calibration weight: `1.0` (kg)
3. Click **[Calibrate]**
4. System calculates calibration factor:
   ```
   K_calib = 9.81 N / (ADC_current - ADC_zero)
   ```
5. Status changes to: `✓ Calibrated`

**Test**:
1. Click **[Test]**
2. Apply and remove weight several times
3. Verify force reading matches applied weight (±0.1 N)

**Calibration data saved to**: `data/calibrations/load_cell_tendon.json`

### Step 2.5: Calibrate Tip Load Cell

Repeat the same procedure for the fingertip load cell:

1. **Zero**: No force on fingertip → Click **[Zero]**
2. **Calibrate**: Place 0.5 kg weight on fingertip → Enter `0.5` → Click **[Calibrate]**
3. **Test**: Verify readings with known weights

**Note**: Use smaller weights for tip calibration (0.2-1.0 kg range).

**Calibration data saved to**: `data/calibrations/load_cell_tip.json`

### Step 2.6: Calibrate Joint Encoder (Optional)

If using AS5600 magnetic encoder for joint angle:

1. Move finger to **neutral position** (e.g., fully extended)
2. Click **[Zero]** under Joint Encoder
3. This position is now defined as 0°

**Calibration data saved to**: `data/calibrations/encoder_joint.json`

### Step 2.7: Verify Calibration

In the **Status** section at bottom of each column, you should see:

```
✓ Calibrated
Zero: 12543
Factor: 0.0785 N/count
Last: 2025-12-28 14:23
```

All three sensors should show **✓ Calibrated** before proceeding.

---

## 3. Manual Control - Verify System

### Step 3.1: Navigate to Manual Control Tab

Click **Manual Control** tab. Layout:

```
┌─────────────────────────┬────────────────────────┐
│  Control Panel (Left)   │  Live Plots (Right)    │
├─────────────────────────┼────────────────────────┤
│ Connection:             │  Position vs Time      │
│ Port: /dev/ttyACM0      │  ┌──────────────────┐  │
│ [Connected]             │  │     ▁▂▃▄▅▆▇█     │  │
│                         │  └──────────────────┘  │
│ Motor Control:          │                        │
│ Mode: Position ▼        │  Force vs Time         │
│ Target: [5000] counts   │  ┌──────────────────┐  │
│ [━━━━━━━━━━━] Slider    │  │     ▁▂▃▄▅▆▇█     │  │
│                         │  └──────────────────┘  │
│ [Enable Motor]          │                        │
│ [Disable Motor]         │  Current vs Time       │
│ [EMERGENCY STOP] ◼      │  ┌──────────────────┐  │
│                         │  │     ▁▂▃▄▅▆▇█     │  │
│ Safety Limits:          │  └──────────────────┘  │
│ Current: 1.0 A          │                        │
│ Force: 20 N             │                        │
│ Position: 0-10000       │                        │
│                         │                        │
│ Sensor Readings:        │                        │
│ Position: 0 counts      │                        │
│ Velocity: 0 RPM         │                        │
│ Current: 0.05 A         │                        │
│ Force (Tendon): 0.0 N   │                        │
│ Force (Tip): 0.0 N      │                        │
│ Joint Angle: 0.0°       │                        │
│                         │                        │
│ [Start Logging]         │                        │
└─────────────────────────┴────────────────────────┘
```

### Step 3.2: Enable Motor

1. **Set Safety Limits** (recommended for first run):
   - Current: `0.5 A` (half of normal limit)
   - Force: `10 N` (conservative)
   - Position: `0` to `5000` (half range)

2. **Select Control Mode**: `Position` (dropdown)

3. **Set Initial Target**: `0` (fully extended)

4. Click **[Enable Motor]**
   - Status bar changes to: `Motor: ENABLED`
   - Motor should hold current position

### Step 3.3: Test Position Control

**Slow Movement Test**:

1. Drag slider to `1000` counts
   - Motor should move smoothly
   - Live plots show position ramping up
   - Watch for any jerking or binding

2. Observe sensor readings:
   - Position should reach ~1000 counts (±50 due to backlash)
   - Force should increase slightly as tendon tensions
   - Current should spike briefly during movement, then settle

3. Return to `0`
   - Motor returns to start position

**Full Range Test** (if no issues observed):

1. Gradually increase safety limit: `Position Max: 10000`
2. Move through positions: `0 → 2500 → 5000 → 7500 → 10000`
3. Monitor force at each position
   - Should stay below 10 N for gentle movements

### Step 3.4: Test Safety Limits

**Current Limit Test**:

1. Set `Current Limit: 0.3 A` (very low, intentionally)
2. Command a large position change: `0 → 5000`
3. Motor should hit current limit and trigger warning
4. **Expected**: Status bar shows `⚠ Current Limit` and auto e-stop
5. Acknowledge warning, re-enable motor
6. Reset current limit to `1.0 A`

**Force Limit Test** (optional, requires load):

1. Manually apply force to fingertip while holding position
2. When force exceeds 10 N, e-stop should trigger
3. This validates safety monitoring is active

### Step 3.5: Test Emergency Stop

1. With motor enabled and moving
2. Click **[EMERGENCY STOP]** button (or press `F1` hotkey)
3. **Expected**:
   - Motor disables immediately (< 10 ms)
   - Alert dialog shows current sensor state
   - User must acknowledge before resuming

4. Re-enable motor to continue

### Step 3.6: Data Logging Test

1. Click **[Start Logging]**
   - GUI prompts for filename or auto-generates timestamp
   - Default: `data/sessions/manual_YYYYMMDD_HHMMSS.csv`

2. Perform a few position changes while logging

3. Click **[Stop Logging]**

4. Verify CSV file created:
   ```bash
   ls -l data/sessions/
   cat data/sessions/manual_20251228_142305.csv | head
   ```

**Expected CSV format**:
```csv
# Test: Manual Control
# Date: 2025-12-28T14:23:05
timestamp,position,velocity,current,force_tendon,force_tip,angle_joint
1703770985.123,0,0,0.05,0.1,0.0,0
1703770986.234,1000,120,0.35,5.2,1.2,15
...
```

### Step 3.7: Disable Motor

When testing is complete:

1. Return to safe position: `Target: 0`
2. Click **[Disable Motor]**
3. Status bar: `Motor: OFF`

**System is now ready for automated testing.**

---

## 4. Automated Test - Static Hold Validation

### Step 4.1: Navigate to Test Library Tab

Click **Test Library** tab. Layout:

```
┌──────────────────────┬────────────────────────────┐
│  Test Catalog (Left) │  Configuration (Right)     │
├──────────────────────┼────────────────────────────┤
│ Available Tests:     │  Test: Static Hold Test    │
│                      │  ──────────────────────────│
│ [x] Torque/Eff       │  Target Force (N):         │
│ [ ] Hysteresis       │  [11.8] ━━━━━━━━           │
│ [x] Stiffness        │  Range: 0.0 - 50.0         │
│ [x] Static Hold      │                            │
│ [ ] Endurance        │  Duration (min):           │
│                      │  [5.0] ━━━━━━━━            │
│ Description:         │  Range: 1.0 - 120.0        │
│ ────────────────     │                            │
│ Hold constant force  │  Sample Interval (s):      │
│ for extended         │  [1.0] ━━━━━━━━            │
│ duration. Validates  │  Range: 0.1 - 10.0         │
│ 1.2kg/finger target  │                            │
│ and monitors         │  Force Tolerance (%):      │
│ stability.           │  [10.0] ━━━━━━━━           │
│                      │  Range: 1.0 - 50.0         │
│ Estimated Duration:  │                            │
│ 5.2 minutes          │  Max Drift (counts):       │
│                      │  [100] ━━━━━━━━            │
│ [Run Selected]       │  Range: 10 - 1000          │
│ [Stop]               │                            │
│ [Pause/Resume]       │  [Reset to Defaults]       │
│                      │  [Run Test]                │
├──────────────────────┴────────────────────────────┤
│ Progress:                                         │
│ [━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━] 45%      │
│ Status: Holding force... 2.3/5.0 min              │
├───────────────────────────────────────────────────┤
│ Results:                                          │
│                                                   │
│ Starting Static Hold Test...                     │
│ Applying 11.8N force...                          │
│ Holding force...                                 │
│ T+1min: Force=11.7N, Drift=12 counts             │
│ T+2min: Force=11.6N, Drift=18 counts             │
│ ...                                              │
└───────────────────────────────────────────────────┘
```

### Step 4.2: Select Static Hold Test

1. In the **Test Catalog** (left panel), click **Static Hold Test**
2. Description appears showing test purpose and method
3. **Estimated Duration** updates based on parameters

### Step 4.3: Configure Test Parameters

For a **quick tutorial** (5 minute test instead of full 30 min):

**Target Force**: `11.8 N` (default, equivalent to 1.2 kg fingertip)
- This validates the target force capability
- Adjust if needed based on your mechanism

**Duration**: `5.0 min` (shortened for tutorial)
- Full validation uses 30 min
- 5 min is sufficient to detect initial creep

**Sample Interval**: `1.0 s`
- How often to log data
- 1 Hz is good balance between resolution and file size

**Force Tolerance**: `10.0 %`
- Acceptable force variation
- Warning triggers if actual force deviates > 10% from target

**Max Drift**: `100 counts`
- Maximum position creep allowed
- Warning triggers if position drifts > 100 counts from start

**Estimated Duration**: Updates to `~5.2 minutes`

### Step 4.4: Run the Test

1. **Verify motor is disabled** (safety check before automated test)

2. Click **[Run Test]**

3. **Confirmation dialog** (for long tests):
   ```
   This test will take approximately 5.2 minutes.
   Continue?
   [Yes] [No]
   ```

4. Click **[Yes]**

### Step 4.5: Monitor Progress

**Progress Bar**:
- Shows completion: `0% → 100%`
- Updates every second

**Status Messages** (in Results panel):
```
Starting Static Hold Test...
Applying 11.8N force...          [Progress: 5%]
Holding force...                 [Progress: 10%]
T+1min: Force=11.7N, Drift=12    [Progress: 30%]
T+2min: Force=11.6N, Drift=18    [Progress: 50%]
T+3min: Force=11.5N, Drift=23    [Progress: 70%]
T+4min: Force=11.4N, Drift=27    [Progress: 90%]
T+5min: Force=11.3N, Drift=31    [Progress: 100%]
```

**Live Observations**:
- **Force should remain stable** (~11.8 N ± 1.0 N)
- **Drift should be minimal** (< 100 counts)
- **Current should be steady** (no spikes indicate stable torque)

**Warnings** (if limits exceeded):
```
WARNING: Force error 12.3% exceeds tolerance
```

If warnings appear frequently:
- Tendon may be slipping
- Creep rate is too high (consider steel cable)
- PID gains may need tuning

### Step 4.6: Test Completion

When test finishes:

```
Test complete

================================
TEST RESULTS
================================

Summary:
  target_force_N: 11.8
  avg_force_N: 11.52
  force_std_N: 0.18
  max_drift_counts: 31
  avg_current_A: 0.42
  max_force_error_percent: 4.2

Data logged to: data/sessions/static_hold_20251228_142512.csv
```

**Interpretation**:
- ✓ **avg_force_N**: Close to target (11.52 N vs. 11.8 N)
- ✓ **force_std_N**: Low variation (0.18 N = 1.5%)
- ✓ **max_drift**: Within limit (31 < 100 counts)
- ✓ **max_force_error**: Within tolerance (4.2% < 10%)

**PASS**: System meets validation criteria for 5-minute hold!

For full validation, repeat with `Duration: 30 min`.

---

## 5. Review Results

### Step 5.1: Locate Log File

Test results are saved to `data/sessions/` directory:

```bash
ls -lh data/sessions/
```

Output:
```
-rw-r--r-- 1 user user 12K Dec 28 14:30 static_hold_20251228_142512.csv
```

### Step 5.2: Open in Spreadsheet Software

**Excel / LibreOffice Calc**:

1. Open file: `static_hold_20251228_142512.csv`
2. Data loads with columns:
   ```
   time_sec | position | force_tip | current | drift | force_error_percent
   ```

**Preview**:
```
time_sec  position  force_tip  current  drift  force_error_percent
0.0       5423      11.8       0.45     0      0.0
1.0       5424      11.7       0.44     1      0.8
2.0       5425      11.7       0.43     2      0.8
...
300.0     5454      11.3       0.42     31     4.2
```

### Step 5.3: Create Plots

**Plot 1: Force vs. Time**

1. Select columns: `time_sec` (X-axis), `force_tip` (Y-axis)
2. Create **Line Chart**
3. **Expected**: Relatively flat line around 11.8 N
4. Slight downward trend indicates creep

**Plot 2: Position Drift vs. Time**

1. Select columns: `time_sec`, `drift`
2. Create **Line Chart**
3. **Expected**: Gradual increase (tendon stretching)
4. Should stay below 100 counts

**Plot 3: Force Error vs. Time**

1. Select columns: `time_sec`, `force_error_percent`
2. Create **Line Chart**
3. **Expected**: Stays below 10% tolerance line
4. Spikes indicate control issues or disturbances

### Step 5.4: Validation Check

Compare results to acceptance criteria:

| Metric | Target | Measured | Status |
|--------|--------|----------|--------|
| Average Force | 11.8 N | 11.52 N | ✓ PASS |
| Force Stability | < 2% drop | 4.2% drop | ⚠ MARGINAL (5 min test) |
| Max Drift | < 100 counts | 31 counts | ✓ PASS |
| Force Variation | < 10% | 4.2% | ✓ PASS |

**Note**: 4.2% force drop over 5 minutes is acceptable. For 30-minute test, expect 10-15% total drop (within spec if < 20%).

### Step 5.5: Export Summary Report

For documentation, create summary report:

**Static Hold Test Report**

```
Test Date: 2025-12-28 14:25:12
Duration: 5.0 minutes
Target Force: 11.8 N (1.2 kg fingertip)

RESULTS:
✓ Average Force: 11.52 N (97.6% of target)
✓ Standard Deviation: 0.18 N (1.5%)
✓ Maximum Drift: 31 counts (31% of limit)
✓ Force Error: 4.2% (42% of tolerance)

VERDICT: PASS

NOTES:
- Creep rate: 0.84% per minute
- Current stable at 0.42 A
- No safety violations
- Recommend 30-minute validation test

Attachments:
- force_vs_time.png
- drift_vs_time.png
- static_hold_20251228_142512.csv
```

---

## 6. Troubleshooting

### Connection Issues

**Problem**: "Port not found" or "Connection failed"

**Solutions**:
- Check USB cable connection
- Verify Teensy is powered (LED should be on)
- Try different USB port
- Check port permissions (Linux):
  ```bash
  sudo chmod 666 /dev/ttyACM0
  # Or add user to dialout group:
  sudo usermod -a -G dialout $USER
  # Log out and back in
  ```
- Verify firmware is uploaded to Teensy

**Problem**: "Connected but no response to PING"

**Solutions**:
- Verify baudrate is 115200
- Check firmware serial protocol implementation
- Try manual serial test:
  ```bash
  screen /dev/ttyACM0 115200
  # Type: PING
  # Should see: ACK PONG
  ```

### Calibration Issues

**Problem**: "Force readings are negative"

**Solution**:
- Re-zero load cell with no load
- Check load cell wiring (swap + and -)
- Verify ADC reference voltage

**Problem**: "Force readings don't match applied weight"

**Solutions**:
- Re-run calibration with accurate known weight
- Check that weight is fully supported by tendon (not resting on mechanism)
- Verify load cell orientation (compression vs. tension)
- Use multiple calibration points (0, 0.5, 1.0, 2.0 kg)

**Problem**: "Readings are noisy"

**Solutions**:
- Enable ADC filtering in firmware
- Increase sample averaging (e.g., average 10 samples)
- Check for ground loops or EMI
- Use shielded cables for ADC signals

### Motor Control Issues

**Problem**: "Motor doesn't move when enabled"

**Solutions**:
- Verify ESCON driver is powered (LED indicator)
- Check motor cable connections
- Increase current limit (may be too restrictive)
- Test ESCON with Maxon EPOS Studio software
- Check direction signal (motor may be in wrong mode)

**Problem**: "Motor oscillates or vibrates"

**Solutions**:
- Reduce PID gains (especially $K_p$ and $K_d$)
- Check for mechanical binding or friction
- Verify encoder is working (check counts changing smoothly)
- Reduce control loop frequency if too aggressive

**Problem**: "Position error is large (>500 counts)"

**Solutions**:
- Check for tendon slack or slipping on spool
- Verify encoder alignment (magnetic sensor to magnet distance)
- Increase PID gains to improve tracking
- Check for gearbox binding

### Test Failures

**Problem**: "Force drops rapidly during hold test"

**Causes & Solutions**:
- **Tendon creep**: Pre-stretch tendon with break-in cycling (100-1000 cycles)
- **Slipping**: Check spool attachment, may need set screw or adhesive
- **Thermal drift**: Motor heating causes torque reduction—add active cooling

**Problem**: "Excessive drift (>100 counts)"

**Causes & Solutions**:
- **Tendon compliance**: Use stiffer material (steel cable)
- **Gearbox backlash**: Consider precision gearbox upgrade
- **PID control**: Ensure position controller is active (not just torque mode)

**Problem**: "High backlash (>200 counts) in hysteresis test"

**Causes & Solutions**:
- **Gearbox**: Inherent backlash of GPX 22 HP is ~1.5° (acceptable)
- **Tendon**: Pre-tension to eliminate slack
- **Compliance**: Shorten tendon routing to reduce stretch

### Data Logging Issues

**Problem**: "CSV file is empty or corrupted"

**Solutions**:
- Verify write permissions to `data/sessions/` directory
- Check disk space
- Ensure test ran to completion (not interrupted)
- Check Python logging module for errors

**Problem**: "Missing data points in CSV"

**Solutions**:
- Reduce sample interval (currently 1 s, try 0.5 s)
- Check for buffer overflows in logger
- Verify sensor reading function doesn't block

### Safety System Issues

**Problem**: "E-stop triggers unexpectedly"

**Causes**:
- Check safety limits (may be too conservative)
- Verify sensor noise isn't causing false triggers
- Inspect safety monitor logic (10 Hz loop may see transients)

**Solution**:
- Increase limit margins slightly
- Add hysteresis to safety checks (e.g., trigger at 110%, release at 90%)
- Filter sensor readings before safety check

---

## Next Steps

Congratulations! You've completed the quick start tutorial. You can now:

1. **Run Full Validation Suite**:
   - 30-minute static hold test
   - Hysteresis test (10 positions across range)
   - Torque/Efficiency test (map $\eta(\tau)$ curve)
   - Endurance test (10,000 cycles overnight)

2. **Explore Other Tabs**:
   - **Tendon Testing**: Compliance, Creep, Friction tests
   - **Finger Testing**: ROM, Grip strength, Precision grasp
   - **Live Monitor**: Real-time plotting during automated tests
   - **Data Review**: Browse and export historical test data

3. **Advanced Configuration**:
   - PID tuning for better position control
   - Motion profiles (trapezoidal vs. S-curve)
   - Cycle testing (automated flex-extend sequences)

4. **Documentation**:
   - Read [THEORY.md](THEORY.md) for engineering background
   - Read [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md) to add new hardware platforms
   - Check [PROJECT_STATUS.md](../PROJECT_STATUS.md) for system architecture

---

## Quick Reference Commands

**Emergency Stop**: `F1` hotkey or red button

**Port Permissions** (Linux):
```bash
sudo usermod -a -G dialout $USER
```

**Verify Serial**:
```bash
screen /dev/ttyACM0 115200
```

**Launch GUI**:
```bash
cd /path/to/test-gui
python3 main.py
```

**Find Log Files**:
```bash
ls -lh data/sessions/
```

**Test with Mock Controller** (no hardware):
```json
// In data/config.json:
{
  "hardware": {
    "platform": "mock"
  }
}
```

---

## Support

If you encounter issues not covered in this tutorial:

1. Check [THEORY.md](THEORY.md) Section 8 for validation criteria
2. Review [Troubleshooting](#6-troubleshooting) section
3. Inspect Python console output for error messages
4. Check firmware serial monitor for communication issues
5. Contact test bench support team

---

*Tutorial Version: 1.0*
*Last Updated: 2025-12-28*
*Estimated Completion Time: 30 minutes*
