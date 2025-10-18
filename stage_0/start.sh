#!/bin/bash
# start.sh
# Exit immediately if a command exits with a non-zero status
set -o errexit  

# Run the app using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port $PORT
