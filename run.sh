#!/bin/bash

# Switch to the directory where this script is located
cd "$(dirname "$0")"

echo "============================================="
echo "   Running Executive Email Scraper"
echo "============================================="
echo ""

# Ensure uv is in PATH if it was just installed
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

if ! command -v uv &> /dev/null; then
    echo "❌ 'uv' not found. Please run ./setup.sh (or setup.command) first."
    
    # Keep terminal open if double-clicked
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Run the scraper
uv run scraper.py

echo ""
echo "============================================="
echo "✅ Finished!"
echo "============================================="
echo ""

# Keep terminal open if double-clicked
read -n 1 -s -r -p "Press any key to exit..."
echo ""
