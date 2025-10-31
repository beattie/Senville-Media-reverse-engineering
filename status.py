#!/usr/bin/env python3
"""
Senville/Midea AC Status Checker

Get current status of your air conditioner including temperature,
mode, fan speed, and other settings.

Usage:
    python3 status.py
    python3 status.py --cloud  # Use cloud API instead of local

Requires:
    - .env file with SENVILLE_IP, SENVILLE_TOKEN, SENVILLE_KEY
    - Or MIDEA_ACCOUNT, MIDEA_PASSWORD for cloud mode
"""

import os
import sys
import argparse
from midea_beautiful import appliance_state, connect_to_cloud

def load_env():
    """Load environment variables from .env file if it exists"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def get_status_local(ip=None, token=None, key=None, verbose=0, quiet=False):
    """Get device status via local network"""
    # Try environment variables if not provided
    if not ip:
        ip = os.getenv('SENVILLE_IP')
    if not token:
        token = os.getenv('SENVILLE_TOKEN')
    if not key:
        key = os.getenv('SENVILLE_KEY')

    if not ip or not token or not key:
        print("Error: Missing device credentials!")
        print("Required: SENVILLE_IP, SENVILLE_TOKEN, SENVILLE_KEY")
        print("Run discover.py first to get credentials")
        sys.exit(1)

    if not quiet:
        print(f"Querying device at {ip}...")

    try:
        device = appliance_state(
            address=ip,
            token=token,
            key=key
        )

        print_status(device, verbose=verbose)
        return device

    except Exception as e:
        print(f"Error getting device status: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def get_status_cloud(account=None, password=None, device_id=None):
    """Get device status via cloud API"""
    if not account:
        account = os.getenv('MIDEA_ACCOUNT')
    if not password:
        password = os.getenv('MIDEA_PASSWORD')
    if not device_id:
        device_id = os.getenv('SENVILLE_DEVICE_ID')

    if not account or not password or not device_id:
        print("Error: Missing cloud credentials!")
        print("Required: MIDEA_ACCOUNT, MIDEA_PASSWORD, SENVILLE_DEVICE_ID")
        sys.exit(1)

    print("Connecting to Midea cloud...")

    try:
        cloud = connect_to_cloud(
            account=account,
            password=password
        )

        print(f"Getting status for device {device_id}...")
        device = appliance_state(
            cloud=cloud,
            id=device_id
        )

        print_status(device)
        return device

    except Exception as e:
        print(f"Error getting cloud status: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def print_status(device, verbose=0):
    """
    Print formatted device status

    verbose levels:
    0 = concise (one line)
    1 = verbose (main settings)
    2 = extra verbose (all attributes)
    """
    # Get state object
    state = device.state if hasattr(device, 'state') else device

    if verbose == 0:
        # Concise output
        temp_unit = '°F' if state.fahrenheit else '°C'
        target = state.target_temperature if not state.fahrenheit else c_to_f(state.target_temperature)
        indoor = state.indoor_temperature if not state.fahrenheit else c_to_f(state.indoor_temperature)

        print(f"Power: {'ON' if state.running else 'OFF'} | " +
              f"Mode: {get_mode_string(state.mode)} | " +
              f"Target: {target:.0f}{temp_unit} | " +
              f"Indoor: {indoor:.1f}{temp_unit} | " +
              f"Fan: {state.fan_speed}")
        return

    # Verbose output (level 1+)
    print("\n" + "="*50)
    print("SENVILLE AIR CONDITIONER STATUS")
    print("="*50)

    # Basic status
    print(f"\nPower:           {'ON' if state.running else 'OFF'}")

    # Temperature
    if hasattr(state, 'indoor_temperature'):
        print(f"Indoor Temp:     {state.indoor_temperature}°C ({c_to_f(state.indoor_temperature):.1f}°F)")
    if hasattr(state, 'outdoor_temperature'):
        print(f"Outdoor Temp:    {state.outdoor_temperature}°C ({c_to_f(state.outdoor_temperature):.1f}°F)")
    if hasattr(state, 'target_temperature'):
        print(f"Target Temp:     {state.target_temperature}°C ({c_to_f(state.target_temperature):.1f}°F)")

    # Operating mode
    if hasattr(state, 'mode'):
        mode_str = get_mode_string(state.mode)
        print(f"Mode:            {mode_str}")

    # Fan speed
    if hasattr(state, 'fan_speed'):
        print(f"Fan Speed:       {state.fan_speed}")

    # Additional features
    if hasattr(state, 'vertical_swing'):
        print(f"Vertical Swing:  {state.vertical_swing}")
    if hasattr(state, 'horizontal_swing'):
        print(f"Horizontal Swing:{state.horizontal_swing}")
    if hasattr(state, 'turbo'):
        print(f"Turbo Mode:      {state.turbo}")
    if hasattr(state, 'eco_mode'):
        print(f"Eco Mode:        {state.eco_mode}")
    if hasattr(state, 'comfort_mode'):
        print(f"Comfort Mode:    {state.comfort_mode}")

    # Error code
    if hasattr(state, 'error_code'):
        print(f"Error Code:      {state.error_code}")

    # Extra verbose - show all attributes
    if verbose >= 2:
        print(f"\nDevice Information:")
        if hasattr(device, 'appliance_id'):
            print(f"  Appliance ID:    {device.appliance_id}")
        if hasattr(device, 'serial_number'):
            print(f"  Serial:          {device.serial_number}")
        if hasattr(device, 'mac'):
            print(f"  MAC Address:     {device.mac}")
        if hasattr(device, 'firmware_version'):
            print(f"  Firmware:        {device.firmware_version}")
        if hasattr(device, 'protocol_version'):
            print(f"  Protocol:        V{device.protocol_version}")

        print(f"\nAll state attributes:")
        for attr in dir(state):
            if not attr.startswith('_') and not callable(getattr(state, attr)):
                try:
                    value = getattr(state, attr)
                    # Skip very long data
                    if isinstance(value, (bytes, dict)) and len(str(value)) > 100:
                        print(f"  {attr:20} = <{type(value).__name__} ({len(value)} items)>")
                    else:
                        print(f"  {attr:20} = {value}")
                except:
                    pass

    print("="*50 + "\n")

def get_mode_string(mode):
    """Convert mode number to readable string"""
    modes = {
        1: "Cool",
        2: "Dry",
        3: "Fan",
        4: "Heat",
        5: "Auto"
    }
    return modes.get(mode, f"Unknown ({mode})")

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def main():
    parser = argparse.ArgumentParser(
        description='Get Senville/Midea AC status'
    )
    parser.add_argument(
        '--cloud',
        action='store_true',
        help='Use cloud API instead of local network'
    )
    parser.add_argument(
        '--ip',
        help='Device IP address (overrides env var)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v = verbose, -vv = extra verbose)'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (no "Querying..." message)'
    )

    args = parser.parse_args()

    # Load environment variables
    load_env()

    if args.cloud:
        get_status_cloud()
    else:
        get_status_local(ip=args.ip, verbose=args.verbose, quiet=args.quiet)

if __name__ == '__main__':
    main()
