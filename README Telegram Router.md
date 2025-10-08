# Bidirectional Telegram-MCP Communication System

> **Production-ready system for real-time bidirectional communication between MCP instances and Telegram**

[![Status](https://img.shields.io/badge/status-ready-green)]()
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)]()
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)]()

## 🎯 What Is This?

A complete solution that allows **multiple MCP instances** (running in different IDEs like VSCode, Cursor, or AugmentCode) to:
- ✅ Send tool feedback to **a single Telegram channel**
- ✅ **Wait for user replies** directly from Telegram
- ✅ **Route replies back** to the correct MCP instance
- ✅ Work seamlessly with **any AI assistant** that supports MCP tools

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   IDE #1    │     │   IDE #2    │     │   IDE #3    │
│  (VSCode)   │     │  (Cursor)   │     │(AugmentCode)│
│             │     │             │     │             │
│ MCP:3001 ──┼─────┼─ MCP:3002 ──┼─────┼─ MCP:3003   │
└─────┬───────┘     └──────┬──────┘     └──────┬──────┘
      │                    │                    │
      └────────────────────┼────────────────────┘
                           │
                  ┌────────▼────────┐
                  │ CENTRAL ROUTER  │
                  │   (Node.js)     │
                  │    Port 8080    │
                  └────────┬────────┘
                           │
                  ┌────────▼────────┐
                  │  TELEGRAM BOT   │
                  │                 │
                  │ Single Channel  │
                  └─────────────────┘
```

## ✨ Key Features

- **🔄 Async Tool Pattern**: Tool calls WAIT for Telegram replies before completing
- **🎯 Smart Routing**: Automatically routes replies to the correct MCP instance
- **🧵 Message Threading**: Supports Telegram's reply-to feature for intuitive UX
- **🔌 Multiple Instances**: Run as many MCP servers as you want
- **⏱️ Auto-Cleanup**: Sessions auto-expire after 30 minutes
- **🛡️ Error Handling**: Robust timeout and error handling
- **📊 Monitoring**: Built-in health checks and statistics

## 🚀 Quick Start

### Prerequisites

- **Node.js** ≥ 18.0.0
- **Python** ≥ 3.10
- **Telegram Bot** (create with @BotFather)
- **Telegram Chat ID**

### 1. Install Dependencies

```bash
# Install Node.js dependencies (router)
cd router
npm install

# Install Python dependencies (MCP client)
cd ../mcp-client
pip install -r requirements.txt
```

### 2. Configure Telegram

1. Create a bot: Talk to [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Get your chat ID: Use [@userinfobot](https://t.me/userinfobot)
4. Create `.env` file:

```bash
cd router
cp .env.example .env
# Edit .env with your tokens
```

**router/.env**:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
ROUTER_PORT=8080
```

### 3. Start the Router

```bash
cd router
npm start
```

You should see:
```
═══════════════════════════════════════
🚀 Telegram Router Started Successfully
═══════════════════════════════════════
📡 HTTP Server: http://localhost:8080
📱 Telegram Bot: Connected
💬 Chat ID: 123456789
═══════════════════════════════════════
Ready to route messages! 🎯
```

### 4. Test the System

```bash
cd tests
python test_script.py
```

The test will guide you through:
- ✅ Single instance communication
- ✅ Multiple instances simultaneously
- ✅ Timeout handling
- ✅ Message threading

## 📖 Usage Guide

### For AI Tool Developers

Use the MCP tool in your code:

```python
from telegram_feedback_tool import create_telegram_mcp_server

# Create MCP server with Telegram tools
server = create_telegram_mcp_server(
    instance_name="VSCode-ProjectA",
    callback_port=3001
)

# Run the server
import mcp.server.stdio
async def main():
    await server.telegram.start()
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

asyncio.run(main())
```

### For Direct Integration

Use the client library directly:

```python
from mcp_telegram_client import MCPTelegramClient

client = MCPTelegramClient(
    instance_name="My-App",
    callback_port=3001
)

await client.start()

# Ask user and WAIT for reply
reply = await client.request_input(
    "What color do you want for the button?"
)
print(f"User chose: {reply}")

# Just notify
await client.send_notification("Task completed!")

# Request confirmation
confirmed = await client.request_confirmation(
    "Do you want to proceed?"
)
if confirmed:
    # Do something
    pass
```

### Available MCP Tools

When integrated, these tools are available to the AI:

#### 1. `ask_user_telegram`
Ask user a question and WAIT for reply.

```json
{
  "question": "What's your favorite color?",
  "context": {"component": "button"},
  "timeout_seconds": 300
}
```

#### 2. `notify_user_telegram`
Send notification without waiting.

```json
{
  "message": "File processed successfully!",
  "context": {"file": "data.csv"}
}
```

#### 3. `confirm_with_user_telegram`
Ask for yes/no confirmation.

```json
{
  "question": "Delete all files?",
  "timeout_seconds": 300
}
```

## 🎭 Example Conversations

### Example 1: Button Color

```
User: "Claude, create a submit button"

Claude: "I'll create the button, but let me ask what color you'd like"

[calls ask_user_telegram: "What color for the submit button?"]

→ Telegram: "🔧 [VSCode-ProjectA]
            What color for the submit button?
            Session: abc12345...
            Reply to this message"

User (in Telegram): "blue"

[Tool completes: "User replied via Telegram: blue"]

Claude: "Perfect! Creating a blue submit button..."
```

### Example 2: File Processing

```
Claude: "Processing 1000 files..."

[calls notify_user_telegram: "Started processing..."]

→ Telegram: Notification sent

... (processing happens) ...

[calls confirm_with_user_telegram: "Found duplicates. Delete them?"]

→ Telegram: "🔧 [Cursor-ProjectB]
            Found duplicates. Delete them?
            [✅ Yes] [❌ No]"

User: *clicks Yes*

[Tool returns: "User confirmed"]

Claude: "Deleting duplicates..."

[calls notify_user_telegram: "Processing complete! Deleted 50 duplicates."]
```

## 🔧 Configuration

### Router Configuration

**Environment Variables** (`router/.env`):

```env
TELEGRAM_BOT_TOKEN=xxx           # Your Telegram bot token
TELEGRAM_CHAT_ID=xxx             # Your Telegram chat ID
ROUTER_PORT=8080                 # Router HTTP port
SESSION_CLEANUP_INTERVAL=300000  # Cleanup interval (ms)
SESSION_MAX_AGE=1800000          # Session max age (ms)
```

### MCP Client Configuration

**Environment Variables**:

```env
ROUTER_URL=http://localhost:8080  # Router URL
INSTANCE_NAME=VSCode-ProjectA     # Your instance name
CALLBACK_PORT=3001                # Your callback port
DEFAULT_TIMEOUT=300               # Default timeout (seconds)
```

**Python**:

```python
client = MCPTelegramClient(
    instance_name="My-Instance",
    callback_port=3001,
    router_url="http://localhost:8080"
)
```

## 📊 Monitoring

### Router Endpoints

- `GET /health` - Health check
- `GET /sessions` - List active sessions
- `GET /instances` - List registered instances

### Telegram Commands

- `/list` - Show active sessions
- `/stats` - Show router statistics
- `/help` - Show help message

### Example Usage

```bash
# Check router health
curl http://localhost:8080/health

# List sessions
curl http://localhost:8080/sessions

# List instances
curl http://localhost:8080/instances
```

## 🧪 Testing

### Run All Tests

```bash
cd tests
python test_script.py
```

### Run Specific Tests

```bash
# Single instance test
python test_script.py single

# Multiple instances test
python test_script.py multi

# Timeout test
python test_script.py timeout

# Threading test
python test_script.py threading

# Interactive test
python test_script.py interactive
```

## 🐛 Troubleshooting

### Router won't start

**Issue**: `Error: Cannot find module 'express'`

**Solution**:
```bash
cd router
npm install
```

### Client can't connect

**Issue**: `Failed to register with router`

**Solution**:
1. Ensure router is running
2. Check `ROUTER_URL` is correct
3. Check firewall settings

### Telegram not receiving messages

**Issue**: Messages not appearing in Telegram

**Solution**:
1. Verify `TELEGRAM_BOT_TOKEN` is correct
2. Verify `TELEGRAM_CHAT_ID` is correct
3. Start a conversation with your bot first
4. Check router logs for errors

### Timeout issues

**Issue**: Tool always times out

**Solution**:
1. Check router is running
2. Verify Telegram bot is working
3. Ensure you're replying to the correct message
4. Increase timeout if needed

## 📁 Project Structure

```
mcp-telegram-bidirectional/
├── router/
│   ├── telegram-router.js       # Central router
│   ├── package.json              # Node dependencies
│   └── .env.example              # Config template
├── mcp-client/
│   ├── mcp_telegram_client.py   # Client library
│   ├── telegram_feedback_tool.py # MCP tool
│   └── requirements.txt          # Python dependencies
├── tests/
│   └── test_script.py            # Test suite
├── memory/
│   └── bidirectional-telegram-mcp-implementation.md  # Full docs
└── README.md                     # This file
```

## 🤝 Contributing

This is a production-ready implementation. Feel free to:
- Report issues
- Suggest improvements
- Submit pull requests

## 📝 License

MIT License - Feel free to use in your projects!

## 🙏 Acknowledgments

Built with love for the MCP community!

---

**Need help?** Check the full documentation in `memory/bidirectional-telegram-mcp-implementation.md`

**Built**: October 5, 2025  
**Status**: ✅ Production Ready
