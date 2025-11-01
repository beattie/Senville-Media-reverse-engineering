# Senville AC Control - Quick Reference

## Web Interface

**Start server:**
```bash
cd ~/senville
./start_web.sh
```

**Access:**
```
http://localhost:5000              # Main control dashboard
http://localhost:5000/schedules.html   # Scheduling interface
```

**Features:**
- Real-time status updates
- Full AC control via web UI
- Schedule management
- REST API for automation
- Mobile-friendly design

**See:** WEB_INTERFACE.md and AUTOMATION.md

## Scheduling

**Create schedules via CLI:**
```bash
# Add morning warmup schedule
python3 manage_schedules.py add "Morning Heat" "07:00" --power on --mode heat --temp-f 70

# List all schedules
python3 manage_schedules.py list

# Start scheduler daemon
python3 scheduler.py --daemon
```

**Or use web interface:**
http://localhost:5000/schedules.html

**See:** AUTOMATION.md for full documentation

## Command Line (Run from anywhere)

### Check Status
```bash
senville-status           # Concise one-line
senville-status -v        # Verbose details
senville-status -vv       # Extra verbose (all attributes)
senville-status -q        # Quiet (no "Querying..." message)
```

### Simple Control
```bash
senville --power on
senville --power off
senville --temp 22              # Celsius
senville --temp-f 72            # Fahrenheit
senville --mode cool
senville --mode heat
senville --power on --mode cool --temp-f 68
```

### Full Control (All Features)
```bash
senville-control --vswing on    # Vertical swing on
senville-control --vswing off   # Vertical swing off
senville-control --hswing on    # Horizontal swing on
senville-control --fan-speed 60 # Set fan speed
senville-control --power on --mode cool --temp-f 72 --vswing off --fan-speed 60
```

## Settings

### Modes
- `auto` - Automatic
- `cool` - Cooling
- `heat` - Heating
- `dry` - Dehumidifier
- `fan` - Fan only

### Fan Speeds
- `20` - Low
- `40` - Med-Low
- `60` - Medium
- `80` - Med-High
- `102` - Auto

### Temperature Range
- **Celsius:** 16-31°C
- **Fahrenheit:** 60-87°F

## Files Location

**Directory:** `~/senville/`

**Scripts:**
- `status.py` - Check AC status
- `control_simple.py` - Basic control
- `control_full.py` - Full control with swing/fan
- `discover.py` - Find devices

**Config:**
- `.env` - Your device credentials

**Documentation:**
- `README.md` - Complete guide
- `WEB_INTERFACE.md` - Web dashboard & REST API
- `senville-protocol-documentation.md` - Protocol details
- `senville-control-guide.md` - Usage guide
- `QUICK_REFERENCE.md` - This file

## Examples

```bash
# Morning: Turn on heat at 68°F
senville --power on --mode heat --temp-f 68

# Check current status
senville-status

# Adjust temperature
senville --temp-f 72

# Turn on swing for better circulation
senville-control --vswing on

# Evening: Turn off
senville --power off

# Quick check
senville-status -q
```

## Device Info

- **IP:** ${SENVILLE_IP}
- **ID:** ${SENVILLE_DEVICE_ID}
- **MAC:** ${SENVILLE_MAC}
- **Model:** OSK105 (Midea-based)

## Features

✅ Local control (no cloud needed)
✅ Power on/off
✅ Temperature control (°C or °F)
✅ Mode selection (auto/cool/heat/dry/fan)
✅ Fan speed control
✅ Vertical/horizontal swing
✅ Multiple verbosity levels
✅ Works from any directory
✅ Web interface & REST API

---

**Created:** 2025-10-30
**Updated:** 2025-10-31
**Status:** Fully operational ✅
