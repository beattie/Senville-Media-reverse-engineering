#!/bin/bash
# Start the Senville AC Web Interface

cd "$(dirname "$0")"
source venv/bin/activate

# Check if already running
if pgrep -f "python3 api_server.py" > /dev/null; then
    echo "Web server is already running!"
    echo "To restart: ./restart_web.sh"
    echo "To stop: pkill -f 'python3 api_server.py'"
    exit 0
fi

# Start in background by default, foreground if --fg specified
if [ "$1" = "--fg" ]; then
    echo "Starting in foreground mode (Ctrl+C to stop)..."
    python3 api_server.py
else
    echo "Starting web server in background..."
    nohup python3 api_server.py > /tmp/senville_api.log 2>&1 &
    sleep 2
    echo ""
    echo "Web server started!"
    echo "Access at: http://localhost:5000"
    echo ""
    echo "To view logs: tail -f /tmp/senville_api.log"
    echo "To stop: pkill -f 'python3 api_server.py'"
    echo "To restart: ./restart_web.sh"
fi
