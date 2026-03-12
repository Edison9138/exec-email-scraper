#!/bin/bash

# Switch to the directory where this script is located
cd "$(dirname "$0")"

# Exit on error
set -e

echo "============================================="
echo "   Executive Email Scraper - 1-Click Setup"
echo "============================================="
echo ""

# 1. Check if uv is installed, if not install it
if ! command -v uv &> /dev/null; then
    echo "📦 'uv' (Python package manager) not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the env to make uv available in this script
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    elif [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    fi
    export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo "❌ Failed to install 'uv'. Please install manually: https://docs.astral.sh/uv/"
        
        # Keep terminal open if double-clicked on Mac
        read -n 1 -s -r -p "Press any key to exit..."
        exit 1
    fi
    echo "✅ 'uv' installed successfully!"
else
    echo "✅ 'uv' is already installed."
fi

# 2. Install Python dependencies
echo ""
echo "📦 Installing project dependencies..."
uv sync
echo "✅ Dependencies installed!"

# 3. Setup .env file
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "⚠️  IMPORTANT: Please open the '.env' file and add your Hunter.io API key!"
    else
        echo "HUNTER_API_KEY=your_key_here" > .env
        echo "✅ Created .env file."
        echo "⚠️  IMPORTANT: Please open the '.env' file and add your Hunter.io API key!"
    fi
else
    echo "✅ .env file already exists."
fi

# 4. Process companies.txt example
if [ ! -f "companies.txt" ]; then
    echo "## Example Member" > companies.txt
    echo "stripe.com" >> companies.txt
    echo "✅ Created example companies.txt file"
else
    echo "✅ companies.txt already exists."
fi

echo ""
echo "============================================="
echo "🎉 Setup Complete!"
echo "============================================="
echo ""
echo "Next steps:"
echo "1. Edit the '.env' file to add your Hunter.io API key"
echo "2. Edit the 'companies.txt' file to add the domains you want to search"
echo "3. Run the scraper by using: ./run.sh (or double-clicking run.command on Mac)"
echo ""

# Keep terminal open if double-clicked
read -n 1 -s -r -p "Press any key to exit..."
echo ""
