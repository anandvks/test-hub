# API Reference

Technical API documentation for Test Bench GUI.

## Hardware Layer

### HardwareController (Base Class)

Abstract base class for all platform implementations.

```python
from hardware.base_controller import HardwareController

class MyController(HardwareController):
    def connect(self) -> bool:
        """Connect to hardware."""
        pass

    def disconnect(self):
        """Disconnect from hardware."""
        pass

    def get_sensors(self) -> Optional[Dict]:
        """Read all sensor values."""
        pass
```

### Factory Function

```python
from hardware import create_controller, list_platforms

# List available platforms
platforms = list_platforms()

# Create controller
controller = create_controller('mock')
controller.connect()
```

## Test Protocols

### BaseTest

Abstract base class for all test protocols.

```python
from protocols.base_test import BaseTest

class MyTest(BaseTest):
    def get_name(self) -> str:
        """Return test name."""
        return "My Custom Test"

    def get_parameters(self) -> dict:
        """Return configurable parameters."""
        return {
            'force': {
                'type': 'float',
                'default': 1000.0,
                'min': 0,
                'max': 5000,
                'unit': 'mN'
            }
        }

    def run(self, config: dict, progress_callback=None) -> dict:
        """Execute test and return results."""
        pass
```

## Data Management

### DataLogger

Real-time data logging with buffering.

```python
from data.logger import DataLogger

logger = DataLogger(buffer_size=10000)

# Log data point
logger.buffer.append({
    'timestamp': time.time(),
    'force': 1234.5,
    'position': 5678
})
```

### ConfigManager

Configuration persistence.

```python
from data.config_manager import ConfigManager

config = ConfigManager()
platform = config.config['hardware']['platform']
```

## Utilities

### UnitConverter

Unit conversion utilities.

```python
from utils.units import UnitConverter

# Force conversions
newtons = UnitConverter.mn_to_newtons(1000)  # 1.0 N
kg = UnitConverter.newtons_to_kg(9.81)       # 1.0 kg

# Torque conversions
nm = UnitConverter.mnm_to_nm(1000)           # 1.0 Nm
```

## GUI Components

### Creating Custom Tabs

```python
from tkinter import ttk

class MyCustomTab(ttk.Frame):
    def __init__(self, parent, hardware, logger):
        super().__init__(parent)
        self.hardware = hardware
        self.logger = logger
        self._create_widgets()

    def _create_widgets(self):
        # Create GUI elements
        pass
```

## Safety System

### SafetyMonitor

Real-time safety monitoring.

```python
from hardware.safety import SafetyMonitor

safety = SafetyMonitor(controller)

# Check safety conditions
is_safe = safety.check_all()

# Get violations
violations = safety.get_violations()
```

## Examples

### Read Sensors

```python
controller = create_controller('mock')
controller.connect()

data = controller.get_sensors()
print(f"Force: {data['force_tendon']} mN")
print(f"Position: {data['position']} counts")
```

### Run Test

```python
from protocols.registry import TestRegistry

hardware = {'controller': controller, 'safety': safety}
registry = TestRegistry(hardware, logger)

# Get test
test = registry.get_test('hold')

# Configure
config = {
    'target_force': 1200,
    'duration': 300
}

# Run
results = test.run(config)
```

### Export Data

```python
from data.exporter import DataExporter

exporter = DataExporter(session)
exporter.export_csv('output.csv')
exporter.export_json('output.json')
exporter.export_plots('plots.png')
```

## Next Steps

- [Testing](testing.md) - Write tests for your code
- [Contributing](contributing.md) - Contribution guidelines
- [Platform Guide](../technical/platform-guide.md) - Add platforms
