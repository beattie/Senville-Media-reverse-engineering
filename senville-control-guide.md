# Senville/Midea Mini-Split Control Guide

## Python Libraries for Control

### Option 1: midea-beautiful-air (Recommended)
**Best for:** Standalone Python scripts and CLI usage
**Supports:** Air conditioners, dehumidifiers
**Protocol:** Cloud API, V3 local, V2 local

### Option 2: midea-ac-py + msmart
**Best for:** Home Assistant integration
**Supports:** Air conditioners (model 0xac only)
**Protocol:** LAN control with V3 authentication

---

## Installation

### midea-beautiful-air
```bash
pip install --upgrade midea-beautiful-air
```

Requirements: Python 3.8+

### msmart (for discovery)
```bash
pip3 install msmart
```

---

## Step 1: Discover Your Device

### Method A: Using midea-beautiful-air
```bash
# Discover all devices on network
midea-beautiful-air-cli discover --account YOUR_EMAIL --password YOUR_PASSWORD

# Get credentials (token and key)
midea-beautiful-air-cli discover --account YOUR_EMAIL --password YOUR_PASSWORD --credentials
```

**Output will include:**
- IP address
- Device ID
- Token (128 characters)
- Key/K1 (64 characters)
- Supported features

### Method B: Using msmart
```bash
# Basic discovery
midea-discover

# With Midea account credentials
midea-discover -a YOUR_EMAIL -p YOUR_PASSWORD

# Target specific IP
midea-discover -i 192.168.1.100

# Multiple broadcast attempts
midea-discover -c 5
```

**Save these values:**
```
IP Address: 192.168.1.100
Device ID: 123456789012345
Token: ACEDDA53831AE5DC... (128 chars)
K1/Key: CFFA10FC... (64 chars)
```

---

## Step 2: Check Device Status

### Command Line
```bash
# Local network (requires token/key)
midea-beautiful-air-cli status \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY

# Cloud-based (no token needed, but requires internet)
midea-beautiful-air-cli status \
  --id YOUR_DEVICE_ID \
  --account YOUR_EMAIL \
  --password YOUR_PASSWORD \
  --cloud

# Enable debug logging
midea-beautiful-air-cli status \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --log DEBUG \
  --verbose
```

### Python Script
```python
from midea_beautiful import appliance_state

# Query device status
device = appliance_state(
    address="192.168.1.100",
    token="YOUR_TOKEN",
    key="YOUR_KEY"
)

# Print all properties
print(f"Power: {device.running}")
print(f"Temperature: {device.indoor_temperature}")
print(f"Target: {device.target_temperature}")
print(f"Mode: {device.mode}")
print(f"Fan Speed: {device.fan_speed}")
```

---

## Step 3: Control Your Air Conditioner

### Command Line Examples

#### Power Control
```bash
# Turn ON
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --running 1

# Turn OFF
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --running 0
```

#### Temperature Control
```bash
# Set to 22°C (72°F)
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --temperature 22

# Temperature range: 16-31°C (60-87°F)
```

#### Mode Control
```bash
# Mode values:
# 1 = Cool
# 2 = Dry
# 3 = Fan
# 4 = Heat
# 5 = Auto (if supported)

# Set to cooling mode
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --mode 1

# Set to heat mode
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --mode 4
```

#### Multiple Settings at Once
```bash
# Turn on, set to cool mode, 22°C
midea-beautiful-air-cli set \
  --ip 192.168.1.100 \
  --token YOUR_TOKEN \
  --key YOUR_KEY \
  --running 1 \
  --mode 1 \
  --temperature 22
```

---

## Python Control Scripts

### Basic Control Script
```python
#!/usr/bin/env python3
from midea_beautiful import appliance_state

# Device credentials
IP = "192.168.1.100"
TOKEN = "YOUR_TOKEN_HERE"
KEY = "YOUR_KEY_HERE"

def get_status():
    """Get current AC status"""
    device = appliance_state(address=IP, token=TOKEN, key=KEY)
    return device

def set_temperature(temp):
    """Set target temperature"""
    # Note: Control requires using the full state update
    # This is a simplified example
    device = appliance_state(address=IP, token=TOKEN, key=KEY)
    device.target_temperature = temp
    device.apply()  # Apply changes
    return device

def power_on():
    """Turn AC on"""
    device = appliance_state(address=IP, token=TOKEN, key=KEY)
    device.running = True
    device.apply()
    return device

def power_off():
    """Turn AC off"""
    device = appliance_state(address=IP, token=TOKEN, key=KEY)
    device.running = False
    device.apply()
    return device

if __name__ == "__main__":
    # Get current status
    status = get_status()
    print(f"Current temperature: {status.indoor_temperature}°C")
    print(f"Target temperature: {status.target_temperature}°C")
    print(f"Power: {'ON' if status.running else 'OFF'}")
    print(f"Mode: {status.mode}")
```

### Discovery Script
```python
#!/usr/bin/env python3
from midea_beautiful import find_appliances

# Midea account credentials
ACCOUNT = "your@email.com"
PASSWORD = "your_password"

# Discover all devices
appliances = find_appliances(
    account=ACCOUNT,
    password=PASSWORD
)

# Print discovered devices
for appliance in appliances:
    print(f"Device found:")
    print(f"  Type: {appliance.type}")
    print(f"  ID: {appliance.id}")
    print(f"  IP: {appliance.address}")
    print(f"  Name: {appliance.name}")
    print(f"  Token: {appliance.token}")
    print(f"  Key: {appliance.key}")
    print()
```

### Advanced Control Script
```python
#!/usr/bin/env python3
import sys
from midea_beautiful import appliance_state

# Configuration
CONFIG = {
    "ip": "192.168.1.100",
    "token": "YOUR_TOKEN",
    "key": "YOUR_KEY"
}

class SenvilleController:
    def __init__(self, ip, token, key):
        self.ip = ip
        self.token = token
        self.key = key

    def get_device(self):
        """Get device state"""
        return appliance_state(
            address=self.ip,
            token=self.token,
            key=self.key
        )

    def print_status(self):
        """Print current status"""
        device = self.get_device()
        print("=== Senville AC Status ===")
        print(f"Power: {'ON' if device.running else 'OFF'}")
        print(f"Indoor Temp: {device.indoor_temperature}°C")
        print(f"Outdoor Temp: {device.outdoor_temperature}°C")
        print(f"Target Temp: {device.target_temperature}°C")
        print(f"Mode: {device.mode}")
        print(f"Fan Speed: {device.fan_speed}")
        print("========================")

    def set_cool_mode(self, temperature):
        """Set to cooling mode at specified temperature"""
        print(f"Setting cool mode at {temperature}°C...")
        # Implementation depends on library API
        # Use CLI for now as Python API may vary
        import subprocess
        subprocess.run([
            "midea-beautiful-air-cli", "set",
            "--ip", self.ip,
            "--token", self.token,
            "--key", self.key,
            "--running", "1",
            "--mode", "1",
            "--temperature", str(temperature)
        ])

    def set_heat_mode(self, temperature):
        """Set to heating mode at specified temperature"""
        print(f"Setting heat mode at {temperature}°C...")
        import subprocess
        subprocess.run([
            "midea-beautiful-air-cli", "set",
            "--ip", self.ip,
            "--token", self.token,
            "--key", self.key,
            "--running", "1",
            "--mode", "4",
            "--temperature", str(temperature)
        ])

if __name__ == "__main__":
    controller = SenvilleController(
        CONFIG["ip"],
        CONFIG["token"],
        CONFIG["key"]
    )

    # Show status
    controller.print_status()

    # Example: Set to cool mode at 22°C
    # controller.set_cool_mode(22)
```

---

## Environment Variables Setup

Create a `.env` file to store credentials:

```bash
# .env file
SENVILLE_IP=192.168.1.100
SENVILLE_TOKEN=YOUR_TOKEN_HERE
SENVILLE_KEY=YOUR_KEY_HERE
MIDEA_ACCOUNT=your@email.com
MIDEA_PASSWORD=your_password
```

Load in Python scripts:
```python
import os
from dotenv import load_dotenv

load_dotenv()

IP = os.getenv("SENVILLE_IP")
TOKEN = os.getenv("SENVILLE_TOKEN")
KEY = os.getenv("SENVILLE_KEY")
```

Install python-dotenv:
```bash
pip install python-dotenv
```

---

## Troubleshooting

### Discovery Issues
- Ensure device is powered on and connected to WiFi
- Check that you're on the same network as the device
- Try multiple broadcast attempts: `midea-discover -c 10`
- Verify Midea account credentials are correct

### Connection Issues
- Verify IP address hasn't changed (use DHCP reservation)
- Check firewall isn't blocking port 6444
- Ensure token/key are correct (128 and 64 characters)
- Try cloud-based control if local fails

### Command Failures
- Some features may not be supported by your model
- Check device firmware version
- Enable debug logging: `--log DEBUG --verbose`
- Verify command syntax and parameter values

### SK103 Disconnection
- Don't poll too frequently (wait 30+ seconds between requests)
- Consider using cloud API instead of local
- May need to power cycle device if it disconnects

---

## Mode Reference

| Mode | Value | Description |
|------|-------|-------------|
| Cool | 1 | Cooling mode |
| Dry  | 2 | Dehumidification |
| Fan  | 3 | Fan only (no cooling/heating) |
| Heat | 4 | Heating mode |
| Auto | 5 | Automatic (if supported) |

---

## Temperature Limits

- **Minimum:** 16°C (60°F)
- **Maximum:** 31°C (87°F)
- **Step:** 1°C (configurable in some implementations)

---

## Additional Features

Depending on your model, you may be able to control:
- Fan speed levels
- Swing mode (horizontal/vertical)
- Turbo/boost mode
- Eco/energy-saving mode
- Sleep mode
- Display brightness
- Beep/prompt tone

Refer to the library documentation for model-specific features.

---

## Cloud vs Local Control

### Cloud Control
**Pros:**
- No token/key required
- Works from anywhere with internet
- More stable than SK103 local polling

**Cons:**
- Requires internet connection
- Slower response time
- Depends on Midea cloud service availability

### Local Control (LAN)
**Pros:**
- Faster response
- No internet required
- More privacy (no cloud dependency)

**Cons:**
- Requires token/key extraction
- SK103 may disconnect under heavy load
- Must be on same network

---

## Security Best Practices

1. **Store credentials securely**
   - Use environment variables or `.env` files
   - Never commit credentials to git
   - Add `.env` to `.gitignore`

2. **Network security**
   - Use DHCP reservations for stable IP addresses
   - Consider VLAN isolation for IoT devices
   - Monitor network traffic for unexpected connections

3. **Access control**
   - Limit who has access to control scripts
   - Use strong Midea account passwords
   - Enable 2FA on Midea account if available

---

## Resources

- **midea-beautiful-air:** https://github.com/nbogojevic/midea-beautiful-air
- **midea-ac-py:** https://github.com/mac-zhou/midea-ac-py
- **msmart library:** https://github.com/mac-zhou/midea-msmart
- **Protocol documentation:** See `senville-protocol-documentation.md`

---

## Quick Reference Commands

```bash
# Discover devices
midea-beautiful-air-cli discover --account EMAIL --password PASS --credentials

# Get status
midea-beautiful-air-cli status --ip IP --token TOKEN --key KEY

# Turn on in cool mode at 22°C
midea-beautiful-air-cli set --ip IP --token TOKEN --key KEY --running 1 --mode 1 --temperature 22

# Turn off
midea-beautiful-air-cli set --ip IP --token TOKEN --key KEY --running 0
```

---

**Last Updated:** 2025-10-30
