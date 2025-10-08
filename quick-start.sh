#!/bin/bash
# Quick Start Script for Linux/macOS
# This script helps you get started with the Telegram-MCP Router

set -e

echo "========================================"
echo "  Telegram-MCP Quick Start (Unix)"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

echo "[OK] Node.js and Python are installed"
echo ""

# Check if we're in the right directory
if [ ! -f "router/package.json" ]; then
    echo "[ERROR] Please run this script from the project root directory"
    exit 1
fi

echo "Step 1: Installing Node.js dependencies..."
echo ""
cd router
npm install
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Node.js dependencies"
    exit 1
fi
cd ..
echo "[OK] Node.js dependencies installed"
echo ""

echo "Step 2: Installing Python dependencies..."
echo ""
cd mcp-client
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Python dependencies"
    exit 1
fi
cd ..
echo "[OK] Python dependencies installed"
echo ""

echo "Step 3: Checking environment configuration..."
echo ""
if [ ! -f "router/.env" ]; then
    echo "[WARNING] .env file not found!"
    echo ""
    echo "Creating .env from template..."
    cp router/.env.example router/.env
    echo ""
    echo "========================================"
    echo " IMPORTANT: Configure your .env file"
    echo "========================================"
    echo ""
    echo "Please edit router/.env with:"
    echo "  1. Your Telegram bot token"
    echo "  2. Your Telegram chat ID"
    echo ""
    echo "To get these:"
    echo "  - Bot token: Talk to @BotFather on Telegram"
    echo "  - Chat ID: Talk to @userinfobot on Telegram"
    echo ""
    echo "Opening .env file in default editor..."
    ${EDITOR:-nano} router/.env
else
    echo "[OK] .env file exists"
fi
echo ""

echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure you've configured router/.env with your:"
echo "   - TELEGRAM_BOT_TOKEN"
echo "   - TELEGRAM_CHAT_ID"
echo ""
echo "2. Start the router:"
echo "   cd router"
echo "   npm start"
echo ""
echo "3. In a new terminal, run tests:"
echo "   cd tests"
echo "   python3 test_script.py"
echo ""
echo "4. Or run an example server:"
echo "   cd examples"
echo "   python3 example_server_1.py"
echo ""
echo "For detailed instructions, see docs/SETUP.md"
echo ""
