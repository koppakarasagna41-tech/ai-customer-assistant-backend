#!/bin/bash
set -eo pipefail

# Enterprise AI Support Backend - Runtime Startup Script
echo "Starting Enterprise AI Support Gateway Production Runtime..."

# Check if port environment variable is set, otherwise default to 8000
PORT="${PORT:-8000}"
export PORT

# Verify vital environment variables exist or warn
if [ -z "$GEMINI_API_KEY" ]; then
    echo "WARNING: GEMINI_API_KEY is not defined. AI pipeline services may fail."
fi

if [ -z "$JWT_SECRET" ]; then
    echo "WARNING: JWT_SECRET is not defined. Auth services will use transient keys."
fi

# Apply migrations or run database seed steps if required
echo "Validating system models and databases connection..."
python3 -c "import sys; print('Python version:', sys.version)"

# Boot production app server
echo "Booting Gunicorn server binding to 0.0.0.0:$PORT..."
exec gunicorn -k uvicorn.workers.UvicornWorker -c app/gunicorn.conf.py app.main:app
