#!/usr/bin/env python3
"""
Manage Senville AC Schedules via Command Line

Usage:
    python3 manage_schedules.py list
    python3 manage_schedules.py add "Morning Heat" "07:00" --power on --mode heat --temp 70
    python3 manage_schedules.py delete <id>
"""

import json
import argparse
import os
from datetime import datetime

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'schedules.json')

def load_schedules():
    """Load schedules from JSON file"""
    if not os.path.exists(SCHEDULE_FILE):
        return []
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading schedules: {e}")
        return []

def save_schedules(schedules):
    """Save schedules to JSON file"""
    try:
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedules, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving schedules: {e}")
        return False

def list_schedules():
    """List all schedules"""
    schedules = load_schedules()

    if not schedules:
        print("No schedules found")
        return

    print(f"\nTotal schedules: {len(schedules)}\n")
    print(f"{'ID':<5} {'Enabled':<10} {'Name':<25} {'Time':<10} {'Days':<20}")
    print("=" * 80)

    for s in schedules:
        enabled = "✓" if s.get('enabled', True) else "✗"
        days = ', '.join(s.get('days', [])) or 'Every day'
        print(f"{s['id']:<5} {enabled:<10} {s['name']:<25} {s['time']:<10} {days:<20}")

        # Show actions
        actions = []
        action = s['action']
        if 'power' in action:
            actions.append(f"power={action['power']}")
        if 'mode' in action:
            actions.append(f"mode={action['mode']}")
        if 'temperature' in action:
            unit = '°F' if action.get('fahrenheit') else '°C'
            actions.append(f"temp={action['temperature']}{unit}")
        if 'fan_speed' in action:
            actions.append(f"fan={action['fan_speed']}")

        print(f"      Actions: {', '.join(actions)}")

        if s.get('last_run'):
            last_run = datetime.fromisoformat(s['last_run']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"      Last run: {last_run}")

        print()

def add_schedule(name, time, days, power, mode, temp, temp_f, fan_speed):
    """Add a new schedule"""
    schedules = load_schedules()

    # Generate ID
    schedule_id = max([s.get('id', 0) for s in schedules], default=0) + 1

    # Build action
    action = {}
    if power is not None:
        action['power'] = (power.lower() == 'on')
    if mode is not None:
        action['mode'] = mode.lower()
    if temp is not None:
        action['temperature'] = temp
        action['fahrenheit'] = False
    if temp_f is not None:
        action['temperature'] = temp_f
        action['fahrenheit'] = True
    if fan_speed is not None:
        action['fan_speed'] = fan_speed

    if not action:
        print("Error: No actions specified")
        return False

    schedule = {
        'id': schedule_id,
        'name': name,
        'time': time,
        'days': days if days else [],
        'action': action,
        'enabled': True,
        'created_at': datetime.now().isoformat(),
        'last_run': None
    }

    schedules.append(schedule)
    if save_schedules(schedules):
        print(f"Schedule created successfully (ID: {schedule_id})")
        return True
    return False

def delete_schedule(schedule_id):
    """Delete a schedule"""
    schedules = load_schedules()
    original_count = len(schedules)

    schedules = [s for s in schedules if s['id'] != schedule_id]

    if len(schedules) == original_count:
        print(f"Schedule {schedule_id} not found")
        return False

    if save_schedules(schedules):
        print(f"Schedule {schedule_id} deleted")
        return True
    return False

def enable_schedule(schedule_id, enabled=True):
    """Enable or disable a schedule"""
    schedules = load_schedules()

    for s in schedules:
        if s['id'] == schedule_id:
            s['enabled'] = enabled
            if save_schedules(schedules):
                status = "enabled" if enabled else "disabled"
                print(f"Schedule {schedule_id} {status}")
                return True
            return False

    print(f"Schedule {schedule_id} not found")
    return False

def main():
    parser = argparse.ArgumentParser(
        description='Manage Senville AC Schedules',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all schedules
  python3 manage_schedules.py list

  # Add a schedule
  python3 manage_schedules.py add "Morning Warmup" "07:00" --power on --mode heat --temp-f 70

  # Add schedule for specific days
  python3 manage_schedules.py add "Weekend Cool" "09:00" --days mon tue wed thu fri --mode cool --temp-f 74

  # Delete a schedule
  python3 manage_schedules.py delete 1

  # Enable/disable a schedule
  python3 manage_schedules.py enable 1
  python3 manage_schedules.py disable 1
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command')

    # List command
    subparsers.add_parser('list', help='List all schedules')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new schedule')
    add_parser.add_argument('name', help='Schedule name')
    add_parser.add_argument('time', help='Time in HH:MM format (24-hour)')
    add_parser.add_argument('--days', nargs='+', choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                            help='Days of week (leave empty for every day)')
    add_parser.add_argument('--power', choices=['on', 'off'], help='Power on or off')
    add_parser.add_argument('--mode', choices=['auto', 'cool', 'heat', 'dry', 'fan'], help='Operating mode')
    add_parser.add_argument('--temp', type=int, help='Temperature in Celsius')
    add_parser.add_argument('--temp-f', type=int, help='Temperature in Fahrenheit')
    add_parser.add_argument('--fan-speed', type=int, choices=[20, 40, 60, 80, 102], help='Fan speed')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a schedule')
    delete_parser.add_argument('id', type=int, help='Schedule ID')

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable a schedule')
    enable_parser.add_argument('id', type=int, help='Schedule ID')

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable a schedule')
    disable_parser.add_argument('id', type=int, help='Schedule ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'list':
        list_schedules()
    elif args.command == 'add':
        add_schedule(args.name, args.time, args.days, args.power, args.mode,
                     args.temp, args.temp_f, args.fan_speed)
    elif args.command == 'delete':
        delete_schedule(args.id)
    elif args.command == 'enable':
        enable_schedule(args.id, True)
    elif args.command == 'disable':
        enable_schedule(args.id, False)

if __name__ == '__main__':
    main()
