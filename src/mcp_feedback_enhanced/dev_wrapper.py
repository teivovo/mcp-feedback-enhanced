#!/usr/bin/env python3
"""
Development Wrapper for MCP Feedback Enhanced
==============================================

This module provides a development mode wrapper that maintains a persistent
stdio connection with VS Code while managing the actual MCP server backend
as a restartable subprocess. This enables hot-reload functionality for rapid
development cycles without needing to restart VS Code.

Architecture:
    VS Code (stdio) ↔ DevWrapper (persistent) ↔ Backend (restartable)

Key Features:
- Persistent stdio connection maintenance
- Backend subprocess lifecycle management
- Graceful shutdown and crash recovery
- Message proxying between VS Code and backend
- Hot-reload support via reload marker file
- Comprehensive stderr monitoring and crash detection (FIXED 2025-10-08)

Author: MCP Feedback Enhanced Team
Version: 2.5.4-stderr-fix
"""

import asyncio
import os
import subprocess
import sys
import tempfile
import time
from typing import Optional
from datetime import datetime
from pathlib import Path

# Import existing utilities for consistency
from .debug import server_debug_log as debug_log
from .dev_proxy import MessageProxy
from .utils.error_handler import ErrorHandler, ErrorType
from .utils.resource_manager import get_resource_manager, register_process


# Setup detailed runtime logging
def setup_runtime_log():
    """Setup detailed runtime logging to project logs folder"""
    try:
        # Get project root (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create log file with DTG
        dtg = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"devwrapper_runtime_{dtg}.log"

        return log_file
    except Exception as e:
        print(f"Failed to setup runtime log: {e}", file=sys.stderr)
        return None


# Global runtime log file
RUNTIME_LOG = setup_runtime_log()


def runtime_log(message: str, level: str = "INFO"):
    """
    Log detailed runtime information to both debug log and file.

    Args:
        message: Log message
        level: Log level (INFO, DEBUG, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_msg = f"[{timestamp}] [{level}] {message}"

    # Log to debug (stderr)
    debug_log(f"[{level}] {message}")

    # Log to file
    if RUNTIME_LOG:
        try:
            with open(RUNTIME_LOG, "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
        except Exception:
            pass  # Don't fail if logging fails


class DevWrapper:
    """
    Development wrapper that maintains persistent stdio connection while
    managing the MCP server backend as a restartable subprocess.
    """

    def __init__(self):
        """Initialize the development wrapper."""
        runtime_log("=" * 60, "INFO")
        runtime_log("DevWrapper.__init__() called", "INFO")
        runtime_log(f"Runtime log file: {RUNTIME_LOG}", "INFO")
        runtime_log("=" * 60, "INFO")

        self.backend_process: Optional[subprocess.Popen] = None
        self.backend_pid: Optional[int] = None
        self.is_running = False
        self.reload_marker_path = os.path.join(
            tempfile.gettempdir(), "mcp_reload_request"
        )
        runtime_log(f"Reload marker path: {self.reload_marker_path}", "DEBUG")

        # Crash loop prevention
        self.last_spawn_time = 0.0
        self.spawn_failure_count = 0
        self.max_spawn_failures = 5
        runtime_log("Crash loop prevention initialized", "DEBUG")

        # Initialize message proxy
        runtime_log("Initializing MessageProxy...", "DEBUG")
        self.proxy = MessageProxy()
        runtime_log("MessageProxy initialized", "INFO")

        # Initialize file watcher (optional)
        self.file_watcher = None
        runtime_log("Initializing file watcher...", "DEBUG")
        self._init_file_watcher()
        runtime_log(f"File watcher: {self.file_watcher}", "INFO")

        debug_log("=== MCP Development Wrapper Initialized ===")
        debug_log("Hot-reload enabled")
        debug_log("Call reload_server() tool to restart backend")
        debug_log("==========================================")
        runtime_log("DevWrapper initialization complete", "INFO")

    def _init_file_watcher(self):
        """Initialize optional file watcher for automatic reload."""
        try:
            from .dev_file_watcher import FileWatcher, is_watchdog_available

            if not is_watchdog_available():
                debug_log("watchdog not installed, auto-reload disabled")
                debug_log("Install with: pip install watchdog")
                return

            # Watch the src/mcp_feedback_enhanced directory
            import os
            watch_path = os.path.join(
                os.path.dirname(__file__), ".."
            )
            watch_path = os.path.abspath(watch_path)

            self.file_watcher = FileWatcher(
                watch_path=watch_path,
                reload_callback=self.reload_backend
            )

            debug_log(f"File watcher initialized for: {watch_path}")

        except ImportError as e:
            debug_log(f"File watcher not available: {e}")
            debug_log("Manual reload only (call reload_server() tool)")
        except Exception as e:
            debug_log(f"Failed to initialize file watcher: {e}")
            debug_log("Manual reload only (call reload_server() tool)")

    def spawn_backend(self) -> bool:
        """
        Spawn the backend MCP server subprocess.

        Returns:
            bool: True if backend spawned successfully, False otherwise
        """
        try:
            runtime_log("=" * 60, "INFO")
            runtime_log("spawn_backend() called", "INFO")

            # Crash loop prevention
            current_time = time.time()
            time_since_last_spawn = current_time - self.last_spawn_time

            if time_since_last_spawn < 2.0:  # Less than 2 seconds since last spawn
                self.spawn_failure_count += 1
                runtime_log(f"Rapid respawn detected (#{self.spawn_failure_count}), time since last: {time_since_last_spawn:.2f}s", "WARNING")

                if self.spawn_failure_count >= self.max_spawn_failures:
                    runtime_log(f"CRITICAL: Backend crash loop detected ({self.spawn_failure_count} failures)", "ERROR")
                    debug_log(f"Backend crash loop detected - {self.spawn_failure_count} rapid failures")
                    debug_log("Check backend_stderr_*.log and backend_crash_*.log files for error details")
                    return False

                # Exponential backoff delay
                delay = min(2 ** self.spawn_failure_count, 10)  # Max 10 seconds
                runtime_log(f"Applying backoff delay: {delay}s", "INFO")
                debug_log(f"Applying {delay}s backoff delay before respawn...")
                time.sleep(delay)
            else:
                # Reset failure count if enough time has passed
                if self.spawn_failure_count > 0:
                    runtime_log(f"Resetting failure count (was {self.spawn_failure_count})", "INFO")
                self.spawn_failure_count = 0

            self.last_spawn_time = current_time
            debug_log("Spawning backend MCP server...")

            # Command to launch backend server
            # Use sys.executable to ensure we use the same Python interpreter
            cmd = [sys.executable, "-m", "mcp_feedback_enhanced", "server"]
            runtime_log(f"Backend command: {' '.join(cmd)}", "DEBUG")

            # Prepare environment - inherit current env but ensure MCP_DEV_MODE is NOT set
            # This prevents the backend from entering dev mode recursively
            env = os.environ.copy()
            if "MCP_DEV_MODE" in env:
                del env["MCP_DEV_MODE"]
                runtime_log("Removed MCP_DEV_MODE from backend environment", "DEBUG")

            # Platform-specific subprocess creation
            if sys.platform == "win32":
                # Windows: Use CREATE_NEW_PROCESS_GROUP for clean shutdown
                # Follow pattern from mcp-client/router_manager.py:65-72
                self.backend_process = subprocess.Popen(
                    cmd,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0,
                    encoding="utf-8",
                    errors="replace",
                )
            else:
                # Unix-like systems: Standard subprocess
                self.backend_process = subprocess.Popen(
                    cmd,
                    env=env,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=0,
                    encoding="utf-8",
                    errors="replace",
                )

            # Register with ResourceManager for tracking and auto-cleanup
            self.backend_pid = register_process(
                self.backend_process,
                description="MCP-Dev-Backend",
                auto_cleanup=True,
            )

            debug_log(f"Backend spawned successfully (PID: {self.backend_pid})")
            runtime_log(f"Backend process spawned with PID: {self.backend_pid}", "INFO")

            # Wait briefly to ensure backend starts
            time.sleep(0.5)

            # Check if process is still alive
            returncode = self.backend_process.poll()
            if returncode is not None:
                runtime_log(f"Backend process exited immediately with code: {returncode}", "ERROR")
                debug_log(f"Backend process exited immediately after spawn (code: {returncode})")

                # Try to read ALL stderr to see what went wrong
                try:
                    stderr_output = self.backend_process.stderr.read()
                    if stderr_output:
                        runtime_log(f"Backend immediate crash stderr: {stderr_output}", "ERROR")
                        debug_log(f"Backend stderr: {stderr_output}")
                        # Also write to dedicated crash log
                        if RUNTIME_LOG:
                            crash_log = RUNTIME_LOG.parent / f"backend_crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                            try:
                                with open(crash_log, "w", encoding="utf-8") as f:
                                    f.write(f"Backend crashed immediately after spawn\n")
                                    f.write(f"Exit code: {returncode}\n")
                                    f.write(f"Timestamp: {datetime.now()}\n")
                                    f.write(f"Command: {' '.join(cmd)}\n")
                                    f.write(f"\n{'='*60}\n")
                                    f.write(f"STDERR OUTPUT:\n")
                                    f.write(f"{'='*60}\n")
                                    f.write(stderr_output)
                                runtime_log(f"Crash details written to: {crash_log}", "INFO")
                            except Exception as e:
                                runtime_log(f"Could not write crash log: {e}", "WARNING")
                except Exception as e:
                    runtime_log(f"Could not read backend stderr: {e}", "ERROR")
                    debug_log(f"Could not read backend stderr: {e}")
                return False

            runtime_log("Backend process started successfully and is running", "INFO")
            return True

        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e,
                context={"operation": "backend_spawn"},
                error_type=ErrorType.PROCESS,
            )
            debug_log(f"Failed to spawn backend [Error ID: {error_id}]: {e}")
            return False

    def terminate_backend(self, timeout: int = 5) -> bool:
        """
        Gracefully terminate the backend subprocess.

        Args:
            timeout: Maximum seconds to wait for graceful exit

        Returns:
            bool: True if terminated successfully, False otherwise
        """
        if not self.backend_process:
            return True

        try:
            debug_log("Terminating backend process...")

            # Unregister from ResourceManager first
            if self.backend_pid:
                get_resource_manager().unregister_process(self.backend_pid)

            # Send termination signal
            self.backend_process.terminate()

            # Wait for graceful exit
            try:
                self.backend_process.wait(timeout=timeout)
                debug_log("Backend terminated gracefully")
                return True
            except subprocess.TimeoutExpired:
                debug_log(f"Backend did not exit within {timeout}s, force killing...")
                self.backend_process.kill()
                self.backend_process.wait()
                debug_log("Backend force killed")
                return True

        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e,
                context={"operation": "backend_termination"},
                error_type=ErrorType.PROCESS,
            )
            debug_log(f"Backend termination failed [Error ID: {error_id}]: {e}")
            return False
        finally:
            self.backend_process = None
            self.backend_pid = None

    def reload_backend(self) -> bool:
        """
        Reload the backend by terminating and respawning it.

        Returns:
            bool: True if reload successful, False otherwise
        """
        debug_log("=== RELOADING BACKEND ===")

        # Enter buffering mode
        self.proxy.start_buffering()

        # Terminate existing backend
        if not self.terminate_backend():
            debug_log("Failed to terminate backend, aborting reload")
            self.proxy.stop_buffering()
            return False

        # Brief pause to ensure clean shutdown
        time.sleep(0.5)

        # Spawn new backend
        if not self.spawn_backend():
            debug_log("Failed to spawn new backend after reload")
            self.proxy.stop_buffering()
            return False

        # Replay buffered messages
        if self.backend_process and self.backend_process.stdin:
            self.proxy.replay_buffered_messages(self.backend_process.stdin)

        # Exit buffering mode
        self.proxy.stop_buffering()

        debug_log("=== RELOAD COMPLETE ===")
        return True

    def check_reload_marker(self) -> bool:
        """
        Check if reload marker file exists.

        Returns:
            bool: True if reload requested, False otherwise
        """
        if os.path.exists(self.reload_marker_path):
            try:
                os.remove(self.reload_marker_path)
                debug_log("Reload marker detected")
                return True
            except Exception as e:
                debug_log(f"Failed to remove reload marker: {e}")
        return False

    def forward_messages(self):
        """
        Forward messages between VS Code (stdio) and backend subprocess
        using the MessageProxy for proper JSON-RPC handling.

        Uses threading to handle bidirectional I/O on Windows where select()
        doesn't work on stdin.
        """
        import select
        import threading
        import queue

        runtime_log("=" * 60, "INFO")
        runtime_log("forward_messages() called", "INFO")
        runtime_log(f"Platform: {sys.platform}", "INFO")
        debug_log("Starting message forwarding loop with MessageProxy...")

        # Create queues for thread communication
        stdin_queue = queue.Queue()
        backend_queue = queue.Queue()

        # Message counters for logging
        stdin_msg_count = [0]
        backend_msg_count = [0]

        def read_stdin():
            """Thread to read from stdin"""
            runtime_log("read_stdin thread started", "DEBUG")
            while self.is_running:
                try:
                    line = sys.stdin.readline()
                    if line:
                        stdin_msg_count[0] += 1
                        runtime_log(f"STDIN READ #{stdin_msg_count[0]}: {line[:100]}...", "DEBUG")
                        stdin_queue.put(line)
                except Exception as e:
                    runtime_log(f"Error reading stdin: {e}", "ERROR")
                    debug_log(f"Error reading stdin: {e}")
                    break
            runtime_log("read_stdin thread exiting", "DEBUG")

        def read_backend():
            """Thread to read from backend stdout"""
            runtime_log("read_backend thread started", "DEBUG")
            while self.is_running and self.backend_process:
                try:
                    if self.backend_process and self.backend_process.stdout:
                        line = self.backend_process.stdout.readline()
                        if line:
                            backend_msg_count[0] += 1
                            runtime_log(f"BACKEND READ #{backend_msg_count[0]}: {line[:100]}...", "DEBUG")
                            backend_queue.put(line)
                except Exception as e:
                    runtime_log(f"Error reading backend: {e}", "ERROR")
                    debug_log(f"Error reading backend: {e}")
                    break
            runtime_log("read_backend thread exiting", "DEBUG")

        def read_backend_stderr():
            """Thread to read from backend stderr - CRITICAL for crash diagnosis"""
            runtime_log("read_backend_stderr thread started", "DEBUG")
            stderr_line_count = [0]
            while self.is_running and self.backend_process:
                try:
                    if self.backend_process and self.backend_process.stderr:
                        line = self.backend_process.stderr.readline()
                        if line:
                            stderr_line_count[0] += 1
                            # Log ALL stderr output - this is where crashes are reported
                            runtime_log(f"BACKEND STDERR #{stderr_line_count[0]}: {line.strip()}", "ERROR")
                            debug_log(f"Backend stderr: {line.strip()}")
                            # Also write to a dedicated stderr log file
                            if RUNTIME_LOG:
                                stderr_log = RUNTIME_LOG.parent / f"backend_stderr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                                try:
                                    with open(stderr_log, "a", encoding="utf-8") as f:
                                        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] {line}")
                                except Exception:
                                    pass
                except Exception as e:
                    runtime_log(f"Error reading backend stderr: {e}", "ERROR")
                    debug_log(f"Error reading backend stderr: {e}")
                    break
            runtime_log("read_backend_stderr thread exiting", "DEBUG")

        # Start reader threads on Windows
        if sys.platform == "win32":
            runtime_log("Starting I/O threads for Windows...", "INFO")
            stdin_thread = threading.Thread(target=read_stdin, daemon=True)
            backend_thread = threading.Thread(target=read_backend, daemon=True)
            backend_stderr_thread = threading.Thread(target=read_backend_stderr, daemon=True)
            stdin_thread.start()
            backend_thread.start()
            backend_stderr_thread.start()
            debug_log("Started I/O threads for Windows (including stderr monitor)")
            runtime_log("I/O threads started successfully (stdin, stdout, stderr)", "INFO")

        while self.is_running:
            try:
                # Check for reload marker every iteration
                if self.check_reload_marker():
                    self.reload_backend()
                    # Restart backend threads after reload
                    if sys.platform == "win32":
                        backend_thread = threading.Thread(target=read_backend, daemon=True)
                        backend_stderr_thread = threading.Thread(target=read_backend_stderr, daemon=True)
                        backend_thread.start()
                        backend_stderr_thread.start()
                        runtime_log("Backend threads restarted after reload", "INFO")

                # Check if backend is still alive
                if self.backend_process and self.backend_process.poll() is not None:
                    returncode = self.backend_process.poll()
                    runtime_log(f"Backend process died with exit code: {returncode}", "ERROR")
                    debug_log(f"Backend process died (exit code: {returncode}), attempting restart...")

                    # Try to capture any remaining stderr before restart
                    try:
                        if self.backend_process.stderr:
                            remaining_stderr = self.backend_process.stderr.read()
                            if remaining_stderr:
                                runtime_log(f"Final backend stderr: {remaining_stderr[:500]}", "ERROR")
                                debug_log(f"Backend final stderr: {remaining_stderr[:500]}")
                    except Exception as e:
                        runtime_log(f"Could not read final stderr: {e}", "WARNING")

                    if not self.spawn_backend():
                        debug_log("Failed to restart backend, exiting wrapper")
                        break
                    # Restart backend threads
                    if sys.platform == "win32":
                        backend_thread = threading.Thread(target=read_backend, daemon=True)
                        backend_stderr_thread = threading.Thread(target=read_backend_stderr, daemon=True)
                        backend_thread.start()
                        backend_stderr_thread.start()
                        runtime_log("Backend threads restarted after crash", "INFO")

                # Forward stdin to backend (VS Code → Backend)
                if sys.platform == "win32":
                    # Windows: Use queue from thread
                    try:
                        line = stdin_queue.get(timeout=0.01)
                        if line and self.backend_process:
                            runtime_log(f"Processing stdin message: {line[:80]}...", "DEBUG")
                            message = self.proxy.parse_jsonrpc(line)
                            if message:
                                runtime_log(f"Parsed JSON-RPC: method={message.get('method', 'N/A')}, id={message.get('id', 'N/A')}", "INFO")
                                if self.proxy.is_buffering:
                                    runtime_log("Buffering message (reload in progress)", "DEBUG")
                                    self.proxy.buffer_message(message)
                                else:
                                    runtime_log("Forwarding to backend", "DEBUG")
                                    self.proxy.forward_to_backend(
                                        message, self.backend_process.stdin
                                    )
                                    runtime_log("Message forwarded to backend successfully", "DEBUG")
                    except queue.Empty:
                        pass
                else:
                    # Unix: Use select for non-blocking I/O
                    readable, _, _ = select.select([sys.stdin], [], [], 0.01)
                    if readable and self.backend_process:
                        line = sys.stdin.readline()
                        if line:
                            message = self.proxy.parse_jsonrpc(line)
                            if message:
                                if self.proxy.is_buffering:
                                    self.proxy.buffer_message(message)
                                else:
                                    self.proxy.forward_to_backend(
                                        message, self.backend_process.stdin
                                    )

                # Forward backend stdout to VS Code (Backend → VS Code)
                if sys.platform == "win32":
                    # Windows: Use queue from thread
                    try:
                        line = backend_queue.get(timeout=0.01)
                        if line:
                            runtime_log(f"Processing backend message: {line[:80]}...", "DEBUG")
                            message = self.proxy.parse_jsonrpc(line)
                            if message:
                                runtime_log(f"Parsed backend JSON-RPC: id={message.get('id', 'N/A')}, has_result={('result' in message)}, has_error={('error' in message)}", "INFO")
                                runtime_log("Forwarding to VS Code", "DEBUG")
                                self.proxy.forward_to_vscode(message)
                                runtime_log("Message forwarded to VS Code successfully", "DEBUG")
                    except queue.Empty:
                        pass
                else:
                    # Unix: Use select
                    if self.backend_process and self.backend_process.stdout:
                        readable, _, _ = select.select(
                            [self.backend_process.stdout], [], [], 0.01
                        )
                        if readable:
                            line = self.backend_process.stdout.readline()
                            if line:
                                message = self.proxy.parse_jsonrpc(line)
                                if message:
                                    self.proxy.forward_to_vscode(message)

                # Periodic cleanup of timed-out requests
                if int(time.time()) % 10 == 0:  # Every 10 seconds
                    self.proxy.cleanup_timed_out_requests()

            except KeyboardInterrupt:
                debug_log("Received interrupt signal")
                break
            except Exception as e:
                error_id = ErrorHandler.log_error_with_context(
                    e,
                    context={"operation": "message_forwarding"},
                    error_type=ErrorType.SYSTEM,
                )
                debug_log(f"Message forwarding error [Error ID: {error_id}]: {e}")

    def run(self) -> int:
        """
        Main entry point for the development wrapper.

        Returns:
            int: Exit code (0 for success, 1 for failure)
        """
        try:
            # Spawn initial backend
            if not self.spawn_backend():
                debug_log("Failed to spawn initial backend")
                return 1

            self.is_running = True

            # Start file watcher if available
            if self.file_watcher:
                try:
                    self.file_watcher.start()
                except Exception as e:
                    debug_log(f"Failed to start file watcher: {e}")
                    debug_log("Continuing with manual reload only")

            # Start message forwarding
            self.forward_messages()

            return 0

        except Exception as e:
            error_id = ErrorHandler.log_error_with_context(
                e, context={"operation": "wrapper_run"}, error_type=ErrorType.SYSTEM
            )
            debug_log(f"Wrapper run failed [Error ID: {error_id}]: {e}")
            return 1
        finally:
            self.is_running = False

            # Stop file watcher
            if self.file_watcher:
                try:
                    self.file_watcher.stop()
                except Exception as e:
                    debug_log(f"Error stopping file watcher: {e}")

            self.terminate_backend()
            debug_log("Development wrapper shutdown complete")

