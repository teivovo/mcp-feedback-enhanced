"""
Example MCP Server 1 - VSCode Project A
Simple example showing how to use the Telegram feedback tool
"""

import asyncio
import os
import sys

# Add mcp-client to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-client'))

from telegram_feedback_tool import create_telegram_mcp_server
import mcp.server.stdio


async def main():
    """Run the MCP server."""
    
    # Create server
    server = create_telegram_mcp_server(
        instance_name="VSCode-ProjectA",
        callback_port=3001,
        router_url="http://localhost:8080"
    )
    
    print("=" * 60)
    print("🚀 MCP Server: VSCode-ProjectA")
    print("=" * 60)
    print("Port: 3001")
    print("Tools available:")
    print("  • ask_user_telegram - Ask user questions")
    print("  • notify_user_telegram - Send notifications")
    print("  • confirm_with_user_telegram - Request confirmations")
    print("=" * 60)
    print("\nStarting server...\n")
    
    # Start Telegram client
    await server.telegram.start()
    
    # Run MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
