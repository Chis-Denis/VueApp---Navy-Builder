#!/bin/bash
# Script to run the Python script to delete ships with ID > threshold
# Usage: ./delete_last_ships.sh [threshold_id]
# If threshold_id is not provided, default 1000 will be used

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "../../venv" ]; then
    source ../../venv/bin/activate
fi

# Run the Python script with argument if provided
if [ -z "$1" ]; then
    echo "Deleting ships with ID > 1000..."
    python "$DIR/delete_last_100000_ships.py"
else
    echo "Deleting ships with ID > $1..."
    python "$DIR/delete_last_100000_ships.py" "$1"
fi

# Deactivate virtual environment if it was activated
if [ -d "../../venv" ]; then
    deactivate
fi

echo "Operation completed." 