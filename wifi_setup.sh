#!/bin/bash
# WiFi Monitor Mode Setup Script
# Sets up your wireless adapter for packet capture

set -e  # Exit on error

INTERFACE="wlp3s0"

echo "=== Senville WiFi Packet Capture Setup ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges."
    echo "Please run with: sudo ./wifi_setup.sh"
    exit 1
fi

echo "Step 1: Killing interfering processes..."
airmon-ng check kill

echo
echo "Step 2: Setting ${INTERFACE} to monitor mode..."

# Method 1: Using airmon-ng (recommended)
airmon-ng start ${INTERFACE}

# The interface name usually changes to wlp3s0mon
MON_INTERFACE="${INTERFACE}mon"

echo
echo "Step 3: Verifying monitor mode..."
iw dev

echo
echo "=== Setup Complete ==="
echo "Monitor interface: ${MON_INTERFACE}"
echo
echo "Next steps:"
echo "  1. Identify your Senville device:"
echo "     sudo airodump-ng ${MON_INTERFACE}"
echo
echo "  2. Note the BSSID (MAC) and Channel"
echo
echo "  3. Start capture (replace XX with channel, YY:... with BSSID):"
echo "     sudo airodump-ng -c XX --bssid YY:YY:YY:YY:YY:YY -w senville_capture ${MON_INTERFACE}"
echo
echo "  4. Use Senville app to generate traffic"
echo
echo "  5. Stop capture with Ctrl+C"
echo
echo "  6. Analyze with: python3 analyze_capture.py senville_capture-01.cap"
echo
