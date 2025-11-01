#!/bin/bash
# Capture traffic between Senville app and AC unit
# This captures TCP traffic on port 6444 to the AC device

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

DEVICE_IP="${SENVILLE_IP:-192.168.1.100}"
CAPTURE_FILE="senville_app_traffic"
INTERFACE="${NETWORK_INTERFACE:-eth0}"

echo "=== Senville App Traffic Capture ==="
echo "Device IP: $DEVICE_IP"
echo "Interface: $INTERFACE"
echo "Capture file: ${CAPTURE_FILE}.pcap"
echo
echo "INSTRUCTIONS:"
echo "1. This will capture traffic between your phone and the AC"
echo "2. After starting capture, use the Senville app on your phone"
echo "3. Perform these actions in the app:"
echo "   - Turn AC on"
echo "   - Change temperature"
echo "   - Turn AC off"
echo "   - Change mode (cool/heat/fan)"
echo "4. Press Ctrl+C when done"
echo
echo "Starting capture in 5 seconds..."
sleep 5

sudo tcpdump -i $INTERFACE -w ${CAPTURE_FILE}.pcap \
    "host $DEVICE_IP and port 6444"

echo
echo "Capture saved to: ${CAPTURE_FILE}.pcap"
echo "Analyze with: python3 analyze_capture.py ${CAPTURE_FILE}.pcap"
