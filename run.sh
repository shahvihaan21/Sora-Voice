#!/usr/bin/env bash
set -e

echo "==================================================="
echo "            Sora Voice Assistant Launcher          "
echo "==================================================="

# Check for Python 3
if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[ERROR] Python 3 was not found on your system."
    echo "Please install Python 3.10-3.12."
    exit 1
fi

# Set up virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment 'venv'..."
    $PY_CMD -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install / update dependencies
echo "[INFO] Checking dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Launch application
echo "[INFO] Launching Sora Voice..."
python run.py
