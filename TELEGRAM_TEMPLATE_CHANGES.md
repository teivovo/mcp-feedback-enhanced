# Telegram Message Template Changes

## Summary of Changes

### 1. Message Format Simplification (`telegram_manager.py`)

**Before:**
```
🔔 Feedback Request • ProjectName

📁 C:\path\to\project
⏰ Oct 06, 03:23

━━━━━━━━━━━━━━━━━━━━

📝 AI Work Summary:

[summary]

(Summary truncated. See full details in UI)

━━━━━━━━━━━━━━━━━━━━

✅ What to do next:
  • Review the changes in the feedback interface
  • Provide approval or request modifications
  • Upload screenshots if clarification needed

🔗 Open Feedback Interface (http://127.0.0.1:8779/)

Session ID: mcp_session_1759692214
```

**After:**
```
ProjectName

[summary]
```

### 1.1 Orange Code Block Fix (October 7, 2025)

**Issue:** Messages were appearing in orange code blocks in Telegram

**Root Cause:** The `<blockquote>` HTML tag renders as an orange code block in Telegram

**Fix:** Removed `<blockquote>` tags from message formatting

**Before:**
```python
message = f"""<b>{safe_project}</b>

<blockquote>{safe_summary}</blockquote>"""
```

**After:**
```python
message = f"""<b>{safe_project}</b>

{safe_summary}"""
```

**Result:** Messages now display with clean formatting, no orange blocks

### 2. Reply Handling (`telegram-router.js`)

**Changes:**
- ✅ Removed reply button keyboard
- ✅ Removed button callback handlers
- ✅ Uses native Telegram reply-to-message metadata
- ✅ Falls back to last message if no reply detected

**How it works now:**
1. User receives telegram message with work summary
2. User swipes to reply (standard Telegram reply)
3. Router detects `reply_to_message` metadata
4. Routes response to correct session automatically

### 3. Session End Notifications (`telegram_manager.py` + `feedback_session.py`)

**New Feature:**
When MCP tool session ends (timeout, expired, error), users receive:
```
ProjectName

⏱️ Session ended: timeout
```

**Implementation:**
- Added `send_session_end_notification()` function
- Integrated into session cleanup method
- Triggers on: TIMEOUT, EXPIRED, ERROR

## Files Modified

1. `src/mcp_feedback_enhanced/utils/telegram_manager.py`
   - Simplified `format_feedback_notification()` 
   - Added `send_session_end_notification()`

2. `router/telegram-router.js`
   - Removed reply button from message sending
   - Removed `getDefaultKeyboard()` function
   - Simplified callback query handler

3. `src/mcp_feedback_enhanced/web/models/feedback_session.py`
   - Added telegram notification on session cleanup
   - Triggers for timeout/expired/error reasons

## Benefits

✅ Cleaner, more readable messages
✅ Native Telegram reply experience
✅ Automatic session tracking via message metadata
✅ User notification when sessions end
✅ No chunking artifacts (messages already support multi-part)
