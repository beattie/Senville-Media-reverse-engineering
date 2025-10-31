#!/bin/bash
# Senville Control - Quick Start Guide

cat << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║     Senville/Midea Mini-Split Control & Reverse Engineering   ║
╚═══════════════════════════════════════════════════════════════╝

QUICK START GUIDE
═════════════════

STEP 1: DISCOVER YOUR DEVICE
────────────────────────────
source venv/bin/activate
python3 discover.py --account YOUR_EMAIL --password YOUR_PASSWORD

This will output your device IP, token, and key.


STEP 2: CONFIGURE
─────────────────
cp .env.example .env
nano .env    # Add your credentials from step 1


STEP 3: CONTROL YOUR AC
───────────────────────

Check status:
  python3 status.py

Turn on in cool mode at 22°C:
  python3 control.py --power on --mode cool --temp 22

Turn off:
  python3 control.py --power off

Change temperature:
  python3 control.py --temp 24


WIFI PACKET CAPTURE (Advanced)
═══════════════════════════════

Enable monitor mode:
  sudo ./wifi_setup.sh

Scan for device:
  sudo airodump-ng wlp3s0mon
  (Note the BSSID and Channel)

Capture traffic:
  sudo ./capture_traffic.sh -c CHANNEL -b MAC_ADDRESS
  (Use app while capturing to generate traffic)

Analyze capture:
  python3 analyze_capture.py senville_capture-01.cap

Restore WiFi:
  sudo ./wifi_restore.sh


FILES IN THIS DIRECTORY
═══════════════════════

Control Scripts:
  discover.py          - Find devices and get credentials
  status.py            - Check AC status
  control.py           - Control AC (power, temp, mode)

WiFi Capture:
  wifi_setup.sh        - Enable monitor mode
  wifi_restore.sh      - Restore normal WiFi
  capture_traffic.sh   - Capture packets
  analyze_capture.py   - Analyze captures

Documentation:
  README.md                              - This guide
  senville-protocol-documentation.md     - Protocol specs
  senville-control-guide.md              - Detailed usage

Configuration:
  .env.example         - Example configuration
  .env                 - Your credentials (create this)


VIRTUAL ENVIRONMENT
═══════════════════

Activate:      source venv/bin/activate
Deactivate:    deactivate

Installed packages:
  - midea-beautiful-air
  - msmart
  - scapy
  - python-dotenv


NEED HELP?
══════════

View README:
  less README.md

View protocol docs:
  less senville-protocol-documentation.md

View control guide:
  less senville-control-guide.md


═══════════════════════════════════════════════════════════════

Happy hacking! 🚀

EOF
