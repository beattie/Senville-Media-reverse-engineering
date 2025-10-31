#!/usr/bin/env python3
"""
Senville/Midea AC Control Script

Control your air conditioner via command line.

Usage Examples:
    # Turn on in cool mode at 22°C
    python3 control.py --power on --mode cool --temp 22

    # Turn off
    python3 control.py --power off

    # Set to heat mode at 24°C
    python3 control.py --mode heat --temp 24

    # Change temperature only
    python3 control.py --temp 20

Requires:
    .env file with SENVILLE_IP, SENVILLE_TOKEN, SENVILLE_KEY
"""

import os
import sys
import argparse
import subprocess

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

def get_credentials():
    """Get device credentials from environment"""
    ip = os.getenv('SENVILLE_IP')
    token = os.getenv('SENVILLE_TOKEN')
    key = os.getenv('SENVILLE_KEY')

    if not ip or not token or not key:
        print("Error: Missing device credentials!")
        print("Required: SENVILLE_IP, SENVILLE_TOKEN, SENVILLE_KEY")
        print("Run discover.py first to get credentials and add them to .env")
        sys.exit(1)

    return ip, token, key

def control_device(power=None, mode=None, temp=None, fan_speed=None):
    """
    Control the AC device using midea-beautiful-air-cli

    Args:
        power: 'on' or 'off'
        mode: 'cool', 'heat', 'dry', 'fan', 'auto'
        temp: Temperature in Celsius (16-31)
        fan_speed: Fan speed setting
    """
    ip, token, key = get_credentials()

    # Build command
    cmd = [
        './venv/bin/midea-beautiful-air-cli',
        'set',
        '--ip', ip,
        '--token', token,
        '--key', key
    ]

    # Add parameters
    if power is not None:
        running = '1' if power.lower() == 'on' else '0'
        cmd.extend(['--running', running])

    if mode is not None:
        mode_map = {
            'cool': '1',
            'dry': '2',
            'fan': '3',
            'heat': '4',
            'auto': '5'
        }
        mode_num = mode_map.get(mode.lower())
        if mode_num:
            cmd.extend(['--mode', mode_num])
        else:
            print(f"Error: Invalid mode '{mode}'")
            print("Valid modes: cool, dry, fan, heat, auto")
            sys.exit(1)

    if temp is not None:
        if 16 <= temp <= 31:
            cmd.extend(['--temperature', str(temp)])
        else:
            print(f"Error: Temperature {temp}°C out of range")
            print("Valid range: 16-31°C (60-87°F)")
            sys.exit(1)

    if fan_speed is not None:
        cmd.extend(['--fan-speed', str(fan_speed)])

    # Execute command
    print(f"Sending command to {ip}...")
    print(f"Command: {' '.join(cmd[5:])}")  # Show params only, not credentials

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("\nSuccess!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed")
        if e.stderr:
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("\nError: midea-beautiful-air-cli not found")
        print("Run: pip install midea-beautiful-air")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Control Senville/Midea air conditioner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Turn on in cool mode at 22°C:
    python3 control.py --power on --mode cool --temp 22

  Turn off:
    python3 control.py --power off

  Set to heat mode at 24°C:
    python3 control.py --mode heat --temp 24

  Change temperature only:
    python3 control.py --temp 20
        """
    )

    parser.add_argument(
        '--power',
        choices=['on', 'off'],
        help='Turn AC on or off'
    )
    parser.add_argument(
        '--mode',
        choices=['cool', 'heat', 'dry', 'fan', 'auto'],
        help='Operating mode'
    )
    parser.add_argument(
        '--temp',
        type=int,
        metavar='CELSIUS',
        help='Target temperature (16-31°C)'
    )
    parser.add_argument(
        '--fan-speed',
        type=int,
        metavar='SPEED',
        help='Fan speed setting'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Check if any action specified
    if not any([args.power, args.mode, args.temp, args.fan_speed]):
        parser.print_help()
        print("\nError: No action specified")
        sys.exit(1)

    # Load environment
    load_env()

    # Control device
    success = control_device(
        power=args.power,
        mode=args.mode,
        temp=args.temp,
        fan_speed=args.fan_speed
    )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
