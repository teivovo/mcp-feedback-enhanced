# MCP Feedback Enhanced - Project Overview

## Project Purpose
Bidirectional feedback system connecting MCP (Model Context Protocol) tools with Telegram for remote interactive workflows. Enables AI assistants to request user feedback via Telegram and receive responses that are routed back to the correct MCP session.

## Core Architecture

### Components
1. **MCP Server** (`src/mcp_feedback_enhanced/`) - Python-based feedback server
2. **Telegram Router** (`router/telegram-router.js`) - Node.js message routing hub
3. **MCP Clients** (`mcp-client/`) - Python clients that connect MCP instances to router
4. **Web UI** (`src/mcp_feedback_enhanced/web/`) - Local browser interface for feedback

### Communication Flow
```
MCP Tool → Python Client → Router → Telegram → User
                                              ↓
                                         Reply via swipe
                                              ↓
User Reply → Router → Python Client → MCP Tool
```

## Image Upload Support

### Overview
Users can submit images with feedback via both MCP tool and Web GUI. Images are stored locally and accessible via URLs for LLM processing.

### Architecture
```
User uploads image → Backend saves to disk → Generates URL → LLM accesses via URL
                                          ↓
                                    Telegram displays image
```

### Technical Specifications
- **Supported Formats**: PNG, JPEG, GIF, WebP, BMP
- **Size Limit**: 10MB per image (enforced by router)
- **Storage Location**: `router/uploads/` directory
- **URL Format**: `http://localhost:8080/uploads/[uuid].png`
- **Filename Format**: UUID v4 + .png extension (e.g., `abc-123-def-456.png`)

### Usage Examples

#### MCP Tool (via Python Client)
```python
from mcp_telegram_client import MCPTelegramClient

client = MCPTelegramClient(instance_id="my-instance")
await client.start()

# Send notification with image
await client.send_notification(
    message="Check this screenshot",
    images=[image_base64]  # Base64-encoded image data
)

# Ask question with image
response = await client.send_and_wait_for_reply(
    message="Does this look correct?",
    images=[image_base64],
    timeout=300
)
```

#### Web GUI
1. Start web server: `uvx mcp-feedback-enhanced test --web`
2. Upload image via:
   - File picker (click upload button)
   - Drag and drop
   - Clipboard paste (Ctrl+V)
3. Submit feedback - image automatically included

### Backend Implementation
Images are processed by `WebFeedbackSession._process_images()`:
- Decodes base64 image data
- Saves to `router/uploads/` with UUID filename
- Generates accessible URL
- Returns both bytes (for MCP) and URL (for LLM)

### LLM Response Format
When images are included, the feedback text contains:
```
=== 圖片附件概要 ===
用戶提供了 1 張圖片：

  1. screenshot.png (12.3 KB)
     🔗 URL: http://localhost:8080/uploads/abc-123-def-456.png
     💡 LLM 可以直接訪問此 URL 查看圖片
     Base64 預覽: iVBORw0KGgoAAAANSUhEUgAAAA...
```

### File Cleanup
Implement periodic cleanup to prevent disk space issues:
```python
from pathlib import Path
import time

def cleanup_old_files(uploads_dir: Path, max_age_hours: int = 24):
    """Delete files older than max_age_hours"""
    cutoff_time = time.time() - (max_age_hours * 3600)
    for file in uploads_dir.glob("*.png"):
        if file.stat().st_mtime < cutoff_time:
            file.unlink()
```

### Troubleshooting

#### Images not appearing in Telegram
- **Check**: Router is running (`node telegram-router.js`)
- **Check**: Telegram bot token is valid in `router/.env`
- **Check**: Router console for error messages

#### URLs not accessible
- **Check**: Router is serving on port 8080
- **Check**: Firewall allows localhost:8080
- **Check**: Files exist in `router/uploads/` directory

#### Images too large
- **Solution**: Compress images before upload
- **Limit**: 10MB per image (router enforced)
- **Tool**: Use image compression tools or reduce resolution

#### Disk space issues
- **Solution**: Run cleanup function regularly
- **Monitor**: `router/uploads/` directory size
- **Automate**: Set up cron job for cleanup

## Critical File Locations

### Core Source Files
- **Message Template**: `src/mcp_feedback_enhanced/utils/telegram_manager.py`
  - `format_feedback_notification()` - Main message formatter (line ~750)
  - `send_session_end_notification()` - Session end messages (line ~880)
  
- **Router**: `router/telegram-router.js`
  - Message routing logic and session tracking
  - Reply-to-message detection
  
- **Session Management**: `src/mcp_feedback_enhanced/web/models/feedback_session.py`
  - WebFeedbackSession class handles cleanup and state
  - Triggers telegram notifications on timeout/error

### Test Scripts
- `tests/test_script.py` - Main testing entry point
  - `python tests/test_script.py single` - Test single instance
  - `python tests/test_script.py multi` - Test multiple instances
  - `python tests/test_script.py interactive` - Interactive mode

### Configuration
- `router/.env` - Telegram bot token and chat ID
- `.env.example` - Template for configuration
- `mcp_config.json` - MCP server configuration

## Development Tools & Commands

### Starting the Router
```powershell
cd router
npm install  # First time only
node telegram-router.js
```
**Port**: 8080 (HTTP API for MCP instances)

### Running Tests
```powershell
cd C:\Users\KelvinLAW\Documents\augment-projects\mcp-feedback-dev
$env:PYTHONIOENCODING="utf-8"  # CRITICAL: Prevents encoding errors
python tests/test_script.py single
```

### File Editing with Desktop Commander
- **Always use absolute paths** for reliability
- **Use edit_block** for surgical changes to specific sections
- **Use write_file with chunking** for new files (≤30 lines per chunk)
- Paths auto-normalize (forward/back slashes both work)

## Windows-Specific Issues

### Unicode/Encoding Errors
**Problem**: PowerShell uses cp1252 encoding, causing errors with emoji/unicode
**Solution**: Always set before running Python scripts:
```powershell
$env:PYTHONIOENCODING="utf-8"
```

### Port Already in Use
**Problem**: `EADDRINUSE: address already in use :::8080`
**Solution**: Router already running, use existing instance
**Check**: `netstat -ano | findstr :8080`

### Shell Operators
- PowerShell: Use `;` not `&&` for command chaining
- Commands: `cd path; command` works, `cd path && command` fails

## Message Format (Current Implementation)

### Standard Message
```
ProjectName

[work summary]
```

### Session End Notification
```
ProjectName

⏱️ Session ended: timeout
```

**What was removed** (October 2025):
- ❌ Datetime stamps (⏰ Oct 06, 03:23)
- ❌ File paths (📁 C:\path\to\project)
- ❌ Footer with session ID and links
- ❌ Truncation notes
- ❌ Reply button keyboards
- ❌ "What to do next" instructions
- ❌ `<blockquote>` tags (caused orange code blocks) - October 7, 2025

## Reply Handling

### How Replies Work
1. **Primary**: Reply-to-message metadata (swipe to reply in Telegram)
   - Router checks `msg.reply_to_message.message_id`
   - Maps to correct session via `messageThreads` Map
   
2. **Fallback**: Most recent session
   - If no reply-to detected, routes to last active session
   - Silent fallback (no warning message to user)

3. **Session Tracking**
   - Each message gets unique session_id
   - Router maintains `sessions` Map with session→instance mapping
   - Message log kept for all sent messages

## Testing Workflow

### Before Testing
1. Start router: `cd router && node telegram-router.js`
2. Verify router started (check "Ready to route messages! 🎯")
3. Set encoding: `$env:PYTHONIOENCODING="utf-8"`

### Single Instance Test
```powershell
python tests/test_script.py single
```
**What it tests**: Basic send→reply→route cycle

### Multiple Instance Test
```powershell
python tests/test_script.py multi
```
**What it tests**: 
- 3 instances send messages simultaneously
- Reply routing works correctly per instance
- No cross-talk between sessions

### Verification Checklist
- ✅ Messages appear in Telegram with correct format
- ✅ Replying to specific message routes to correct instance
- ✅ Router logs show "✅ Successfully delivered"
- ✅ Test script shows "✅ Received: [response]"

## Common Workflows

### Adding New Message Types
1. Edit `telegram_manager.py::format_feedback_notification()`
2. Keep HTML escape for user content: `html.escape(text)`
3. Test with `test_script.py single`

### Modifying Router Behavior
1. Edit `router/telegram-router.js`
2. Restart router (Ctrl+C, then restart)
3. Router doesn't require npm install after code changes

### Session Cleanup Notifications
Location: `feedback_session.py` line ~800
Triggers on: TIMEOUT, EXPIRED, ERROR cleanup reasons
Sends via: `send_session_end_notification()`

## Project Structure
```
mcp-feedback-dev/
├── src/mcp_feedback_enhanced/
│   ├── utils/
│   │   └── telegram_manager.py          # Message formatting
│   ├── web/
│   │   └── models/
│   │       └── feedback_session.py      # Session management
│   └── ...
├── router/
│   ├── telegram-router.js               # Core routing logic
│   ├── .env                             # Bot config
│   └── package.json
├── mcp-client/
│   ├── mcp_telegram_client.py           # MCP→Router client
│   └── telegram_feedback_tool.py
├── tests/
│   └── test_script.py                   # Main test suite
└── TELEGRAM_TEMPLATE_CHANGES.md         # Recent changes doc
```

## Key Design Decisions

### Why Router + Clients Architecture?
- Multiple MCP instances can share one Telegram bot
- Router handles session multiplexing
- Clients register with router, get unique callback URLs

### Why No Reply Buttons?
- Native Telegram reply (swipe) provides better UX
- Reply-to metadata includes full message context
- Reduces message clutter
- Message log provides session tracking fallback

### Why Session End Notifications?
- User knows when MCP tool timed out
- Prevents confusion about why no response
- Simple notification doesn't clutter conversation

## Recent Changes (October 2025)
See `TELEGRAM_TEMPLATE_CHANGES.md` for detailed changelog.

**Summary:**
- Simplified message format (removed metadata overhead)
- Removed reply button keyboards
- Native Telegram reply handling via metadata
- Added session end notifications
- Router falls back silently to most recent session

## Troubleshooting

### "Router not responding"
1. Check if router running: `netstat -ano | findstr :8080`
2. Restart router: `cd router && node telegram-router.js`
3. Verify Telegram bot token in `router/.env`

### "Encoding errors in test output"
```powershell
$env:PYTHONIOENCODING="utf-8"
```
Add this to every PowerShell session before running tests.

### "Reply went to wrong instance"
- Check if you used Telegram reply feature (swipe)
- Router logs show which session was used
- Verify `messageThreads` mapping in router

### "Message format looks wrong"
- Check `telegram_manager.py` line ~780
- Verify HTML escaping: `html.escape(text)`
- Test changes with `test_script.py single`

## Development Notes

### When Editing Python Files
- Use Desktop Commander's `edit_block` tool
- Always include exact whitespace in `old_string`
- Test changes before committing

### When Editing JavaScript Files  
- Router changes require restart
- No build step needed
- Check syntax with router startup logs

### Adding Features
1. Update relevant source files
2. Update this PROJECT_OVERVIEW.md
3. Add tests to `test_script.py` if needed
4. Document in TELEGRAM_TEMPLATE_CHANGES.md

## Contact Points for AI Assistants

**User Preference**: Kelvin prefers direct, actionable guidance. Skip verbose explanations unless specifically requested.

**Project Base**: `C:\Users\KelvinLAW\Documents\augment-projects\mcp-feedback-dev`

**Always Remember**:
- Set UTF-8 encoding before Python commands
- Use absolute paths with Desktop Commander
- Router must be running for tests
- Check message format in Telegram after changes
