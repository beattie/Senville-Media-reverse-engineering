# Setup Instructions

This project uses environment variables for configuration to keep sensitive data out of git.

## Quick Start

### 1. Install Dependencies

```bash
# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install midea-beautiful-air msmart-ng python-dotenv
```

### 2. Configure Your Device

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your device information
nano .env  # or use your preferred editor
```

Required variables in `.env`:
- `SENVILLE_IP` - Your AC unit's IP address
- `SENVILLE_TOKEN` - Authentication token (get via discovery)
- `SENVILLE_KEY` - Authentication key (get via discovery)

Optional variables:
- `SENVILLE_DEVICE_ID` - Device ID from discovery
- `SENVILLE_MAC` - MAC address of your device
- `NETWORK_INTERFACE` - For packet capture scripts (e.g., eth0)
- `PHONE_IP` - For phone-to-AC packet capture

### 3. Discover Your Device

```bash
source venv/bin/activate

# Discover device on your network
msmart-ng discover YOUR_AC_IP_ADDRESS

# This will output your device's token and key
# Add these to your .env file
```

### 4. Generate Documentation

```bash
# Generate personalized documentation with your device info
./generate_local.sh
```

This creates `*.local.md` files with your actual IP addresses for easy reference.
The `.local` files are automatically ignored by git.

### 5. Test Connection

```bash
# Quick test
./troubleshoot.sh

# Or check status
source venv/bin/activate
python3 status.py
```

## File Structure

### Configuration Files
- `.env.example` - Template configuration (safe to commit)
- `.env` - Your actual configuration (gitignored)

### Documentation
- `*.md` - Template docs with `${VARIABLE}` placeholders (in git)
- `*.local.md` - Generated docs with your real values (gitignored)

### Scripts
- `generate_local.sh` - Generates `.local` files from templates
- All Python scripts automatically read from `.env`
- Shell scripts use environment variables from `.env`

## Security

**Safe to commit:**
- Template files with `${VARIABLE}` syntax
- `.env.example`
- Scripts that read from `.env`

**Never commit:**
- `.env` - Contains your credentials
- `*.local.md` - Contains your IP addresses
- `*.pcap` - Packet captures
- `scheduler.pid` - Runtime files
- `schedules.json` - Your personal schedules

All sensitive files are in `.gitignore`.

## Usage

Once configured, you can:

```bash
# View your personalized docs
cat PROJECT_NOTES.local.md

# Use the control scripts (they read .env automatically)
python3 control_simple.py --power on
python3 status.py

# Start the web interface
./start_web.sh
```

## Updating Documentation

If you need to update docs:

1. Edit the template files (e.g., `PROJECT_NOTES.md`)
2. Use `${VARIABLE_NAME}` syntax for values from `.env`
3. Run `./generate_local.sh` to update your `.local` files
4. The template files (with placeholders) are committed to git
5. Your `.local` files (with real values) stay on your machine

## Troubleshooting

If `./generate_local.sh` doesn't work:
- Make sure `.env` exists and has all required variables
- Check that `envsubst` or `perl` is installed
- Run with bash explicitly: `bash -x ./generate_local.sh`

If scripts can't find your device:
- Verify `.env` has correct `SENVILLE_IP`
- Check device is powered on and connected to WiFi
- Run `./troubleshoot.sh` for detailed diagnostics
