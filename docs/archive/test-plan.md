We need a test bench for a tendon-driven system with a **5–6 kg static hold** target as an ambitious and precise engineering task. At this scale, the primary challenges are not just the motors, but **friction losses**, **tendon elongation**, and **mechanical rigidity** of the bench itself.

Since we are using high-quality motors like Maxon or Faulhaber, the bench must be capable of measuring whether the "bottleneck" is the actuator torque or the tendon's physical properties (creep, snap, or routing friction).

### 1. Core Mechanical Layout

To validate a tendon design, you need a "Modular Finger Bed" where you can swap out routing geometries.

* **The Motor Block:** Use a heavy aluminum plate (e.g., 15–20mm MIC-6) to prevent vibrations or flexing. Maxon/Faulhaber motors should be mounted with high-resolution encoders.
* **The Spool System:** Design a spool that prevents "tendon climbing" (where the tendon winds over itself, changing the effective radius). Use a helical groove if possible.
* **Routing Pulleys:** These should be the variables. Use ball-bearing pulleys to test "ideal" scenarios, then swap in 3D-printed bushings or "foul" paths to test the tendon's abrasion resistance and friction.

### 2. Essential Instrumentation

To validate the design against a 6kg (approx. 60N) load, your bench needs to "see" the force at three specific points:

* **Tendon Tension Sensors (Load Cells):** Place an S-type or "button" load cell in-line with the tendon between the motor and the finger. This tells you exactly how much force the motor is putting *into* the system.
* **Fingertip Force Sensor:** Use a 6-axis F/T (Force/Torque) sensor or a simple single-axis load cell at the "contact point" to see how much force is actually delivered.
> **The Efficiency Metric:** . In tendon systems, this is often surprisingly low (40–70%) due to routing friction.


* **Joint Angle Encoders:** Even if your motors have encoders, tendons stretch. You need absolute magnetic encoders (like the AS5600 or similar) directly at the finger joints to measure "backlash" caused by tendon compliance.

### 3. Structural Design for 5–6 kg Static Holds

A 6 kg hold across five fingers implies high internal tensions. If your finger geometry has a small moment arm (e.g., a 5mm pulley at the joint), a 1kg tip force might require **10–20kg of tension** on the tendon.

| Component | Recommendation |
| --- | --- |
| **Tendon Material** | Use **UHMWPE (Dyneema/Spectra)** or **Technora**. Steel cables of this size often fatigue too quickly around small robot pulleys. |
| **Motor Gearing** | Use Maxon’s **GP series planetary gearheads**. Ensure the "Continuous Torque" rating matches your 6kg hold, as "Peak Torque" will cause the motor to overheat during a static hold. |
| **Frame Rigidity** | Use 4040 or 4080 **T-slot aluminum extrusions** for the base. At 60N loads, a 3D-printed or thin plastic base will flex, ruining your precision data. |

### 4. Validation Protocols (What to test)

Once the bench is built, run these three specific tests:

1. **Stiffness Mapping:** Lock the motor and apply external force to the finger. Measure how much the finger moves. This validates the tendon's Young’s Modulus and "bedding-in" (initial stretch).
2. **Hysteresis Loop:** Move the finger to a position from the "open" direction, then from the "closed" direction. The difference in encoder readings is your friction/stretch error.
3. **Static Endurance:** Hold the 6kg load for 30 minutes. Monitor motor temperature and tendon "creep" (gradual lengthening).

