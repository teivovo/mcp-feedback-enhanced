# Architecture Diagram: Stderr Monitoring Fix

## Before Fix (Broken)

```
┌─────────────────────────────────────────────────────────────────┐
│                         VS Code                                  │
│                    (MCP Client)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ stdio
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DevWrapper Process                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Main Thread (forward_messages)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stdin_thread                                            │  │
│  │  Reads from VS Code                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  backend_thread                                          │  │
│  │  Reads backend STDOUT only                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ❌ NO STDERR READER THREAD                                     │
│                                                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ stdin/stdout/stderr
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Process                               │
│              (python -m mcp_feedback_enhanced server)            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stdout → JSON-RPC responses                            │  │
│  │           ✅ READ by backend_thread                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stderr → Error messages, tracebacks                    │  │
│  │           ❌ NEVER READ (goes to void)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  💥 CRASHES with error to stderr                                │
│  ❌ Error invisible to wrapper                                  │
│  🔄 Wrapper detects death, respawns                             │
│  💥 Crashes again with same error                               │
│  🔄 Infinite respawn loop                                       │
└─────────────────────────────────────────────────────────────────┘
```

## After Fix (Working)

```
┌─────────────────────────────────────────────────────────────────┐
│                         VS Code                                  │
│                    (MCP Client)                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ stdio
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DevWrapper Process                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Main Thread (forward_messages)                          │  │
│  │  - Monitors backend health                               │  │
│  │  - Applies crash loop prevention                         │  │
│  │  - Exponential backoff on failures                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stdin_thread                                            │  │
│  │  Reads from VS Code                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  backend_thread                                          │  │
│  │  Reads backend STDOUT                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  backend_stderr_thread ✨ NEW!                           │  │
│  │  Reads backend STDERR                                    │  │
│  │  Logs to:                                                │  │
│  │  - devwrapper_runtime_*.log                             │  │
│  │  - backend_stderr_*.log                                 │  │
│  │  - Debug output                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ stdin/stdout/stderr
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Process                               │
│              (python -m mcp_feedback_enhanced server)            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stdout → JSON-RPC responses                            │  │
│  │           ✅ READ by backend_thread                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  stderr → Error messages, tracebacks                    │  │
│  │           ✅ READ by backend_stderr_thread ✨            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  💥 CRASHES with error to stderr                                │
│  ✅ Error captured and logged                                   │
│  🔄 Wrapper detects death, applies backoff                      │
│  ⏱️  Waits 2s, 4s, 8s... (exponential)                          │
│  🛑 Stops after 5 failures                                      │
│  📊 All errors visible in logs                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Error Capture

### Before Fix:
```
Backend Error
    ↓
stderr (subprocess.PIPE)
    ↓
❌ NEVER READ
    ↓
Lost forever
```

### After Fix:
```
Backend Error
    ↓
stderr (subprocess.PIPE)
    ↓
backend_stderr_thread.readline()
    ↓
┌─────────────────────────────────────┐
│ Log to multiple destinations:       │
│                                     │
│ 1. Runtime log (inline)             │
│    [ERROR] BACKEND STDERR #1: ...   │
│                                     │
│ 2. Dedicated stderr log             │
│    backend_stderr_*.log             │
│                                     │
│ 3. Debug output (if enabled)        │
│    stderr: ...                      │
│                                     │
│ 4. Crash log (if immediate exit)    │
│    backend_crash_*.log              │
└─────────────────────────────────────┘
    ↓
Developer sees error!
```

## Crash Loop Prevention Flow

```
Backend Spawn Attempt
    ↓
Check: Time since last spawn
    ↓
┌─────────────────────────────────────┐
│ < 2 seconds?                        │
└─────────────────────────────────────┘
    │
    ├─ NO ──→ Reset failure count
    │         Spawn normally
    │
    └─ YES ─→ Increment failure count
              │
              ├─ Count < 5?
              │   │
              │   ├─ YES ─→ Apply backoff
              │   │         delay = 2^count seconds
              │   │         (max 10s)
              │   │         Wait, then spawn
              │   │
              │   └─ NO ──→ STOP
              │             Log: "Crash loop detected"
              │             Return failure
              │             Exit wrapper
```

## Thread Lifecycle

```
DevWrapper.run()
    ↓
spawn_backend()
    ↓
Start 3 reader threads:
    ├─ stdin_thread (daemon)
    ├─ backend_thread (daemon)
    └─ backend_stderr_thread (daemon) ✨ NEW!
    ↓
forward_messages() loop
    │
    ├─ Check backend health
    │   │
    │   └─ Dead? ─→ Log exit code
    │               Read remaining stderr
    │               Apply backoff
    │               Respawn
    │               Restart threads
    │
    ├─ Forward stdin → backend
    ├─ Forward backend stdout → VS Code
    └─ (stderr handled by thread)
    ↓
Cleanup on exit
```

## Log File Structure

```
logs/
├── devwrapper_runtime_20251008_025012.log
│   ├── [INFO] DevWrapper initialized
│   ├── [INFO] Backend spawned (PID: 12345)
│   ├── [DEBUG] STDIN READ #1: {"method":"initialize"...
│   ├── [DEBUG] BACKEND READ #1: {"jsonrpc":"2.0"...
│   ├── [ERROR] BACKEND STDERR #1: Port 8765 in use ✨
│   ├── [ERROR] BACKEND STDERR #2: Traceback... ✨
│   ├── [ERROR] Backend died with exit code: 1 ✨
│   └── [WARNING] Rapid respawn detected ✨
│
├── backend_stderr_20251008_025012.log ✨ NEW!
│   ├── [2025-10-08 02:50:12.385] Port 8765 in use
│   ├── [2025-10-08 02:50:12.386] Traceback...
│   └── [2025-10-08 02:50:12.387] OSError: Port in use
│
└── backend_crash_20251008_025012.log ✨ NEW!
    ├── Backend crashed immediately after spawn
    ├── Exit code: 1
    ├── Timestamp: 2025-10-08 02:50:12
    ├── Command: python -m mcp_feedback_enhanced server
    ├── ============================================
    ├── STDERR OUTPUT:
    ├── ============================================
    └── [Full error traceback]
```

## Key Improvements Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Stderr Reading** | ❌ Never | ✅ Continuous thread |
| **Error Visibility** | ❌ Invisible | ✅ Multiple logs |
| **Crash Detection** | ⚠️ Basic | ✅ Enhanced with context |
| **Respawn Behavior** | 🔄 Infinite loop | ✅ Exponential backoff |
| **Failure Limit** | ❌ None | ✅ Stops after 5 |
| **Diagnostic Info** | ❌ Minimal | ✅ Comprehensive |
| **Log Files** | 1 | 3 (runtime, stderr, crash) |

## Testing Proof

```
Crash Simulation Test:
┌─────────────────────────────────────────────────────────────┐
│ Fake Backend                                                │
│ ├─ Outputs to stdout: {"jsonrpc":"2.0"...}                 │
│ ├─ Outputs to stderr: "CRITICAL ERROR: Port in use"        │
│ └─ Exits with code 1                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Stderr Reader Thread                                        │
│ ├─ Captures: "CRITICAL ERROR: Port in use"                 │
│ ├─ Captures: "Traceback..."                                │
│ └─ Captures: "OSError: Port 8765 already in use"           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Test Result                                                 │
│ ✅ SUCCESS! Stderr was captured                             │
│ ✅ All error lines logged                                   │
│ ✅ This proves the fix is working!                          │
└─────────────────────────────────────────────────────────────┘
```

---

**Visual Summary:**

- ✨ = New feature added by fix
- ✅ = Working correctly
- ❌ = Not working / missing
- 🔄 = Loop / retry
- 💥 = Crash
- 🛑 = Stop
- ⏱️ = Delay
- 📊 = Logging

**The fix transforms an invisible, undebuggable problem into a visible, solvable one.**

