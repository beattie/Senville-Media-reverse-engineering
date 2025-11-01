#!/bin/bash
# Try all supported app backends to authenticate
# Usage: ./try_all_apps.sh EMAIL PASSWORD

if [ $# -ne 2 ]; then
    echo "Usage: $0 EMAIL PASSWORD"
    echo ""
    echo "Example:"
    echo "  $0 your@email.com yourpassword"
    echo ""
    echo "This script tries different Midea app backends to find one that works"
    echo "for authentication with your Midea/Senville account."
    exit 1
fi

EMAIL="$1"
PASSWORD="$2"

source venv/bin/activate

echo "Trying different Midea app backends..."
echo "Email: $EMAIL"
echo

for APP in "NetHome Plus" "Midea Air" "MSmartHome" "Ariston Clima"; do
    echo "=== Trying: $APP ==="
    midea-beautiful-air-cli discover \
        --account "$EMAIL" \
        --password "$PASSWORD" \
        --app "$APP" \
        --credentials 2>&1 | head -20
    echo
    echo "Press Enter to try next app, or Ctrl+C to stop..."
    read
done

echo "All apps tried."
