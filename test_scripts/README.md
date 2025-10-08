# MCP Tool Test Scripts

This directory contains scripts to test MCP tool functionality without needing an IDE.

## Purpose

These scripts allow you to:
- **Test the MCP tool directly** - Call `interactive_feedback()` without going through Claude/IDE
- **Debug Telegram notifications** - Verify Telegram integration works independently  
- **Rapid iteration** - Test changes without restarting the IDE
- **CI/CD integration** - Automate testing in pipelines

## Files

### `test_mcp_tool.py`

Main test script that can run in two modes:

1. **Telegram Test** (default, fast)
   - Tests only Telegram notification sending
   - Doesn't open web UI
   - Quick verification (~2 seconds)

2. **Full Test** (complete workflow)
   - Tests entire `interactive_feedback()` function
   - Opens web UI
   - Creates session and waits for feedback
   - Complete end-to-end test

## Usage

### Quick Start (Telegram Test)

```bash
# From project root
python test_scripts/test_mcp_tool.py
```

This sends a test notification to Telegram and confirms it works.

### Full Tool Test

```bash
# Test complete MCP tool workflow
python test_scripts/test_mcp_tool.py --full
```

This:
1. Initializes config manager
2. Sends Telegram notification
3. Opens web UI for feedback
4. Returns MCP tool response

### All Options

```bash
# Telegram test only (explicit)
python test_scripts/test_mcp_tool.py --telegram

# Full MCP tool test
python test_scripts/test_mcp_tool.py --full

# Help
python test_scripts/test_mcp_tool.py --help
```

## What Gets Tested

### Telegram Test Mode
- ✅ Config manager initialization
- ✅ Telegram configuration validation  
- ✅ Message formatting (Markdown/HTML)
- ✅ API connection to Telegram
- ✅ Notification delivery

### Full Test Mode
All of the above, plus:
- ✅ Web UI server startup
- ✅ Session creation
- ✅ Browser opening
- ✅ Complete MCP tool return flow

## Prerequisites

### 1. Telegram Configuration

Edit `mcp_config.json` in project root:

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  }
}
```

Get these from:
- **bot_token**: [@BotFather](https://t.me/botfather) on Telegram
- **chat_id**: [@userinfobot](https://t.me/userinfobot) or [@RawDataBot](https://t.me/RawDataBot)

### 2. Python Environment

```bash
# Make sure you're in the project root
cd C:\Users\KelvinLAW\Documents\augment-projects\mcp-feedback-dev

# Activate virtual environment (if using one)
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e .
```

## Output

### Successful Telegram Test

```
================================================================================
Initializing Test Environment
================================================================================

✅ Config manager module imported
📄 Config path: C:\...\mcp_config.json
✅ Config manager initialized
📱 Telegram enabled: True
✅ Telegram is properly configured

================================================================================
Telegram Notification Test
================================================================================

✅ telegram_manager imported
📱 Sending test notification...
   Project: C:\...\mcp-feedback-dev
   Summary length: 289 chars

================================================================================
✅ SUCCESS! Notification sent to Telegram
================================================================================

📱 Check your Telegram app now!
📄 Check telegram_diagnostic.log for details
```

### Failed Test

```
❌ FAILED - Notification not sent

🔍 Check telegram_diagnostic.log for error details
```

## Debugging

### Check Logs

1. **Telegram operations**: `telegram_diagnostic.log` (project root)
2. **General logs**: `logs/` directory

### Common Issues

**Telegram disabled**
```bash
# Check config
cat mcp_config.json | grep -A 5 telegram

# Verify bot token and chat_id are set
```

**Import errors**
```bash
# Make sure you're in project root
pwd

# Reinstall package
pip install -e .
```

**Config not found**
```bash
# Make sure mcp_config.json exists in project root
ls -la mcp_config.json
```

## How It Works

The test script:

1. **Sets up Python path** - Adds `src/` so it can import the MCP module
2. **Initializes config** - Loads `mcp_config.json` and sets up config manager
3. **Validates Telegram** - Checks that bot_token and chat_id are configured
4. **Calls MCP function** - Either:
   - `send_telegram_notification()` for quick test
   - `interactive_feedback()` for full test
5. **Reports results** - Shows success/failure with diagnostic info

## Integration with IDE

These tests verify the same functionality that the IDE uses when it calls the MCP tool:

```
IDE (Claude.app)
    ↓
MCP Client
    ↓
MCP Server (your code)
    ↓
interactive_feedback()
    ↓
Telegram Notification
```

The test script skips the IDE/MCP Client layers and calls the server code directly.

## When to Use

### Use Telegram Test When:
- 🔄 Iterating on Telegram message formatting
- 🐛 Debugging notification issues
- ⚡ Quick verification after code changes
- 📱 Testing bot token / chat_id configuration

### Use Full Test When:
- 🔍 Debugging complete workflow
- 🌐 Testing web UI integration
- 📊 Verifying session management
- 🎯 End-to-end validation before deployment

## CI/CD Integration

Add to your workflow:

```yaml
# .github/workflows/test.yml
- name: Test MCP Tool
  run: python test_scripts/test_mcp_tool.py --telegram
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

## Advanced Usage

### Custom Test Messages

Edit the `summary` variable in `test_telegram_notification()` or `test_interactive_feedback()` to send different test messages.

### Testing Different Configs

```bash
# Point to different config
export MCP_CONFIG_PATH=/path/to/other/config.json
python test_scripts/test_mcp_tool.py
```

### Debugging Mode

The script already sets `MCP_DEBUG=true` environment variable for verbose logging.

## Next Steps

After running tests:

1. ✅ Verify Telegram notification received
2. ✅ Check `telegram_diagnostic.log` for execution trace
3. ✅ If full test: Interact with web UI
4. ✅ Make changes to your code
5. ✅ Run tests again to verify

---

**Questions?** Check the main project README or open an issue.
