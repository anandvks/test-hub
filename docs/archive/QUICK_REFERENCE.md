# Quick Reference Guide

**Test Bench GUI - Command Reference**

Last Updated: 2025-12-28

---

## 🚀 Essential Commands

### Launch the GUI
```bash
python main.py
```

### Run System Validation
```bash
# Full validation
python validate_system.py

# Quick validation
python validate_system.py --quick

# Test specific platform
python validate_system.py --platform teensy
```

### Start Documentation Server
```bash
cd docs
python3 -m http.server 8000
# Open: http://localhost:8000/index.html
```

### Platform Testing
```bash
python test_platforms.py mock
python test_platforms.py teensy
```

---

## ⚙️ Configuration

### Change Platform
Edit `config.json`:
```json
{
  "hardware": {
    "platform": "mock"
  }
}
```

Options: `"teensy"`, `"imx8"`, `"rpi"`, `"mock"`

### Platform-Specific Config

**Teensy**:
```json
"teensy": {
  "port": "/dev/ttyACM0",
  "baudrate": 115200
}
```

**IMX8**:
```json
"imx8": {
  "host": "192.168.1.100",
  "port": 5000
}
```

**Raspberry Pi**:
```json
"rpi": {
  "spi_bus": 0,
  "spi_device": 0,
  "i2c_bus": 1
}
```

---

## 📂 Important Directories

```
test-gui/
├── data/sessions/          # Test data output
├── data/calibrations/      # Calibration files
├── docs/                   # Documentation
└── logs/                   # Error logs (if any)
```

---

## 🧪 Running Tests

### From GUI
1. Launch: `python main.py`
2. Go to **Test Library** tab
3. Select test from list
4. Configure parameters
5. Click **Run Test**
6. Monitor in **Live Monitor** tab
7. Review in **Data Review** tab

### Via Code (Example)
```python
from hardware import create_controller
from tests.registry import TestRegistry
from data.logger import DataLogger

# Setup
controller = create_controller('mock')
controller.connect()
logger = DataLogger()

# Create registry
hardware = {'controller': controller, 'safety': None}
registry = TestRegistry(hardware, logger)

# Get test
test = registry.get_test('hold')

# Configure
config = {
    'target_force': 11800,  # mN
    'duration': 300,        # seconds
    'sample_interval': 1.0,
    'tolerance': 0.1
}

# Run
result = test.run(config)
print(result)
```

---

## 🔧 Troubleshooting

### GUI Won't Start
```bash
# Check dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.8+

# Check for errors
python main.py 2>&1 | tee error.log
```

### Connection Failed
```bash
# Teensy: Check port
ls /dev/ttyACM*  # Linux
ls /dev/cu.usb*  # macOS

# Add user to dialout group (Linux)
sudo usermod -a -G dialout $USER
# Then logout and login

# IMX8: Check network
ping 192.168.1.100
telnet 192.168.1.100 5000
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

---

## 📊 Data Export

### Export Session from GUI
1. Go to **Data Review** tab
2. Select session from tree
3. Click **Export** tab
4. Choose format (CSV, JSON, PNG)
5. Click **Export Selected**

### Export Programmatically
```python
from data.session import SessionManager
from data.exporter import BatchExporter
from pathlib import Path

# Load session
sm = SessionManager()
session = sm.load_session('20251228_143022_session')

# Export
exporter = BatchExporter(session)
exporter.export_session(
    Path('exports/my_export'),
    formats=['csv', 'json', 'txt']
)
```

---

## 🔍 Common Tasks

### View System Status
```bash
python validate_system.py --quick
```

### List Available Platforms
```python
from hardware import list_platforms
print(list_platforms())
```

### Check Config
```python
from data.config_manager import ConfigManager
cm = ConfigManager()
print(cm.get('hardware', 'platform'))
```

### List Sessions
```python
from data.session import SessionManager
sm = SessionManager()
sessions = sm.list_sessions(sort_by='created')
for s in sessions:
    print(f"{s['session_id']}: {s['num_tests']} tests")
```

---

## 🎨 GUI Keyboard Shortcuts

- **F1** - Emergency Stop
- **Ctrl+Q** - Quit application
- **Ctrl+R** - Refresh ports (Manual Control tab)
- **Ctrl+L** - Toggle logging (Manual Control tab)

---

## 📖 Documentation Links

- **README**: `README.md` - Complete user guide
- **Theory**: `docs/THEORY.md` - Engineering background
- **Tutorial**: `docs/TUTORIAL.md` - 30-minute quick start
- **Platform Guide**: `docs/PLATFORM_GUIDE.md` - Porting guide
- **Status**: `PROJECT_STATUS.md` - Project overview
- **Changelog**: `CHANGELOG.md` - Version history
- **Web Portal**: http://localhost:8000/index.html (after starting server)

---

## 🆘 Getting Help

### Check Documentation
1. Read `README.md` for user guide
2. Read `docs/TUTORIAL.md` for step-by-step
3. Check `TROUBLESHOOTING.md` for common issues

### Run Diagnostics
```bash
# System validation
python validate_system.py

# Platform test
python test_platforms.py mock

# Check logs
tail -f logs/app.log  # If logging enabled
```

### Report Issues
Include:
- Python version: `python --version`
- OS: `uname -a` (Linux/Mac) or `ver` (Windows)
- Platform: From `config.json`
- Error message: Full traceback
- Steps to reproduce

---

## 💡 Quick Tips

### Tip 1: Start with Mock
Always test with `platform: "mock"` first before using real hardware.

### Tip 2: Use Quick Validation
Run `python validate_system.py --quick` before each session.

### Tip 3: Export Often
Export important sessions to prevent data loss.

### Tip 4: Check Documentation Website
Use the web portal for easier navigation: http://localhost:8000

### Tip 5: Calibrate Regularly
Recalibrate sensors before important tests.

---

## 📝 Development

### Add New Test
1. Create `tests/my_test.py`
2. Inherit from `BaseTest`
3. Implement required methods
4. Add to `tests/registry.py`

### Add New Platform
1. Create `hardware/myplatform_controller.py`
2. Inherit from `HardwareController`
3. Implement all abstract methods
4. Add to `hardware/__init__.py` factory
5. Update `config.json`

See `docs/PLATFORM_GUIDE.md` for details.

---

## 🎯 Validation Criteria

Quick reference for test success:

- **Static Force**: 5-6 kg (50-60 N)
- **Efficiency**: > 40%
- **Backlash**: < 5° (< 200 counts)
- **Stiffness**: > 10 N/mm
- **Creep**: < 2% over 30 min
- **Endurance**: < 10% loss over 10k cycles

---

## 📞 Support

- **Documentation**: `README.md`, `docs/`
- **Validation**: `python validate_system.py`
- **Examples**: `docs/TUTORIAL.md`

---

**Happy Testing!** 🚀
