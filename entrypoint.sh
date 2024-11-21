#!/bin/sh
# Calculate optimal number of workers
NUM_CORES=$(nproc)
WORKERS=$((2 * NUM_CORES + 1))

echo "Starting Uvicorn with $WORKERS workers"
exec uvicorn main:app --reload --workers $WORKERS --port 8000 --host 0.0.0.0