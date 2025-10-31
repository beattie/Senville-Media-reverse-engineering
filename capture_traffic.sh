#!/bin/bash
# WiFi Traffic Capture Script for Senville Device
# Captures packets from a specific device for analysis

set -e

# Default values
INTERFACE="wlp3s0mon"
CHANNEL=""
BSSID=""
OUTPUT="senville_capture"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--channel)
            CHANNEL="$2"
            shift 2
            ;;
        -b|--bssid)
            BSSID="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -i|--interface)
            INTERFACE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: sudo ./capture_traffic.sh [OPTIONS]"
            echo
            echo "Options:"
            echo "  -c, --channel CHANNEL    WiFi channel (required)"
            echo "  -b, --bssid   BSSID      Device MAC address (required)"
            echo "  -o, --output  FILE       Output filename (default: senville_capture)"
            echo "  -i, --interface IFACE    Monitor interface (default: wlp3s0mon)"
            echo "  -h, --help               Show this help"
            echo
            echo "Example:"
            echo "  sudo ./capture_traffic.sh -c 6 -b AA:BB:CC:DD:EE:FF"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run with -h for help"
            exit 1
            ;;
    esac
done

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script requires sudo privileges."
    echo "Please run with: sudo ./capture_traffic.sh [OPTIONS]"
    exit 1
fi

# Validate required parameters
if [ -z "$CHANNEL" ] || [ -z "$BSSID" ]; then
    echo "Error: Channel and BSSID are required!"
    echo
    echo "First, scan for devices:"
    echo "  sudo airodump-ng ${INTERFACE}"
    echo
    echo "Then run:"
    echo "  sudo ./capture_traffic.sh -c CHANNEL -b BSSID"
    echo
    echo "Run with -h for more options"
    exit 1
fi

echo "=== Senville WiFi Packet Capture ==="
echo "Interface: ${INTERFACE}"
echo "Channel:   ${CHANNEL}"
echo "BSSID:     ${BSSID}"
echo "Output:    ${OUTPUT}-01.cap"
echo
echo "Press Ctrl+C to stop capture"
echo
echo "While capturing:"
echo "  - Use the Senville mobile app"
echo "  - Turn AC on/off"
echo "  - Change temperature"
echo "  - Change modes"
echo "  - This generates traffic to analyze"
echo
sleep 3

# Start capture
airodump-ng \
    -c ${CHANNEL} \
    --bssid ${BSSID} \
    -w ${OUTPUT} \
    ${INTERFACE}

echo
echo "Capture saved to: ${OUTPUT}-01.cap"
echo "Analyze with: python3 analyze_capture.py ${OUTPUT}-01.cap"
