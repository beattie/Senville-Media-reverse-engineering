#!/bin/bash
# Install Senville AC services

echo "Installing Senville AC systemd services..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo:"
    echo "  sudo ./install_services.sh"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Install API server service
echo "Installing API server service..."
cp "$SCRIPT_DIR/senville-api.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable senville-api.service

# Install scheduler service
echo "Installing scheduler service..."
cp "$SCRIPT_DIR/senville-scheduler.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable senville-scheduler.service

echo ""
echo "Installation complete!"
echo ""
echo "To start the services:"
echo "  sudo systemctl start senville-api"
echo "  sudo systemctl start senville-scheduler"
echo ""
echo "To check status:"
echo "  sudo systemctl status senville-api"
echo "  sudo systemctl status senville-scheduler"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u senville-api -f"
echo "  sudo journalctl -u senville-scheduler -f"
echo ""
echo "Web interface will be available at: http://localhost:5000"
echo ""
