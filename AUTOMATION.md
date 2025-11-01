# Senville AC Automation & Scheduling

Complete automation system for scheduling temperature changes, modes, and other AC settings.

## Features

- ⏰ **Time-based schedules** - Run actions at specific times
- 📅 **Day selection** - Run on specific days or every day
- 🔄 **Background daemon** - Runs continuously checking for schedules
- 🌐 **Web interface** - Manage schedules through the dashboard
- 💻 **CLI tools** - Command-line schedule management
- 🔌 **REST API** - Integrate with other systems
- 🚀 **Systemd service** - Auto-start on boot (optional)

## Quick Start

### 1. Access Web Interface

The easiest way to manage schedules is through the web interface:

```bash
# Start the web server (if not already running)
./start_web.sh

# Open in browser
http://localhost:5000/schedules.html
```

### 2. Start the Scheduler

The scheduler needs to be running to execute schedules. You can start it:

**Via Web Interface:**
- Go to http://localhost:5000/schedules.html
- Click "Start Scheduler" button

**Via Command Line:**
```bash
# Start in foreground (see output)
python3 scheduler.py

# Start as background daemon
python3 scheduler.py --daemon

# Check status
python3 scheduler.py --status

# Stop daemon
python3 scheduler.py --stop
```

### 3. Create Schedules

**Via Web Interface:**
1. Go to http://localhost:5000/schedules.html
2. Click "+ Add New Schedule"
3. Fill in the form:
   - Name: e.g., "Morning Warmup"
   - Time: e.g., "07:00"
   - Days: Select specific days or leave empty for every day
   - Actions: Set power, mode, temperature, fan speed
4. Click "Save Schedule"

**Via Command Line:**
```bash
# Morning: Turn on heat at 70°F
python3 manage_schedules.py add "Morning Warmup" "07:00" --power on --mode heat --temp-f 70

# Afternoon: Cool to 74°F
python3 manage_schedules.py add "Afternoon Cool" "15:00" --mode cool --temp-f 74

# Night: Turn off (weekdays only)
python3 manage_schedules.py add "Night Off" "23:00" --days mon tue wed thu fri --power off

# List all schedules
python3 manage_schedules.py list
```

## Web Interface Guide

### Scheduler Status Dashboard

The schedules page shows:
- **Scheduler Status**: Running or Stopped
- **Active Schedules**: How many schedules are enabled
- **Start/Stop buttons**: Control the scheduler daemon

### Schedule List

Each schedule shows:
- **Name and time**
- **Days** it runs on
- **Actions** it will perform
- **Last run time**
- **Toggle** to enable/disable
- **Edit** button to modify
- **Delete** button to remove

### Creating/Editing Schedules

**Schedule Name**: Descriptive name (e.g., "Morning Warmup", "Bedtime")

**Time**: 24-hour format (e.g., 07:00, 14:30, 23:00)

**Days of Week**:
- Check specific days: Mon, Tue, Wed, Thu, Fri, Sat, Sun
- Leave all unchecked: Runs every day

**Actions** (all optional):
- **Power**: On or Off
- **Mode**: Auto, Cool, Heat, Dry, Fan
- **Temperature**: 60-87°F (or 16-31°C)
- **Fan Speed**: Low, Med-Low, Medium, Med-High, Auto

At least one action must be specified.

## Command-Line Management

### List Schedules

```bash
python3 manage_schedules.py list
```

Shows all schedules with ID, name, time, days, and actions.

### Add Schedule

```bash
python3 manage_schedules.py add NAME TIME [OPTIONS]
```

**Examples:**

```bash
# Turn on heat in the morning
python3 manage_schedules.py add "Morning Heat" "07:00" \
  --power on --mode heat --temp-f 68

# Cool down in afternoon (weekdays)
python3 manage_schedules.py add "Work Cool" "15:00" \
  --days mon tue wed thu fri \
  --mode cool --temp-f 72

# Turn off at night
python3 manage_schedules.py add "Night Off" "23:00" \
  --power off

# Set eco mode with fan
python3 manage_schedules.py add "Eco Mode" "09:00" \
  --mode fan --fan-speed 40
```

**Options:**
- `--days mon tue wed thu fri sat sun` - Specific days
- `--power on|off` - Turn on or off
- `--mode auto|cool|heat|dry|fan` - Operating mode
- `--temp N` - Temperature in Celsius
- `--temp-f N` - Temperature in Fahrenheit
- `--fan-speed 20|40|60|80|102` - Fan speed

### Delete Schedule

```bash
python3 manage_schedules.py delete <ID>
```

Example:
```bash
python3 manage_schedules.py delete 1
```

### Enable/Disable Schedule

```bash
python3 manage_schedules.py enable <ID>
python3 manage_schedules.py disable <ID>
```

Useful to temporarily disable a schedule without deleting it.

## Scheduler Daemon

### Manual Control

```bash
# Start in foreground (see logs)
python3 scheduler.py

# Start as daemon
python3 scheduler.py --daemon

# Check status
python3 scheduler.py --status

# Stop daemon
python3 scheduler.py --stop
```

### What It Does

The scheduler:
1. Checks for schedules every 30 seconds
2. Runs schedules when time matches (within 1-minute window)
3. Applies all actions specified in the schedule
4. Records last run time
5. Continues running in background

### Logs

When running in foreground, you'll see output like:

```
============================================================
Senville AC Scheduler Service
============================================================
Started at: 2025-10-31 07:00:00
Schedule file: /home/beattie/senville/schedules.json
Checking schedules every 30 seconds...
============================================================

[2025-10-31 07:00:00] Executing schedule: Morning Warmup
  Applied: power: on, mode: heat, temp: 70°F
```

## Auto-Start on Boot

To have the scheduler start automatically when your system boots:

### Install Systemd Service

```bash
sudo ./install_services.sh
```

This installs the systemd service and enables it.

### Control Service

```bash
# Start service
sudo systemctl start senville-scheduler

# Stop service
sudo systemctl stop senville-scheduler

# Check status
sudo systemctl status senville-scheduler

# View logs
sudo journalctl -u senville-scheduler -f

# Enable auto-start on boot
sudo systemctl enable senville-scheduler

# Disable auto-start
sudo systemctl disable senville-scheduler
```

## Schedule Examples

### Daily Routine

```bash
# Morning warmup at 6:30 AM
python3 manage_schedules.py add "Morning Warmup" "06:30" \
  --power on --mode heat --temp-f 68

# Daytime comfort at 9 AM
python3 manage_schedules.py add "Day Comfort" "09:00" \
  --mode auto --temp-f 72

# Evening cool at 6 PM
python3 manage_schedules.py add "Evening Cool" "18:00" \
  --mode cool --temp-f 70

# Night off at 11 PM
python3 manage_schedules.py add "Night Off" "23:00" \
  --power off
```

### Weekday vs Weekend

```bash
# Weekday morning (earlier)
python3 manage_schedules.py add "Weekday Morning" "06:00" \
  --days mon tue wed thu fri \
  --power on --mode heat --temp-f 68

# Weekend morning (sleep in)
python3 manage_schedules.py add "Weekend Morning" "08:00" \
  --days sat sun \
  --power on --mode heat --temp-f 68
```

### Seasonal Schedules

**Summer (Cooling):**
```bash
python3 manage_schedules.py add "Summer Day" "07:00" \
  --power on --mode cool --temp-f 74

python3 manage_schedules.py add "Summer Night" "22:00" \
  --mode cool --temp-f 72
```

**Winter (Heating):**
```bash
python3 manage_schedules.py add "Winter Morning" "06:00" \
  --power on --mode heat --temp-f 70

python3 manage_schedules.py add "Winter Night" "22:00" \
  --mode heat --temp-f 65
```

### Energy Saving

```bash
# Away mode (weekdays 9-5)
python3 manage_schedules.py add "Away Start" "09:00" \
  --days mon tue wed thu fri \
  --power off

python3 manage_schedules.py add "Away End" "17:00" \
  --days mon tue wed thu fri \
  --power on --mode auto --temp-f 72
```

## REST API

The scheduling system provides REST API endpoints for integration.

### Get All Schedules

```bash
curl http://localhost:5000/api/schedules
```

### Create Schedule

```bash
curl -X POST http://localhost:5000/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "API Schedule",
    "time": "14:00",
    "days": ["mon", "wed", "fri"],
    "action": {
      "power": true,
      "mode": "cool",
      "temperature": 72,
      "fahrenheit": true
    }
  }'
```

### Update Schedule

```bash
curl -X PUT http://localhost:5000/api/schedules/1 \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false
  }'
```

### Delete Schedule

```bash
curl -X DELETE http://localhost:5000/api/schedules/1
```

### Check Scheduler Status

```bash
curl http://localhost:5000/api/scheduler/status
```

### Start/Stop Scheduler

```bash
# Start
curl -X POST http://localhost:5000/api/scheduler/start

# Stop
curl -X POST http://localhost:5000/api/scheduler/stop
```

## Data Storage

Schedules are stored in:
```
/home/beattie/senville/schedules.json
```

This is a JSON file containing all schedule definitions.

### Schedule Format

```json
{
  "id": 1,
  "name": "Morning Warmup",
  "time": "07:00",
  "days": ["mon", "tue", "wed", "thu", "fri"],
  "action": {
    "power": true,
    "mode": "heat",
    "temperature": 70,
    "fahrenheit": true,
    "fan_speed": 60
  },
  "enabled": true,
  "created_at": "2025-10-31T09:00:00",
  "last_run": "2025-10-31T07:00:00"
}
```

### Backup Schedules

```bash
# Backup
cp schedules.json schedules.backup.json

# Restore
cp schedules.backup.json schedules.json
```

## Troubleshooting

### Scheduler Not Running Schedules

**Check scheduler is running:**
```bash
python3 scheduler.py --status
```

**Check schedule is enabled:**
```bash
python3 manage_schedules.py list
```

**Check time and days match:**
- Schedules run when the current time matches (within 1-minute window)
- Day of week must match if specified

**View scheduler logs:**
```bash
# If running in foreground, check terminal output
# If running as systemd service:
sudo journalctl -u senville-scheduler -f
```

### Schedule Runs But AC Doesn't Change

**Check AC is reachable:**
```bash
ping ${SENVILLE_IP}
python3 status.py
```

**Check credentials:**
```bash
cat .env
```

**Test manual control:**
```bash
python3 control_full.py --power on --temp-f 72
```

### Web Interface Can't Start/Stop Scheduler

**Check permissions:**
The web server needs to execute Python scripts. If running under a different user, permissions may be an issue.

**Check paths:**
Verify paths in `api_server.py` match your setup.

### Schedules Not Showing in Web Interface

**Refresh the page** - Press Ctrl+R or F5

**Check browser console** - Press F12 and look for errors

**Check API endpoint:**
```bash
curl http://localhost:5000/api/schedules
```

## Advanced Usage

### Dynamic Schedules Based on Weather

Combine with weather API to adjust temperature:

```python
import requests

# Get weather
weather = requests.get('http://api.weather.com/...').json()
temp_outside = weather['temperature']

# Adjust indoor target
if temp_outside > 85:
    target = 70  # Cool more on hot days
else:
    target = 74  # Normal cooling

# Update schedule or control directly
```

### Multiple Zones

If you have multiple AC units, create separate schedule sets:

```bash
# Living room schedules
python3 manage_schedules.py add "LR Morning" "07:00" ...

# Bedroom schedules
python3 manage_schedules.py add "BR Morning" "06:30" ...
```

Note: Current system supports one unit. For multiple units, you'd need to modify the code to accept device parameters.

### Vacation Mode

Disable all schedules while away:

```bash
# Disable all
for id in $(python3 manage_schedules.py list | grep -oP '^\d+'); do
    python3 manage_schedules.py disable $id
done

# Re-enable when back
for id in $(python3 manage_schedules.py list | grep -oP '^\d+'); do
    python3 manage_schedules.py enable $id
done
```

Or simpler - just stop the scheduler:
```bash
python3 scheduler.py --stop
```

## Files

- `scheduler.py` - Scheduler daemon
- `manage_schedules.py` - CLI schedule manager
- `schedules.json` - Schedule storage
- `scheduler.pid` - Daemon PID file
- `senville-scheduler.service` - Systemd service
- `install_services.sh` - Service installer
- `web/schedules.html` - Web interface
- `web/schedules.js` - Web interface JavaScript
- `web/schedules.css` - Web interface styling

## Tips

1. **Start simple** - Create one or two schedules first
2. **Test thoroughly** - Watch the scheduler run for a day before relying on it
3. **Backup schedules** - Copy `schedules.json` before major changes
4. **Use descriptive names** - Makes management easier
5. **Check logs** - Monitor the scheduler output to ensure schedules run
6. **Set reminders** - Update schedules when seasons change
7. **Disable unused schedules** - Rather than deleting, for easy re-enabling

---

**Created:** 2025-10-31
**Status:** Fully functional
**Access:** http://localhost:5000/schedules.html
