"""
Router Manager - Auto-starts and manages the Telegram Router
Ensures router runs when MCP instances start and stops when they're done
"""
import subprocess
import time
import os
import sys
import requests
import atexit
import signal
from pathlib import Path
from typing import Optional

class RouterManager:
    def __init__(self):
        self.router_process: Optional[subprocess.Popen] = None
        self.router_url = os.getenv('ROUTER_URL', 'http://localhost:8080')
        self.router_port = int(os.getenv('ROUTER_PORT', '8080'))
        
        # Find router directory
        current_dir = Path(__file__).parent
        self.router_dir = current_dir.parent / 'router'
        self.router_script = self.router_dir / 'telegram-router.js'
        
        # Reference count for multiple MCP instances
        self._reference_count = 0
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n[ROUTER MANAGER] Received shutdown signal, cleaning up...")
        self.cleanup()
        sys.exit(0)
    
    def is_router_running(self) -> bool:
        """Check if router is already running"""
        try:
            response = requests.get(f'{self.router_url}/health', timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_router(self) -> bool:
        """Start the router as a subprocess"""
        if self.is_router_running():
            print(f"[ROUTER] Router already running at {self.router_url} ✓")
            self._reference_count += 1
            return True
        
        if not self.router_script.exists():
            print(f"[ROUTER] ERROR: Router script not found at {self.router_script}")
            return False
        
        print(f"[ROUTER] Starting router from {self.router_dir}...")
        
        try:
            # Start router as subprocess
            # TEMPORARY DEBUG: Don't pipe stdout/stderr to see error messages
            if sys.platform == 'win32':
                # Windows: Use CREATE_NEW_PROCESS_GROUP to allow clean shutdown
                self.router_process = subprocess.Popen(
                    ['node', 'telegram-router.js'],
                    cwd=str(self.router_dir),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # Unix: Standard subprocess
                self.router_process = subprocess.Popen(
                    ['node', 'telegram-router.js'],
                    cwd=str(self.router_dir)
                )
            
            # Wait for router to start
            max_attempts = 30
            for attempt in range(max_attempts):
                if self.is_router_running():
                    print(f"[ROUTER] Router started successfully! ✅")
                    self._reference_count = 1
                    return True
                time.sleep(0.5)
            
            print("[ROUTER] ERROR: Router failed to start within timeout")
            self.stop_router()
            return False
            
        except FileNotFoundError:
            print("[ROUTER] ERROR: Node.js not found. Please install Node.js")
            return False
        except Exception as e:
            print(f"[ROUTER] ERROR starting router: {e}")
            return False
    
    def stop_router(self):
        """Stop the router subprocess"""
        if self.router_process is None:
            return
        
        # Decrement reference count
        self._reference_count = max(0, self._reference_count - 1)
        
        # Only stop if no more references
        if self._reference_count > 0:
            print(f"[ROUTER] Router still in use by {self._reference_count} instance(s)")
            return
        
        print("[ROUTER] Stopping router...")
        try:
            if sys.platform == 'win32':
                # Windows: Send CTRL_BREAK_EVENT
                self.router_process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                # Unix: Send SIGTERM
                self.router_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.router_process.wait(timeout=5)
                print("[ROUTER] Router stopped gracefully ✓")
            except subprocess.TimeoutExpired:
                print("[ROUTER] Router didn't stop gracefully, forcing...")
                self.router_process.kill()
                self.router_process.wait()
                print("[ROUTER] Router force stopped ✓")
                
        except Exception as e:
            print(f"[ROUTER] Error stopping router: {e}")
        finally:
            self.router_process = None
    
    def ensure_router_available(self) -> bool:
        """Ensure router is running, start if needed"""
        if self.is_router_running():
            self._reference_count += 1
            return True
        return self.start_router()
    
    def cleanup(self):
        """Cleanup on exit"""
        if self._reference_count > 0:
            self._reference_count = 0
            self.stop_router()

# Global singleton instance
_router_manager: Optional[RouterManager] = None

def get_router_manager() -> RouterManager:
    """Get or create the global router manager instance"""
    global _router_manager
    if _router_manager is None:
        _router_manager = RouterManager()
    return _router_manager

def ensure_router_running() -> bool:
    """Convenience function to ensure router is running"""
    return get_router_manager().ensure_router_available()

def stop_router():
    """Convenience function to stop the router"""
    if _router_manager is not None:
        _router_manager.stop_router()