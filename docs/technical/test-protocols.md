# Test Protocols

Detailed documentation of the 5 automated test protocols.

---

## Overview

All tests inherit from `BaseTest` and provide:

- Configurable parameters
- Progress callbacks
- Duration estimation
- Result summarization

---

## 1. Torque Efficiency Test

### Purpose

Measure efficiency of the tendon transmission system across the operating range.

### Parameters

- **Max Torque**: Maximum motor torque (mNm)
- **Steps**: Number of measurement points
- **Hold Time**: Time at each point (seconds)

### Methodology

1. Apply increasing torque from 0 to max
2. Measure tendon force and motor current
3. Calculate efficiency: η = (F_tendon × r) / (I × K_t)
4. Plot efficiency vs. torque

### Results

- Efficiency curve
- Peak efficiency point
- Average efficiency
- Recommendations

---

## 2. Hysteresis Test

### Purpose

Quantify backlash and compliance in the transmission system.

### Parameters

- **Max Force**: Maximum tendon force (mN)
- **Cycles**: Number of loading cycles
- **Rate**: Loading rate (mN/s)

### Methodology

1. Ramp force from 0 to max
2. Hold briefly at peak
3. Ramp force back to 0
4. Measure position throughout
5. Calculate hysteresis loop area

### Results

- Hysteresis curve (force vs. position)
- Backlash measurement (encoder counts)
- Energy loss per cycle
- Compliance (N/mm)

---

## 3. Stiffness Test

### Purpose

Measure effective stiffness of the finger mechanism.

### Parameters

- **Test Points**: Number of force levels
- **Max Force**: Maximum force to apply (mN)
- **Settle Time**: Stabilization time (seconds)

### Methodology

1. Apply discrete force levels
2. Wait for position to stabilize
3. Record force-position pairs
4. Fit linear regression
5. Calculate stiffness: K = ΔF / Δx

### Results

- Stiffness coefficient (N/mm)
- Linearity (R² value)
- Force-deflection curve
- Recommended operating range

---

## 4. Static Hold Test

### Purpose

Validate ability to maintain constant force over time (critical for grasping).

### Parameters

- **Target Force**: Desired holding force (mN)
- **Duration**: Hold time (seconds)
- **Tolerance**: Acceptable deviation (%)

### Methodology

1. Ramp to target force
2. Engage PID force controller
3. Maintain force for specified duration
4. Monitor position drift
5. Record force stability metrics

### Results

- Force stability (mean ± std dev)
- Position drift rate (counts/min)
- Maximum deviation
- Control performance metrics

---

## 5. Endurance Test

### Purpose

Long-term wear testing under repeated loading cycles.

### Parameters

- **Cycles**: Number of load cycles
- **Force Range**: Min to max force (mN)
- **Frequency**: Cycle frequency (Hz)
- **Checkpoints**: Data save interval

### Methodology

1. Cycle between min and max force
2. Monitor for degradation:
   - Hysteresis increase
   - Friction increase
   - Efficiency decrease
3. Save checkpoint data
4. Generate trend plots

### Results

- Cycle count completed
- Degradation metrics over time
- Failure modes (if any)
- Remaining life estimate

---

## Custom Test Development

### Creating a New Test

```python
from protocols.base_test import BaseTest

class MyCustomTest(BaseTest):
    def get_name(self) -> str:
        return "My Custom Test"

    def get_parameters(self) -> dict:
        return {
            'param1': {
                'type': 'float',
                'default': 1.0,
                'min': 0,
                'max': 10,
                'unit': 'N',
                'description': 'First parameter'
            }
        }

    def run(self, config, progress_callback=None):
        # Test implementation
        pass
```

### Adding to Registry

Edit `protocols/registry.py`:

```python
from .my_custom_test import MyCustomTest

self.tests = {
    # ... existing tests
    'my_custom': MyCustomTest(hardware, logger)
}
```

---

## Next Steps

- [Tutorial](../user-guide/tutorial.md) - Run tests step-by-step
- [Engineering Theory](theory.md) - Mathematical foundations
- [API Reference](../development/api.md) - Code documentation
