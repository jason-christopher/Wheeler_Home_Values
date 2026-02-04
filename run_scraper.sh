#!/bin/bash

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Update Playwright to the latest version
echo "Updating Playwright..."
pip install --upgrade playwright

# Install/update Chromium browser for Playwright
echo "Updating Playwright Chromium..."
playwright install chromium

# Run the scraper
echo "Starting scraper..."
python -m home_values.playwright_scraper
