@echo off
REM MCP Feedback Enhanced Development Wrapper
REM This script ensures the module runs with the correct environment

cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

REM Set PYTHONPATH to include src directory
set PYTHONPATH=%~dp0src

REM Run the module with all arguments
%PYTHON_CMD% -m mcp_feedback_enhanced %*
