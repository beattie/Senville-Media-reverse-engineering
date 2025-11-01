#!/bin/bash
# Start Senville AC Control GUI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Please create .env from .env.example first"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d venv ]; then
    source venv/bin/activate
fi

# Check if required packages are installed
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: tkinter not installed"
    echo ""
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  macOS: Included with Python"
    exit 1
fi

python3 -c "import midea_beautiful" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: midea-beautiful-air not installed"
    echo ""
    echo "Install with:"
    echo "  pip install midea-beautiful-air"
    exit 1
fi

# Start the GUI
python3 gui_control.py
