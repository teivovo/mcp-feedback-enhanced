#!/usr/bin/env python3
"""
Trigger MCP Server Reload
=========================

This script triggers a hot reload of the MCP server backend by creating
the reload marker file that the dev wrapper monitors.

Usage:
    python trigger_reload.py
"""
import os
import tempfile
import time

def trigger_reload():
    """Create reload marker file to trigger backend restart"""
    reload_marker = os.path.join(tempfile.gettempdir(), "mcp_reload_request")
    
    print("=" * 80)
    print("MCP Server Reload Trigger")
    print("=" * 80)
    print()
    
    try:
        # Create marker file with timestamp
        with open(reload_marker, "w") as f:
            f.write(str(time.time()))
        
        print(f"✅ Reload marker created: {reload_marker}")
        print()
        print("The dev wrapper will detect this marker and reload the backend.")
        print("Check the runtime log for reload activity:")
        print("  logs/devwrapper_runtime_*.log")
        print()
        print("Expected log entries:")
        print("  - 'Reload marker detected'")
        print("  - '=== RELOADING BACKEND ==='")
        print("  - 'Backend process terminated'")
        print("  - 'Backend process spawned with PID: XXXXX'")
        print("  - '=== RELOAD COMPLETE ==='")
        print()
        print("The reload should complete in 1-2 seconds.")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create reload marker: {e}")
        return False

if __name__ == "__main__":
    success = trigger_reload()
    exit(0 if success else 1)

