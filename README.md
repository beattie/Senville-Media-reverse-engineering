# Senville/Midea Mini-Split Reverse Engineering & Control

Complete toolkit for controlling and reverse engineering Senville/Midea mini-split air conditioners.

## Contents

This repository contains:

1. **Control Scripts** - Python scripts to discover and control your AC
2. **WiFi Capture Tools** - Scripts to capture and analyze WiFi protocol traffic
3. **Documentation** - Comprehensive protocol documentation

## Quick Start

### 1. Install Dependencies

The virtual environment is already set up with all required packages:
- `midea-beautiful-air` - Control library
- `msmart` - Discovery tool
- `scapy` - Packet analysis
- `python-dotenv` - Environment configuration

### 2. Discover Your Device

```bash
# Activate virtual environment
source venv/bin/activate

# Discover devices on your network
python3 discover.py --account YOUR_EMAIL --password YOUR_PASSWORD
```

This will output your device credentials:
- IP Address
- Device ID
- Token (128 characters)
- Key (64 characters)

### 3. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your credentials from step 2
nano .env
```

### 4. Control Your AC

#### Check Status
```bash
python3 status.py
```

#### Control Commands
```bash
# Turn on in cool mode at 22°C
python3 control.py --power on --mode cool --temp 22

# Turn off
python3 control.py --power off

# Change temperature
python3 control.py --temp 24

# Set to heat mode
python3 control.py --mode heat --temp 25
```

---

## WiFi Packet Capture & Analysis

For deeper protocol reverse engineering, you can capture and analyze WiFi traffic.

### Prerequisites

Ensure you have:
- Wireless adapter with monitor mode support
- aircrack-ng suite installed
- Root/sudo access

### Step 1: Enable Monitor Mode

```bash
sudo ./wifi_setup.sh
```

This will:
- Kill interfering processes
- Set adapter to monitor mode
- Create `wlp3s0mon` interface

### Step 2: Scan for Your Device

```bash
sudo airodump-ng wlp3s0mon
```

Note your Senville device's:
- **BSSID** (MAC address)
- **Channel number**

Press Ctrl+C to stop scanning.

### Step 3: Capture Traffic

```bash
# Replace CHANNEL and BSSID with your device's values
sudo ./capture_traffic.sh -c CHANNEL -b AA:BB:CC:DD:EE:FF
```

While capturing:
1. Open the Senville mobile app
2. Turn AC on/off
3. Change temperature
4. Change modes
5. Adjust fan speed

Press Ctrl+C when done.

### Step 4: Analyze Captured Packets

```bash
# Basic analysis
python3 analyze_capture.py senville_capture-01.cap

# Verbose analysis
python3 analyze_capture.py senville_capture-01.cap --verbose
```

This will show:
- Packet statistics
- TCP/UDP connections
- Payloads on ports 6444 and 6445
- Protocol patterns

### Step 5: Restore Normal WiFi

```bash
sudo ./wifi_restore.sh
```

---

## Script Reference

### Control Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `discover.py` | Find devices and get credentials | `python3 discover.py -a EMAIL -p PASS` |
| `status.py` | Check AC status | `python3 status.py` |
| `control.py` | Control AC settings | `python3 control.py --power on --temp 22` |

### WiFi Capture Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `wifi_setup.sh` | Enable monitor mode | `sudo ./wifi_setup.sh` |
| `wifi_restore.sh` | Restore managed mode | `sudo ./wifi_restore.sh` |
| `capture_traffic.sh` | Capture packets | `sudo ./capture_traffic.sh -c CH -b MAC` |
| `analyze_capture.py` | Analyze captures | `python3 analyze_capture.py file.cap` |

---

## Documentation

### Protocol Documentation
See `senville-protocol-documentation.md` for:
- Network protocol details (TCP/UDP, ports)
- UART protocol specifications
- Packet structure and format
- Authentication & encryption
- Command codes and formats
- Known limitations

### Control Guide
See `senville-control-guide.md` for:
- Step-by-step setup instructions
- Command-line examples
- Python API usage
- Troubleshooting tips

---

## Protocol Overview

### Network Ports
- **6444** - TCP (encrypted commands)
- **6445** - UDP (device discovery)

### UART Interface
- **Baud Rate:** 9600 8N1
- **Start Byte:** 0xAA
- **Commands:** 0x41 (control), 0xB5 (capabilities)

### Authentication (V3)
- **Token:** 128-character hex string
- **Key:** 64-character hex string
- Retrieved via cloud API

### Supported Commands
- Power on/off
- Temperature (16-31°C / 60-87°F)
- Modes: Cool, Heat, Fan, Dry, Auto
- Fan speed control
- Eco/sleep modes

---

## Architecture

```
┌─────────────┐         ┌──────────┐         ┌─────────┐
│ Mobile App  │ <-----> │ WiFi Net │ <-----> │ SK103   │
│  (Control)  │  TCP    │  Router  │  WiFi   │ Dongle  │
└─────────────┘  6444   └──────────┘         └────┬────┘
                                                    │
┌─────────────┐                                    │ UART
│ Python      │                                    │ 9600
│ Scripts     │                                    │
│ (This Repo) │                              ┌─────┴─────┐
└─────────────┘                              │ AC Unit   │
                                             │ (Indoor)  │
                                             └───────────┘
```

---

## Environment Variables

Required in `.env` file:

```bash
# Device network settings
SENVILLE_IP=192.168.1.100
SENVILLE_DEVICE_ID=123456789012345

# V3 authentication
SENVILLE_TOKEN=<128-char-token>
SENVILLE_KEY=<64-char-key>

# Cloud credentials (for discovery)
MIDEA_ACCOUNT=your@email.com
MIDEA_PASSWORD=your_password
```

---

## Troubleshooting

### Discovery Issues
- Ensure device is powered and connected to WiFi
- Be on the same network as the device
- Verify Midea account credentials
- Try cloud mode: `python3 status.py --cloud`

### Connection Issues
- Check IP address hasn't changed (use DHCP reservation)
- Verify token/key are correct
- Check firewall isn't blocking port 6444
- Try discovery again to refresh credentials

### Monitor Mode Issues
- Ensure wireless adapter supports monitor mode
- Check that aircrack-ng is installed
- Run `sudo airmon-ng check kill` manually
- Verify no other processes are using the adapter

### Capture Shows No Traffic
- Verify correct channel and BSSID
- Ensure device is actively communicating
- Use app to generate traffic
- Check monitor interface is up: `iw dev`

---

## Security & Legal

### Authorized Use Only
- Only reverse engineer devices you own
- Do not access networks you don't control
- Respect local laws regarding reverse engineering
- Use for educational/research purposes

### Credential Security
- Never commit `.env` to version control
- Store tokens/keys securely
- Use strong Midea account passwords
- Limit access to control scripts

---

## Resources

### GitHub Projects
- [mac-zhou/midea-ac-py](https://github.com/mac-zhou/midea-ac-py) - Home Assistant integration
- [nbogojevic/midea-beautiful-air](https://github.com/nbogojevic/midea-beautiful-air) - Python client
- [dudanov/MideaUART](https://github.com/dudanov/MideaUART) - Arduino UART library
- [reneklootwijk/node-mideahvac](https://github.com/reneklootwijk/node-mideahvac) - Node.js implementation

### Documentation
- `senville-protocol-documentation.md` - Protocol specifications
- `senville-control-guide.md` - Usage guide

---

## Contributing

Findings and improvements welcome! If you discover:
- New protocol features
- Additional command codes
- Better decryption methods
- Model-specific variations

Please document and share your findings!

---

## License

Educational and research use. Respect manufacturer's terms of service.

---

## Compatibility

**Tested Brands:** Senville, Midea

**Should Work With:** Klimaire, AirCon, Century, Pridiom, Thermocore, Comfee, Toshiba, Carrier, Goodman, Friedrich, Samsung, Kenmore, Trane, Lennox, LG, Electrolux, Qlima, Artel, Inventor, Dimstal/Simando, Pioneer

**Requirements:**
- Python 3.8+
- WiFi adapter with monitor mode (for packet capture)
- Linux (Debian/Ubuntu tested)

---

**Created:** 2025-10-30
**Status:** Fully functional control, packet capture tools ready
