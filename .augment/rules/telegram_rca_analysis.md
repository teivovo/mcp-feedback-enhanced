# 🔍 Root Cause Analysis: Telegram Notifications Not Working from MCP Tool Calls

**Date:** October 5, 2025  
**Issue:** Test messages work, but MCP tool call notifications don't reach Telegram  
**Methodology:** 5 Whys + Atomic Execution Trace  
**Status:** 🔴 ROOT CAUSE IDENTIFIED

---

## Executive Summary

**Problem:** User receives Telegram test messages from Web UI but NOT from MCP tool calls  
**Root Cause:** Config Manager only initialized when `MCP_DEBUG=true`, causing production mode to fail  
**Impact:** 100% failure of Telegram notifications in production (non-debug) mode  
**Fix Complexity:** Simple (move 3 lines of code outside debug block)

---

## Symptom Analysis

### ✅ What Works
- Test connection button in Web UI → Telegram message received
- Web UI launches successfully
- MCP tool calls execute
- Feedback collection works

### ❌ What Doesn't Work
- MCP tool calls → NO Telegram message
- `interactive_feedback()` executes but silent on Telegram
- No errors visible to user

### 🤔 Key Observation
**Same Telegram credentials work in one path but not the other**

---

## Atomic Execution Trace

### Path 1: Test Message (Working ✅)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEST MESSAGE EXECUTION TRACE                      │
└─────────────────────────────────────────────────────────────────────┘

STEP 1: User clicks "Test Connection" in Web UI
  ├─ Browser sends: POST /telegram/api/test-connection
  └─ Target: telegram_routes.py:test_telegram_connection()

STEP 2: Web UI starts (context: Web server already running)
  ├─ File: web/main.py:WebUIManager.__init__()
  ├─ FastAPI app created
  ├─ Routes loaded (including telegram_routes.py)
  └─ Server listening on port 8765

STEP 3: telegram_routes.py receives request
  ├─ File: web/routes/telegram_routes.py
  ├─ Function: test_telegram_connection()
  └─ Code:
      ```python
      @router.post("/api/test-connection")
      async def test_telegram_connection():
          if not is_telegram_enabled():  # <-- FIRST CHECK
              raise HTTPException(503, "Not configured")
      ```

STEP 4: Check if Telegram enabled
  ├─ Function: is_telegram_enabled()
  ├─ File: utils/config_manager.py:706
  └─ Code:
      ```python
      def is_telegram_enabled() -> bool:
          manager = get_config_manager()  # <-- GET GLOBAL INSTANCE
          return manager.is_telegram_enabled() if manager else False
      ```

STEP 5: Get config manager instance
  ├─ Function: get_config_manager()
  ├─ File: utils/config_manager.py:691
  └─ Code:
      ```python
      _global_config_manager: Optional[ConfigManager] = None
      
      def get_config_manager() -> Optional[ConfigManager]:
          return _global_config_manager
      ```

❓ QUESTION: Was _global_config_manager initialized?
  
STEP 6: Check Web UI startup initialization
  ├─ Searching: web/ directory for initialize_config_manager
  ├─ Result: NO matches found
  └─ Conclusion: Web UI does NOT initialize config manager

🔴 CRITICAL: If Web UI doesn't initialize config_manager, how does test work?

STEP 7: Alternative path - Environment variables!
  ├─ File: utils/config_manager.py:ConfigManager.is_telegram_enabled()
  ├─ Priority order: Environment > Config File > Defaults
  └─ Code examination needed...
```

Let me check how config manager loads Telegram config:

<function_calls>
<invoke name="desktop-commander:read_file">
<parameter name="path">C:\Users\KelvinLAW\Documents\augment-projects\mcp-feedback-dev\src\mcp_feedback_enhanced\utils\config_manager.py