# Contributing

Thank you for your interest in contributing to Test Bench GUI!

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a feature branch
4. Make your changes
5. Run tests
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/test-hub.git
cd test-hub

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov pytest-mock

# Run tests
pytest
```

## Code Style

### Python Style Guide

Follow [PEP 8](https://pep8.org/):

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters max
- **Imports**: Grouped (standard, third-party, local)
- **Naming**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Docstrings

Use Google-style docstrings:

```python
def calculate_efficiency(force: float, current: float) -> float:
    """
    Calculate transmission efficiency.

    Args:
        force: Tendon force in Newtons
        current: Motor current in Amps

    Returns:
        Efficiency as a percentage (0-100)

    Example:
        >>> eff = calculate_efficiency(10.0, 0.5)
        >>> print(f"{eff:.1f}%")
        85.2%
    """
    pass
```

### Type Hints

Use type hints where helpful:

```python
from typing import Dict, List, Optional

def get_sensors(self) -> Optional[Dict[str, float]]:
    """Read all sensor values."""
    pass
```

## Testing Requirements

All contributions must include tests:

### Unit Tests

```python
# tests/test_my_feature.py
import pytest

def test_my_function():
    """Test my new function."""
    result = my_function(42)
    assert result == expected_value
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# All tests must pass
python3 validate_system.py
```

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

- Write clean, documented code
- Add/update tests
- Update documentation

### 3. Commit Changes

Use clear commit messages:

```bash
git add .
git commit -m "Add new torque control algorithm

- Implement adaptive PID tuning
- Add unit tests for controller
- Update documentation"
```

### 4. Push to GitHub

```bash
git push origin feature/my-new-feature
```

### 5. Create Pull Request

- Go to GitHub repository
- Click "New Pull Request"
- Fill in description:
  - What does this PR do?
  - Why is it needed?
  - How was it tested?
  - Any breaking changes?

### PR Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Commit messages clear

## Areas for Contribution

### High Priority
- Additional test protocols
- New platform support
- Performance optimizations
- Bug fixes

### Medium Priority
- UI improvements
- Additional export formats
- Enhanced visualizations
- Code coverage increase

### Good First Issues
- Documentation improvements
- Example scripts
- Tutorial updates
- Test additions

## Communication

- **Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions
- **Discussions**: Questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

Be respectful and constructive in all interactions.

## Questions?

Open an issue or discussion on GitHub.
