---
type: "agent_requested"
description: "Procedure to restart MCP server and Feedback Tool with user assistance for the purpose of testing code changes"
---

## MCP Server Restart Protocol

When you make code changes that require an MCP server restart, follow this exact sequence:

### Pre-Restart Phase

**Step 0: Notify User via Feedback Tool**
- Call `interactive_feedback_mcp-feedback-enhanced` with:
  - `timeout`: 86400 (24 hours)
  - `summary`: Detailed explanation including:
    - What changes were applied (file paths, specific modifications)
    - Rationale for each change
    - Expected behavior after restart
    - Explicit request: "Please restart your MCP server (close and reopen your IDE/editor)"

### Restart Detection Phase

**Step 1: Monitor for Connection Close**
- After calling the Feedback tool, watch for the error: `Tool execution failed: MCP error -32000: Connection closed`
- This error indicates the user has restarted the MCP server
- Do NOT attempt any tool calls while waiting for this signal

**Step 2: Wait for Server Initialization**
- Once connection close is detected, call `sleep_Sleep_MCP` with `seconds: 10`
- If the sleep call fails with an error or shows tool unavailability:
  - Retry up to 10 times with 1-second intervals between attempts
  - Each retry should call `sleep_Sleep_MCP` with `seconds: 10`
- Wait for the full 10-second sleep duration to complete

### Verification Phase

**Step 3: Test New Server with Feedback Tool**
- After the 10-second wait, call `interactive_feedback_mcp-feedback-enhanced` again with:
  - `timeout`: 86400 (24 hours)
  - `summary`: "Testing server restart - please confirm the changes are working as expected. [Describe what to test]"

**Step 4: Handle Verification Results**

**If the Feedback tool call SUCCEEDS:**
- Proceed to Step 5 (Success Path)

**If the Feedback tool call FAILS:**
- This indicates your code changes caused startup errors
- Follow the Error Recovery Path (Steps 4a-4e)

### Error Recovery Path

**Step 4a: Investigate Logs**
- Check MCP debug logs in `logs/mcp_debug_*.log`
- Look for Python tracebacks, import errors, syntax errors
- Identify the exact file and line number causing the failure
- Base your analysis on EVIDENCE from logs, not assumptions

**Step 4b: Apply Fixes**
- Fix the identified errors in the code
- Commit the fixes with a descriptive message
- Document what was wrong and how it was fixed

**Step 4c: Notify User (Without Feedback Tool)**
- Print a contextual response directly in the conversation (not via Feedback tool since it's broken)
- Explain: "The server failed to start due to [specific error]. I've applied fixes to [files]. Please restart your MCP server again."

**Step 4d: Wait for User Restart**
- Call `sleep_Sleep_MCP` with `seconds: 180` (3 minutes)
- Monitor for connection close during this sleep period
- If connection closes before 3 minutes, the user has restarted

**Step 4e: Repeat Verification**
- When sleep completes or connection closes, return to Step 2 (Wait for Server Initialization)
- Continue the cycle until the Feedback tool call succeeds

### Success Path

**Step 5: Confirm Changes Are Active**
- The Feedback tool is now running with your latest changes
- The web GUI should reflect all modifications
- Wait for user feedback via:
  - Web GUI interface
  - Telegram (if integrated)
  - Direct text response in the Feedback tool

**Step 6: Validate Expected Behavior**
- Guide the user through testing the specific changes
- Confirm the fix/feature works as intended
- Address any issues or unexpected behavior

### Important Notes

- **Always use 86400 seconds (24 hours) timeout** for Feedback tool calls
- **Never assume** - always check logs for actual errors
- **Be patient** - Server restart can take 5-15 seconds
- **Connection close is the signal** - Don't proceed until you see it
- **Sleep tool failures are normal** during restart - retry up to 10 times
- **If stuck in error loop** - Ask user to manually check server logs and report errors