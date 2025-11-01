#!/bin/bash
# Restart the Senville AC Web Interface

echo "Stopping web server..."
pkill -f "python3 api_server.py"
sleep 1

echo "Starting web server..."
cd "$(dirname "$0")"
source venv/bin/activate
nohup python3 api_server.py > /tmp/senville_api.log 2>&1 &

sleep 2

echo ""
echo "Web server restarted!"
echo "Access at: http://localhost:5000"
echo ""
echo "To view logs: tail -f /tmp/senville_api.log"
