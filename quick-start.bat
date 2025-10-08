@echo off
REM Quick Start Script for Windows
REM This script helps you get started with the Telegram-MCP Router

echo ========================================
echo   Telegram-MCP Quick Start (Windows)
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Node.js and Python are installed
echo.

REM Check if we're in the right directory
if not exist "router\package.json" (
    echo [ERROR] Please run this script from the project root directory
    pause
    exit /b 1
)

echo Step 1: Installing Node.js dependencies...
echo.
cd router
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Node.js dependencies
    pause
    exit /b 1
)
cd ..
echo [OK] Node.js dependencies installed
echo.

echo Step 2: Installing Python dependencies...
echo.
cd mcp-client
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies
    pause
    exit /b 1
)
cd ..
echo [OK] Python dependencies installed
echo.

echo Step 3: Checking environment configuration...
echo.
if not exist "router\.env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating .env from template...
    copy router\.env.example router\.env >nul
    echo.
    echo ========================================
    echo  IMPORTANT: Configure your .env file
    echo ========================================
    echo.
    echo Please edit router\.env with:
    echo   1. Your Telegram bot token
    echo   2. Your Telegram chat ID
    echo.
    echo To get these:
    echo   - Bot token: Talk to @BotFather on Telegram
    echo   - Chat ID: Talk to @userinfobot on Telegram
    echo.
    echo Press any key to open .env file in notepad...
    pause >nul
    start notepad router\.env
    echo.
    echo After editing .env, press any key to continue...
    pause >nul
) else (
    echo [OK] .env file exists
)
echo.

echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Make sure you've configured router\.env with your:
echo    - TELEGRAM_BOT_TOKEN
echo    - TELEGRAM_CHAT_ID
echo.
echo 2. Start the router:
echo    cd router
echo    npm start
echo.
echo 3. In a new terminal, run tests:
echo    cd tests
echo    python test_script.py
echo.
echo 4. Or run an example server:
echo    cd examples
echo    python example_server_1.py
echo.
echo For detailed instructions, see docs\SETUP.md
echo.
echo Press any key to exit...
pause >nul
