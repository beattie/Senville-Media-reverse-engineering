#!/bin/bash
# Capture traffic between phone and AC

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
fi

PHONE_IP="${PHONE_IP:-192.168.1.50}"
AC_IP="${SENVILLE_IP:-192.168.1.100}"
CAPTURE_FILE="phone_to_ac"
INTERFACE="${NETWORK_INTERFACE:-eth0}"

echo "=== Capturing Traffic Between Phone and AC ==="
echo "Phone IP:     $PHONE_IP"
echo "AC IP:        $AC_IP"
echo "Interface:    $INTERFACE"
echo "Capture file: ${CAPTURE_FILE}.pcap"
echo
echo "INSTRUCTIONS:"
echo "1. Use the Senville app on your phone NOW"
echo "2. Turn AC on"
echo "3. Change temperature"
echo "4. Change mode"
echo "5. Turn AC off"
echo "6. Press Ctrl+C when done"
echo
echo "Starting capture in 3 seconds..."
sleep 3

# Capture traffic between phone and AC
sudo tcpdump -i $INTERFACE -w ${CAPTURE_FILE}.pcap -v \
    "(host $PHONE_IP and host $AC_IP)"

echo
echo "Capture complete!"
ls -lh ${CAPTURE_FILE}.pcap
echo
echo "Analyze with:"
echo "  python3 analyze_capture.py ${CAPTURE_FILE}.pcap"
echo "  python3 extract_credentials.py ${CAPTURE_FILE}.pcap"
