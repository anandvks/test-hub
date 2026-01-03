# Hardware Setup

Wiring diagrams and hardware configuration for the Test Bench GUI.

## Bill of Materials

### Motor System
- **Motor**: Maxon ECX TORQUE 22 L (539534)
- **Gearbox**: GPX 22 HP, 231:1 reduction (223094)
- **Driver**: ESCON 24/2 DC servo controller

### Sensors
- **Load Cells**: 2× TAL220 (10 kg capacity)
- **ADC**: HX711 24-bit (for Teensy) or ADS1256 (for RPi)
- **Encoder**: Incremental quadrature (4096 CPR recommended)

### Control Platforms

| Platform | Communication | Best For |
|----------|--------------|----------|
| **Teensy 4.1** | Serial/USB | Development, prototyping |
| **IMX8** | Ethernet/TCP | Production, networked systems |
| **Raspberry Pi** | SPI/I2C | Embedded applications |
| **Mock** | In-memory | Testing without hardware |

## Wiring Diagrams

### Teensy 4.1 Setup

```
Motor Driver (ESCON 24/2)
├── PWM Signal ─────> Pin 2 (PWM)
├── Direction ──────> Pin 3 (Digital)
├── Enable ─────────> Pin 4 (Digital)
└── Current Sense ──> Pin A0 (Analog)

Encoder
├── Channel A ──────> Pin 5 (Digital)
├── Channel B ──────> Pin 6 (Digital)
└── Index ──────────> Pin 7 (Digital)

Load Cell (HX711)
├── DOUT (Tendon) ──> Pin 8 (Digital)
├── SCK (Tendon) ───> Pin 9 (Digital)
├── DOUT (Tip) ─────> Pin 10 (Digital)
└── SCK (Tip) ──────> Pin 11 (Digital)

Power
├── Teensy 5V ─────> USB
└── Motor 24V ─────> External PSU
```

### Raspberry Pi Setup

```
Motor Driver (ESCON 24/2)
├── PWM Signal ─────> GPIO 18 (PWM)
├── Direction ──────> GPIO 23
├── Enable ─────────> GPIO 24
└── Current Sense ──> ADS1256 CH0

Load Cells (ADS1256)
├── Tendon ────────> CH1
└── Tip ───────────> CH2

Encoder (via SPI)
├── MISO ──────────> GPIO 9
├── MOSI ──────────> GPIO 10
├── SCLK ──────────> GPIO 11
└── CS ────────────> GPIO 8
```

## Safety Wiring

**Critical**: Always implement hardware safety limits!

```
Emergency Stop Circuit
├── E-Stop Button ──> NC contact
├── Current Limit ──> Comparator → Kill signal
└── Position Limits > Limit switches
```

## Calibration

See the [Tutorial](tutorial.md#calibration) for step-by-step calibration procedures.

## Next Steps

- [Quick Start](../getting-started/quick-start.md) - Run your first test
- [Tutorial](tutorial.md) - Complete user guide
- [Platform Guide](../technical/platform-guide.md) - Add custom platforms
