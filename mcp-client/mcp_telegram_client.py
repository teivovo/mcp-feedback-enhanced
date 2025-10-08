"""
MCP Telegram Client Library
Provides integration between MCP servers and the Telegram Router
Auto-starts router if not running, auto-stops when client shuts down
"""
import asyncio
import aiohttp
from aiohttp import web
import uuid
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from router_manager import get_router_manager

class MCPTelegramClient:
    def __init__(
        self,
        instance_name: str,
        callback_port: int = 3001,
        router_url: str = None,
        auto_cleanup: bool = True
    ):
        self.instance_id = f"mcp-{callback_port}"
        self.instance_name = instance_name
        self.callback_port = callback_port
        self.router_url = router_url or os.getenv('ROUTER_URL', 'http://localhost:8080')
        self.callback_url = f"http://localhost:{callback_port}/callback"
        self.auto_cleanup = auto_cleanup
        
        # Session management
        self.pending_sessions: Dict[str, asyncio.Future] = {}
        
        # Web server
        self.app = web.Application()
        self.app.router.add_post('/callback', self.handle_callback)
        self.app.router.add_get('/health', self.handle_health)
        self.runner = None
        self.site = None
        
        # HTTP session for router communication
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Router manager
        self.router_manager = get_router_manager()
        
        # Shutdown flag
        self._shutting_down = False
    
    async def start(self):
        """Start the client - ensures router is running and registers with it"""
        # Ensure router is available
        print("[CLIENT] Ensuring router is available...")
        if not self.router_manager.ensure_router_available():
            raise RuntimeError("Failed to start router")
        
        # Start callback server
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, 'localhost', self.callback_port)
        await self.site.start()
        print(f"[OK] Callback server listening on port {self.callback_port}")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession()
        
        # Register with router
        await self._register_with_router()
    
    async def stop(self):
        """Stop the client and optionally stop router"""
        if self._shutting_down:
            return
        self._shutting_down = True
        
        print(f"\n[SHUTDOWN] Stopping {self.instance_name}...")
        
        # Clean up pending sessions
        for session_id, future in self.pending_sessions.items():
            if not future.done():
                future.set_exception(Exception("Client shutting down"))
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Stop callback server
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        
        # Stop router if we're the last instance
        if self.auto_cleanup:
            self.router_manager.stop_router()
        
        print(f"[SHUTDOWN] {self.instance_name} stopped ✓")
    
    async def _register_with_router(self, max_retries: int = 3):
        """Register this instance with the router"""
        for attempt in range(max_retries):
            try:
                async with self.session.post(
                    f'{self.router_url}/register',
                    json={
                        'instance_id': self.instance_id,
                        'instance_name': self.instance_name,
                        'port': self.callback_port,
                        'callback_url': self.callback_url
                    },
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        print(f"✅ Registered with router as {self.instance_name}")
                        return
                    else:
                        text = await response.text()
                        print(f"[WARN] Registration failed: {text}")
            except Exception as e:
                print(f"[WARN] Registration attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        
        raise RuntimeError("Failed to register with router after multiple attempts")
    
    async def handle_callback(self, request):
        """Handle incoming callbacks from router"""
        try:
            data = await request.json()
            session_id = data.get('session_id')
            message = data.get('message', '')
            image_urls = data.get('image_urls', [])
            
            if not session_id:
                return web.json_response({'error': 'Missing session_id'}, status=400)
            
            # Format response with text and images
            formatted_response = self._format_reply(message, image_urls)
            
            print(f"📥 Received reply for session {session_id}")
            print(f"   Text: {message if message else '(none)'}")
            print(f"   Images: {len(image_urls)}")
            
            # Resolve the pending future
            if session_id in self.pending_sessions:
                future = self.pending_sessions.pop(session_id)
                if not future.done():
                    future.set_result(formatted_response)
            else:
                print(f"[WARN] No pending session found for {session_id}")
            
            return web.json_response({'status': 'processed'})
            
        except Exception as e:
            print(f"[ERROR] Callback handler error: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    def _format_reply(self, message: str, image_urls: list) -> str:
        """Format reply with text and image instructions"""
        parts = []
        
        # Add text if present
        if message and message.strip():
            parts.append(f"User replied: \"{message}\"")
        
        # Add image instructions if present
        if image_urls:
            parts.append(f"\n📸 Images attached ({len(image_urls)}):")
            for i, url in enumerate(image_urls, 1):
                parts.append(f"  {i}. {url}")
            parts.append("\n⚠️ IMPORTANT: Use your browser/web tool to view these images at the URLs above.")
        
        return "\n".join(parts) if parts else "(empty reply)"
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'instance_id': self.instance_id,
            'instance_name': self.instance_name
        })
    
    async def send_and_wait_for_reply(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        reply_markup: Optional[Dict[str, Any]] = None,
        images: Optional[list] = None
    ) -> str:
        """
        Send a message to Telegram and wait for user reply
        
        Args:
            message: Message to send
            context: Optional context data
            timeout: Timeout in seconds (default: 5 minutes)
            reply_markup: Optional Telegram reply markup (inline keyboard, etc.)
            images: Optional list of base64-encoded images
        
        Returns:
            User's reply from Telegram
        
        Raises:
            TimeoutError: If no reply within timeout
            RuntimeError: If send fails
        """
        session_id = str(uuid.uuid4())
        
        # Create future for this session
        future = asyncio.Future()
        self.pending_sessions[session_id] = future
        
        try:
            # Prepare payload
            payload = {
                'instance_id': self.instance_id,
                'session_id': session_id,
                'message': message,
                'context': context or {},
                'reply_markup': reply_markup
            }
            
            # Add images if provided
            if images:
                payload['images'] = images
            
            # Send to router
            async with self.session.post(
                f'{self.router_url}/send',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Failed to send message: {text}")
            
            # Wait for reply with timeout
            try:
                reply = await asyncio.wait_for(future, timeout=timeout)
                return reply
            except asyncio.TimeoutError:
                self.pending_sessions.pop(session_id, None)
                raise TimeoutError(f"No reply received within {timeout} seconds")
                
        except Exception as e:
            self.pending_sessions.pop(session_id, None)
            raise
    
    async def send_notification(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        images: Optional[list] = None
    ):
        """
        Send a notification to Telegram without waiting for reply
        
        Args:
            message: Message to send
            context: Optional context data
            images: Optional list of base64-encoded images
        """
        try:
            # Prepare payload
            payload = {
                'instance_id': self.instance_id,
                'session_id': str(uuid.uuid4()),
                'message': message,
                'context': context or {},
                'notification_only': True
            }
            
            # Add images if provided
            if images:
                payload['images'] = images
            
            async with self.session.post(
                f'{self.router_url}/send',
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Failed to send notification: {text}")
        except Exception as e:
            print(f"[ERROR] Failed to send notification: {e}")
            raise
    
    async def request_confirmation(
        self,
        question: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 300,
        images: Optional[list] = None
    ) -> bool:
        """
        Request yes/no confirmation from user
        
        Args:
            question: Question to ask
            context: Optional context data
            timeout: Timeout in seconds
            images: Optional list of base64-encoded images
        
        Returns:
            True if user confirms, False otherwise
        """
        reply = await self.send_and_wait_for_reply(
            f"❓ {question}\n\n(Reply 'yes' or 'no')",
            context=context,
            timeout=timeout,
            images=images
        )
        
        return reply.lower().strip() in ['yes', 'y', 'ok', 'sure', 'confirm']
    
    async def request_input(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: int = 300
    ) -> str:
        """
        Request input from user
        
        Args:
            prompt: Prompt to show
            context: Optional context data
            timeout: Timeout in seconds
        
        Returns:
            User's input
        """
        return await self.send_and_wait_for_reply(
            f"📝 {prompt}",
            context=context,
            timeout=timeout
        )