#!/usr/bin/env bash

set -e

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Run Flask app
FLASK_APP=app flask run  