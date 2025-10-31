# Senville AC Control - Quick Reference

## Commands (Run from anywhere)

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

- **IP:** 192.168.254.183
- **ID:** 149533581404890
- **MAC:** B8:8C:29:60:97:8A
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

---

**Created:** 2025-10-30
**Status:** Fully operational ✅
