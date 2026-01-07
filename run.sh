#!/usr/bin/env bash
set -euo pipefail

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UV_BIN=/home/kitajima/.local/bin/uv

# echo $SCRIPT_DIR

# Check if "logs" directory exists, if not create it
if [ ! -d "./logs" ]; then
  mkdir $SCRIPT_DIR/logs
fi

# Execute the Python script with uv and redirect output to log file
"$UV_BIN" run $SCRIPT_DIR/scripts/main.py 
