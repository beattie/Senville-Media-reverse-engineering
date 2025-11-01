# Senville AC Control - Desktop GUI

Simple desktop application for controlling your Senville/Midea mini-split AC with a graphical interface.

## Features

- 📊 **Real-time Status Display** - View current temperature, mode, fan speed, swing settings
- 🎛️ **Full Control** - Power, mode, temperature, fan speed, swing controls
- 🔄 **Auto-refresh** - Status updates every 5 seconds
- 🌡️ **Temperature Units** - Toggle between Fahrenheit and Celsius
- 🖥️ **Native Desktop App** - No browser needed, uses Python tkinter

## Screenshot

```
┌─────────────────────────────────────────┐
│      Senville AC Control                │
│      Device: ${SENVILLE_IP}             │
│                                          │
│  ┌─ Current Status ──────────────────┐  │
│  │ Power:         ON                  │  │
│  │ Mode:          Cool                │  │
│  │ Target Temp:   72°F                │  │
│  │ Indoor Temp:   75°F                │  │
│  │ Fan Speed:     Medium              │  │
│  │ V-Swing:       OFF                 │  │
│  │ H-Swing:       OFF                 │  │
│  │ Last Updated:  14:32:15            │  │
│  └────────────────────────────────────┘  │
│                                          │
│  ┌─ Controls ─────────────────────────┐  │
│  │ Power:    [ ON ] [ OFF ]           │  │
│  │ Mode:     [▼ cool        ]         │  │
│  │ Temp:     [━━━●━━━━━━] 72°F ⚪°F ⚫°C│  │
│  │ Fan:      [▼ Medium      ]         │  │
│  │ V-Swing:  ☐ Enable                │  │
│  │ H-Swing:  ☐ Enable                │  │
│  └────────────────────────────────────┘  │
│                                          │
│  [  Refresh Status  ] ☑ Auto-refresh    │
│                                          │
│  Status: Ready                           │
└─────────────────────────────────────────┘
```

## Installation

### Prerequisites

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3-tk
```

**Linux (Fedora):**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
tkinter is included with Python - no extra installation needed

**Windows:**
tkinter is included with Python - no extra installation needed

**Python packages:**
```bash
source venv/bin/activate
pip install midea-beautiful-air python-dotenv
```

## Quick Start

### 1. Configure Your Device

Ensure `.env` is configured with your device credentials:
```bash
cp .env.example .env
nano .env  # Add your SENVILLE_IP, TOKEN, KEY
```

### 2. Launch the GUI

**Easy way (recommended):**
```bash
./start_gui.sh
```

**Manual way:**
```bash
source venv/bin/activate
python3 gui_control.py
```

### 3. Use the Interface

The GUI is divided into sections:

**Current Status (top):**
- Shows live status from your AC
- Updates automatically every 5 seconds (if auto-refresh enabled)
- Last updated timestamp

**Controls (middle):**
- **Power buttons** - Turn AC on or off
- **Mode dropdown** - Select: Auto, Cool, Heat, Dry, Fan
- **Temperature slider** - Adjust target temperature
  - Toggle °F/°C with radio buttons
  - Range: 60-87°F (16-31°C)
- **Fan speed dropdown** - Select fan speed
- **Swing checkboxes** - Enable/disable vertical and horizontal swing

**Action buttons (bottom):**
- **Refresh Status** - Manual refresh
- **Auto-refresh checkbox** - Enable/disable automatic 5-second updates

## Features in Detail

### Status Display

Shows real-time information:
- **Power** - ON (green) or OFF (red)
- **Mode** - Current operating mode
- **Target Temp** - Desired temperature
- **Indoor Temp** - Current room temperature
- **Fan Speed** - Current fan setting
- **V-Swing / H-Swing** - Swing status

### Power Control

Quick on/off buttons:
```
Click "ON"  → Turns AC on with current settings
Click "OFF" → Turns AC off
```

### Mode Selection

Choose operating mode from dropdown:
- **Auto** - Automatic heating/cooling
- **Cool** - Cooling mode
- **Heat** - Heating mode
- **Dry** - Dehumidifier mode
- **Fan** - Fan only (no heating/cooling)

Changes apply immediately when selected.

### Temperature Control

Use the slider to set target temperature:
- **Drag slider** - Adjust temperature
- **Click rail** - Jump to temperature
- **°F/°C toggle** - Switch units (slider updates automatically)

**Temperature Ranges:**
- Fahrenheit: 60-87°F
- Celsius: 16-31°C

Temperature changes apply when you release the slider or click a new position.

### Fan Speed Control

Select from dropdown:
- **Auto** - Automatic fan speed
- **Low** - Quietest, least airflow
- **Med-Low** - Low-medium speed
- **Medium** - Moderate speed
- **Med-High** - Medium-high speed
- **High** - Maximum airflow (may be noisy)

### Swing Control

Enable/disable oscillation:
- **Vertical Swing** - Up/down oscillation
- **Horizontal Swing** - Left/right oscillation
- Check/uncheck to toggle

### Auto-Refresh

Keep status up-to-date automatically:
- ☑ **Enabled** - Refreshes every 5 seconds
- ☐ **Disabled** - Manual refresh only

Auto-refresh is enabled by default.

## Keyboard Shortcuts

Currently none - all controls are mouse/touch based.

Future enhancement could add:
- `R` - Refresh
- `Space` - Toggle power
- `+/-` - Adjust temperature
- `Esc` - Close application

## Troubleshooting

### "Connection Error" on startup

**Problem:** Cannot connect to AC device

**Solutions:**
1. Verify device is powered on and connected to WiFi
2. Check `.env` has correct `SENVILLE_IP`
3. Test connectivity: `ping ${SENVILLE_IP}`
4. Run troubleshooter: `./troubleshoot.sh`
5. Rediscover device: `python3 discover.py ${SENVILLE_IP}`

### "Configuration Error" - .env not found

**Problem:** Missing `.env` file

**Solution:**
```bash
cp .env.example .env
nano .env  # Add your credentials
```

### GUI doesn't start - "tkinter not found"

**Problem:** Python tkinter module not installed

**Solutions:**

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

**macOS/Windows:**
tkinter should be included - reinstall Python if missing

### Status shows "--" for all values

**Problem:** Device not responding

**Solutions:**
1. Click "Refresh Status" button
2. Check network connectivity
3. Verify credentials in `.env`
4. Check device is powered on

### Changes don't apply

**Problem:** Commands sent but device doesn't respond

**Solutions:**
1. Wait a few seconds - commands may take time
2. Check "Last Updated" timestamp - should change after command
3. Try manual refresh
4. Check device status via web interface or command line
5. Restart device if unresponsive

### GUI freezes

**Problem:** Application becomes unresponsive

**Solutions:**
1. Commands run in background threads - may take 5-10 seconds
2. Check status bar at bottom for current operation
3. If truly frozen, close and restart: `./start_gui.sh`
4. Check network latency to device

### Temperature slider jumps when switching °F/°C

**Problem:** Slider position changes during unit conversion

**Expected behavior:** Value is converted (e.g., 72°F → 22°C)

This is normal - the slider updates to show equivalent temperature in new unit.

## Advanced Usage

### Running from Different Directory

The GUI can be started from any directory:
```bash
/path/to/senville/start_gui.sh
```

Or:
```bash
cd /path/to/senville
python3 gui_control.py
```

### Running Multiple Instances

You can run multiple GUI windows if you have multiple AC units:

1. Create separate `.env` files:
   ```bash
   cp .env .env.bedroom
   cp .env .env.living_room
   ```

2. Modify `gui_control.py` to use different `.env` file

3. Or run different instances from different directories

### Desktop Launcher (Linux)

Create a desktop launcher file:

**`~/.local/share/applications/senville-ac.desktop`:**
```ini
[Desktop Entry]
Type=Application
Name=Senville AC Control
Comment=Control your Senville mini-split AC
Exec=/home/YOUR_USER/senville/start_gui.sh
Icon=temperature
Terminal=false
Categories=Utility;
```

After creating, the app appears in your application menu.

### Run on Startup (Linux)

Add to startup applications:

**Ubuntu/GNOME:**
1. Open "Startup Applications"
2. Click "Add"
3. Name: Senville AC Control
4. Command: `/home/YOUR_USER/senville/start_gui.sh`
5. Click "Add"

**Auto-start requirements:**
- Device must be on same network at boot
- `.env` must be configured
- Will run minimized/in background

## Comparison with Other Interfaces

| Feature | GUI | Web Interface | CLI |
|---------|-----|---------------|-----|
| Setup | ✅ Easy | 🔶 Moderate | 🔶 Moderate |
| Status Display | ✅ Visual | ✅ Visual | 📝 Text |
| Auto-refresh | ✅ Yes | ✅ Yes | ❌ Manual |
| Remote Access | ❌ Local only | ✅ Network | ✅ SSH |
| Mobile Friendly | ❌ No | ✅ Yes | 📱 Via SSH |
| Browser Required | ❌ No | ✅ Yes | ❌ No |
| Resource Usage | 💾 Low | 💾 Low | 💾 Minimal |
| Scheduling | ❌ No | ✅ Yes | ✅ Yes |

**Recommendations:**
- **GUI** - Best for desktop control, single user, local access
- **Web** - Best for multiple users, remote access, mobile devices
- **CLI** - Best for scripting, automation, SSH access

## Technical Details

### Framework

- **GUI Library:** tkinter (Python standard library)
- **Threading:** Background threads for API calls (non-blocking UI)
- **Update Rate:** 5-second auto-refresh (configurable)
- **Connection:** Reuses device connection for efficiency

### Dependencies

Required Python packages:
- `midea-beautiful-air` - Device control
- `python-dotenv` - Configuration loading
- `tkinter` - GUI framework (usually pre-installed)

### Performance

- **Startup time:** ~1-2 seconds
- **Command latency:** 1-3 seconds (network dependent)
- **Memory usage:** ~50-80 MB
- **CPU usage:** <1% idle, <5% during updates

### Architecture

```
┌──────────────┐
│   GUI App    │
│  (tkinter)   │
└──────┬───────┘
       │
       ├─ Status Refresh Thread (every 5s)
       ├─ Control Threads (on demand)
       │
       v
┌──────────────┐
│ .env Config  │ ← SENVILLE_IP, TOKEN, KEY
└──────────────┘
       │
       v
┌──────────────────┐
│ midea-beautiful  │ ← Python library
└────────┬─────────┘
         │
         v
┌──────────────┐
│  AC Device   │ ← TCP port 6444
│  ${SENVILLE_IP}  │
└──────────────┘
```

## Limitations

1. **Single device** - One GUI window controls one AC unit
2. **Local network only** - Requires direct network access
3. **No scheduling** - Use web interface or CLI for schedules
4. **No history** - Status is real-time only, no logging
5. **Desktop only** - Not suitable for mobile devices
6. **No offline mode** - Requires network connection to device

## Future Enhancements

Possible improvements:
- [ ] Multi-device support (tabs or windows)
- [ ] Temperature history graphs
- [ ] Scheduling integration
- [ ] System tray icon
- [ ] Keyboard shortcuts
- [ ] Dark mode theme
- [ ] Customizable refresh interval
- [ ] Alert notifications
- [ ] Quick presets (sleep mode, away mode, etc.)

## Related Documentation

- `README.md` - Main project documentation
- `WEB_INTERFACE.md` - Web dashboard alternative
- `QUICK_REFERENCE.md` - Command-line interface
- `senville-control-guide.md` - Detailed control guide

## Credits

Built using:
- Python 3 and tkinter
- midea-beautiful-air library
- Midea V3 protocol reverse engineering

---

**Created:** 2025-11-01
**Status:** Fully functional desktop GUI
