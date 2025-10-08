"""
Example MCP Server 3 - AugmentCode Project C
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mcp-client'))

from telegram_feedback_tool import create_telegram_mcp_server
import mcp.server.stdio


async def main():
    server = create_telegram_mcp_server(
        instance_name="AugmentCode-ProjectC",
        callback_port=3003,
        router_url="http://localhost:8080"
    )
    
    print("=" * 60)
    print("🚀 MCP Server: AugmentCode-ProjectC")
    print("=" * 60)
    print("Port: 3003")
    print("=" * 60)
    print("\nStarting server...\n")
    
    await server.telegram.start()
    
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
