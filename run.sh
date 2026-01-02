#!/usr/bin/env bash
set -euo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo $SCRIPT_DIR

# Change to the project root directory
cd $SCRIPT_DIR

# find the full path of uv
UV_BIN=$(command -v uv || true)
if [ -z "$UV_BIN" ]; then
  echo "ERROR: 'uv' not found in PATH" >&2
  exit 1
fi

# Check if "logs" directory exists, if not create it
if [ ! -d "./logs" ]; then
  mkdir ./logs
fi

# Execute the Python script with uv and redirect output to log file
"$UV_BIN" run ./scripts/main.py >> ./logs/uv_cron.log 2>&1
