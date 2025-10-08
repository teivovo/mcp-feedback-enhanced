# Testing Checklist: Stderr Monitoring Fix

## Pre-Test Verification

### ✅ Code Changes Applied
- [x] `src/mcp_feedback_enhanced/dev_wrapper.py` modified
- [x] Stderr reader thread added (lines 459-484)
- [x] Crash detection enhanced (lines 217-257)
- [x] Crash loop prevention added (lines 93-112, 162-199)
- [x] Restart handling improved (lines 445-481)

### ✅ Syntax Validation
- [x] No compilation errors
- [x] Python syntax valid
- [x] All imports present

### ✅ Test Proof
- [x] Crash simulation test passed
- [x] Stderr capture proven working
- [x] Documentation complete

---

## Testing Steps

### Step 1: Environment Check

```bash
# Check current directory
pwd
# Should be: mcp-feedback-dev

# Check Python environment
python --version
# Should be: Python 3.11.x

# Check virtual environment
which python
# Should point to .venv

# Check logs directory exists
ls -la logs/
```

**Expected:** All checks pass, logs directory exists

---

### Step 2: Start MCP Server

#### Option A: Via VS Code (Recommended)
1. Open VS Code
2. Open Command Palette (Ctrl+Shift+P)
3. Type "MCP" or look for MCP-related commands
4. Server should start automatically

#### Option B: Manual Start (for testing)
```bash
# Set dev mode
export MCP_DEV_MODE=true
export MCP_DEBUG=true

# Start server
python -m mcp_feedback_enhanced
```

**Expected:** 
- Process starts
- No immediate errors
- New runtime log created in `logs/`

---

### Step 3: Check Initial Logs

```bash
# Find latest runtime log
ls -lt logs/devwrapper_runtime_*.log | head -1

# View last 30 lines
tail -30 logs/devwrapper_runtime_*.log
```

**Look for:**
- ✅ `DevWrapper.__init__() called`
- ✅ `spawn_backend() called`
- ✅ `Backend process spawned with PID: XXXXX`
- ✅ `I/O threads started successfully (stdin, stdout, stderr)`
- ✅ `read_backend_stderr thread started`

**Red flags:**
- ❌ `Backend process exited immediately`
- ❌ `BACKEND STDERR` messages
- ❌ Rapid respawn messages

---

### Step 4: Trigger Interactive Feedback

#### Via VS Code:
1. Open any file
2. Ask AI assistant to use `interactive_feedback` tool
3. Or manually trigger via MCP client

#### Via Test Script:
```bash
python test_e2e_with_tool_call.py
```

**Expected:**
- Tool call sent
- Backend processes request
- Web UI attempts to launch

---

### Step 5: Check for Errors

```bash
# Check for stderr logs
ls -la logs/backend_stderr_*.log

# Check for crash logs
ls -la logs/backend_crash_*.log

# View runtime log
tail -50 logs/devwrapper_runtime_*.log
```

**Scenario A: No Error Logs** ✅
- No `backend_stderr_*.log` files
- No `backend_crash_*.log` files
- Runtime log shows normal operation
- **Result:** Backend working normally!

**Scenario B: Stderr Logs Present** ⚠️
- `backend_stderr_*.log` files exist
- Contains error messages
- **Result:** Backend had errors, but they're now VISIBLE!

**Scenario C: Crash Logs Present** 🔥
- `backend_crash_*.log` files exist
- Contains full crash context
- **Result:** Backend crashed immediately, but error is CAPTURED!

---

### Step 6: Analyze Errors (if present)

#### Read Stderr Log:
```bash
cat logs/backend_stderr_*.log
```

**Common errors and solutions:**

1. **Port already in use**
   ```
   OSError: [Errno 48] Address already in use
   Port 8765 is already in use
   ```
   **Solution:** Kill process using port 8765 or change port

2. **Permission denied**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution:** Check file/directory permissions

3. **Module not found**
   ```
   ModuleNotFoundError: No module named 'xxx'
   ```
   **Solution:** Install missing dependency

4. **Configuration error**
   ```
   KeyError: 'xxx'
   ConfigurationError: xxx
   ```
   **Solution:** Check configuration files

#### Read Crash Log:
```bash
cat logs/backend_crash_*.log
```

**Contains:**
- Exit code
- Timestamp
- Command used
- Full stderr output

---

### Step 7: Verify Crash Loop Prevention

If backend crashes repeatedly:

```bash
# Watch runtime log in real-time
tail -f logs/devwrapper_runtime_*.log
```

**Look for:**
- ✅ `Rapid respawn detected (#1)`
- ✅ `Applying backoff delay: 2s`
- ✅ `Rapid respawn detected (#2)`
- ✅ `Applying backoff delay: 4s`
- ✅ `Rapid respawn detected (#3)`
- ✅ `Applying backoff delay: 8s`
- ✅ `CRITICAL: Backend crash loop detected (5 failures)`

**Expected behavior:**
- Delays increase exponentially (2s, 4s, 8s, 10s, 10s)
- Stops after 5 failures
- Clear error messages in logs

---

### Step 8: Test Web UI Launch

If backend doesn't crash:

**Expected:**
1. Browser opens automatically
2. Web UI loads at `http://localhost:8765`
3. Feedback form displays
4. Can submit feedback

**If Web UI doesn't open:**
1. Check runtime log for port number
2. Manually open `http://localhost:8765`
3. Check for port conflicts
4. Check stderr logs for errors

---

## Success Criteria

### ✅ Minimum Success (Problem is Debuggable)
- [ ] Stderr monitoring thread starts
- [ ] Any backend errors are captured in logs
- [ ] Crash loop prevention works
- [ ] Error messages are clear and actionable

### ✅ Full Success (Everything Works)
- [ ] Backend starts without errors
- [ ] Web UI launches successfully
- [ ] Can submit feedback
- [ ] No stderr/crash logs created

---

## Troubleshooting Guide

### Issue: No logs created
**Cause:** Wrapper not starting
**Solution:** 
```bash
# Check if process is running
ps aux | grep mcp_feedback_enhanced

# Try manual start
python -m mcp_feedback_enhanced
```

### Issue: Logs show rapid respawn
**Cause:** Backend crashing immediately
**Solution:**
1. Check `backend_crash_*.log` for error
2. Check `backend_stderr_*.log` for details
3. Fix the underlying issue (port, permissions, etc.)

### Issue: No stderr captured
**Cause:** Backend not outputting to stderr
**Solution:**
- This is actually good! Means no errors
- Check if Web UI launched successfully

### Issue: Crash loop doesn't stop
**Cause:** Bug in crash loop prevention
**Solution:**
1. Check runtime log for failure count
2. Verify backoff delays are applied
3. Should stop after 5 failures

---

## Verification Commands

### Quick Health Check:
```bash
# One-liner to check everything
echo "=== Runtime Log ===" && \
tail -20 logs/devwrapper_runtime_*.log && \
echo -e "\n=== Stderr Logs ===" && \
ls -la logs/backend_stderr_*.log 2>/dev/null || echo "None (good!)" && \
echo -e "\n=== Crash Logs ===" && \
ls -la logs/backend_crash_*.log 2>/dev/null || echo "None (good!)"
```

### Monitor in Real-Time:
```bash
# Watch for new log entries
watch -n 1 'tail -10 logs/devwrapper_runtime_*.log'
```

### Check Process Status:
```bash
# Find MCP processes
ps aux | grep mcp_feedback_enhanced

# Check if port is in use
netstat -an | grep 8765
# or
lsof -i :8765
```

---

## Expected Test Results

### Test 1: Normal Operation
```
✅ Backend starts
✅ Stderr thread starts
✅ No errors in logs
✅ Web UI launches
✅ Can submit feedback
```

### Test 2: Backend Crash (Port Conflict)
```
✅ Backend starts
✅ Stderr thread starts
✅ Error captured: "Port 8765 in use"
✅ Crash log created with full details
✅ Crash loop prevention activates
✅ Stops after 5 attempts
```

### Test 3: Backend Crash (Other Error)
```
✅ Backend starts
✅ Stderr thread starts
✅ Error captured in stderr log
✅ Error visible in runtime log
✅ Can identify and fix issue
```

---

## Post-Test Actions

### If Everything Works:
1. ✅ Mark issue as resolved
2. ✅ Commit changes
3. ✅ Update documentation
4. ✅ Deploy to production

### If Errors Found:
1. ✅ Error is now visible (success!)
2. ✅ Review stderr/crash logs
3. ✅ Identify root cause
4. ✅ Fix underlying issue
5. ✅ Re-test

---

## Reporting Results

### Success Report Template:
```
✅ TESTING COMPLETE

Environment:
- OS: [Windows/Linux/Mac]
- Python: [version]
- MCP Version: [version]

Results:
- Backend started: [YES/NO]
- Stderr monitoring: [WORKING]
- Errors captured: [YES/NO]
- Web UI launched: [YES/NO]
- Crash loop prevention: [TESTED/NOT TESTED]

Logs:
- Runtime log: [size, key entries]
- Stderr log: [exists/not exists]
- Crash log: [exists/not exists]

Conclusion:
[Everything working / Errors found but visible / Issue identified]
```

---

## Quick Reference

**Key Files:**
- `src/mcp_feedback_enhanced/dev_wrapper.py` - Modified code
- `logs/devwrapper_runtime_*.log` - Main log
- `logs/backend_stderr_*.log` - Stderr only
- `logs/backend_crash_*.log` - Crash details

**Key Log Messages:**
- `read_backend_stderr thread started` - Stderr monitoring active
- `BACKEND STDERR #N:` - Error captured
- `Backend died with exit code:` - Crash detected
- `Rapid respawn detected` - Crash loop prevention
- `CRITICAL: Backend crash loop detected` - Stopped after 5 failures

**Test Scripts:**
- `test_crash_simulation.py` - Proves fix works
- `test_e2e_with_tool_call.py` - Full workflow test
- `test_backend_direct.py` - Backend only test

---

**Ready to test! Follow the steps above and report results.**

