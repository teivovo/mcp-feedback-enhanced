#!/usr/bin/env python3
"""
Development runner for MCP Feedback Enhanced
This script ensures the module runs with the correct Python environment and path setup.
"""

import os
import sys
import subprocess

def main():
    """Run the MCP feedback enhanced module with proper environment setup"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the src directory to Python path
    src_dir = os.path.join(script_dir, "src")
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = src_dir
    
    # Use the virtual environment Python if available
    venv_python = os.path.join(script_dir, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        python_cmd = venv_python
    else:
        python_cmd = sys.executable
    
    # Run the module
    cmd = [python_cmd, "-m", "mcp_feedback_enhanced"] + sys.argv[1:]
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()
