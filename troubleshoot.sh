#!/bin/bash
# Troubleshoot Senville AC Connection

echo "=========================================="
echo "Senville AC Connection Troubleshooter"
echo "=========================================="
echo ""

# Test 1: Network connectivity
echo "1. Testing network connectivity..."
if ping -c 2 -W 3 192.168.254.183 > /dev/null 2>&1; then
    echo "   ✓ AC is reachable on network"
else
    echo "   ✗ AC is not reachable"
    echo "   - Check if AC is powered on"
    echo "   - Check WiFi connection"
    exit 1
fi

echo ""
# Test 2: Port connectivity
echo "2. Testing TCP port 6444..."
if timeout 3 bash -c "</dev/tcp/192.168.254.183/6444" 2>/dev/null; then
    echo "   ✓ Port 6444 is open"
else
    echo "   ✗ Port 6444 is not responding"
fi

echo ""
# Test 3: Device discovery
echo "3. Testing device discovery..."
cd "$(dirname "$0")"
source venv/bin/activate > /dev/null 2>&1
timeout 15 msmart-ng discover 192.168.254.183 2>&1 | grep -q "Found 1 devices" && \
    echo "   ✓ Device discovered successfully" || \
    echo "   ✗ Discovery failed"

echo ""
# Test 4: Direct connection
echo "4. Testing direct connection (may take 10-15 seconds)..."
timeout 20 python3 -c "
from midea_beautiful import appliance_state
import os

with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key] = value

try:
    device = appliance_state(
        address=os.getenv('SENVILLE_IP'),
        token=os.getenv('SENVILLE_TOKEN'),
        key=os.getenv('SENVILLE_KEY')
    )
    state = device.state
    if state.running or state.target_temperature > 0:
        print('   ✓ Connection successful')
        print(f'   Status: Power={state.running}, Temp={state.target_temperature}')
    else:
        print('   ⚠ Connected but got zero values (device may need restart)')
except Exception as e:
    print(f'   ✗ Connection failed: {type(e).__name__}')
" 2>&1 | grep -v "Error getting device capabilities"

echo ""
echo "=========================================="
echo "Recommendations:"
echo "=========================================="
echo ""
echo "If tests failed, try these steps:"
echo ""
echo "1. Power cycle the AC:"
echo "   - Turn off AC completely"
echo "   - Wait 30 seconds"
echo "   - Turn back on"
echo "   - Wait 1 minute for WiFi to connect"
echo ""
echo "2. Refresh credentials:"
echo "   ./restart_web.sh"
echo ""
echo "3. Re-discover device:"
echo "   source venv/bin/activate"
echo "   msmart-ng discover 192.168.254.183"
echo "   # Update .env with new token/key if changed"
echo ""
echo "4. Check WiFi signal:"
echo "   - Ensure AC has good WiFi signal"
echo "   - Reduce distance to router"
echo "   - Check for interference"
echo ""
