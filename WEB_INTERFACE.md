# Senville AC Web Interface

Modern web dashboard for controlling your Senville mini-split air conditioner.

## Features

- **Real-time status monitoring** - Updates every 5 seconds
- **Full control** - Power, mode, temperature, fan speed, and swing
- **Modern UI** - Clean, responsive design that works on desktop and mobile
- **REST API** - JSON API for integration with other systems
- **No cloud required** - All local control

## Quick Start

### 1. Start the Server

From the senville directory:

```bash
./start_web.sh
```

Or manually:

```bash
source venv/bin/activate
python3 api_server.py
```

### 2. Access the Dashboard

Open your web browser and navigate to:

```
http://localhost:5000
```

Or from another device on your network:

```
http://YOUR_IP:5000
```

To find your IP address:
```bash
hostname -I | awk '{print $1}'
```

### 3. Control Your AC

The dashboard provides:

- **Power Control** - Turn AC on/off with large buttons
- **Mode Selection** - Auto, Cool, Heat, Dry, Fan
- **Temperature** - Adjust with +/- buttons or type directly
- **Fan Speed** - Low, Med-Low, Medium, Med-High, Auto
- **Swing Control** - Toggle vertical and horizontal oscillation

## REST API Reference

### Base URL

```
http://localhost:5000/api
```

### Endpoints

#### Get Status

```
GET /api/status
```

Returns current AC state:

```json
{
  "success": true,
  "data": {
    "running": true,
    "mode": "cool",
    "target_temperature": 72.0,
    "indoor_temperature": 75.0,
    "outdoor_temperature": 85.0,
    "fan_speed": 60,
    "vertical_swing": false,
    "horizontal_swing": false,
    "fahrenheit": true,
    "eco_mode": false,
    "turbo_mode": false
  }
}
```

#### Set Power

```
POST /api/power
Content-Type: application/json

{
  "on": true
}
```

#### Set Mode

```
POST /api/mode
Content-Type: application/json

{
  "mode": "cool"
}
```

Valid modes: `auto`, `cool`, `heat`, `dry`, `fan`

#### Set Temperature

```
POST /api/temperature
Content-Type: application/json

{
  "temperature": 72,
  "fahrenheit": true
}
```

- Temperature range: 16-31°C (60-87°F)
- `fahrenheit` is optional (defaults to false)

#### Set Fan Speed

```
POST /api/fan
Content-Type: application/json

{
  "speed": 60
}
```

Valid speeds: `20` (Low), `40` (Med-Low), `60` (Medium), `80` (Med-High), `102` (Auto)

#### Set Swing

```
POST /api/swing
Content-Type: application/json

{
  "vertical": true,
  "horizontal": false
}
```

Both fields are optional - include only what you want to change.

#### Set Multiple Parameters

```
POST /api/control
Content-Type: application/json

{
  "running": true,
  "mode": "cool",
  "temperature": 72,
  "fahrenheit": true,
  "fan_speed": 60,
  "vertical_swing": false,
  "horizontal_swing": false
}
```

All fields are optional - include only what you want to change.

## API Examples

### Using curl

```bash
# Get status
curl http://localhost:5000/api/status

# Turn AC on
curl -X POST http://localhost:5000/api/power \
  -H "Content-Type: application/json" \
  -d '{"on": true}'

# Set to cool mode at 72°F
curl -X POST http://localhost:5000/api/control \
  -H "Content-Type: application/json" \
  -d '{"running": true, "mode": "cool", "temperature": 72, "fahrenheit": true}'
```

### Using Python

```python
import requests

API_BASE = "http://localhost:5000/api"

# Get status
response = requests.get(f"{API_BASE}/status")
status = response.json()
print(status)

# Turn AC on and set to cool at 72°F
requests.post(f"{API_BASE}/control", json={
    "running": True,
    "mode": "cool",
    "temperature": 72,
    "fahrenheit": True
})
```

### Using JavaScript

```javascript
// Get status
fetch('/api/status')
  .then(response => response.json())
  .then(data => console.log(data));

// Turn AC on
fetch('/api/power', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ on: true })
});
```

## Integration Examples

### Home Assistant

Add to your `configuration.yaml`:

```yaml
rest_command:
  senville_power_on:
    url: "http://YOUR_IP:5000/api/power"
    method: POST
    content_type: "application/json"
    payload: '{"on": true}'

  senville_power_off:
    url: "http://YOUR_IP:5000/api/power"
    method: POST
    content_type: "application/json"
    payload: '{"on": false}'

  senville_set_temp:
    url: "http://YOUR_IP:5000/api/temperature"
    method: POST
    content_type: "application/json"
    payload: '{"temperature": {{ temp }}, "fahrenheit": true}'
```

### Node-RED

Use HTTP request nodes:

1. **Status Monitor Node**
   - Method: GET
   - URL: `http://YOUR_IP:5000/api/status`
   - Trigger: Inject node (every 5 seconds)

2. **Control Node**
   - Method: POST
   - URL: `http://YOUR_IP:5000/api/control`
   - Body: JSON object with desired settings

### Cron Job Schedule

Create temperature schedules with cron:

```bash
# Morning - warm up (7 AM)
0 7 * * * curl -X POST http://localhost:5000/api/control -H "Content-Type: application/json" -d '{"running": true, "mode": "heat", "temperature": 70, "fahrenheit": true}'

# Day - cool down (9 AM)
0 9 * * * curl -X POST http://localhost:5000/api/control -H "Content-Type: application/json" -d '{"running": true, "mode": "cool", "temperature": 74, "fahrenheit": true}'

# Night - turn off (11 PM)
0 23 * * * curl -X POST http://localhost:5000/api/power -H "Content-Type: application/json" -d '{"on": false}'
```

## Mobile Access

### Access from Phone/Tablet

1. Find your computer's IP address:
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. On your mobile device, open browser and go to:
   ```
   http://YOUR_IP:5000
   ```

3. For easier access, add to home screen:
   - **iOS**: Tap Share button → "Add to Home Screen"
   - **Android**: Tap menu (⋮) → "Add to Home screen"

### Create PWA (Progressive Web App)

To make the interface installable, add a manifest file (future enhancement).

## Security

### Local Network Only (Default)

By default, the server binds to `0.0.0.0` which makes it accessible on your local network. This is safe if your network is secure.

### Restrict to Localhost

To only allow access from the same machine, edit `api_server.py`:

```python
app.run(host='127.0.0.1', port=5000, debug=False)
```

### Add Authentication (Future)

For internet-exposed installations, add authentication:

1. Use Flask-HTTPAuth
2. Add API key validation
3. Use HTTPS with SSL certificates
4. Set up reverse proxy (nginx, Caddy)

## Troubleshooting

### Server Won't Start

**Error: "Address already in use"**

Another service is using port 5000. Find it:
```bash
sudo lsof -i :5000
```

Kill the process or change the port in `api_server.py`.

**Error: "Missing credentials"**

Ensure `.env` file exists with valid credentials:
```bash
cat .env
```

### Can't Access from Other Devices

**Check firewall:**
```bash
sudo ufw allow 5000
```

**Verify server is listening on all interfaces:**
```bash
netstat -tln | grep 5000
```

You should see `0.0.0.0:5000`, not `127.0.0.1:5000`.

**Find your IP address:**
```bash
hostname -I
```

### Dashboard Shows "Disconnected"

1. Check AC is powered on and connected to WiFi
2. Verify IP address in `.env` is correct
3. Test connectivity: `ping ${SENVILLE_IP}`
4. Check API status endpoint:
   ```bash
   curl http://localhost:5000/api/status
   ```

### Commands Don't Work

1. Check browser console for errors (F12)
2. Verify credentials are valid in `.env`
3. Test API directly with curl
4. Check AC responds to direct Python scripts

## Advanced Usage

### Run as Background Service

Create systemd service (`/etc/systemd/system/senville-web.service`):

```ini
[Unit]
Description=Senville AC Web Interface
After=network.target

[Service]
Type=simple
User=beattie
WorkingDirectory=/home/beattie/senville
ExecStart=/home/beattie/senville/venv/bin/python3 /home/beattie/senville/api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable senville-web
sudo systemctl start senville-web
```

### Use Production Server

For better performance, use gunicorn:

```bash
source venv/bin/activate
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Custom Port

Change port in `api_server.py`:

```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

## Files

- `api_server.py` - Flask REST API server
- `start_web.sh` - Startup script
- `web/index.html` - Dashboard HTML
- `web/style.css` - Dashboard styling
- `web/app.js` - Dashboard JavaScript

## Architecture

```
┌─────────────┐
│   Browser   │
│  (Dashboard)│
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────┐
│   Flask     │
│  API Server │
└──────┬──────┘
       │ Python
       │
┌──────▼──────┐
│  midea-     │
│  beautiful  │
│   -air      │
└──────┬──────┘
       │ TCP (6444)
       │
┌──────▼──────┐
│  Senville   │
│  AC Unit    │
└─────────────┘
```

## Next Steps

- Add user authentication
- Create PWA manifest for installation
- Add historical data logging
- Create scheduling interface
- Add energy usage tracking
- Multi-zone support

---

**Created:** 2025-10-31
**Status:** Fully functional
**Access:** http://localhost:5000
