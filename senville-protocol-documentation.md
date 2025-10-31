# Senville/Midea Mini-Split WiFi Protocol Documentation

## Overview

Senville mini-split air conditioners are rebranded **Midea** units. The WiFi adapter protocol has been reverse engineered by the community through Android app analysis and UART sniffing.

**Affected Brands:** Midea, Senville, Klimaire, AirCon, Century, Pridiom, Thermocore, Comfee, Toshiba, Carrier, Goodman, Friedrich, Samsung, Kenmore, Trane, Lennox, LG, Electrolux, Qlima, Artel, Inventor, Dimstal/Simando, Pioneer

---

## Hardware Architecture

### WiFi Dongle Connection
- **Interface:** UART (TTL serial level)
- **Baud Rate:** 9600 8N1 (9600 baud, 8 data bits, no parity, 1 stop bit)
- **Physical Connectors:**
  - JST-XH male/female connector
  - USB Type-A female connector (on some models)
- **Dongle Model:** SK103 SmartKey (most common)

### Communication Flow
```
Mobile App <---> WiFi Network <---> SK103 Dongle <---> UART <---> AC Unit
    (TCP/UDP)                         (Port 6444)      (9600 8N1)
```

---

## Network Protocol

### Discovery
- **Protocol:** UDP broadcast
- **Port:** 6445
- **Process:**
  1. Client broadcasts discovery packet on port 6445
  2. Devices respond with description packets
  3. Communication switches to TCP for commands

### Command Communication
- **Protocol:** TCP (encrypted)
- **Port:** 6444
- **Encryption:** Yes (proprietary, version-dependent)
- **Format:** Binary packets with hex encoding

### Known Issues
⚠️ **SK103 Stability:** When using LAN communication and polling frequently, the SK103 may disconnect from WiFi and require power cycling to reconnect.

---

## Authentication & Security

### V2 Protocol (Legacy)
- Older firmware versions
- Less secure authentication
- Simpler packet structure

### V3 Protocol (Current - Firmware 3.0.8+)
- **Required Credentials:**
  - **Token:** 128-character hex string
  - **K1 Key:** 64-character hex string
  - **Authentication Key Example:** `022BA2C782A41BFFBED33B769AA0889E6EC858D43DB74306A207EFD74C1066B5`

- **Credential Acquisition:**
  - Retrieved from Midea MSmartHome cloud API
  - Requires user account credentials
  - Use `midea-discover` tool for automated retrieval
  - Credentials are reusable across sessions

### Cloud API
- **Application:** NetHome Plus (primary)
- **Authentication:** Application key + Application ID pairs
- **Alternative Apps:** Require matching app key/ID pairs

---

## Packet Structure

### UART Packet Format
Based on observed traffic from UART sniffing:

```
AA 1E AC B2 00 00 00 00 03 0D 01 01 04 4A 05 A8 C0 FF 00 00 01 01 00 00 00 00 00 00 00 00 B6
```

**Known Components:**
- **Start Byte:** `AA` (consistent across all messages)
- **Length Indicator:** Second byte (0x1E = 30 bytes in example)
- **Message Type/Command:** Third byte (0xAC in example)
- **Data Payload:** Variable length
- **Checksum:** Last 1-2 bytes (0xB6, 0xCD9C, etc.)

### Message Direction
- **SK Messages:** From WiFi SmartKey dongle to appliance
- **AP Messages:** From appliance back to dongle

### Command Codes
- **0x41:** Status query and primary control command
- **0xB5:** Capabilities query (not supported by all units)
- **0xAC:** Observed in UART traffic (purpose unknown)

---

## Supported Commands

### Power Control
- Power On
- Power Off

### Temperature Control
- **Range:** 16-31°C (60-87°F)
- **Adjustment:** 1-degree increments

### Operating Modes
1. **Cool** - Cooling mode
2. **Heat** - Heating mode
3. **Fan** - Fan only (no heating/cooling)
4. **Dry** - Dehumidification mode
5. **Auto** - Automatic mode selection

### Fan Speed Control
- Multiple speed settings
- Fan speed levels vary by model

### Advanced Features
- Timer configuration
- Sleep mode
- Eco mode
- Ion mode (on supported models)
- Pump control (dehumidifiers)

---

## Status Properties

### Reported Values (80+ properties)
- Current temperature
- Target temperature
- Indoor temperature
- Outdoor temperature (if sensor available)
- Humidity level
- Fan speed
- Operating mode
- Power state
- Error codes
- Timer settings
- Feature flags

### Unknown Bit Flags
Properties named `byte*n*bit*m*` represent undocumented flag bits:
- `byte3bit3`
- `byte3bit34`
- Additional bits with unknown meanings

These likely control undocumented features or manufacturer-specific functions.

---

## Reverse Engineering Methods

### 1. Android App Analysis
- Decompile Senville/Midea Android APK
- Extract API endpoints and authentication methods
- Analyze network traffic from app

### 2. UART Sniffing
**Hardware Setup:**
```
AC Unit <---> USB-TTL Adapter <---> Computer (Sniffer)
    |
    +-------> ESP8266 TCP-Serial Bridge <---> WiFi
```

**Tools:**
- ESP8266 running esp-link firmware (TCP-serial bridge)
- USB-TTL interface (3.3V logic level)
- Node.js sniffer script
- Logic analyzer (optional)

**Process:**
1. Replace SmartKey with ESP8266 bridge
2. Connect original SmartKey via USB-TTL to computer
3. Monitor bidirectional UART traffic
4. Generate commands via mobile app
5. Correlate app actions with UART packets

### 3. WiFi Packet Capture
**Tools:**
- Wireshark/tshark
- tcpdump
- aircrack-ng suite (for monitor mode)

**Challenges:**
- Encrypted TCP payload (port 6444)
- Requires WPA/WPA2 key if capturing encrypted WiFi
- May need MITM for HTTPS cloud communication

---

## Network Protocol Details

### Device Configuration
**Required Parameters:**
1. IP Address (discovered via UDP broadcast)
2. Appliance ID (unique device identifier)
3. Token + K1 Key (V3 devices only)

### Communication Modes
1. **Cloud-based:** Through Midea cloud servers (internet required)
2. **Local LAN V3:** Direct TCP to device (requires token/key)
3. **Local LAN V2:** Direct TCP to device (legacy firmware)
4. **Serial Bridge:** Custom dongle with TCP-serial forwarding

---

## Existing Open Source Implementations

### Python
- **mac-zhou/midea-ac-py** - Home Assistant integration
- **nbogojevic/midea-beautiful-air** - Python client with cloud and LAN support
- **pcap-decrypt.py** - Packet capture decryption tool

### Node.js
- **reneklootwijk/node-mideahvac** - SK103 and serial bridge support
- **reneklootwijk/midea-uartsniffer** - UART protocol sniffer

### Arduino/ESP
- **dudanov/MideaUART** - Arduino library for UART control
- **uncle-yura/esphome-midea-ac** - ESPHome component
- **WiserUFBA/ArduMideaWrapper** - Arduino wrapper

### Other Platforms
- **bricky/midea-openhab** - OpenHAB integration

---

## Recommended Reverse Engineering Approach

### For WiFi Traffic Analysis:

1. **Setup Monitor Mode**
   ```bash
   sudo airmon-ng start wlp3s0
   ```

2. **Capture Traffic**
   ```bash
   sudo airodump-ng -c <channel> --bssid <device_mac> -w capture wlp3s0mon
   ```

3. **Generate Test Traffic**
   - Use mobile app to send commands
   - Power on/off
   - Temperature changes
   - Mode switches
   - Fan speed adjustments

4. **Analyze with Wireshark**
   - Filter for device IP/MAC
   - Examine TCP port 6444 traffic
   - Look for patterns in encrypted payload
   - Correlate timestamps with app actions

5. **Decrypt (if possible)**
   - Extract token/key from device
   - Use existing Python libraries as reference
   - Implement decryption based on known algorithms

### For UART Analysis (Recommended):

1. **Hardware Setup**
   - USB-TTL adapter (3.3V logic)
   - Connect to AC unit's UART pins
   - Monitor TX/RX lines

2. **Capture Serial Data**
   ```bash
   screen /dev/ttyUSB0 9600
   # or
   cat /dev/ttyUSB0 | xxd
   ```

3. **Analyze Packet Structure**
   - Identify start/stop bytes
   - Determine length fields
   - Calculate checksum algorithm
   - Map commands to functions

---

## Known Limitations

1. **Encryption:** V3 protocol uses proprietary encryption
2. **Documentation:** No official protocol specification from manufacturer
3. **Cloud Dependency:** Initial setup often requires cloud authentication
4. **Firmware Variations:** Different firmware versions may use different protocols
5. **Stability Issues:** SK103 WiFi disconnection under heavy polling
6. **Incomplete Reverse Engineering:** Many bit flags remain undocumented

---

## Security Considerations

### For Authorized Testing Only
- Only reverse engineer devices you own
- Do not attempt to control devices on networks you don't control
- Respect local laws regarding reverse engineering and protocol analysis
- Use for educational, research, or personal automation purposes

### Privacy
- Credentials (tokens, keys) are sensitive
- Do not share device tokens publicly
- Redact authentication data in logs and documentation

---

## Next Steps for Further Research

1. **Packet Capture:** Capture and analyze encrypted TCP traffic on port 6444
2. **Decryption:** Reverse engineer V3 encryption algorithm
3. **Cloud API:** Document cloud API endpoints and authentication
4. **Bit Flags:** Identify meaning of unknown byte/bit flags
5. **Model Variations:** Document protocol differences across device models
6. **Capabilities Command:** Decode 0xB5 capabilities response format
7. **Error Codes:** Create comprehensive error code mapping
8. **Extended Features:** Identify commands for advanced features (timers, schedules, etc.)

---

## References

- GitHub: mac-zhou/midea-ac-py
- GitHub: reneklootwijk/node-mideahvac
- GitHub: reneklootwijk/midea-uartsniffer
- GitHub: dudanov/MideaUART
- GitHub: nbogojevic/midea-beautiful-air
- GitHub: uncle-yura/esphome-midea-ac
- Home Assistant Midea Integration Community

---

## Document Version
- **Created:** 2025-10-30
- **Based on:** Community reverse engineering efforts (2018-2025)
- **Status:** Living document - protocol may evolve with firmware updates
