Validation Plan: Tendon-Driven Finger Test Bench (Maxon GPX 22 HP)
Target: 5–6 kg Static Hold / ~1.2 kg per Finger
Motor: Maxon ECX TORQUE 22 L (BLDC + Hall Sensors)
Gearbox: GPX 22 HP 231:1 (3-stage, Max 3.3 Nm continuous)
Tendon: 2.0mm Dyneema DM20
1. System Specifications & Theoretical Torque
The 231:1 reduction provides immense torque but requires careful monitoring of the 3.3 Nm limit.
Calculated Output: Motor continuous torque is 48.1 mNm. $48.1 \times 231 \times 0.65 (\text{efficiency}) \approx 7.2 \text{ Nm}$.
Safety Limit: The gearbox is rated for 3.3 Nm continuous. You must limit motor current to $\approx 1.0\text{A}$ to avoid damaging the gearbox teeth, despite the motor being capable of more.
Holding Force: With a 20mm spool, 3.3 Nm provides 330N (33kg) of pull—vastly exceeding your 1.2kg per finger requirement. This gives you a massive overhead for friction.
2. Updated Bill of Materials (BOM)
Category
Component
Specification
Qty
Actuation
Maxon ECX TORQUE 22 L
22mm BLDC with Hall Sensors
1
Gearbox
Maxon GPX 22 HP
231:1 Reduction (High Power)
1
Control
Teensy 4.1
600MHz Microcontroller (Real-time)
1
Driver
Maxon ESCON 24/2
4-Quadrant Servo Controller (PWM/Dir)
1
Power
DC Power Supply
24V, 5A minimum
1
Sensing
Load Cells
S-Type (Tension) & Button (Tip)
2
Sensing
ADC
HX711 or ADS1256 (for Load Cells)
2
Tendon
Dyneema DM20
2.0mm Diameter
5m

3. Execution Plan
Phase 1: Torque & Efficiency Test
Validate how much current ($I$) is required to overcome the internal friction of the 231:1 gearbox + 2mm Dyneema.
Test: Command a constant current to the motor. Measure the actual pull force.
Success: Fingertip force reaches 1.2kg without motor current exceeding 0.5A.
Phase 2: Loop Config Validation
Test the "Force-Doubling" path. With the 231:1 gearbox, you may find the Direct Config is already sufficient, allowing you to avoid the friction penalty of the return loop.
4. Success Criteria
Gearbox Protection: Torque command never exceeds 3.3 Nm (monitored via ESCON current limit).
Hold Stability: Position drift at 1.2kg hold is $<0.5^\circ$ over 30 minutes.
Efficiency: Total system efficiency (Motor electrical power vs Tip mechanical power) $> 40\%$.

Test Bench Validation Plan & German Sourcing
1. High-Cycle Endurance Strategy (10,000 Cycles)
This test validates the interaction between the 2mm Dyneema DM20 and the Maxon GPX 22 HP.
Automation: The Python GUI commands the Teensy 4.1 to cycle through a "flex-hold-extend" sequence.
KPIs: * Transmission Efficiency: Drop in output force per unit of motor current.
Mechanical Drift: Cumulative error in the "Turns for Flexion" setpoint.
Hysteresis: Total backlash from the 231:1 gearbox plus the elastic stretch of the 2mm tendon.
2. Component Sourcing (Germany / EU)
Component
Recommendation
Vendor (DE)
Purpose
USB Dynamometer
Sauter FL-S / FH-S
Kern & Sohn
USB/RS232 interface for real-time force logging. Highly robust for cycle testing.
Alt. Dynamometer
PCE-DFG N 50
PCE Instruments
Standard DE lab tool with USB interface and PC software.
Motor & Gearbox
ECX Torque 22 L + GPX 22 HP
Maxon Deutschland
Sexau HQ. Precision BLDC and high-torque gearbox.
Shaft Encoder
AS5600 (Magnetic)
Mouser.de / DigiKey.de
Mounted on the output shaft for absolute turns measurement.
Tendon Line
Dyneema DM20 (2mm)
Marlow / Yachting Shops
High breaking strength, zero creep. Local maritime suppliers in DE stock this.
Mechanical Frame
4080 / 4040 Profiles
Misumi.de
Schwalbach. High rigidity for the 60N+ test bed.
Bearings/Pulleys
Stainless Ball Bearings
Mädler GmbH
Stuttgart. High-load precision pulleys.

3. The USB Dynamometer Interface
For a 10,000 cycle test, using a dedicated USB Dynamometer like the Sauter FH or PCE-DFG is superior to a raw load cell because:
Direct PC Integration: They often show up as a Virtual COM port or HID device.
Internal Sampling: They sample at high rates (up to 1000Hz) and have internal overload protection.
Accuracy: Calibrated out of the box with certificates required for formal validation reports.
4. Execution Workflow
Step 1: Baseline Hysteresis. Run the finger to 3.5 turns. Record shaft position vs. motor encoder.
Step 2: Cycle Load. Run 100 cycles at 50% load to "seat" the tendon.
Step 3: The Endurance Marathon. Run the remaining 9,900 cycles via the Python GUI, logging every 10th cycle to CSV.
Step 4: Post-Analysis. Compare the Hysteresis graph at Cycle 1 vs. Cycle 10,000. Any widening of the loop indicates mechanical wear.



