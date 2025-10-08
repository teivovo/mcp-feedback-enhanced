#!/usr/bin/env python3
"""
Check Running MCP Server State
==============================

This script checks the state of the currently running MCP server
by examining the global instances and bridge status.
"""

import sys
import asyncio
import importlib
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def check_server_state():
    """Check the current state of the running MCP server"""
    print("🔍 Checking Running MCP Server State")
    print("=" * 50)
    
    try:
        # Import the modules to access global instances
        from mcp_feedback_enhanced.utils import config_manager
        from mcp_feedback_enhanced.utils import logging_middleware  
        from mcp_feedback_enhanced.utils import mcp_telegram_bridge
        
        print("\n1. Configuration Manager Status:")
        config_mgr = config_manager._global_config_manager
        if config_mgr:
            print("   ✅ Global config manager exists")
            telegram_config = config_mgr.get_telegram_config()
            if telegram_config:
                print(f"   ✅ Telegram enabled: {telegram_config.enabled}")
                print(f"   ✅ Auto-forwarding: {telegram_config.enable_auto_forwarding}")
                print(f"   ✅ Bridge enabled: {telegram_config.enable_bridge}")
            else:
                print("   ❌ No Telegram config")
        else:
            print("   ❌ No global config manager")
        
        print("\n2. Logging Middleware Status:")
        middleware = logging_middleware._global_middleware
        if middleware:
            print("   ✅ Global middleware exists")
            print(f"   📊 Total calls: {middleware.stats['total_calls']}")
            print(f"   🔗 Telegram callback: {'✅ Set' if middleware.telegram_callback else '❌ Not set'}")
            print(f"   📝 Log entries: {len(middleware.log_entries)}")
        else:
            print("   ❌ No global middleware")
        
        print("\n3. Telegram Bridge Status:")
        bridge = mcp_telegram_bridge._global_bridge
        if bridge:
            print("   ✅ Global bridge exists")
            status = bridge.get_bridge_status()
            print(f"   🔌 Status: {status['status']}")
            print(f"   🏃 Running: {status['is_running']}")
            print(f"   👥 Active sessions: {status['active_sessions']}")
            print(f"   🔄 Auto-forwarding: {status['config']['enable_auto_forwarding']}")
            
            # Check if middleware callback is properly set
            if hasattr(bridge, 'logging_middleware') and bridge.logging_middleware:
                callback_set = bridge.logging_middleware.telegram_callback is not None
                print(f"   📞 Middleware callback: {'✅ Set' if callback_set else '❌ Not set'}")
                
                # Check if it's the same middleware instance
                same_instance = bridge.logging_middleware is middleware
                print(f"   🔗 Same middleware instance: {'✅ Yes' if same_instance else '❌ No'}")
            else:
                print("   ❌ Bridge has no middleware reference")
                
        else:
            print("   ❌ No global bridge")
        
        print("\n4. Testing Manual Event Generation:")
        if middleware and bridge and bridge.status.value == "connected":
            print("   🧪 Generating test MCP events...")
            
            # Generate a test event
            call_id = middleware.log_tool_call_start(
                "manual_test_tool",
                request_data={"test": "manual_event"},
                session_id="test_session_123"
            )
            print(f"   ✅ Generated start event: {call_id}")
            
            # Wait a moment for async processing
            await asyncio.sleep(2)
            
            middleware.log_tool_call_end(
                call_id,
                response_data={"result": "manual_test_success"}
            )
            print(f"   ✅ Generated end event")
            
            # Wait for forwarding
            await asyncio.sleep(3)
            print("   📱 Check Telegram for test messages!")
            
        else:
            print("   ⚠️  Cannot test - middleware or bridge not ready")
            if not middleware:
                print("      - No middleware")
            if not bridge:
                print("      - No bridge")
            elif bridge.status.value != "connected":
                print(f"      - Bridge not connected (status: {bridge.status.value})")
        
        print("\n5. Bridge Connection Details:")
        if bridge:
            try:
                # Check Telegram manager
                if hasattr(bridge, 'telegram_manager'):
                    print("   ✅ Bridge has telegram_manager")
                    
                    # Test direct connection
                    success, message = await bridge.telegram_manager.test_connection()
                    print(f"   🔗 Direct connection test: {'✅ Success' if success else '❌ Failed'}")
                    if not success:
                        print(f"      Error: {message}")
                else:
                    print("   ❌ Bridge has no telegram_manager")
                    
            except Exception as e:
                print(f"   ❌ Connection test error: {e}")
        
    except Exception as e:
        print(f"❌ Error checking server state: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_server_state())
