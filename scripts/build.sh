#!/bin/bash
set -eo pipefail

# Enterprise AI Support Backend - Build & Verification Script
echo "Starting Enterprise AI Support Gateway Build & Verification..."

# Upgrade pip
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing python dependencies from requirements.txt..."
pip install --no-cache-dir -r requirements.txt

# Run syntax/import validations
echo "Validating code syntax compilation across modules..."
python3 -m py_compile app/**/*.py app/*.py

# Verify FastAPI application instantiation runs without boot crashes
echo "Validating application routing schema initialization..."
python3 -c "from app.main import app; print('FastAPI app routing table verified successfully. Endpoints:', len(app.routes))"

echo "Build and pre-deployment validation successfully completed!"
