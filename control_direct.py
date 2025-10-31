#!/usr/bin/env python3
"""
Direct Senville/Midea AC Control Script (using msmart-ng)

Control your air conditioner directly via local network.

Usage Examples:
    # Turn on
    python3 control_direct.py --power on

    # Set temperature
    python3 control_direct.py --temp 22

    # Change mode
    python3 control_direct.py --mode cool

    # Turn on in cool mode at 22°C
    python3 control_direct.py --power on --mode cool --temp 22

    # Turn off
    python3 control_direct.py --power off
"""

import os
import sys
import argparse
import asyncio
from msmart.device import AirConditioner as AC

def load_env():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

async def control_ac(power=None, mode=None, temp=None, fan_speed=None):
    """Control the AC unit"""

    # Get credentials from environment
    ip = os.getenv('SENVILLE_IP')
    token = os.getenv('SENVILLE_TOKEN')
    key = os.getenv('SENVILLE_KEY')
    device_id = int(os.getenv('SENVILLE_DEVICE_ID'))

    if not all([ip, token, key, device_id]):
        print("Error: Missing credentials in .env file")
        print("Required: SENVILLE_IP, SENVILLE_TOKEN, SENVILLE_KEY, SENVILLE_DEVICE_ID")
        sys.exit(1)

    print(f"Connecting to {ip}...")

    # Create device
    device = AC(
        ip=ip,
        port=6444,
        device_id=device_id,
        token=bytes.fromhex(token),
        key=bytes.fromhex(key)
    )

    # Refresh current state
    print("Getting current state...")
    await device.refresh()

    print(f"Current state: Power={'ON' if device.running else 'OFF'}, " +
          f"Temp={device.target_temperature}°C, Mode={device.mode}")

    # Apply changes
    changed = False

    if power is not None:
        new_state = (power.lower() == 'on')
        if device.running != new_state:
            device.running = new_state
            changed = True
            print(f"Setting power: {'ON' if new_state else 'OFF'}")

    if mode is not None:
        mode_map = {
            'auto': 1,
            'cool': 2,
            'dry': 3,
            'heat': 4,
            'fan': 5
        }
        new_mode = mode_map.get(mode.lower())
        if new_mode and device.mode != new_mode:
            device.mode = new_mode
            changed = True
            print(f"Setting mode: {mode}")

    if temp is not None:
        if 16 <= temp <= 31:
            if device.target_temperature != temp:
                device.target_temperature = temp
                changed = True
                print(f"Setting temperature: {temp}°C")
        else:
            print(f"Error: Temperature {temp}°C out of range (16-31)")
            sys.exit(1)

    if fan_speed is not None:
        # Fan speed values: 20, 40, 60, 80, 102 (auto)
        valid_speeds = [20, 40, 60, 80, 102]
        if fan_speed in valid_speeds:
            if device.fan_speed != fan_speed:
                device.fan_speed = fan_speed
                changed = True
                print(f"Setting fan speed: {fan_speed}")
        else:
            print(f"Error: Fan speed must be one of: {valid_speeds}")
            sys.exit(1)

    # Apply changes
    if changed:
        print("\nApplying changes...")
        await device.apply()
        print("✓ Success!")

        # Refresh to confirm
        await device.refresh()
        print(f"\nNew state: Power={'ON' if device.running else 'OFF'}, " +
              f"Temp={device.target_temperature}°C, Mode={device.mode}")
    else:
        print("\nNo changes requested")

def main():
    parser = argparse.ArgumentParser(
        description='Control Senville/Midea air conditioner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Turn on in cool mode at 22°C:
    python3 control_direct.py --power on --mode cool --temp 22

  Turn off:
    python3 control_direct.py --power off

  Set to heat mode at 24°C:
    python3 control_direct.py --mode heat --temp 24

  Change temperature only:
    python3 control_direct.py --temp 20

  Set fan speed:
    python3 control_direct.py --fan 60

Fan speeds: 20, 40, 60, 80, 102 (auto)
Modes: auto, cool, dry, heat, fan
        """
    )

    parser.add_argument(
        '--power',
        choices=['on', 'off'],
        help='Turn AC on or off'
    )
    parser.add_argument(
        '--mode',
        choices=['auto', 'cool', 'dry', 'heat', 'fan'],
        help='Operating mode'
    )
    parser.add_argument(
        '--temp',
        type=int,
        metavar='CELSIUS',
        help='Target temperature (16-31°C)'
    )
    parser.add_argument(
        '--fan',
        type=int,
        metavar='SPEED',
        help='Fan speed (20, 40, 60, 80, 102)'
    )

    args = parser.parse_args()

    # Check if any action specified
    if not any([args.power, args.mode, args.temp, args.fan]):
        parser.print_help()
        print("\nError: No action specified")
        sys.exit(1)

    # Load environment
    load_env()

    # Control device
    asyncio.run(control_ac(
        power=args.power,
        mode=args.mode,
        temp=args.temp,
        fan_speed=args.fan
    ))

if __name__ == '__main__':
    main()
