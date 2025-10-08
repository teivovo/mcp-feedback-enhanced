#!/usr/bin/env python3
"""
Force Debug Test and Log Analysis
=================================

This script will force debug logging and check the current state.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Force debug mode
os.environ['MCP_DEBUG'] = 'true'

print("🔍 Analyzing MCP Debug Logging")
print("=" * 50)

# Test debug logging
from mcp_feedback_enhanced.debug import debug_log

print("\n1. Testing debug logging...")
debug_log("=== FORCED DEBUG TEST START ===", "FORCE_TEST")
debug_log("Testing if debug logging works", "FORCE_TEST")
debug_log("Current working directory: " + os.getcwd(), "FORCE_TEST")
debug_log("MCP_DEBUG environment: " + os.getenv("MCP_DEBUG", "not_set"), "FORCE_TEST")
debug_log("=== FORCED DEBUG TEST END ===", "FORCE_TEST")

# Check log file
logs_dir = Path("logs")
if logs_dir.exists():
    print("✅ Logs directory exists")
    log_files = list(logs_dir.glob("*.log"))
    
    if log_files:
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        print(f"📄 Latest log file: {latest_log}")
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            content = f.read()
            
        lines = content.strip().split('\n') if content.strip() else []
        print(f"📊 Total log lines: {len(lines)}")
        
        if lines:
            print("\n📋 Recent log entries:")
            for line in lines[-10:]:  # Show last 10 lines
                print(f"   {line}")
                
            # Look for server startup messages
            startup_lines = [line for line in lines if "啟動" in line or "STARTUP" in line or "服務器" in line]
            if startup_lines:
                print(f"\n🚀 Server startup messages found: {len(startup_lines)}")
                for line in startup_lines:
                    print(f"   {line}")
            else:
                print("\n⚠️  No server startup messages found in logs")
                
            # Look for bridge messages
            bridge_lines = [line for line in lines if "橋接器" in line or "BRIDGE" in line or "Telegram" in line]
            if bridge_lines:
                print(f"\n🌉 Bridge messages found: {len(bridge_lines)}")
                for line in bridge_lines:
                    print(f"   {line}")
            else:
                print("\n⚠️  No bridge messages found in logs")
                
            # Look for tool call messages
            tool_lines = [line for line in lines if "tool" in line.lower() or "工具" in line]
            if tool_lines:
                print(f"\n🔧 Tool call messages found: {len(tool_lines)}")
                for line in tool_lines[-5:]:  # Show last 5
                    print(f"   {line}")
            else:
                print("\n⚠️  No tool call messages found in logs")
        else:
            print("📄 Log file is empty")
    else:
        print("❌ No log files found")
else:
    print("❌ Logs directory does not exist")

print("\n" + "=" * 50)
print("🎯 ANALYSIS SUMMARY:")

# Check if server is actually logging
if logs_dir.exists() and list(logs_dir.glob("*.log")):
    latest_log = max(logs_dir.glob("*.log"), key=lambda f: f.stat().st_mtime)
    with open(latest_log, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "啟動" in content or "STARTUP" in content:
        print("✅ Server startup logs found - server is logging")
    else:
        print("⚠️  Server startup logs NOT found - server may not be in debug mode")
        
    if "橋接器" in content or "BRIDGE" in content:
        print("✅ Bridge logs found - bridge initialization logged")
    else:
        print("❌ Bridge logs NOT found - bridge may not be initializing")
        
    if "interactive_feedback" in content:
        print("✅ Tool call logs found - tools are being logged")
    else:
        print("⚠️  Tool call logs NOT found - tools may not be logging")
else:
    print("❌ No logs found - server is likely not in debug mode")

print("\n💡 RECOMMENDATIONS:")
print("1. If no server logs found: Restart server with MCP_DEBUG=true")
print("2. If no bridge logs found: Check bridge initialization errors")
print("3. If no tool logs found: Check middleware setup")
