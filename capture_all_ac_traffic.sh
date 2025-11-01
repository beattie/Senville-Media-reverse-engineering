#!/bin/bash
# Capture ALL traffic to/from the AC device

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

DEVICE_IP="${SENVILLE_IP:-192.168.1.100}"
CAPTURE_FILE="senville_all_traffic"
INTERFACE="${NETWORK_INTERFACE:-eth0}"

echo "=== Capturing ALL Traffic to/from Senville AC ==="
echo "Device IP: $DEVICE_IP"
echo "Interface: $INTERFACE"
echo "Capture file: ${CAPTURE_FILE}.pcap"
echo
echo "BEFORE YOU START:"
echo "1. Make sure your phone is on the SAME WiFi network as this computer"
echo "2. Check your phone's WiFi settings - what network is it connected to?"
echo "3. Your phone and AC should be on the same network subnet"
echo
echo "DURING CAPTURE:"
echo "1. Use the Senville app on your phone"
echo "2. Turn AC on/off"
echo "3. Change temperature"
echo "4. Change modes"
echo "5. Press Ctrl+C when done"
echo
echo "Starting in 5 seconds..."
sleep 5

# Capture ALL traffic to/from the AC device (any port, any protocol)
sudo tcpdump -i $INTERFACE -w ${CAPTURE_FILE}.pcap -v \
    "host $DEVICE_IP"

echo
echo "Capture saved to: ${CAPTURE_FILE}.pcap"
echo
echo "Check capture size:"
ls -lh ${CAPTURE_FILE}.pcap
echo
echo "Analyze with: python3 analyze_capture.py ${CAPTURE_FILE}.pcap"
