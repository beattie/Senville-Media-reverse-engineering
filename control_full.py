#!/usr/bin/env python3
"""
Full Senville/Midea AC Control Script

Control all aspects of your air conditioner.

Usage:
    python3 control_full.py --power on --mode cool --temp-f 72
    python3 control_full.py --vswing on --hswing off
    python3 control_full.py --fan-speed 60
"""

import os
import sys
import argparse
from midea_beautiful import appliance_state

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

def f_to_c(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return (fahrenheit - 32) * 5 / 9

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9 / 5) + 32

def control_ac(power=None, mode=None, temp=None, temp_f=None,
               fahrenheit=None, vswing=None, hswing=None, fan_speed=None):
    """Control the AC unit"""

    # Get credentials
    ip = os.getenv('SENVILLE_IP')
    token = os.getenv('SENVILLE_TOKEN')
    key = os.getenv('SENVILLE_KEY')

    if not all([ip, token, key]):
        print("Error: Missing credentials in .env file")
        sys.exit(1)

    print(f"Connecting to {ip}...")

    # Get current state
    device = appliance_state(address=ip, token=token, key=key)
    state = device.state

    temp_unit = '°F' if state.fahrenheit else '°C'
    current_temp = state.target_temperature if not state.fahrenheit else c_to_f(state.target_temperature)

    print(f"Current Status:")
    print(f"  Power:      {'ON' if state.running else 'OFF'}")
    print(f"  Mode:       {state.mode}")
    print(f"  Temp:       {current_temp:.1f}{temp_unit}")
    print(f"  Fan Speed:  {state.fan_speed}")
    print(f"  V-Swing:    {'ON' if state.vertical_swing else 'OFF'}")
    print(f"  H-Swing:    {'ON' if state.horizontal_swing else 'OFF'}")

    # Build command
    changes = {}

    if power is not None:
        new_power = (power.lower() == 'on')
        changes['running'] = new_power
        print(f"→ Setting power: {'ON' if new_power else 'OFF'}")

    if mode is not None:
        mode_map = {
            'auto': 1,
            'cool': 2,
            'dry': 3,
            'heat': 4,
            'fan': 5
        }
        new_mode = mode_map.get(mode.lower())
        if new_mode:
            changes['mode'] = new_mode
            print(f"→ Setting mode: {mode}")

    # Handle temperature in Celsius
    if temp is not None:
        if 16 <= temp <= 31:
            changes['target_temperature'] = float(temp)
            print(f"→ Setting temperature: {temp}°C ({c_to_f(temp):.1f}°F)")
        else:
            print(f"Error: Temperature {temp}°C out of range (16-31°C / 60-87°F)")
            sys.exit(1)

    # Handle temperature in Fahrenheit
    if temp_f is not None:
        celsius = f_to_c(temp_f)
        if 16 <= celsius <= 31:
            changes['target_temperature'] = float(celsius)
            print(f"→ Setting temperature: {temp_f}°F ({celsius:.1f}°C)")
        else:
            print(f"Error: Temperature {temp_f}°F out of range (60-87°F / 16-31°C)")
            sys.exit(1)

    if fahrenheit is not None:
        use_f = (fahrenheit.lower() in ['true', 'on'])
        changes['fahrenheit'] = use_f
        print(f"→ Setting display to: {'Fahrenheit' if use_f else 'Celsius'}")

    # Vertical swing (up/down oscillation)
    if vswing is not None:
        swing_on = (vswing.lower() in ['on', 'true'])
        changes['vertical_swing'] = swing_on
        print(f"→ Setting vertical swing: {'ON' if swing_on else 'OFF'}")

    # Horizontal swing (left/right oscillation)
    if hswing is not None:
        swing_on = (hswing.lower() in ['on', 'true'])
        changes['horizontal_swing'] = swing_on
        print(f"→ Setting horizontal swing: {'ON' if swing_on else 'OFF'}")

    # Fan speed
    if fan_speed is not None:
        # Valid speeds: 20, 40, 60, 80, 102 (auto)
        valid_speeds = [20, 40, 60, 80, 102]
        if fan_speed in valid_speeds:
            changes['fan_speed'] = fan_speed
            print(f"→ Setting fan speed: {fan_speed}")
        else:
            print(f"Error: Fan speed must be one of: {valid_speeds}")
            print("  20 = Low, 40 = Med-Low, 60 = Medium, 80 = Med-High, 102 = Auto")
            sys.exit(1)

    if not changes:
        print("\nNo changes requested")
        return

    # Apply changes
    print("\nSending command...")
    try:
        # Set new state
        for attr, value in changes.items():
            setattr(state, attr, value)

        # Apply using device
        device.apply()

        print("✓ Command sent successfully!")
        print("\nRun 'python3 status.py' to verify the changes")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Full control for Senville/Midea air conditioner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 control_full.py --power on --mode cool --temp-f 72
  python3 control_full.py --vswing on
  python3 control_full.py --fan-speed 60
  python3 control_full.py --power on --mode heat --temp-f 68 --vswing off

Fan speeds: 20, 40, 60, 80, 102
Modes: auto, cool, dry, heat, fan
        """
    )

    parser.add_argument('--power', choices=['on', 'off'], help='Turn AC on or off')
    parser.add_argument('--mode', choices=['auto', 'cool', 'dry', 'heat', 'fan'], help='Operating mode')
    parser.add_argument('--temp', type=int, metavar='C', help='Target temperature in Celsius (16-31°C)')
    parser.add_argument('--temp-f', type=int, metavar='F', help='Target temperature in Fahrenheit (60-87°F)')
    parser.add_argument('--fahrenheit', choices=['on', 'off'], help='Display in Fahrenheit (on) or Celsius (off)')
    parser.add_argument('--vswing', choices=['on', 'off'], help='Vertical swing (up/down oscillation)')
    parser.add_argument('--hswing', choices=['on', 'off'], help='Horizontal swing (left/right oscillation)')
    parser.add_argument('--fan-speed', type=int, choices=[20, 40, 60, 80, 102], help='Fan speed (20=Low, 102=Auto)')

    args = parser.parse_args()

    if not any([args.power, args.mode, args.temp, args.temp_f, args.fahrenheit,
                args.vswing, args.hswing, args.fan_speed]):
        parser.print_help()
        print("\nError: No action specified")
        sys.exit(1)

    load_env()
    control_ac(power=args.power, mode=args.mode, temp=args.temp, temp_f=args.temp_f,
               fahrenheit=args.fahrenheit, vswing=args.vswing, hswing=args.hswing,
               fan_speed=args.fan_speed)

if __name__ == '__main__':
    main()
