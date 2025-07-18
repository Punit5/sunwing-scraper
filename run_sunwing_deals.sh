#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run the script
"$SCRIPT_DIR/myvenv/bin/python" "$SCRIPT_DIR/sunwing_deals.py" "$@" 