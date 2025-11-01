#!/usr/bin/env python3
"""
Senville AC Scheduler Service

Runs scheduled temperature/mode changes automatically.

Usage:
    python3 scheduler.py             # Run scheduler
    python3 scheduler.py --daemon    # Run as daemon
    python3 scheduler.py --status    # Check scheduler status
"""

import os
import sys
import time
import json
import signal
import argparse
from datetime import datetime, time as dt_time
from pathlib import Path
from midea_beautiful import appliance_state

# Schedule storage file
SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'schedules.json')
PID_FILE = os.path.join(os.path.dirname(__file__), 'scheduler.pid')

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

def f_to_c(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return (fahrenheit - 32) * 5 / 9

def c_to_f(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9 / 5) + 32

def get_device():
    """Get device connection"""
    ip = os.getenv('SENVILLE_IP')
    token = os.getenv('SENVILLE_TOKEN')
    key = os.getenv('SENVILLE_KEY')

    if not all([ip, token, key]):
        raise ValueError("Missing credentials in .env file")

    return appliance_state(address=ip, token=token, key=key)

def execute_schedule(schedule):
    """Execute a schedule action"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Executing schedule: {schedule['name']}")

        device = get_device()
        state = device.state

        action = schedule['action']
        changes = []

        # Power
        if 'power' in action:
            state.running = action['power']
            changes.append(f"power: {'on' if action['power'] else 'off'}")

        # Mode
        if 'mode' in action:
            mode_map = {'auto': 1, 'cool': 2, 'dry': 3, 'heat': 4, 'fan': 5}
            if action['mode'] in mode_map:
                state.mode = mode_map[action['mode']]
                changes.append(f"mode: {action['mode']}")

        # Temperature
        if 'temperature' in action:
            temp = action['temperature']
            use_f = action.get('fahrenheit', False)
            temp_c = f_to_c(temp) if use_f else temp
            if 16 <= temp_c <= 31:
                state.target_temperature = float(temp_c)
                changes.append(f"temp: {temp}°{'F' if use_f else 'C'}")

        # Fan speed
        if 'fan_speed' in action:
            speed = action['fan_speed']
            if speed in [20, 40, 60, 80, 102]:
                state.fan_speed = speed
                changes.append(f"fan: {speed}")

        # Swing
        if 'vertical_swing' in action:
            state.vertical_swing = action['vertical_swing']
            changes.append(f"v-swing: {'on' if action['vertical_swing'] else 'off'}")

        if 'horizontal_swing' in action:
            state.horizontal_swing = action['horizontal_swing']
            changes.append(f"h-swing: {'on' if action['horizontal_swing'] else 'off'}")

        if changes:
            device.apply()
            print(f"  Applied: {', '.join(changes)}")

            # Update last run time
            schedule['last_run'] = datetime.now().isoformat()
            return True
        else:
            print("  No changes to apply")
            return False

    except Exception as e:
        print(f"  Error executing schedule: {e}")
        return False

def check_schedule(schedule, now):
    """Check if a schedule should run now"""
    if not schedule.get('enabled', True):
        return False

    current_time = now.time()
    current_day = now.strftime('%a').lower()

    # Parse schedule time
    try:
        schedule_time = dt_time.fromisoformat(schedule['time'])
    except:
        print(f"Invalid time format in schedule: {schedule['time']}")
        return False

    # Check if it's the right time (within 1 minute window)
    time_match = (
        schedule_time.hour == current_time.hour and
        schedule_time.minute == current_time.minute
    )

    if not time_match:
        return False

    # Check days
    days = schedule.get('days', [])
    if not days:
        # If no days specified, run every day
        return True

    # Check if today is in the schedule
    return current_day in [d.lower() for d in days]

def run_scheduler_loop():
    """Main scheduler loop"""
    print("=" * 60)
    print("Senville AC Scheduler Service")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Schedule file: {SCHEDULE_FILE}")
    print(f"Checking schedules every 30 seconds...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    last_minute = -1

    try:
        while True:
            now = datetime.now()
            current_minute = now.minute

            # Only check schedules once per minute
            if current_minute != last_minute:
                last_minute = current_minute

                schedules = load_schedules()

                for schedule in schedules:
                    if check_schedule(schedule, now):
                        success = execute_schedule(schedule)
                        if success:
                            # Save updated last_run time
                            save_schedules(schedules)

            # Sleep for 30 seconds
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n\nScheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nScheduler error: {e}")
        sys.exit(1)

def start_daemon():
    """Start scheduler as daemon"""
    # Check if already running
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is running
            try:
                os.kill(pid, 0)
                print(f"Scheduler is already running (PID: {pid})")
                sys.exit(1)
            except OSError:
                # Process not running, remove stale PID file
                os.remove(PID_FILE)
        except:
            pass

    # Fork process
    try:
        pid = os.fork()
        if pid > 0:
            # Parent process
            print(f"Scheduler started in background (PID: {pid})")
            print(f"To stop: kill {pid}")
            sys.exit(0)
    except OSError as e:
        print(f"Fork failed: {e}")
        sys.exit(1)

    # Child process
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # Second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.exit(1)

    # Write PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()

    # Run scheduler
    run_scheduler_loop()

def stop_daemon():
    """Stop running scheduler daemon"""
    if not os.path.exists(PID_FILE):
        print("Scheduler is not running")
        return False

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Try to terminate the process
        os.kill(pid, signal.SIGTERM)

        # Wait a bit and check if it's stopped
        time.sleep(1)

        try:
            os.kill(pid, 0)
            print(f"Scheduler (PID: {pid}) is still running, forcing...")
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

        # Remove PID file
        os.remove(PID_FILE)
        print(f"Scheduler stopped (PID: {pid})")
        return True

    except Exception as e:
        print(f"Error stopping scheduler: {e}")
        return False

def check_status():
    """Check scheduler status"""
    if not os.path.exists(PID_FILE):
        print("Scheduler: Not running")
        return False

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # Check if process is running
        try:
            os.kill(pid, 0)
            print(f"Scheduler: Running (PID: {pid})")

            # Load and display schedules
            schedules = load_schedules()
            enabled_count = sum(1 for s in schedules if s.get('enabled', True))
            print(f"Schedules: {len(schedules)} total, {enabled_count} enabled")

            if schedules:
                print("\nActive schedules:")
                for s in schedules:
                    if s.get('enabled', True):
                        days = ', '.join(s.get('days', ['Every day']))
                        print(f"  - {s['name']}: {s['time']} ({days})")

            return True
        except OSError:
            print("Scheduler: Not running (stale PID file)")
            os.remove(PID_FILE)
            return False
    except Exception as e:
        print(f"Error checking status: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Senville AC Scheduler Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scheduler.py              # Run scheduler (foreground)
  python3 scheduler.py --daemon     # Run as background daemon
  python3 scheduler.py --stop       # Stop daemon
  python3 scheduler.py --status     # Check status
        """
    )

    parser.add_argument('--daemon', action='store_true', help='Run as background daemon')
    parser.add_argument('--stop', action='store_true', help='Stop running daemon')
    parser.add_argument('--status', action='store_true', help='Check scheduler status')

    args = parser.parse_args()

    load_env()

    if args.status:
        check_status()
    elif args.stop:
        stop_daemon()
    elif args.daemon:
        start_daemon()
    else:
        run_scheduler_loop()

if __name__ == '__main__':
    main()
