#!/bin/bash
# WiFi Monitor Mode Restore Script
# Restores your wireless adapter to managed mode

set -e  # Exit on error

INTERFACE="wlp3s0"
MON_INTERFACE="${INTERFACE}mon"

echo "=== Restoring WiFi to Managed Mode ==="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges."
    echo "Please run with: sudo ./wifi_restore.sh"
    exit 1
fi

echo "Stopping monitor mode on ${MON_INTERFACE}..."
airmon-ng stop ${MON_INTERFACE} 2>/dev/null || true

echo
echo "Restarting NetworkManager..."
systemctl start NetworkManager 2>/dev/null || service network-manager start 2>/dev/null || true

echo
echo "Bringing up ${INTERFACE}..."
ip link set ${INTERFACE} up 2>/dev/null || true

echo
echo "Current wireless interfaces:"
iw dev

echo
echo "=== Restore Complete ==="
echo "Your WiFi should now be back to normal managed mode."
echo "You can reconnect to your WiFi network."
