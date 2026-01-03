# Testing

Complete testing guide for Test Bench GUI.

## Overview

The project uses two complementary testing approaches:

1. **Unit Tests** (pytest) - Fast, isolated component tests
2. **System Validation** - Comprehensive integration testing

## Unit Tests (pytest)

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_hardware.py

# Run with coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_hardware.py      # Hardware controller tests
├── test_protocols.py     # Test protocol tests
├── test_utils.py         # Utility function tests
└── test_data.py          # Data management tests
```

### Writing Unit Tests

```python
import pytest
from hardware import create_controller

def test_mock_controller_creation():
    """Test creating mock controller."""
    controller = create_controller('mock')
    assert controller is not None
    assert controller.connected

def test_sensor_reading(mock_controller):
    """Test reading sensors."""
    data = mock_controller.get_sensors()
    assert 'force_tendon' in data
    assert 'position' in data
```

### Fixtures

Available fixtures in `conftest.py`:

- `mock_controller` - Connected mock hardware controller
- `data_logger` - Data logger instance
- `config_manager` - Configuration manager

## System Validation

### Running Validation

```bash
# Full validation (all 52 checks)
python3 validate_system.py

# Quick validation (subset)
python3 validate_system.py --quick

# Test specific platform
python3 validate_system.py --platform teensy
```

### Validation Coverage

**Module Imports** (13 checks):
- Hardware controllers
- Test protocols
- Data management
- Utilities

**Hardware Factory** (5 checks):
- Platform listing
- Controller creation
- Interface compliance

**Interface Tests** (12+ checks per platform):
- Connection
- Sensor reading
- Motor commands
- PID control
- Data streaming

**Test Registry** (8 checks):
- Protocol discovery
- Parameter validation
- Duration estimation

**Data Management** (10 checks):
- Logging
- Session management
- Export functionality

## Continuous Integration

### GitHub Actions (Future)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pytest
        run: pytest --cov
      - name: Run validation
        run: python3 validate_system.py
```

## Test Markers

Use pytest markers to organize tests:

```python
@pytest.mark.unit
def test_conversion():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_full_workflow():
    """Slower integration test."""
    pass

@pytest.mark.hardware
def test_actual_device():
    """Requires physical hardware."""
    pass
```

Run specific markers:
```bash
pytest -m unit          # Fast tests only
pytest -m "not hardware"  # Skip hardware tests
```

## Code Coverage

### Generate Coverage Report

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### Coverage Goals

- **Overall**: > 80%
- **Critical paths**: > 90%
- **Hardware abstraction**: > 85%
- **Utilities**: > 95%

## Platform Testing

Test all platform implementations:

```bash
python3 test_platforms.py mock
python3 test_platforms.py teensy  # Requires hardware
```

## Manual Testing Checklist

Before each release:

- [ ] All automated tests passing
- [ ] Manual control works on all platforms
- [ ] Each test protocol completes successfully
- [ ] Data export formats (CSV, JSON, PNG)
- [ ] Calibration workflows
- [ ] Emergency stop functionality
- [ ] Connection error handling
- [ ] Documentation up-to-date

## Debugging Tests

### Verbose Output

```bash
pytest -vv --tb=long
```

### Run Single Test

```bash
pytest tests/test_hardware.py::TestMockController::test_connect -v
```

### Print Debugging

```bash
pytest -s  # Show print statements
```

### Use pdb

```python
import pdb; pdb.set_trace()
```

## Next Steps

- [Contributing](contributing.md) - Contribution guidelines
- [API Reference](api.md) - Code documentation
- [Platform Guide](../technical/platform-guide.md) - Add platforms
