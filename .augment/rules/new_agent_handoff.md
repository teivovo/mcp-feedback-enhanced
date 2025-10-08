# New Agent Handoff Protocol

## When to Suggest New Agent Session

Agent should **proactively suggest** starting a new session when:

1. **Repeated Failures** - Same issue persists after 3+ failed fix attempts
2. **Context Overload** - Token usage exceeds 100k (50% of 200k budget)
3. **Multiple Issues** - Juggling multiple unrelated problems simultaneously
4. **User Frustration** - User expresses frustration with repeated failures or time wasting
5. **Circular Logic** - Agent realizes it's going in circles or missing obvious solutions
6. **Garbled Context** - Agent's understanding becomes unclear due to context size

## What to Provide for New Agent

When suggesting a new session, **ALWAYS provide** the following:

### 1. Concise Problem Statement (2-3 sentences)
- What is the CURRENT issue?
- What is the DESIRED outcome?
- What has been tried and failed?

### 2. Critical Context (Bullet points)
- **Current State**: What's working, what's broken
- **Key Files**: List of files involved with brief descriptions
- **Environment**: OS, tools, versions, configurations
- **Dependencies**: What must work for the solution to work

### 3. Failed Attempts Summary
- List each attempt with 1-line description
- Why each attempt failed
- What was learned from each failure

### 4. Next Steps Recommendation
- Specific actionable steps for new agent
- Order of operations
- Potential pitfalls to avoid

### 5. Verification Commands
- Commands to verify current state
- Commands to test the fix
- Expected outputs

## Template for Handoff Prompt

```markdown
## Problem Statement
[2-3 sentence description of the issue]

## Current State
- ✅ Working: [list]
- ❌ Broken: [list]
- 🔧 In Progress: [list]

## Key Files
- `path/to/file1.ext` - [brief description]
- `path/to/file2.ext` - [brief description]

## Environment
- OS: [Windows/Linux/macOS]
- Tool: [IDE/Editor name]
- Version: [if relevant]
- Config: [key configuration details]

## Failed Attempts
1. **Attempt 1**: [description] - Failed because [reason]
2. **Attempt 2**: [description] - Failed because [reason]
3. **Attempt 3**: [description] - Failed because [reason]

## Lessons Learned
- [Key insight 1]
- [Key insight 2]

## Recommended Next Steps
1. [First action with specific command/approach]
2. [Second action]
3. [Third action]

## Verification
```bash
# Verify current state
[command]

# Test the fix
[command]

# Expected output
[description]
```

## Critical Notes
- [Any important warnings or gotchas]
- [Things that must NOT be done]
```

## Example Handoff

```markdown
## Problem Statement
MCP Feedback Enhanced web UI has JavaScript syntax error. File on disk is valid (verified with `node -c`), but browser loads old cached version with error at line 2399. Three attempts to fix caching failed.

## Current State
- ✅ Working: MCP server starts, Python backend functional, file on disk is valid
- ❌ Broken: Browser loads old cached app.js, web UI crashes on load
- 🔧 In Progress: Cache busting attempts (version number changes not working)

## Key Files
- `src/mcp_feedback_enhanced/web/static/js/app.js` - Main frontend app (2423 lines, valid syntax)
- `src/mcp_feedback_enhanced/web/templates/index.html` - HTML template with script tags
- `src/mcp_feedback_enhanced/web/main.py` - FastAPI web server

## Environment
- OS: Windows 11
- IDE: Augment Code
- Python: 3.11
- Browser: Chrome/Edge (caching issue)
- MCP Server: Local development version

## Failed Attempts
1. **Version number change**: Changed `?v=2025010505` to `?v=2025010808` - Browser still loaded old file
2. **Git checkout**: Reverted to working commit, re-applied fix - Browser cache persisted
3. **Process kill**: Killed Python processes - Browser cache still not cleared

## Lessons Learned
- Browser cache is more aggressive than expected
- Version query parameters alone don't force reload
- Web server restart doesn't clear browser cache
- Need to verify what file is ACTUALLY being served, not just what's on disk

## Recommended Next Steps
1. **Check web server static file serving**: Verify FastAPI is serving from correct directory
   ```bash
   # Check if there's a __pycache__ or compiled version
   Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
   ```

2. **Add timestamp-based cache busting**: Use actual timestamp instead of manual version
   ```python
   # In main.py or template rendering
   import time
   version = str(int(time.time()))
   ```

3. **Force browser hard refresh**: Instruct user to use Ctrl+Shift+R or clear browser cache manually

4. **Verify served file**: Add logging to see what file is actually being served
   ```python
   # In FastAPI static file handler
   logger.debug(f"Serving: {file_path}, size: {os.path.getsize(file_path)}")
   ```

## Verification
```bash
# Verify file on disk is valid
node -c src/mcp_feedback_enhanced/web/static/js/app.js

# Check file size (should be 2423 lines)
wc -l src/mcp_feedback_enhanced/web/static/js/app.js

# Check for cached Python files
Get-ChildItem -Recurse -Filter "*.pyc"

# After fix, browser console should show:
# ✅ FeedbackApp 主模組載入完成
# (No syntax errors)
```

## Critical Notes
- DO NOT modify app.js without verifying syntax with `node -c` first
- Browser cache is the enemy - always verify what's being served
- User is frustrated with repeated failures - be thorough and test before suggesting fixes
```

## Best Practices

1. **Be Honest**: If you're stuck, admit it and suggest fresh start
2. **Be Specific**: Don't say "there's an issue" - say exactly what's wrong
3. **Be Actionable**: Give concrete commands, not vague suggestions
4. **Be Thorough**: Include all context needed for new agent to succeed
5. **Be Respectful**: User's time is valuable - don't waste it with repeated failures

## Red Flags That Indicate Need for New Session

- 🚩 Agent says "let me try again" more than 3 times
- 🚩 Agent suggests same solution with minor variations
- 🚩 Agent asks user to do same action repeatedly
- 🚩 Agent's explanations become vague or contradictory
- 🚩 User says "you're wasting my time"
- 🚩 Token usage > 100k
- 🚩 Agent realizes it's missing obvious solutions

## After Handoff

When user starts new session with handoff prompt:

1. **Acknowledge the handoff**: "I see you've been working on [issue] with a previous agent"
2. **Verify understanding**: Summarize the problem in your own words
3. **Propose approach**: Outline your plan before executing
4. **Get approval**: Ask user if approach makes sense before proceeding
5. **Execute systematically**: Follow the recommended steps, verify each step
6. **Report progress**: Keep user informed of what's working

---

**Remember**: A fresh start with clear context is better than continuing in circles. Respect the user's time and resources.

