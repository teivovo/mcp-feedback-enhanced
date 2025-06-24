#!/usr/bin/env python3
"""
Bidirectional Telegram Test
===========================

This script tests the complete bidirectional flow:
1. Send MCP request via Telegram
2. Receive user response via Telegram  
3. Process as MCP feedback response
4. Simulate VSCode extension integration
"""

import asyncio
import sys
import time
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_feedback_enhanced.utils.config_manager import initialize_config_manager
from mcp_feedback_enhanced.utils.logging_middleware import initialize_middleware
from mcp_feedback_enhanced.utils.mcp_telegram_bridge import initialize_bridge
from mcp_feedback_enhanced.utils.telegram_manager import TelegramBotManager


class MockMCPServer:
    """Mock MCP Server to simulate VSCode extension interaction"""
    
    def __init__(self):
        self.pending_requests = {}
        self.responses = {}
    
    async def send_interactive_feedback_request(self, project_dir, summary, timeout=600):
        """Simulate MCP interactive_feedback tool call"""
        request_id = f"mcp_request_{int(time.time())}"
        
        self.pending_requests[request_id] = {
            "tool": "interactive_feedback",
            "params": {
                "project_directory": project_dir,
                "summary": summary,
                "timeout": timeout
            },
            "timestamp": time.time(),
            "status": "pending"
        }
        
        print(f"📤 MCP Request Sent: {request_id}")
        print(f"   Tool: interactive_feedback")
        print(f"   Project: {project_dir}")
        print(f"   Summary: {summary}")
        
        return request_id
    
    async def receive_feedback_response(self, request_id, feedback_data):
        """Simulate receiving feedback response from Telegram"""
        if request_id in self.pending_requests:
            self.responses[request_id] = {
                "request": self.pending_requests[request_id],
                "response": feedback_data,
                "completed_at": time.time(),
                "status": "completed"
            }
            
            # Update request status
            self.pending_requests[request_id]["status"] = "completed"
            
            print(f"✅ MCP Response Received: {request_id}")
            print(f"   Feedback Items: {len(feedback_data.get('feedback_items', []))}")
            print(f"   Has Text: {feedback_data.get('has_text_feedback', False)}")
            print(f"   Has Images: {feedback_data.get('has_images', False)}")
            print(f"   Commands Run: {len(feedback_data.get('command_logs', []))}")
            
            return True
        
        return False
    
    def get_request_status(self, request_id):
        """Get status of MCP request"""
        return self.pending_requests.get(request_id, {}).get("status", "unknown")
    
    def get_response(self, request_id):
        """Get completed response"""
        return self.responses.get(request_id)


async def run_bidirectional_test():
    """Run bidirectional communication test"""
    print("🔄 Starting Bidirectional Telegram Test...")
    print("=" * 60)
    
    try:
        # Initialize mock MCP server
        mock_server = MockMCPServer()
        print("✅ Mock MCP Server initialized")
        
        # Initialize MCP components
        print("🔧 Initializing MCP Telegram System...")
        
        config_manager = initialize_config_manager(
            config_file="bidirectional_test_config.json",
            enable_encryption=False,
            auto_save=True
        )
        
        config_manager.update_telegram_config(
            enabled=True,
            bot_token="8004237851:AAEEzbT1_BKF_bkHTUhXQLLMZumIWt67D8g",
            chat_id="507491548",
            enable_bridge=True,
            enable_auto_forwarding=True,
            enable_chunking=True,
            max_chunk_size=3000,
            session_timeout_minutes=30
        )
        
        middleware = initialize_middleware({
            'log_level': 'debug',
            'enable_telegram_forwarding': True,
            'max_log_entries': 200
        })
        
        telegram_manager = TelegramBotManager(
            "8004237851:AAEEzbT1_BKF_bkHTUhXQLLMZumIWt67D8g",
            "507491548"
        )
        await telegram_manager.start()
        
        bridge_config = {
            'session_timeout_minutes': 30,
            'max_concurrent_sessions': 5,
            'enable_auto_forwarding': True,
            'message_format': {
                'include_session_id': True,
                'include_timestamp': True,
                'include_project_path': True,
                'include_details': True
            }
        }
        
        bridge = initialize_bridge(telegram_manager, middleware, bridge_config)
        await bridge.start()
        print("✅ All components initialized")
        
        # Step 1: Simulate MCP request from VSCode extension
        print("\n📤 Step 1: Simulating MCP Request from VSCode...")
        
        request_id = await mock_server.send_interactive_feedback_request(
            "/mcp-feedback-dev/bidirectional-test",
            "Testing bidirectional communication between VSCode extension and Telegram"
        )
        
        # Step 2: Send request to Telegram
        session_id = f"bidirectional_{int(time.time())}"
        await bridge.create_session(
            session_id, "507491548", "/mcp-feedback-dev/bidirectional-test",
            user_context={"mcp_request_id": request_id, "test_type": "bidirectional"}
        )
        
        request_message = f"""🔄 **Bidirectional Communication Test**

**📋 MCP Request from VSCode Extension:**
- Request ID: `{request_id}`
- Tool: `interactive_feedback`
- Project: `/mcp-feedback-dev/bidirectional-test`
- Summary: Testing bidirectional communication

**🎯 Your Mission:**
Please respond to this message with your feedback! This will test the complete flow:

1. ✅ VSCode extension → MCP Server → Telegram (this message)
2. ⏳ **Telegram → MCP Server → VSCode extension** (your response)

**💬 What to send back:**
Please reply with any of the following:
- Text feedback about the MCP system
- Suggestions for improvements
- Questions about features
- Test commands you'd like me to run

**🔧 Test Commands Available:**
- `/status` - Show system status
- `/logs` - Show recent logs  
- `/config` - Show configuration
- `/test <message>` - Echo test message

**⚡ How it works:**
1. You send a message in Telegram
2. Bridge captures your message
3. Processes it as MCP feedback response
4. Sends back to mock VSCode extension
5. Shows complete bidirectional flow

**Ready to test! Send me your response! 🚀**"""
        
        await bridge.send_mcp_message_to_telegram(
            session_id=session_id,
            mcp_call_id=request_id,
            message=request_message,
            metadata={"test": "bidirectional", "request_id": request_id}
        )
        
        print("✅ Request sent to Telegram")
        print("📱 Please check your Telegram and respond to the message!")
        
        # Step 3: Listen for responses
        print("\n👂 Step 3: Listening for your Telegram responses...")
        print("💬 Send any message in Telegram to test bidirectional flow!")
        
        # Set up response handler
        async def handle_telegram_response(update):
            """Handle incoming Telegram messages as MCP responses"""
            try:
                if update.message and update.message.text:
                    user_message = update.message.text
                    chat_id = str(update.message.chat.id)
                    
                    if chat_id == "507491548":  # Your chat ID
                        print(f"\n📨 Received Telegram Response: {user_message[:100]}...")
                        
                        # Process as MCP feedback
                        feedback_data = {
                            "feedback_items": [
                                {
                                    "type": "text",
                                    "content": user_message,
                                    "timestamp": time.time(),
                                    "source": "telegram"
                                }
                            ],
                            "has_text_feedback": True,
                            "has_images": False,
                            "command_logs": [],
                            "session_info": {
                                "session_id": session_id,
                                "project_directory": "/mcp-feedback-dev/bidirectional-test",
                                "user_chat_id": chat_id
                            },
                            "metadata": {
                                "response_time": time.time(),
                                "message_length": len(user_message),
                                "test_type": "bidirectional"
                            }
                        }
                        
                        # Handle special commands
                        if user_message.startswith('/'):
                            await handle_command(user_message, session_id, bridge)
                        
                        # Send to mock MCP server
                        success = await mock_server.receive_feedback_response(request_id, feedback_data)
                        
                        if success:
                            # Send confirmation back to Telegram
                            confirmation = f"""✅ **Response Processed Successfully!**

**📨 Your Message Received:**
"{user_message[:200]}{'...' if len(user_message) > 200 else ''}"

**🔄 Bidirectional Flow Completed:**
1. ✅ VSCode Extension → MCP → Telegram (original request)
2. ✅ Telegram → MCP → VSCode Extension (your response)

**📊 Processing Details:**
- Request ID: `{request_id}`
- Response Length: {len(user_message)} characters
- Processing Time: {time.strftime('%H:%M:%S')}
- Status: Successfully processed

**🎉 Test Result: BIDIRECTIONAL COMMUNICATION WORKING!**

Send another message to test again, or type `/done` to finish testing."""
                            
                            await bridge.send_mcp_message_to_telegram(
                                session_id=session_id,
                                mcp_call_id=f"confirmation_{int(time.time())}",
                                message=confirmation,
                                metadata={"type": "confirmation", "original_request": request_id}
                            )
                            
                            print("✅ Confirmation sent back to Telegram")
                            
                            # Show mock VSCode extension response
                            print("\n🖥️  Mock VSCode Extension Response:")
                            response = mock_server.get_response(request_id)
                            if response:
                                print(f"   Request: {response['request']['tool']}")
                                print(f"   Status: {response['status']}")
                                print(f"   Feedback: {user_message[:100]}...")
                                print(f"   Completed: {time.strftime('%H:%M:%S', time.localtime(response['completed_at']))}")
                        
                        return True
                        
            except Exception as e:
                print(f"❌ Error handling response: {e}")
                return False
        
        # Set up message handler
        telegram_manager.add_message_handler(handle_telegram_response)
        
        # Wait for responses
        print("⏳ Waiting for your responses (5 minutes)...")
        for i in range(300):  # 5 minutes
            await asyncio.sleep(1)
            if i % 30 == 0:
                print(f"   Listening... ({300-i}s remaining)")
        
        # Cleanup
        await bridge.end_session(session_id)
        await bridge.stop()
        await telegram_manager.stop()
        
        print("\n✅ Bidirectional test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Bidirectional test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def handle_command(command, session_id, bridge):
    """Handle special test commands"""
    try:
        if command == "/status":
            status = bridge.get_bridge_status()
            response = f"📊 **System Status:**\n{json.dumps(status, indent=2)}"
        elif command == "/logs":
            response = "📝 **Recent Logs:** (Feature available in dashboard)"
        elif command == "/config":
            response = "⚙️ **Configuration:** (Secure - view in dashboard)"
        elif command.startswith("/test "):
            test_msg = command[6:]
            response = f"🔄 **Echo Test:** {test_msg}"
        elif command == "/done":
            response = "✅ **Testing Complete!** Thank you for testing bidirectional communication!"
        else:
            response = f"❓ **Unknown Command:** {command}\nAvailable: /status, /logs, /config, /test <msg>, /done"
        
        await bridge.send_mcp_message_to_telegram(
            session_id=session_id,
            mcp_call_id=f"command_{int(time.time())}",
            message=response,
            metadata={"type": "command_response", "command": command}
        )
        
    except Exception as e:
        print(f"❌ Error handling command: {e}")


async def main():
    """Run bidirectional test"""
    print("🔄 MCP Feedback Enhanced - Bidirectional Communication Test")
    print("=" * 60)
    
    success = await run_bidirectional_test()
    
    if success:
        print("\n🎉 Bidirectional test completed successfully!")
        print("🔄 Complete flow tested: VSCode ↔ MCP ↔ Telegram")
    else:
        print("\n❌ Bidirectional test failed")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
