# Test Bench GUI

**Comprehensive validation platform for tendon-driven robotic hand systems**

[![Phase 7 Complete](https://img.shields.io/badge/Phase-7%20Complete-success)](https://github.com/anandvks/test-hub)
[![Platform Abstraction](https://img.shields.io/badge/Platform-Abstraction%20Ready-blue)](https://github.com/anandvks/test-hub)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/anandvks/test-hub)

---

## Overview

This is a professional test bench control system for validating tendon-driven finger mechanisms. Designed for precision testing with the Maxon ECX TORQUE 22 L motor and GPX 22 HP gearbox (231:1 reduction), targeting 5-6 kg static hold force.

## Key Features

- **Platform-Agnostic Architecture** - Supports Teensy 4.1, IMX8, Raspberry Pi, and simulation modes
- **5 Automated Test Protocols** - Torque, Hysteresis, Stiffness, Static Hold, and Endurance testing
- **Real-Time Visualization** - Live plotting at 50-100 Hz sample rates
- **Comprehensive Data Management** - Session-based organization with CSV/JSON export
- **Multi-Layer Safety System** - Hardware, firmware, and software protection

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Install dependencies and run your first test in 30 minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quick-start.md)

-   :material-book-open-variant:{ .lg .middle } __Tutorial__

    ---

    Step-by-step guide for using the test bench GUI

    [:octicons-arrow-right-24: Tutorial](user-guide/tutorial.md)

-   :material-math-compass:{ .lg .middle } __Engineering Theory__

    ---

    Mathematical foundations and validation methodology

    [:octicons-arrow-right-24: Theory](technical/theory.md)

-   :material-code-braces:{ .lg .middle } __Platform Guide__

    ---

    Developer guide for porting to new hardware platforms

    [:octicons-arrow-right-24: Platform Guide](technical/platform-guide.md)

</div>

## System Highlights

| Feature | Specification |
|---------|--------------|
| **Hardware Platforms** | 4 (Teensy, IMX8, RPi, Mock) |
| **Automated Tests** | 5 validation protocols |
| **GUI Tabs** | 7 functional interfaces |
| **Data Rate** | 50-100 Hz real-time |
| **Target Force** | 5-6 kg static hold |

## Architecture

The system uses a clean **4-layer modular architecture**:

```mermaid
graph TD
    A[GUI Layer] --> B[Test Logic Layer]
    B --> C[Hardware Abstraction Layer]
    C --> D[Platform-Specific Drivers]
    A --> E[Data Management Layer]
    B --> E
```

## Status

- ✅ Phase 7 Complete - Platform abstraction and GUI
- ✅ Multi-platform support (4 platforms)
- ✅ Comprehensive test protocols (5 automated tests)
- ✅ Real-time data visualization
- ✅ Production-ready codebase

## Next Steps

Ready to get started? Check out the [Quick Start Guide](getting-started/quick-start.md) or dive into the [Tutorial](user-guide/tutorial.md).
