"""
MCP Telegram Feedback Tool
Provides MCP tools for bidirectional Telegram communication
Auto-manages router lifecycle with the MCP server
"""
import asyncio
import os
import signal
import sys
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp_telegram_client import MCPTelegramClient

# Configuration
INSTANCE_NAME = os.getenv('INSTANCE_NAME', 'MCP-Instance')
CALLBACK_PORT = int(os.getenv('CALLBACK_PORT', '3001'))
ROUTER_URL = os.getenv('ROUTER_URL', 'http://localhost:8080')

# Global client instance
telegram_client: MCPTelegramClient = None

# MCP Server
app = Server("telegram-feedback")

async def initialize_client():
    """Initialize the Telegram client"""
    global telegram_client
    
    if telegram_client is None:
        telegram_client = MCPTelegramClient(
            instance_name=INSTANCE_NAME,
            callback_port=CALLBACK_PORT,
            router_url=ROUTER_URL,
            auto_cleanup=True  # Auto-stop router when this client stops
        )
        await telegram_client.start()
        print(f"✅ {INSTANCE_NAME} ready and registered with router")

async def cleanup_client():
    """Cleanup the Telegram client"""
    global telegram_client
    
    if telegram_client is not None:
        await telegram_client.stop()
        telegram_client = None

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def handle_shutdown(signum, frame):
        print("\n[SIGNAL] Received shutdown signal, cleaning up...")
        if telegram_client:
            # Run cleanup in event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(cleanup_client())
            else:
                loop.run_until_complete(cleanup_client())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    if sys.platform == 'win32':
        signal.signal(signal.SIGBREAK, handle_shutdown)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="ask_user_telegram",
            description=(
                "Ask the user a question via Telegram and wait for their reply. "
                "Use this when you need direct input or confirmation from the user. "
                "The tool will BLOCK until the user replies (timeout: 5 minutes). "
                "This is useful for: confirming actions, asking for preferences, "
                "getting feedback, or any interactive decision-making. "
                "Supports sending images along with the question."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask the user"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context information about the question",
                        "additionalProperties": True
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 300 = 5 minutes)",
                        "default": 300
                    },
                    "images": {
                        "type": "array",
                        "description": "Optional array of base64-encoded images to send with the question",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["question"]
            }
        ),
        Tool(
            name="notify_user_telegram",
            description=(
                "Send a notification to the user via Telegram without waiting for reply. "
                "Use this for: status updates, completion notifications, error alerts, "
                "or any one-way communication that doesn't require user response. "
                "Supports sending images along with the notification."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The notification message to send"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context information",
                        "additionalProperties": True
                    },
                    "images": {
                        "type": "array",
                        "description": "Optional array of base64-encoded images to send with the notification",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="confirm_with_user_telegram",
            description=(
                "Ask the user for yes/no confirmation via Telegram. "
                "The tool will BLOCK until the user confirms or declines. "
                "Use this before: executing destructive operations, making important changes, "
                "or any action that requires explicit user approval. "
                "Supports sending images for context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The yes/no question to ask"
                    },
                    "context": {
                        "type": "object",
                        "description": "Optional context information",
                        "additionalProperties": True
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 300 = 5 minutes)",
                        "default": 300
                    },
                    "images": {
                        "type": "array",
                        "description": "Optional array of base64-encoded images for context",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["question"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    # Ensure client is initialized
    await initialize_client()
    
    if name == "ask_user_telegram":
        try:
            question = arguments.get("question")
            context = arguments.get("context", {})
            timeout = arguments.get("timeout", 300)
            images = arguments.get("images", [])
            
            # Send question and wait for reply
            reply = await telegram_client.send_and_wait_for_reply(
                message=question,
                context=context,
                timeout=timeout,
                images=images
            )
            
            return [TextContent(
                type="text",
                text=f"User replied via Telegram: {reply}"
            )]
            
        except TimeoutError:
            return [TextContent(
                type="text",
                text=f"No reply received from user within {timeout} seconds. User may not have seen the message or chose not to respond."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error communicating with Telegram: {str(e)}"
            )]
    
    elif name == "notify_user_telegram":
        try:
            message = arguments.get("message")
            context = arguments.get("context", {})
            images = arguments.get("images", [])
            
            # Send notification
            await telegram_client.send_notification(
                message=message,
                context=context,
                images=images
            )
            
            return [TextContent(
                type="text",
                text="Notification sent to user via Telegram"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error sending notification: {str(e)}"
            )]
    
    elif name == "confirm_with_user_telegram":
        try:
            question = arguments.get("question")
            context = arguments.get("context", {})
            timeout = arguments.get("timeout", 300)
            images = arguments.get("images", [])
            
            # Request confirmation
            confirmed = await telegram_client.request_confirmation(
                question=question,
                context=context,
                timeout=timeout,
                images=images
            )
            
            if confirmed:
                return [TextContent(
                    type="text",
                    text="User confirmed via Telegram"
                )]
            else:
                return [TextContent(
                    type="text",
                    text="User declined via Telegram"
                )]
                
        except TimeoutError:
            return [TextContent(
                type="text",
                text=f"No reply received from user within {timeout} seconds. Treating as declined."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error requesting confirmation: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def run_server():
    """Run the MCP server"""
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Initialize client
    await initialize_client()
    
    try:
        # Run the MCP server
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        # Cleanup on exit
        await cleanup_client()

if __name__ == "__main__":
    asyncio.run(run_server())