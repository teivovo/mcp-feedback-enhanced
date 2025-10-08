# MCP Feedback Enhanced Development Wrapper (PowerShell)
# This script ensures the module runs with the correct environment

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
$VenvPython = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $PythonCmd = $VenvPython
    Write-Host "Using virtual environment Python: $PythonCmd" -ForegroundColor Green
} else {
    $PythonCmd = "python"
    Write-Host "Using system Python: $PythonCmd" -ForegroundColor Yellow
}

# Set PYTHONPATH to include src directory
$SrcDir = Join-Path $ScriptDir "src"
$env:PYTHONPATH = $SrcDir

# Run the module with all arguments
& $PythonCmd -m mcp_feedback_enhanced @Arguments
