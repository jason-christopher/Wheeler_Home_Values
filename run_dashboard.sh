#!/bin/bash

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Run the Streamlit dashboard
echo "Starting Wheeler Home Values Dashboard..."
streamlit run dashboard.py
