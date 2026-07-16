#!/bin/bash
set -eo pipefail

# Enterprise AI Support Backend - Runtime Healthcheck Script
# Used by container runtimes to verify status in microservice clusters.

PORT="${PORT:-8000}"
HEALTH_URL="http://localhost:${PORT}/api/v1/health"

echo "Running health check on $HEALTH_URL..."

# Fetch HTTP status code
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "HEALTH CHECK SUCCESS: Backend gateway is online and responding."
    exit 0
else
    echo "HEALTH CHECK FAILED: Received HTTP status code $HTTP_STATUS from backend health system."
    exit 1
fi
