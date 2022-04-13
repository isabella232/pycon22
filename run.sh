#!/usr/bin/env bash

set -e

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Setup database
#flask db init
#flask db migrate
#flask db upgrade

# Run Flask app
FLASK_APP=app flask run  