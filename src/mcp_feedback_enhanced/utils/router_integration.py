"""
Router Integration Module

Provides clean API for MCP server to interact with Telegram Router.
Handles router lifecycle, registration, and message sending.
"""

import sys
import os
import atexit
from typing import Optional, List
from pathlib import Path

# Add mcp-client to path for RouterManager import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "mcp-client"))

try:
    import requests
except ImportError:
    print("[ROUTER] ERROR: requests library not found. Install with: pip install requests")
    requests = None

from ..debug import debug_log


class RouterIntegration:
    """
    Manages integration with Telegram Router.
    
    Handles:
    - Router lifecycle (start/stop via RouterManager)
    - Instance registration/deregistration
    - Message sending to Telegram
    - Cleanup on exit
    """
    
    def __init__(
        self,
        router_url: str,
        instance_name: str,
        callback_port: int
    ):
        """
        Initialize router integration.
        
        Args:
            router_url: URL of the router (e.g., 'http://localhost:8080')
            instance_name: Human-readable name for this MCP instance
            callback_port: Port for callback endpoint
        """
        self.router_url = router_url
        self.instance_id = f"mcp-{callback_port}"
        self.instance_name = instance_name
        self.callback_port = callback_port
        self.callback_url = f"http://localhost:{callback_port}/callback"
        self._registered = False
        self.router_manager = None
        
        # Import RouterManager
        try:
            from router_manager import get_router_manager
            self.router_manager = get_router_manager()
            debug_log(f"[ROUTER] RouterManager initialized")
        except ImportError as e:
            debug_log(f"[ROUTER] ERROR: Failed to import RouterManager: {e}")
            debug_log(f"[ROUTER] Make sure mcp-client/router_manager.py exists")
        
        # Register cleanup handler
        atexit.register(self.cleanup)
        
        debug_log(f"[ROUTER] RouterIntegration initialized")
        debug_log(f"   Instance ID: {self.instance_id}")
        debug_log(f"   Instance Name: {self.instance_name}")
        debug_log(f"   Callback URL: {self.callback_url}")
        debug_log(f"   Router URL: {self.router_url}")
    
    def ensure_router_running(self) -> bool:
        """
        Ensure router is running, start if needed.

        Returns:
            True if router is running, False otherwise
        """
        debug_log("[ROUTER] ensure_router_running() called")

        if not self.router_manager:
            debug_log("[ROUTER] ERROR: RouterManager not available")
            print("[ROUTER] ERROR: RouterManager not available", file=sys.stderr, flush=True)
            return False

        debug_log(f"[ROUTER] RouterManager available: {self.router_manager}")
        print(f"[ROUTER] RouterManager available: {self.router_manager}", file=sys.stderr, flush=True)

        try:
            debug_log("[ROUTER] Calling router_manager.ensure_router_available()...")
            print("[ROUTER] Calling router_manager.ensure_router_available()...", file=sys.stderr, flush=True)

            result = self.router_manager.ensure_router_available()

            debug_log(f"[ROUTER] ensure_router_available() returned: {result}")
            print(f"[ROUTER] ensure_router_available() returned: {result}", file=sys.stderr, flush=True)

            if result:
                debug_log("[ROUTER] ✅ Router is running")
                print("[ROUTER] ✅ Router is running", file=sys.stderr, flush=True)
            else:
                debug_log("[ROUTER] ❌ Failed to start router")
                print("[ROUTER] ❌ Failed to start router", file=sys.stderr, flush=True)
            return result
        except Exception as e:
            debug_log(f"[ROUTER] ERROR ensuring router running: {e}")
            print(f"[ROUTER] ERROR ensuring router running: {e}", file=sys.stderr, flush=True)
            import traceback
            debug_log(f"[ROUTER] Traceback: {traceback.format_exc()}")
            print(f"[ROUTER] Traceback: {traceback.format_exc()}", file=sys.stderr, flush=True)
            return False
    
    def register_instance(self) -> bool:
        """
        Register this MCP instance with the router.
        
        Returns:
            True if registration successful, False otherwise
        """
        if not requests:
            debug_log("[ROUTER] ERROR: requests library not available")
            return False
        
        # Ensure router is running first
        if not self.ensure_router_running():
            debug_log("[ROUTER] Cannot register: router not running")
            return False
        
        try:
            debug_log(f"[ROUTER] Registering instance: {self.instance_name}")
            
            response = requests.post(
                f"{self.router_url}/register",
                json={
                    "instance_id": self.instance_id,
                    "instance_name": self.instance_name,
                    "port": self.callback_port,
                    "callback_url": self.callback_url
                },
                timeout=5
            )
            
            if response.status_code == 200:
                self._registered = True
                debug_log(f"[ROUTER] ✅ Registration successful")
                debug_log(f"   Response: {response.json()}")
                return True
            else:
                debug_log(f"[ROUTER] ❌ Registration failed: HTTP {response.status_code}")
                debug_log(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            debug_log(f"[ROUTER] ❌ Connection error: Router not reachable at {self.router_url}")
            return False
        except requests.exceptions.Timeout:
            debug_log(f"[ROUTER] ❌ Timeout: Router did not respond within 5 seconds")
            return False
        except Exception as e:
            debug_log(f"[ROUTER] ❌ Registration error: {e}")
            import traceback
            debug_log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def send_to_telegram(
        self,
        session_id: str,
        message: str,
        images: Optional[List[str]] = None
    ) -> bool:
        """
        Send message to Telegram via router.
        
        Args:
            session_id: Unique session identifier
            message: Message text (supports Markdown)
            images: Optional list of base64-encoded images
        
        Returns:
            True if message sent successfully, False otherwise
        """
        if not requests:
            debug_log("[ROUTER] ERROR: requests library not available")
            return False
        
        if not self._registered:
            debug_log("[ROUTER] WARNING: Not registered, attempting registration...")
            if not self.register_instance():
                debug_log("[ROUTER] Cannot send: registration failed")
                return False
        
        try:
            payload = {
                "instance_id": self.instance_id,
                "session_id": session_id,
                "message": message,
                "context": {}
            }
            
            if images:
                payload["images"] = images
                debug_log(f"[ROUTER] Sending message with {len(images)} images")
            
            debug_log(f"[ROUTER] Sending to Telegram: session {session_id[:8]}...")
            
            response = requests.post(
                f"{self.router_url}/send",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                debug_log(f"[ROUTER] ✅ Message sent successfully")
                result = response.json()
                debug_log(f"   Telegram message ID: {result.get('telegram_msg_id')}")
                return True
            else:
                debug_log(f"[ROUTER] ❌ Send failed: HTTP {response.status_code}")
                debug_log(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            debug_log(f"[ROUTER] ❌ Connection error: Router not reachable")
            return False
        except requests.exceptions.Timeout:
            debug_log(f"[ROUTER] ❌ Timeout: Router did not respond within 10 seconds")
            return False
        except Exception as e:
            debug_log(f"[ROUTER] ❌ Send error: {e}")
            import traceback
            debug_log(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def deregister_instance(self) -> bool:
        """
        Deregister this MCP instance from the router.
        
        Returns:
            True if deregistration successful, False otherwise
        """
        if not requests:
            return False
        
        if not self._registered:
            debug_log("[ROUTER] Not registered, skipping deregistration")
            return True
        
        try:
            debug_log(f"[ROUTER] Deregistering instance: {self.instance_name}")
            
            response = requests.post(
                f"{self.router_url}/deregister",
                json={"instance_id": self.instance_id},
                timeout=5
            )
            
            if response.status_code == 200:
                self._registered = False
                debug_log(f"[ROUTER] ✅ Deregistration successful")
                return True
            else:
                debug_log(f"[ROUTER] ⚠️ Deregistration failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            debug_log(f"[ROUTER] ⚠️ Deregistration error: {e}")
            return False
    
    def cleanup(self):
        """Cleanup on exit - deregister from router."""
        if self._registered:
            debug_log("[ROUTER] Cleanup: Deregistering from router...")
            self.deregister_instance()
    
    def is_registered(self) -> bool:
        """Check if instance is registered with router."""
        return self._registered
    
    def get_instance_info(self) -> dict:
        """Get instance information."""
        return {
            "instance_id": self.instance_id,
            "instance_name": self.instance_name,
            "callback_url": self.callback_url,
            "router_url": self.router_url,
            "registered": self._registered
        }

