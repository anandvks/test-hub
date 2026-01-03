# Test Bench Theory and Methodology

**Engineering-Level Documentation for Tendon-Driven Robotic Hand Validation**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Tendon Mechanics](#2-tendon-mechanics)
3. [Material Properties](#3-material-properties)
4. [Gearbox and Transmission](#4-gearbox-and-transmission)
5. [Motor Control Theory](#5-motor-control-theory)
6. [Force Measurement and Calibration](#6-force-measurement-and-calibration)
7. [Test Methodology](#7-test-methodology)
8. [Validation Criteria](#8-validation-criteria)

---

## 1. Introduction

### Overview

Tendon-driven robotic hands offer significant advantages over traditional rigid-link mechanisms: reduced weight at the end effector, improved dexterity through underactuation, and safer human-robot interaction due to inherent compliance. However, these benefits come with unique challenges in force transmission, position accuracy, and long-term reliability.

This test bench validates the performance of a tendon-driven finger mechanism powered by a Maxon ECX TORQUE 22 L motor with GPX 22 HP gearbox (231:1 reduction ratio), targeting **5-6 kg static hold capability** at the fingertip.

### Why Validation Testing is Critical

Unlike rigid mechanisms where kinematics and dynamics are well-defined, cable-driven systems exhibit:

- **Hysteresis**: Backlash from gearbox play and tendon elasticity causes different positions when approaching from opposite directions
- **Creep**: Viscoelastic tendon materials elongate under sustained load, reducing force over time
- **Friction**: Routing paths through pulleys and conduits cause energy loss and position-dependent resistance
- **Compliance**: Tendon stretch and gearbox deflection reduce stiffness, affecting force control accuracy

These non-idealities cannot be predicted from datasheets alone—empirical validation is essential.

### Testing Objectives

This test bench quantifies:

1. **Maximum force capability**: Can the system achieve 1.2 kg per finger (6 kg total for 5 fingers)?
2. **Force stability**: Does creep cause unacceptable force degradation during sustained grips?
3. **Position accuracy**: What is the bidirectional repeatability error (hysteresis)?
4. **Transmission efficiency**: How much motor power is lost to friction and gearbox inefficiency?
5. **Long-term durability**: Does performance degrade over 10,000 flex-extend cycles?

### Success Criteria

- **Static hold**: 50-60 N fingertip force sustained for 30 minutes with < 2% force drop
- **Efficiency**: > 40% mechanical-to-electrical power conversion at nominal torque
- **Backlash**: < 5° joint angle error (< 200 encoder counts)
- **Stiffness**: > 10 N/mm to minimize compliance
- **Endurance**: < 10% efficiency loss after 10,000 cycles

---

## 2. Tendon Mechanics

### Force Transmission Fundamentals

In a cable-driven system, motor torque $\tau_m$ is transmitted to fingertip force $F_{tip}$ through:

$$F_{tip} = \frac{\tau_m \cdot r_{spool}}{r_{joint} \cdot GR \cdot \eta}$$

Where:
- $\tau_m$ = Motor torque (mNm)
- $r_{spool}$ = Spool radius at motor (mm)
- $r_{joint}$ = Moment arm at finger joint (mm)
- $GR$ = Gear reduction ratio (231:1 for GPX 22 HP)
- $\eta$ = Overall transmission efficiency (typically 0.4-0.6)

**Example**: With $r_{spool} = 10$ mm, $r_{joint} = 15$ mm, $GR = 231$, $\eta = 0.5$:

$$F_{tip} = \frac{\tau_m \cdot 10}{15 \cdot 231 \cdot 0.5} = \frac{\tau_m}{173.25}$$

To achieve 60 N (6 kg) fingertip force:

$$\tau_m = 60 \cdot 173.25 = 10,395 \text{ mNm} \approx 10.4 \text{ Nm}$$

This is within the ECX TORQUE 22 L continuous torque rating (~14 mNm, scaled by gearbox).

### Pulley and Routing Efficiency

**Capstan Equation**: When a cable wraps around a pulley through angle $\theta$ with friction coefficient $\mu$:

$$\frac{T_{out}}{T_{in}} = e^{-\mu \theta}$$

For a single 180° pulley ($\theta = \pi$) with $\mu = 0.15$ (steel cable on aluminum pulley):

$$\frac{T_{out}}{T_{in}} = e^{-0.15 \pi} = 0.629$$

This means **37% force loss** per pulley! For a 3-pulley routing path:

$$\eta_{routing} = (0.629)^3 = 0.249 \text{ (25% efficiency)}$$

**Practical Implications**:
- Minimize pulley count
- Use low-friction materials (PTFE-lined conduits, ball-bearing pulleys)
- Increase pulley diameter to reduce wrap angle

### Bowden Cable vs. Direct Routing

**Bowden Cable** (tendon in flexible conduit):
- **Advantages**: Routes through complex geometries, protects tendon
- **Disadvantages**: High friction ($\mu \approx 0.2-0.3$), hysteresis from conduit compliance

**Direct Routing** (tendon over pulleys):
- **Advantages**: Lower friction ($\mu \approx 0.05-0.15$), less hysteresis
- **Disadvantages**: Requires clear line-of-sight paths, tendon wear at pulleys

This test bench uses **direct routing** for maximum efficiency.

### Tendon Tension Distribution

For a multi-joint finger with $n$ tendons controlling $m$ joints ($m \geq n$ for underactuation), the relationship between tendon tensions $\mathbf{T}$ and joint torques $\boldsymbol{\tau}$ is:

$$\boldsymbol{\tau} = \mathbf{R} \mathbf{T}$$

Where $\mathbf{R}$ is the moment arm matrix. For a 2-tendon antagonistic pair:

$$\mathbf{R} = \begin{bmatrix} r_1 & -r_2 \\ 0 & r_2 \end{bmatrix}$$

Solving for tendon tensions:

$$\mathbf{T} = \mathbf{R}^{-1} \boldsymbol{\tau}$$

**Force-doubling mechanisms** (routing both flexor and extensor through a single joint) can double the effective force but introduce additional friction.

---

## 3. Material Properties

### Tendon Material Selection

Common tendon materials for robotic hands:

| Material | Young's Modulus (GPa) | Ultimate Strength (GPa) | Creep | Cost |
|----------|----------------------|------------------------|-------|------|
| **Spectra** (UHMWPE) | 100-120 | 3-4 | High | Medium |
| **Dyneema** (UHMWPE) | 100-150 | 3-4 | High | Medium |
| **Steel cable** (7×19) | 190-210 | 1.5-2 | Low | Low |
| **Kevlar** | 70-120 | 3-4 | Medium | High |
| **Nylon** | 2-4 | 0.07-0.09 | Very High | Low |

This project uses **Spectra fiber** for high strength-to-weight ratio, with the caveat of higher creep.

### Young's Modulus and Compliance

Tendon elongation $\Delta L$ under force $F$ is governed by:

$$\Delta L = \frac{F \cdot L}{E \cdot A}$$

Where:
- $L$ = Original tendon length (mm)
- $E$ = Young's modulus (MPa)
- $A$ = Cross-sectional area (mm²)

**Example**: Spectra tendon (Ø1 mm, $A = 0.785$ mm², $E = 100$ GPa = 100,000 MPa) routed 300 mm with 50 N tension:

$$\Delta L = \frac{50 \cdot 300}{100,000 \cdot 0.785} = 0.191 \text{ mm}$$

This 0.2 mm elongation translates to **position error** and reduced system stiffness.

### Stiffness Test Theory

The **Stiffness Test** measures effective tendon/system stiffness by:

1. Locking motor at position $x_0$
2. Applying external force $F_{ext}$
3. Measuring position displacement $\Delta x$
4. Calculating stiffness: $k = F_{ext} / \Delta x$ (N/mm)

The measured stiffness $k_{system}$ includes contributions from:

$$\frac{1}{k_{system}} = \frac{1}{k_{tendon}} + \frac{1}{k_{gearbox}} + \frac{1}{k_{mounting}}$$

Where:
- $k_{tendon} = E \cdot A / L$ (tendon compliance)
- $k_{gearbox}$ = gearbox torsional stiffness (reflected to output)
- $k_{mounting}$ = structural compliance

Target: $k_{system} > 10$ N/mm for adequate force control.

### Creep and Stress Relaxation

Viscoelastic materials exhibit time-dependent deformation under constant stress (**creep**) or stress decay under constant strain (**stress relaxation**).

**Kelvin-Voigt Model** (creep):

$$\epsilon(t) = \frac{\sigma}{E} \left(1 - e^{-t/\tau}\right)$$

Where $\tau = \eta / E$ is the relaxation time constant ($\eta$ = viscosity).

For Spectra fiber under 50 N load, typical creep rates are 1-3% over 30 minutes.

### Hold Test Theory

The **Static Hold Test** validates creep behavior by:

1. Commanding constant force $F_{target}$
2. Monitoring actual force $F(t)$ for 30 minutes
3. Calculating force decay: $\Delta F = F_0 - F_{30min}$
4. Verifying: $\Delta F / F_0 < 2\%$ (acceptance criterion)

If creep exceeds limits, compensate by:
- Pre-stretching tendons (bedding-in)
- Active force feedback control
- Material substitution (steel cable)

### Hysteresis and Energy Loss

Hysteresis (different loading/unloading paths) arises from:

1. **Tendon internal friction**: Fiber-fiber sliding
2. **Gearbox backlash**: Gear tooth clearance
3. **Pulley friction**: Static vs. kinetic friction transition

Energy dissipated per cycle:

$$E_{loss} = \oint F \, dx = \text{Area of hysteresis loop}$$

**Hysteresis test** quantifies this by approaching positions from both directions.

### Break-In Effects (Bedding-In)

New tendons exhibit higher initial creep and compliance due to:
- Fiber alignment and densification
- Seating into pulleys/guides
- Initial plastic deformation

**Break-In Cycling Test** runs 100-1000 cycles to stabilize properties before validation testing.

---

## 4. Gearbox and Transmission

### Gear Reduction Fundamentals

The Maxon GPX 22 HP gearbox provides:
- **Reduction ratio**: 231:1
- **Efficiency**: ~40-60% (typical for high-reduction planetary)
- **Backlash**: < 1.5° at output (manufacturer spec)

Torque amplification:

$$\tau_{out} = \tau_{motor} \cdot GR \cdot \eta_{gearbox}$$

With $GR = 231$ and $\eta = 0.5$:

$$\tau_{out} = \tau_{motor} \cdot 115.5$$

### Backlash Sources

**1. Gear Tooth Clearance**:

Gear backlash $\theta_{backlash}$ (in degrees) propagates to output position error:

$$\Delta x_{backlash} = \theta_{backlash} \cdot r_{spool} \cdot \frac{\pi}{180}$$

For 1.5° backlash and $r_{spool} = 10$ mm:

$$\Delta x_{backlash} = 1.5 \cdot 10 \cdot \frac{\pi}{180} = 0.262 \text{ mm}$$

**2. Tendon Stretch**:

From Section 3, $\Delta L = 0.191$ mm for 50 N load.

**Total Hysteresis** (gearbox + tendon):

$$\Delta x_{total} = 0.262 + 0.191 = 0.453 \text{ mm}$$

This corresponds to ~**3°** joint angle error for typical finger kinematics.

### Hysteresis Test Theory

The **Hysteresis Loop Test** measures bidirectional positioning error:

1. Approach target position $x_i$ from below: $x_{below} \rightarrow x_i$
2. Record actual position: $x_i^{below}$
3. Approach from above: $x_{above} \rightarrow x_i$
4. Record actual position: $x_i^{above}$
5. Calculate backlash: $\Delta x_i = |x_i^{above} - x_i^{below}|$

Repeat for $n$ positions (typically 10) across range of motion.

**Acceptance**: $\max(\Delta x_i) < 200$ encoder counts (~5° joint angle).

### Transmission Efficiency

Overall efficiency is the product of gearbox and routing efficiencies:

$$\eta_{total} = \eta_{gearbox} \cdot \eta_{routing}$$

For GPX 22 HP ($\eta_{gb} = 0.5$) with 3-pulley routing ($\eta_{route} = 0.25$):

$$\eta_{total} = 0.5 \cdot 0.25 = 0.125 \text{ (12.5%)}$$

This is pessimistic—actual routing efficiency with ball-bearing pulleys is ~70%, giving:

$$\eta_{total} = 0.5 \cdot 0.7 = 0.35 \text{ (35%)}$$

### Torque Test Theory

The **Torque/Efficiency Test** measures $\eta_{total}$ empirically:

1. Command motor torque $\tau_{cmd}$ (via current setpoint)
2. Measure electrical power: $P_{elec} = V_{motor} \cdot I_{motor}$
3. Measure mechanical power: $P_{mech} = F_{tip} \cdot v_{tip}$
4. Calculate efficiency: $\eta = P_{mech} / P_{elec}$

Repeat across torque range (0 - max torque) to map $\eta(\tau)$.

**Expected behavior**:
- Low torque: Low efficiency (friction dominates)
- Mid torque: Peak efficiency (~40-50%)
- High torque: Decreasing efficiency (higher friction with load)

### Friction Losses vs. Velocity

Friction transitions from **static** (Coulomb) to **kinetic** (velocity-dependent):

$$F_{friction} = F_{static} \cdot \text{sgn}(v) + b \cdot v$$

Where:
- $F_{static}$ = Static friction force
- $b$ = Viscous damping coefficient
- $v$ = Velocity

At high speeds, viscous losses dominate; at low speeds, Coulomb friction dominates. This causes efficiency to vary with operating point.

---

## 5. Motor Control Theory

### BLDC Motor Operation

The Maxon ECX TORQUE 22 L is a brushless DC (BLDC) motor with:
- **Torque constant**: $K_t = 14.4$ mNm/A (from datasheet)
- **Continuous current**: 1.04 A
- **Peak current**: 5.2 A (short duration)

### Current-to-Torque Relationship

Motor torque is directly proportional to current:

$$\tau_m = K_t \cdot I_motor$$

For maximum continuous torque:

$$\tau_{cont} = 14.4 \cdot 1.04 = 14.976 \text{ mNm}$$

After gearbox (231:1, 50% efficiency):

$$\tau_{out} = 14.976 \cdot 231 \cdot 0.5 = 1,730 \text{ mNm} = 1.73 \text{ Nm}$$

This output torque, through a 10 mm spool, provides:

$$F_{spool} = \frac{1,730}{10} = 173 \text{ N}$$

Accounting for routing losses (70% efficiency):

$$F_{tip} = 173 \cdot 0.7 = 121 \text{ N} \approx 12 \text{ kg}$$

This **exceeds the 6 kg target** with safety margin.

### PID Control Fundamentals

A PID controller adjusts motor command $u(t)$ based on position error $e(t) = x_{target} - x_{actual}$:

$$u(t) = K_p \cdot e(t) + K_i \int e(t) \, dt + K_d \frac{de(t)}{dt}$$

Where:
- $K_p$ = Proportional gain (immediate response)
- $K_i$ = Integral gain (eliminates steady-state error)
- $K_d$ = Derivative gain (damping, reduces overshoot)

**Tuning guidelines** (Ziegler-Nichols method):
1. Set $K_i = K_d = 0$
2. Increase $K_p$ until oscillation occurs at critical gain $K_{p,crit}$
3. Measure oscillation period $T_{crit}$
4. Calculate PID gains:
   - $K_p = 0.6 \cdot K_{p,crit}$
   - $K_i = 2 K_p / T_{crit}$
   - $K_d = K_p \cdot T_{crit} / 8$

**Stability criteria**: Closed-loop system is stable if all poles of characteristic equation are in left-half complex plane.

### Motion Profiles

**Trapezoidal profile** (constant acceleration):

```
velocity
  ^
  |    /‾‾‾‾\
  |   /      \
  |  /        \
  | /          \
  +--------------> time
     accel cruise decel
```

**S-curve profile** (jerk-limited):

```
velocity
  ^
  |     ,‾‾‾‾‾.
  |   ,'       `.
  |  /           \
  | /             \
  +----------------> time
```

Jerk limiting $J$ (rate of acceleration change) reduces mechanical stress and vibration:

$$J = \frac{da}{dt} \quad \text{(RPM/s²)}$$

Typical values: $J = 10,000 - 100,000$ RPM/s²

### Control Loop Frequency

For stable position control of a gearbox system:

$$f_{control} > 10 \cdot f_{mechanical}$$

Where $f_{mechanical}$ is the first mechanical resonance (typically 50-100 Hz for high-ratio planetary gearboxes).

**Recommended**: $f_{control} \geq 1$ kHz

The Teensy 4.1 (600 MHz ARM Cortex-M7) easily achieves this.

---

## 6. Force Measurement and Calibration

### Load Cell Principles

**Strain Gauge Load Cells** use four strain gauges in a Wheatstone bridge configuration:

```
      R1
  +---/\/\---+
  |          |
 Vex        R2
  |         /\/\
  |          |
  +----+-----+---- Vout+
       |
      R3
      /\/\
       |
  +----+-----+---- Vout-
  |          |
 GND        R4
  |         /\/\
  +---/\/\---+
```

Output voltage:

$$V_{out} = V_{ex} \cdot \frac{R_1 \cdot R_3 - R_2 \cdot R_4}{(R_1 + R_2)(R_3 + R_4)}$$

Under load, resistances change by $\Delta R \propto$ strain.

### Calibration Procedure

**Two-point calibration**:

1. **Zero offset**: With no load, record ADC reading $ADC_0$
2. **Calibration point**: Apply known weight $W_{known}$ (e.g., 1 kg = 9.81 N), record $ADC_1$
3. Calculate calibration factor:

$$K_{calib} = \frac{W_{known}}{ADC_1 - ADC_0}$$

4. For any reading $ADC_x$:

$$F = (ADC_x - ADC_0) \cdot K_{calib}$$

**Multi-point calibration** (higher accuracy):

Perform linear regression on $(ADC_i, W_i)$ pairs to find best-fit $K_{calib}$ and $ADC_0$.

### Force Resolution and Accuracy

**HX711 ADC** (24-bit):
- **Resolution**: $2^{24} = 16,777,216$ counts
- **Range**: 0-20 kg (0-200 N)
- **LSB**: $200 / 16,777,216 = 0.000012$ N ≈ **12 µN**

Practical resolution is limited by noise (~100 µN).

**ADS1256** (24-bit, higher quality):
- Better SNR: ~0.01 N practical resolution

### Fingertip Force vs. Tendon Force

For a simple finger joint:

$$F_{tip} = \frac{F_{tendon} \cdot r_{tendon}}{r_{fingertip}}$$

Where:
- $r_{tendon}$ = Tendon moment arm at joint (~15 mm)
- $r_{fingertip}$ = Distance from joint to fingertip (~40 mm)

**Mechanical advantage**:

$$MA = \frac{r_{tendon}}{r_{fingertip}} = \frac{15}{40} = 0.375$$

For 60 N fingertip force:

$$F_{tendon} = \frac{60}{0.375} = 160 \text{ N}$$

This is **within the 200 N load cell range**.

### Force Control Accuracy

Closed-loop force control accuracy is limited by:

1. **Sensor resolution**: ±0.01 N (ADS1256)
2. **Tendon compliance**: $\Delta F = k_{tendon} \cdot \Delta x$
3. **Control loop bandwidth**: Faster loop → better rejection of disturbances

Target: ±1 N (±10%) for 10 N grasp forces.

---

## 7. Test Methodology

### Torque/Efficiency Test

**Objective**: Map transmission efficiency $\eta(\tau)$ across operating range.

**Procedure**:
1. Ramp motor torque from $\tau_{min}$ to $\tau_{max}$ in $n$ steps (typically 10-20)
2. At each step $i$:
   - Command torque $\tau_i$ (via current setpoint: $I_i = \tau_i / K_t$)
   - Wait settling time (default 2 s)
   - Measure:
     - Motor current $I_{actual}$
     - Motor voltage $V_{motor}$ (assume 24 V supply)
     - Tendon force $F_{tendon}$
     - Fingertip force $F_{tip}$
     - Position $x$ (encoder counts)
     - Velocity $v$ (RPM)
3. Calculate efficiency:

$$\eta_i = \frac{F_{tip,i} \cdot v_{tip,i}}{V_{motor} \cdot I_{actual,i}}$$

Where $v_{tip} = v \cdot r_{spool} / GR$ (convert RPM to linear velocity).

**Expected results**:
- Efficiency peaks at mid-torque (~40-50%)
- Low torque: friction dominates → low efficiency
- High torque: increased friction → decreasing efficiency

**Hysteresis measurement** (optional):
- Ramp torque up, then ramp down
- Plot $F_{up}(\tau)$ vs. $F_{down}(\tau)$
- Hysteresis area = energy loss per cycle

### Hysteresis Test

**Objective**: Quantify backlash from gearbox and tendon compliance.

**Procedure**:
1. Define test positions: $x_1, x_2, ..., x_n$ (linearly spaced from $x_{min}$ to $x_{max}$)
2. Set approach offset $\Delta x$ (e.g., 500 counts)
3. For each position $x_i$:
   - **Approach from below**:
     - Move to $x_i - \Delta x$
     - Wait settling time
     - Move to $x_i$
     - Wait settling time
     - Record actual position $x_i^{below}$
   - **Approach from above**:
     - Move to $x_i + \Delta x$
     - Wait settling time
     - Move to $x_i$
     - Wait settling time
     - Record actual position $x_i^{above}$
   - Calculate backlash: $\Delta x_i = |x_i^{above} - x_i^{below}|$

**Metrics**:
- Average backlash: $\bar{\Delta x} = \frac{1}{n} \sum_i \Delta x_i$
- Maximum backlash: $\max(\Delta x_i)$
- Position-dependence: Plot $\Delta x_i$ vs. $x_i$

**Acceptance**: $\max(\Delta x_i) < 200$ counts (~5° joint angle).

### Stiffness Test

**Objective**: Measure system stiffness $k = F / \Delta x$.

**Procedure**:
1. Lock motor at test position $x_0$ (position control mode, high PID gains)
2. Manually apply external force $F_{ext}$ to fingertip (or use calibrated spring)
3. Record:
   - Applied force $F_{ext}$ (from tip load cell)
   - Position displacement $\Delta x = x_{actual} - x_0$
4. Calculate stiffness:

$$k = \frac{F_{ext}}{\Delta x} \quad \text{(N/mm, assuming counts ≈ mm)}$$

**Expected**: $k > 10$ N/mm for adequate force control.

**Note**: Higher stiffness requires:
- Stiffer tendon material (steel cable)
- Shorter tendon routing (reduce $L$ in $k = EA/L$)
- Stiffer gearbox (lower backlash)

### Static Hold Test

**Objective**: Validate sustained force capability and monitor creep.

**Procedure**:
1. Command constant fingertip force $F_{target}$ (default 11.8 N = 1.2 kg)
   - Convert to tendon force: $F_{tendon} = F_{target} / MA$
   - Convert to motor torque: $\tau = F_{tendon} \cdot r_{spool}$
   - Convert to current: $I = \tau / K_t$
2. Hold for duration $t_{hold}$ (typically 30 min)
3. Sample sensors at interval $\Delta t$ (default 1 s)
4. Monitor:
   - Actual force $F(t)$ (both tendon and tip)
   - Position drift $\Delta x(t) = x(t) - x_0$
   - Motor current $I(t)$
   - Temperature $T(t)$ (if available)
5. Detect failures:
   - Force error: $|F(t) - F_{target}| / F_{target} > 10\%$
   - Excessive drift: $|\Delta x(t)| > 100$ counts

**Metrics**:
- Force stability: $\sigma_F / \bar{F}$ (coefficient of variation)
- Creep rate: $(F_0 - F_{30min}) / F_0$ (should be < 2%)
- Maximum drift: $\max|\Delta x(t)|$

**Thermal effects**: Motor heating can cause gearbox expansion and changing friction. Monitor current increase over time.

### Endurance Test

**Objective**: Validate durability over 10,000 flex-extend cycles.

**Procedure**:
1. Define cycle trajectory:
   - Start position $x_{start}$ (extended, e.g., 0 counts)
   - End position $x_{end}$ (flexed, e.g., 8000 counts)
   - Dwell times: $t_{start}$, $t_{end}$ (default 0.5 s each)
2. For cycle $i = 1$ to $N_{cycles}$ (default 10,000):
   - Move to $x_{start}$, wait $t_{start}$
   - Record sensors: position, force, current
   - Move to $x_{end}$, wait $t_{end}$
   - Record sensors
   - Log data every $N_{log}$ cycles (e.g., every 10th cycle to reduce data volume)
3. **Checkpointing**: Save state every 100 cycles to enable resume if interrupted
4. Monitor degradation metrics:
   - Efficiency: $\eta_i = P_{mech,i} / P_{elec,i}$
   - Position error: $\Delta x_i = x_{cmd} - x_{actual}$
   - Force capability: $F_{max,i}$

**Metrics**:
- Efficiency degradation: $(\eta_1 - \eta_{10000}) / \eta_1$ (should be < 10%)
- Mechanical drift: $|x_{10000} - x_1|$ (accumulated positioning error)
- Force loss: $(F_{1} - F_{10000}) / F_1$

**Expected wear**:
- Initial bedding-in: 10-20% efficiency drop in first 100 cycles
- Steady-state: < 1% per 1000 cycles thereafter

**Failure modes**:
- Tendon fraying: Increased friction, force variation
- Gearbox wear: Increased backlash, noise
- Bearing failure: Catastrophic (rare)

---

## 8. Validation Criteria

### Performance Targets

| Metric | Target | Measurement Method | Acceptance |
|--------|--------|-------------------|------------|
| **Maximum Force** | 50-60 N (5-6 kg) | Torque Test | Achieved continuously for 10 s |
| **Force Stability** | < 2% drop over 30 min | Static Hold Test | $\Delta F / F_0 < 0.02$ |
| **Backlash** | < 5° joint angle (~200 counts) | Hysteresis Test | $\max(\Delta x_i) < 200$ |
| **Stiffness** | > 10 N/mm | Stiffness Test | $k > 10$ N/mm |
| **Efficiency** | > 40% at nominal torque | Torque/Efficiency Test | $\eta_{peak} > 0.40$ |
| **Endurance** | < 10% efficiency loss over 10k cycles | Endurance Test | $\Delta \eta / \eta_0 < 0.10$ |
| **Position Repeatability** | < 100 counts (~2.5° joint) | Hysteresis Test | $\sigma_{position} < 100$ |
| **Current Limit** | < 1.0 A continuous | All Tests | Never exceed safety limit |

### Safety Limits

**Hardware Protection**:
- **Current limit**: 1.0 A continuous (protects gearbox from overload)
- **Peak current**: 2.0 A for < 1 s (starting torque)
- **Force limits**:
  - Tendon: 200 N max (load cell rating)
  - Fingertip: 20 N max (safety during manual interaction)
- **Position limits**: 0-10,000 counts (physical end stops)

**Software Monitoring**:
- Real-time safety monitor at 10 Hz
- Auto e-stop on limit violations
- Watchdog timer: 1 s timeout

### Test Report Checklist

After completing validation tests, verify:

- [ ] **Torque Test**: Efficiency curve shows $\eta_{peak} > 40\%$
- [ ] **Hysteresis Test**: All positions show $\Delta x < 200$ counts
- [ ] **Stiffness Test**: System stiffness $k > 10$ N/mm
- [ ] **Static Hold Test**: 30-minute hold with < 2% force drop
- [ ] **Endurance Test**: 10,000 cycles completed with < 10% efficiency loss
- [ ] **Data Quality**: All CSV files readable, no missing data
- [ ] **Calibration**: Load cells and encoder calibrations up-to-date
- [ ] **Safety**: No e-stop triggers during normal operation

### Failure Analysis

If validation criteria are **not met**:

**Low Force** ($F_{max} < 50$ N):
- Check motor current limit (increase if thermal margin allows)
- Verify routing efficiency (minimize friction, pulley count)
- Inspect gearbox for binding or damage

**Excessive Creep** ($\Delta F / F_0 > 2\%$):
- Run break-in cycling (100-1000 cycles)
- Consider stiffer tendon material (steel cable)
- Implement active force feedback control

**High Backlash** ($\Delta x > 200$ counts):
- Reduce gearbox backlash (consider precision gearbox)
- Pre-tension tendon (eliminate slack)
- Use stiffer tendon (reduce $\Delta L$)

**Low Efficiency** ($\eta < 40\%$):
- Minimize routing friction (PTFE conduits, ball-bearing pulleys)
- Reduce pulley count
- Lubricate gearbox (if applicable)

**Endurance Failure** ($\Delta \eta > 10\%$ over 10k cycles):
- Inspect for tendon fraying or pulley wear
- Check gearbox for particle contamination
- Verify operating temperature < 60°C

---

## References

1. Pratt, G. A., & Williamson, M. M. (1995). *Series elastic actuators*. IEEE/RSJ IROS.
2. Salisbury, J. K., & Craig, J. J. (1982). *Articulated hands: Force control and kinematic issues*. IJRR.
3. Jacobsen, S. C., et al. (1986). *Design of the Utah/MIT dextrous hand*. IEEE ICRA.
4. Dollar, A. M., & Howe, R. D. (2010). *The Highly Adaptive SDM Hand*. IJRR.
5. Maxon Motor AG. (2023). *ECX TORQUE 22 L Catalog*. www.maxongroup.com.
6. Odhner, L. U., et al. (2014). *A compliant, underactuated hand for robust manipulation*. IJRR.

---

## Appendix: Quick Reference Equations

**Force Transmission**:
$$F_{tip} = \frac{\tau_m \cdot r_{spool}}{r_{joint} \cdot GR \cdot \eta}$$

**Tendon Elongation**:
$$\Delta L = \frac{F \cdot L}{E \cdot A}$$

**Stiffness**:
$$k = \frac{F}{\Delta x}$$

**Efficiency**:
$$\eta = \frac{P_{mech}}{P_{elec}} = \frac{F \cdot v}{V \cdot I}$$

**PID Control**:
$$u(t) = K_p \cdot e(t) + K_i \int e(t) \, dt + K_d \frac{de(t)}{dt}$$

**Capstan Friction**:
$$\frac{T_{out}}{T_{in}} = e^{-\mu \theta}$$

**Motor Torque**:
$$\tau_m = K_t \cdot I_{motor}$$

---

*Document Version: 1.0*
*Last Updated: 2025-12-28*
*Contact: Test Bench Engineering Team*
