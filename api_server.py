#!/usr/bin/env python3
"""
Senville/Midea AC REST API Server

Provides a REST API for controlling and monitoring the air conditioner.

Usage:
    python3 api_server.py

Access the web interface at: http://localhost:5000
"""

import os
import sys
import json
import subprocess
import time
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from midea_beautiful import appliance_state
from midea_beautiful.exceptions import MideaError, MideaNetworkError

app = Flask(__name__, static_folder='web')
CORS(app)

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), 'schedules.json')

# Cache for device connection
_device_cache = {'device': None, 'timestamp': 0, 'ttl': 30}

def get_cached_device():
    """Get device with caching to reduce connection overhead"""
    now = time.time()

    # Return cached device if still valid
    if _device_cache['device'] and (now - _device_cache['timestamp']) < _device_cache['ttl']:
        return _device_cache['device']

    # Create new device connection
    ip = os.getenv('SENVILLE_IP')
    token = os.getenv('SENVILLE_TOKEN')
    key = os.getenv('SENVILLE_KEY')

    if not all([ip, token, key]):
        raise ValueError("Missing credentials in .env file")

    device = appliance_state(address=ip, token=token, key=key)

    # Cache the device
    _device_cache['device'] = device
    _device_cache['timestamp'] = now

    return device

def retry_with_backoff(func, max_retries=3, initial_delay=0.5):
    """Retry a function with exponential backoff"""
    delay = initial_delay
    last_error = None

    for attempt in range(max_retries):
        try:
            return func()
        except (MideaNetworkError, MideaError, TimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                # Clear cache on error
                _device_cache['device'] = None
            else:
                raise last_error

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


@app.route('/')
def index():
    """Serve the web dashboard"""
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from web directory"""
    return send_from_directory('web', path)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current AC status"""
    try:
        def fetch_status():
            device = get_cached_device()
            return device.state

        state = retry_with_backoff(fetch_status)

        # Get display unit preference
        use_fahrenheit = state.fahrenheit
        temp_display = c_to_f(state.target_temperature) if use_fahrenheit else state.target_temperature
        indoor_temp = c_to_f(state.indoor_temperature) if use_fahrenheit else state.indoor_temperature
        outdoor_temp = c_to_f(state.outdoor_temperature) if use_fahrenheit else state.outdoor_temperature

        return jsonify({
            'success': True,
            'data': {
                'running': state.running,
                'mode': str(state.mode),
                'target_temperature': round(temp_display, 1),
                'indoor_temperature': round(indoor_temp, 1),
                'outdoor_temperature': round(outdoor_temp, 1),
                'fan_speed': state.fan_speed,
                'vertical_swing': state.vertical_swing,
                'horizontal_swing': state.horizontal_swing,
                'fahrenheit': use_fahrenheit,
                'eco_mode': state.eco_mode if hasattr(state, 'eco_mode') else False,
                'turbo_mode': state.turbo_mode if hasattr(state, 'turbo_mode') else False,
            }
        })
    except (MideaNetworkError, MideaError, TimeoutError) as e:
        return jsonify({
            'success': False,
            'error': f'Communication error: {str(e)}'
        }), 503  # Service Unavailable
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/power', methods=['POST'])
def set_power():
    """Turn AC on or off"""
    try:
        data = request.get_json()
        power_on = data.get('on', True)

        def apply_power():
            device = get_cached_device()
            state = device.state
            state.running = power_on
            device.apply()

        retry_with_backoff(apply_power)

        return jsonify({
            'success': True,
            'message': f"AC turned {'on' if power_on else 'off'}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set operating mode"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'cool').lower()

        mode_map = {
            'auto': 1,
            'cool': 2,
            'dry': 3,
            'heat': 4,
            'fan': 5
        }

        if mode not in mode_map:
            return jsonify({
                'success': False,
                'error': f"Invalid mode. Must be one of: {', '.join(mode_map.keys())}"
            }), 400

        def apply_mode():
            device = get_cached_device()
            state = device.state
            state.mode = mode_map[mode]
            device.apply()

        retry_with_backoff(apply_mode)

        return jsonify({
            'success': True,
            'message': f"Mode set to {mode}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/temperature', methods=['POST'])
def set_temperature():
    """Set target temperature"""
    try:
        data = request.get_json()
        temp = data.get('temperature')
        use_fahrenheit = data.get('fahrenheit', False)

        if temp is None:
            return jsonify({
                'success': False,
                'error': 'Temperature is required'
            }), 400

        # Convert to Celsius if needed
        temp_c = f_to_c(temp) if use_fahrenheit else temp

        if not (16 <= temp_c <= 31):
            return jsonify({
                'success': False,
                'error': 'Temperature out of range (16-31°C / 60-87°F)'
            }), 400

        def apply_temperature():
            device = get_cached_device()
            state = device.state
            state.target_temperature = float(temp_c)
            device.apply()

        retry_with_backoff(apply_temperature)

        return jsonify({
            'success': True,
            'message': f"Temperature set to {temp}°{'F' if use_fahrenheit else 'C'}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fan', methods=['POST'])
def set_fan():
    """Set fan speed"""
    try:
        data = request.get_json()
        fan_speed = data.get('speed')

        valid_speeds = [20, 40, 60, 80, 102]
        if fan_speed not in valid_speeds:
            return jsonify({
                'success': False,
                'error': f"Invalid fan speed. Must be one of: {valid_speeds}"
            }), 400

        def apply_fan():
            device = get_cached_device()
            state = device.state
            state.fan_speed = fan_speed
            device.apply()

        retry_with_backoff(apply_fan)

        return jsonify({
            'success': True,
            'message': f"Fan speed set to {fan_speed}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/swing', methods=['POST'])
def set_swing():
    """Set swing settings"""
    try:
        data = request.get_json()
        vertical = data.get('vertical')
        horizontal = data.get('horizontal')

        def apply_swing():
            device = get_cached_device()
            state = device.state

            if vertical is not None:
                state.vertical_swing = bool(vertical)
            if horizontal is not None:
                state.horizontal_swing = bool(horizontal)

            device.apply()

        retry_with_backoff(apply_swing)

        return jsonify({
            'success': True,
            'message': 'Swing settings updated'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control', methods=['POST'])
def control_all():
    """Set multiple parameters at once"""
    try:
        data = request.get_json()

        def apply_all():
            device = get_cached_device()
            state = device.state
            changes = []

            # Power
            if 'running' in data:
                state.running = bool(data['running'])
                changes.append(f"power: {'on' if state.running else 'off'}")

            # Mode
            if 'mode' in data:
                mode = data['mode'].lower()
                mode_map = {'auto': 1, 'cool': 2, 'dry': 3, 'heat': 4, 'fan': 5}
                if mode in mode_map:
                    state.mode = mode_map[mode]
                    changes.append(f"mode: {mode}")

            # Temperature
            if 'temperature' in data:
                temp = data['temperature']
                use_f = data.get('fahrenheit', False)
                temp_c = f_to_c(temp) if use_f else temp
                if 16 <= temp_c <= 31:
                    state.target_temperature = float(temp_c)
                    changes.append(f"temp: {temp}°{'F' if use_f else 'C'}")

            # Fan speed
            if 'fan_speed' in data:
                speed = data['fan_speed']
                if speed in [20, 40, 60, 80, 102]:
                    state.fan_speed = speed
                    changes.append(f"fan: {speed}")

            # Swing
            if 'vertical_swing' in data:
                state.vertical_swing = bool(data['vertical_swing'])
                changes.append(f"v-swing: {'on' if state.vertical_swing else 'off'}")

            if 'horizontal_swing' in data:
                state.horizontal_swing = bool(data['horizontal_swing'])
                changes.append(f"h-swing: {'on' if state.horizontal_swing else 'off'}")

            if not changes:
                raise ValueError('No valid changes specified')

            device.apply()
            return changes

        changes = retry_with_backoff(apply_all)

        return jsonify({
            'success': True,
            'message': f"Updated: {', '.join(changes)}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Schedule Management Endpoints

def load_schedules():
    """Load schedules from JSON file"""
    if not os.path.exists(SCHEDULE_FILE):
        return []
    try:
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_schedules(schedules):
    """Save schedules to JSON file"""
    try:
        with open(SCHEDULE_FILE, 'w') as f:
            json.dump(schedules, f, indent=2)
        return True
    except Exception:
        return False

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all schedules"""
    try:
        schedules = load_schedules()
        return jsonify({
            'success': True,
            'data': schedules
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create a new schedule"""
    try:
        data = request.get_json()

        # Validate required fields
        if not all(k in data for k in ['name', 'time', 'action']):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: name, time, action'
            }), 400

        schedules = load_schedules()

        # Generate ID
        schedule_id = max([s.get('id', 0) for s in schedules], default=0) + 1

        schedule = {
            'id': schedule_id,
            'name': data['name'],
            'time': data['time'],
            'days': data.get('days', []),
            'action': data['action'],
            'enabled': data.get('enabled', True),
            'created_at': data.get('created_at'),
            'last_run': None
        }

        schedules.append(schedule)
        save_schedules(schedules)

        return jsonify({
            'success': True,
            'data': schedule
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update a schedule"""
    try:
        data = request.get_json()
        schedules = load_schedules()

        # Find schedule
        schedule = None
        for s in schedules:
            if s['id'] == schedule_id:
                schedule = s
                break

        if not schedule:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404

        # Update fields
        if 'name' in data:
            schedule['name'] = data['name']
        if 'time' in data:
            schedule['time'] = data['time']
        if 'days' in data:
            schedule['days'] = data['days']
        if 'action' in data:
            schedule['action'] = data['action']
        if 'enabled' in data:
            schedule['enabled'] = data['enabled']

        save_schedules(schedules)

        return jsonify({
            'success': True,
            'data': schedule
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedules/<int:schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a schedule"""
    try:
        schedules = load_schedules()
        schedules = [s for s in schedules if s['id'] != schedule_id]
        save_schedules(schedules)

        return jsonify({
            'success': True,
            'message': 'Schedule deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scheduler/status', methods=['GET'])
def scheduler_status():
    """Get scheduler daemon status"""
    try:
        pid_file = os.path.join(os.path.dirname(__file__), 'scheduler.pid')
        running = False
        pid = None

        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                # Check if process is running
                try:
                    os.kill(pid, 0)
                    running = True
                except OSError:
                    running = False
            except:
                pass

        schedules = load_schedules()
        enabled_count = sum(1 for s in schedules if s.get('enabled', True))

        return jsonify({
            'success': True,
            'data': {
                'running': running,
                'pid': pid,
                'total_schedules': len(schedules),
                'enabled_schedules': enabled_count
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler daemon"""
    try:
        script_dir = os.path.dirname(__file__)
        venv_python = os.path.join(script_dir, 'venv', 'bin', 'python3')
        scheduler_script = os.path.join(script_dir, 'scheduler.py')

        result = subprocess.run(
            [venv_python, scheduler_script, '--daemon'],
            capture_output=True,
            text=True,
            cwd=script_dir
        )

        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Scheduler started'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Failed to start scheduler'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler daemon"""
    try:
        script_dir = os.path.dirname(__file__)
        venv_python = os.path.join(script_dir, 'venv', 'bin', 'python3')
        scheduler_script = os.path.join(script_dir, 'scheduler.py')

        result = subprocess.run(
            [venv_python, scheduler_script, '--stop'],
            capture_output=True,
            text=True,
            cwd=script_dir
        )

        return jsonify({
            'success': True,
            'message': 'Scheduler stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def main():
    load_env()

    # Verify credentials
    if not all([os.getenv('SENVILLE_IP'), os.getenv('SENVILLE_TOKEN'), os.getenv('SENVILLE_KEY')]):
        print("Error: Missing credentials in .env file")
        sys.exit(1)

    print("=" * 60)
    print("Senville AC REST API Server")
    print("=" * 60)
    print(f"\nDevice IP: {os.getenv('SENVILLE_IP')}")
    print(f"\nServer starting on http://0.0.0.0:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/status           - Get current AC status")
    print("  POST /api/power            - Turn AC on/off")
    print("  POST /api/mode             - Set mode")
    print("  POST /api/temperature      - Set temperature")
    print("  POST /api/fan              - Set fan speed")
    print("  POST /api/swing            - Set swing")
    print("  POST /api/control          - Set multiple parameters")
    print("  GET  /api/schedules        - Get all schedules")
    print("  POST /api/schedules        - Create schedule")
    print("  PUT  /api/schedules/<id>   - Update schedule")
    print("  DELETE /api/schedules/<id> - Delete schedule")
    print("  GET  /api/scheduler/status - Get scheduler status")
    print("  POST /api/scheduler/start  - Start scheduler")
    print("  POST /api/scheduler/stop   - Stop scheduler")
    print("\nWeb Dashboard: http://localhost:5000")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
