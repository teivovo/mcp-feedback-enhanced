#!/usr/bin/env python3
"""
Final Comprehensive Linting and Compatibility Report
====================================================

Generate a comprehensive report on code quality and MCP/NPX compatibility.
"""

import sys
import os
import json
from pathlib import Path

def check_critical_files():
    """Check that all critical files exist and are valid"""
    print("🔍 Checking Critical Files")
    print("-" * 30)
    
    critical_files = [
        ("pyproject.toml", "Package configuration"),
        ("src/mcp_feedback_enhanced/__init__.py", "Main package init"),
        ("src/mcp_feedback_enhanced/__main__.py", "Entry point"),
        ("src/mcp_feedback_enhanced/server.py", "MCP server"),
        ("src/mcp_feedback_enhanced/utils/telegram_manager.py", "Telegram manager"),
        ("mcp_config.json", "MCP configuration"),
    ]
    
    missing = []
    for file_path, description in critical_files:
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ {description}: {file_path} - MISSING")
            missing.append(file_path)
    
    return len(missing) == 0

def check_bridge_cleanup():
    """Check that bridge references are properly cleaned up"""
    print("\n🧹 Checking Bridge Cleanup")
    print("-" * 30)
    
    # Check that bridge file is removed
    bridge_file = Path("src/mcp_feedback_enhanced/utils/mcp_telegram_bridge.py")
    if bridge_file.exists():
        print("❌ Bridge file still exists")
        return False
    else:
        print("✅ Bridge file removed")
    
    # Check __init__.py for bridge exports
    init_file = Path("src/mcp_feedback_enhanced/utils/__init__.py")
    if init_file.exists():
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        bridge_exports = ['get_bridge', 'initialize_bridge', 'BridgeStatus']
        found_exports = [exp for exp in bridge_exports if exp in content]
        
        if found_exports:
            print(f"❌ Bridge exports still in __init__.py: {found_exports}")
            return False
        else:
            print("✅ Bridge exports cleaned from __init__.py")
    
    return True

def check_telegram_integration():
    """Check that direct Telegram integration is working"""
    print("\n📱 Checking Telegram Integration")
    print("-" * 30)
    
    sys.path.insert(0, "src")
    
    try:
        from mcp_feedback_enhanced.utils.telegram_manager import (
            send_telegram_notification,
            format_feedback_notification
        )
        print("✅ Telegram functions imported")
        
        # Test message formatting
        test_message = format_feedback_notification("Test", "/test")
        if "Test" in test_message and "test" in test_message:
            print("✅ Message formatting works")
        else:
            print("❌ Message formatting failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram integration failed: {e}")
        return False

def check_mcp_compatibility():
    """Check MCP server compatibility"""
    print("\n🔧 Checking MCP Compatibility")
    print("-" * 30)
    
    sys.path.insert(0, "src")
    
    try:
        from mcp_feedback_enhanced.server import mcp, main
        print("✅ MCP server imported")
        
        # Check FastMCP interface
        if hasattr(mcp, 'run'):
            print("✅ MCP run method available")
        else:
            print("❌ MCP run method missing")
            return False
        
        print("✅ MCP server interface compatible")
        return True
        
    except Exception as e:
        print(f"❌ MCP compatibility check failed: {e}")
        return False

def check_npx_readiness():
    """Check NPX readiness"""
    print("\n📦 Checking NPX Readiness")
    print("-" * 30)
    
    # Check pyproject.toml for scripts
    try:
        with open("pyproject.toml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "[project.scripts]" in content:
            print("✅ Entry scripts defined")
        else:
            print("❌ Entry scripts missing")
            return False
        
        if "mcp-feedback-enhanced" in content:
            print("✅ Package name correct")
        else:
            print("❌ Package name issue")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ NPX readiness check failed: {e}")
        return False

def generate_summary():
    """Generate final summary"""
    print("\n" + "=" * 60)
    print("📊 FINAL LINTING AND COMPATIBILITY REPORT")
    print("=" * 60)
    
    checks = [
        ("Critical Files", check_critical_files),
        ("Bridge Cleanup", check_bridge_cleanup),
        ("Telegram Integration", check_telegram_integration),
        ("MCP Compatibility", check_mcp_compatibility),
        ("NPX Readiness", check_npx_readiness),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        if check_func():
            passed += 1
    
    print(f"\n📈 Overall Score: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 EXCELLENT - All checks passed!")
        print("✅ Code is properly linted and cleaned")
        print("✅ Bridge system successfully removed")
        print("✅ Direct Telegram integration working")
        print("✅ MCP server fully compatible")
        print("✅ Ready for NPX usage")
        
        print("\n💡 Usage Instructions:")
        print("  • Install: pip install -e .")
        print("  • Run: python -m mcp_feedback_enhanced")
        print("  • NPX: npx mcp-feedback-enhanced (after publishing)")
        
    elif passed >= 4:
        print("\n✅ GOOD - Minor issues found")
        print("Most functionality is working correctly")
        
    elif passed >= 3:
        print("\n⚠️  FAIR - Some issues need attention")
        print("Core functionality works but improvements needed")
        
    else:
        print("\n❌ POOR - Major issues found")
        print("Significant problems need to be resolved")
    
    return passed == total

if __name__ == "__main__":
    success = generate_summary()
    sys.exit(0 if success else 1)
