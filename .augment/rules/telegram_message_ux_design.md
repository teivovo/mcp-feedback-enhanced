# Telegram Notification Message UX Design
**Research & Proposal for MCP Feedback Enhanced**

---

## 📊 Telegram Formatting Constraints (Research Summary)

### Hard Limits
- **Max Length:** 4096 UTF-8 characters per message
- **Rate Limits:** 30 msgs/sec global, 20 msgs/min per group
- **File Size:** 2000 MB (if using sendDocument)

### Supported Formatting (HTML Mode - Recommended)

✅ **Supported:**
```html
<b>bold</b> or <strong>bold</strong>
<i>italic</i> or <em>italic</em>
<u>underline</u>
<s>strikethrough</s>
<code>inline code</code>
<pre>multiline code block</pre>
<pre><code class="python">syntax-highlighted code</code></pre>
<a href="url">hyperlink</a>
<blockquote>quoted text</blockquote>
```

✅ **Emojis:** Full Unicode support (🔔 ✅ ❌ 📁 📝 ⏰ 🤖 etc.)

❌ **NOT Supported:**
- Colors/custom styling
- Headers (H1-H6)
- Bullet/numbered lists (must use unicode: • ‣ ⦿)
- Tables (must use monospace or send as image)
- Horizontal rules
- Nested formatting restrictions

### Best Practices from Research
1. **Use HTML mode** (not MarkdownV2) - easier, fewer escaping issues
2. **Chunk messages** at natural boundaries (sentences/paragraphs)
3. **Emojis for visual hierarchy** (since no colors)
4. **Monospace for data** (`<code>` or `<pre>`)
5. **Links for actions** (e.g., "Open Web UI")

---

## 🎯 UX Design Goals

1. **Immediate Recognition:** User knows which project without reading details
2. **Scannable:** Key info visible at a glance
3. **Actionable:** Clear next steps
4. **Complete:** Match GUI content (AI summary shown)
5. **Mobile-Friendly:** Readable on phone notification
6. **Multi-Project:** Works when user has 5+ projects active

---

## 📱 Proposed Message Format

### Format A: Compact Header (Recommended)

```
🔔 <b>Feedback Request</b> • Project: <code>mcp-feedback-dev</code>

📁 <code>/Users/kelvin/projects/mcp-feedback-dev</code>
⏰ 2025-10-05 14:32:15

<blockquote>
<b>AI Summary:</b>
I've completed implementing the Telegram notification system. The test connection works successfully and messages are being delivered to your Telegram chat. Ready for your review and feedback.
</blockquote>

<b>Actions:</b>
• Open Web UI to provide feedback
• Reply in UI with text, images, or commands
• Session ID: <code>mcp_session_1728140735</code>

<a href="http://127.0.0.1:8765">👉 Open Feedback Interface</a>
```

**Breakdown:**
- **Line 1:** Emoji + bold type + project name in code (stands out)
- **Line 2-3:** Full path + timestamp (context)
- **Line 4-8:** AI summary in blockquote (matches GUI main content)
- **Line 9-12:** Action items with bullets
- **Line 13:** Clickable link to open UI

**Character Count:** ~450 chars (plenty of headroom)

---

### Format B: Visual Hierarchy (More Emojis)

```
🤖 <b>New Feedback Request</b>

📂 <b>Project:</b> <code>mcp-feedback-dev</code>
📍 <code>/Users/kelvin/projects/mcp-feedback-dev</code>
🕐 <code>2025-10-05 14:32:15</code>

━━━━━━━━━━━━━━━━━━━━━━

📝 <b>What AI Completed:</b>

<i>I've completed implementing the Telegram notification system. The test connection works successfully and messages are being delivered to your Telegram chat. Ready for your review and feedback.</i>

━━━━━━━━━━━━━━━━━━━━━━

✅ <b>Next Steps:</b>
  ‣ Open the web interface
  ‣ Provide your feedback
  ‣ Upload images if needed
  ‣ Execute verification commands

🔗 <a href="http://127.0.0.1:8765">Click here to respond</a>

<code>Session: mcp_session_1728140735</code>
```

**Character Count:** ~550 chars

**Pros:** More visual separation, very scannable
**Cons:** More vertical space, might feel cluttered

---

### Format C: Minimal (Push Notification Style)

```
🔔 <b>mcp-feedback-dev</b> needs your feedback

<i>"I've completed implementing the Telegram notification system. Ready for review."</i>

<a href="http://127.0.0.1:8765">Open Feedback UI</a> • <code>Session: ...0735</code>
```

**Character Count:** ~180 chars

**Pros:** Perfect for push notifications, instant comprehension
**Cons:** Missing context (path, timestamp, full summary)

---

## 🏆 Recommended Format: Hybrid Approach

Combine Format A structure with Format B's visual clarity:

```html
🔔 <b>Feedback Request</b> • <code>mcp-feedback-dev</code>

📁 <code>/Users/kelvin/projects/mcp-feedback-dev</code>
⏰ <code>Oct 05, 14:32</code>

━━━━━━━━━━━━━━━━━━━━

<b>📝 AI Work Summary:</b>

<blockquote>
I've completed implementing the Telegram notification system. The test connection works successfully and messages are being delivered to your Telegram chat. Ready for your review and feedback.
</blockquote>

━━━━━━━━━━━━━━━━━━━━

<b>✅ What to do next:</b>
  • Review the changes in the feedback interface
  • Provide approval or request modifications
  • Upload screenshots if clarification needed

🔗 <a href="http://127.0.0.1:8765">Open Feedback Interface</a>

<code>Session ID: mcp_session_1728140735</code>
```

---

## 🎨 Implementation Details

### 1. Project Name Extraction
```python
# From full path: /Users/kelvin/projects/mcp-feedback-dev
project_name = Path(project_directory).name  # → "mcp-feedback-dev"

# Or from last 2 segments for clarity:
parts = Path(project_directory).parts
project_identifier = f"{parts[-2]}/{parts[-1]}"  # → "projects/mcp-feedback-dev"
```

### 2. Timestamp Formatting
```python
from datetime import datetime

# User-friendly format (not ISO)
timestamp = datetime.now().strftime("%b %d, %H:%M")  # → "Oct 05, 14:32"

# Or with timezone if user works across zones
timestamp = datetime.now().astimezone().strftime("%b %d, %H:%M %Z")
# → "Oct 05, 14:32 SGT"
```

### 3. Summary Truncation (if >4096 chars)
```python
MAX_LENGTH = 4096
RESERVED_SPACE = 800  # For header, footer, formatting
MAX_SUMMARY = MAX_LENGTH - RESERVED_SPACE  # 3296 chars

if len(summary) > MAX_SUMMARY:
    summary = summary[:MAX_SUMMARY-3] + "..."
    # Add note: "(truncated, see full summary in UI)"
```

### 4. URL Generation
```python
# Detect environment
if is_wsl_environment():
    # WSL: Use Windows localhost
    url = "http://localhost:8765"
elif is_remote_environment():
    # SSH Remote: Use remote IP or tunneled port
    url = f"http://{server_ip}:8765"
else:
    # Local
    url = f"http://127.0.0.1:{port}"

# Add session param for direct navigation
url += f"?session={session_id}"
```

### 5. HTML Escaping
```python
import html

def escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram"""
    return html.escape(text)

# Usage:
safe_summary = escape_html(summary)
safe_project_path = escape_html(project_directory)
```

---

## 📋 Message Components Checklist

### Must Have (Critical Info)
- [x] Project identifier (name)
- [x] AI summary (main content from GUI)
- [x] Actionable link to open UI
- [x] Timestamp (when feedback requested)

### Should Have (Context)
- [x] Full project path (disambiguation)
- [x] Session ID (troubleshooting)
- [x] Next steps guidance
- [x] Emojis for visual hierarchy

### Nice to Have (Enhanced UX)
- [x] Separator lines (readability)
- [x] Blockquote for summary (emphasis)
- [x] Code formatting for tech terms
- [ ] Preview of files changed (if applicable)
- [ ] Estimated time to review
- [ ] Priority indicator

### Skip (Out of Scope)
- [ ] Inline buttons (requires reply_markup, complicates flow)
- [ ] Images (not needed for notification, shown in GUI)
- [ ] Custom emojis (requires Telegram Premium)
- [ ] Reactions (not supported in bot messages)

---

## 🧪 Testing Matrix

### Test Cases

| Scenario | Expected Behavior | Edge Case |
|----------|------------------|-----------|
| **Short summary (<100 chars)** | Display fully | ✅ Normal |
| **Long summary (>3000 chars)** | Truncate with "..." + note | ⚠️ Handle gracefully |
| **Special chars in path** | Escape properly (`&`, `<`, `>`) | ⚠️ Test |
| **Multiple projects running** | Project name clearly differentiated | ✅ Critical |
| **WSL environment** | URL uses correct hostname | ⚠️ Test |
| **Non-ASCII project names** | UTF-8 display correctly | ⚠️ Test |
| **Very long project path** | Truncate or wrap | ⚠️ Handle |
| **Quick succession (2 projects)** | Both messages arrive in order | ✅ Rate limit aware |

---

## 🔧 Implementation Code Template

```python
# File: utils/telegram_manager.py

def format_feedback_notification(
    summary: str,
    project_directory: str,
    session_id: str,
    web_ui_url: str,
) -> str:
    """
    Format MCP feedback request notification for Telegram.
    
    Uses HTML parse mode for rich formatting.
    Matches GUI content while being mobile-friendly.
    """
    import html
    from datetime import datetime
    from pathlib import Path
    
    # Extract project name
    project_name = Path(project_directory).name
    
    # Format timestamp
    timestamp = datetime.now().strftime("%b %d, %H:%M")
    
    # Escape HTML special characters
    safe_summary = html.escape(summary)
    safe_path = html.escape(project_directory)
    safe_session = html.escape(session_id)
    
    # Truncate summary if needed
    MAX_SUMMARY_LENGTH = 3000
    if len(safe_summary) > MAX_SUMMARY_LENGTH:
        safe_summary = safe_summary[:MAX_SUMMARY_LENGTH-3] + "..."
        truncation_note = "\n<i>(Summary truncated. See full details in UI)</i>"
    else:
        truncation_note = ""
    
    # Build message
    message = f"""🔔 <b>Feedback Request</b> • <code>{html.escape(project_name)}</code>

📁 <code>{safe_path}</code>
⏰ <code>{timestamp}</code>

━━━━━━━━━━━━━━━━━━━━

<b>📝 AI Work Summary:</b>

<blockquote>
{safe_summary}{truncation_note}
</blockquote>

━━━━━━━━━━━━━━━━━━━━

<b>✅ What to do next:</b>
  • Review the changes in the feedback interface
  • Provide approval or request modifications
  • Upload screenshots if clarification needed

🔗 <a href="{web_ui_url}">Open Feedback Interface</a>

<code>Session ID: {safe_session}</code>"""
    
    return message


async def send_telegram_notification(
    summary: str,
    project_directory: str
) -> bool:
    """
    Send formatted notification to Telegram.
    
    This matches the content shown in the GUI and provides
    clear context for multi-project scenarios.
    """
    try:
        from ..utils.config_manager import is_telegram_enabled, get_telegram_config
        
        if not is_telegram_enabled():
            debug_log("Telegram notifications disabled")
            return False
        
        config = get_telegram_config()
        if not config or not config.chat_id or not config.bot_token:
            debug_log("Telegram configuration incomplete")
            return False
        
        # Generate session ID (same as in server.py)
        session_id = f"mcp_session_{int(time.time())}"
        
        # Get Web UI URL (from web manager or config)
        from ..web import get_web_ui_manager
        web_manager = get_web_ui_manager()
        if web_manager:
            web_ui_url = f"http://{web_manager.host}:{web_manager.port}"
        else:
            # Fallback
            web_ui_url = "http://127.0.0.1:8765"
        
        # Format message
        message = format_feedback_notification(
            summary=summary,
            project_directory=project_directory,
            session_id=session_id,
            web_ui_url=web_ui_url
        )
        
        # Send via Telegram Bot Manager
        async with TelegramBotManager(config.bot_token, config.chat_id) as bot:
            result = await bot.send_message(
                message,
                parse_mode="HTML"  # ← Use HTML mode!
            )
        
        if result:
            debug_log(f"Telegram notification sent: message_id={result.get('message_id')}")
            return True
        else:
            debug_log("Telegram notification failed: no result")
            return False
    
    except Exception as e:
        debug_log(f"Telegram notification error: {e}")
        return False
```

---

## 📱 Mobile Notification Preview

When user receives on phone:

```
┌─────────────────────────────────┐
│ MCP Feedback Bot             🔔 │
├─────────────────────────────────┤
│                                 │
│ 🔔 Feedback Request •           │
│    mcp-feedback-dev             │
│                                 │
│ 📁 /Users/kelvin/projects/...   │
│ ⏰ Oct 05, 14:32                │
│                                 │
│ ━━━━━━━━━━━━━━━━━━━━━          │
│                                 │
│ 📝 AI Work Summary:             │
│                                 │
│ │ I've completed implementing   │
│ │ the Telegram notification...  │
│                                 │
│ [Tap to expand]                 │
└─────────────────────────────────┘
```

**On tap:**
- Full message opens
- Link is clickable
- Can copy session ID

---

## ✅ Final Recommendation

**Use the Hybrid Format (shown above) because:**

1. **Immediate Project ID:** Project name in first line
2. **Complete Context:** Path + timestamp for multi-project work
3. **GUI Content Match:** Blockquoted summary = what user sees in web UI
4. **Actionable:** Clear link to open interface
5. **Professional:** Clean, scannable, not cluttered
6. **Telegram-Native:** Uses HTML mode, proper escaping, respects limits
7. **Mobile-Friendly:** Readable in push notification preview

**Character Budget:**
- Header: ~150 chars
- Summary: ~3000 chars available (handles most use cases)
- Footer: ~200 chars
- **Total:** Safely under 4096 limit with room for long summaries

---

## 🚀 Next Steps

1. **Implement** `format_feedback_notification()` function
2. **Update** `send_telegram_notification()` to use HTML mode
3. **Test** with multiple projects simultaneously
4. **Verify** HTML escaping works with special characters
5. **Validate** on actual Telegram mobile app
6. **Measure** user satisfaction (does it help or distract?)

**Ready to implement?**
