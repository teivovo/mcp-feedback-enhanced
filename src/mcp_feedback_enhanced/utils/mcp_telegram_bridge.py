#!/usr/bin/env python3
"""
MCP-Telegram Bidirectional Bridge
=================================

Comprehensive bridge system that connects MCP feedback collection with Telegram messaging.
Provides bidirectional communication between AI assistant and user through Telegram Bot API,
enabling remote monitoring and feedback collection.

Key Features:
- Real-time MCP message forwarding to Telegram
- Telegram response routing back to MCP feedback system
- Session management and message correlation
- Multiple concurrent session support
- WebSocket integration for live updates
- User notification system
- Message threading and context preservation

Author: MCP Feedback Enhanced Team
"""

import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum

from ..debug import debug_log
from .telegram_manager import TelegramBotManager
from .logging_middleware import MCPLoggingMiddleware, MCPLogEntry, MCPEventType
from .message_chunker import MessageChunker, chunk_text, chunk_mcp_response


class BridgeStatus(Enum):
    """Bridge connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DISABLED = "disabled"


class MessageType(Enum):
    """Types of messages in the bridge"""
    MCP_TO_TELEGRAM = "mcp_to_telegram"
    TELEGRAM_TO_MCP = "telegram_to_mcp"
    SYSTEM_NOTIFICATION = "system_notification"
    SESSION_UPDATE = "session_update"


@dataclass
class BridgeMessage:
    """Message structure for bridge communication"""
    id: str
    message_type: MessageType
    timestamp: str
    session_id: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    telegram_message_id: Optional[int] = None
    mcp_call_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BridgeMessage':
        """Create from dictionary"""
        data['message_type'] = MessageType(data['message_type'])
        return cls(**data)


@dataclass
class TelegramSession:
    """Telegram session information"""
    session_id: str
    chat_id: str
    project_directory: str
    start_time: datetime
    last_activity: datetime
    active_mcp_calls: Set[str]
    pending_responses: Dict[str, Dict[str, Any]]
    user_context: Dict[str, Any]
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """Check if session is expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


class MCPTelegramBridge:
    """
    Bidirectional bridge between MCP feedback system and Telegram.
    
    This bridge enables real-time communication by:
    1. Forwarding MCP tool calls and responses to Telegram
    2. Routing Telegram user responses back to MCP feedback system
    3. Managing session context and message correlation
    4. Providing WebSocket updates for live monitoring
    """
    
    def __init__(self, 
                 telegram_manager: TelegramBotManager,
                 logging_middleware: MCPLoggingMiddleware,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP-Telegram bridge.
        
        Args:
            telegram_manager: TelegramBotManager instance
            logging_middleware: MCPLoggingMiddleware instance
            config: Bridge configuration
        """
        self.telegram_manager = telegram_manager
        self.logging_middleware = logging_middleware
        self.config = config or {}
        
        # Bridge state
        self.status = BridgeStatus.DISCONNECTED
        self.is_running = False
        
        # Session management
        self.active_sessions: Dict[str, TelegramSession] = {}
        self.message_correlation: Dict[str, str] = {}  # telegram_msg_id -> mcp_call_id
        self.pending_feedback: Dict[str, Dict[str, Any]] = {}  # session_id -> feedback_data
        
        # WebSocket connections for live updates
        self.websocket_connections: Set[Any] = set()
        
        # Event handlers
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            message_type: [] for message_type in MessageType
        }
        
        # Configuration
        self.session_timeout_minutes = self.config.get('session_timeout_minutes', 30)
        self.max_concurrent_sessions = self.config.get('max_concurrent_sessions', 10)
        self.enable_auto_forwarding = self.config.get('enable_auto_forwarding', True)
        self.message_format_config = self.config.get('message_format', {
            'include_session_id': True,
            'include_timestamp': True,
            'include_project_path': False,
            'include_details': True
        })

        # Initialize message chunker
        chunker_config = self.config.get('chunker', {})
        self.message_chunker = MessageChunker(
            max_chunk_size=chunker_config.get('max_chunk_size', MessageChunker.SAFE_MESSAGE_LENGTH),
            preserve_code_blocks=chunker_config.get('preserve_code_blocks', True),
            preserve_markdown=chunker_config.get('preserve_markdown', True),
            add_navigation=chunker_config.get('add_navigation', True),
            add_previews=chunker_config.get('add_previews', True)
        )

        debug_log("MCPTelegramBridge initialized", "BRIDGE")
    
    async def start(self) -> bool:
        """
        Start the bridge and begin monitoring.
        
        Returns:
            True if started successfully
        """
        try:
            self.status = BridgeStatus.CONNECTING
            debug_log("Starting MCP-Telegram bridge", "BRIDGE")
            
            # Test Telegram connection
            success, message = await self.telegram_manager.test_connection()
            if not success:
                debug_log(f"Telegram connection failed: {message}", "BRIDGE")
                self.status = BridgeStatus.ERROR
                return False
            
            # Set up logging middleware event handler
            self.logging_middleware.set_telegram_callback(self._handle_mcp_event)
            
            # Start background tasks
            self.is_running = True
            asyncio.create_task(self._session_cleanup_task())
            asyncio.create_task(self._telegram_polling_task())
            
            self.status = BridgeStatus.CONNECTED
            debug_log("MCP-Telegram bridge started successfully", "BRIDGE")
            
            # Send startup notification
            await self._send_system_notification("🚀 MCP-Telegram Bridge Connected", {
                "status": "connected",
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            debug_log(f"Failed to start bridge: {e}", "BRIDGE")
            self.status = BridgeStatus.ERROR
            return False
    
    async def stop(self):
        """Stop the bridge and cleanup resources"""
        debug_log("Stopping MCP-Telegram bridge", "BRIDGE")
        
        self.is_running = False
        self.status = BridgeStatus.DISCONNECTED
        
        # Send shutdown notification
        await self._send_system_notification("🔌 MCP-Telegram Bridge Disconnected", {
            "status": "disconnected",
            "timestamp": datetime.now().isoformat(),
            "active_sessions": len(self.active_sessions)
        })
        
        # Cleanup sessions
        self.active_sessions.clear()
        self.message_correlation.clear()
        self.pending_feedback.clear()
        
        debug_log("MCP-Telegram bridge stopped", "BRIDGE")
    
    def add_message_handler(self, message_type: MessageType, handler: Callable[[BridgeMessage], None]):
        """Add a message handler for specific message types"""
        self.message_handlers[message_type].append(handler)
        debug_log(f"Added message handler for {message_type.value}", "BRIDGE")
    
    def add_websocket_connection(self, websocket):
        """Add a WebSocket connection for live updates"""
        self.websocket_connections.add(websocket)
        debug_log(f"Added WebSocket connection, total: {len(self.websocket_connections)}", "BRIDGE")
    
    def remove_websocket_connection(self, websocket):
        """Remove a WebSocket connection"""
        self.websocket_connections.discard(websocket)
        debug_log(f"Removed WebSocket connection, total: {len(self.websocket_connections)}", "BRIDGE")
    
    async def create_session(self, 
                           session_id: str,
                           chat_id: str,
                           project_directory: str,
                           user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a new Telegram session.
        
        Args:
            session_id: Unique session identifier
            chat_id: Telegram chat ID
            project_directory: Project directory path
            user_context: Additional user context
            
        Returns:
            True if session created successfully
        """
        try:
            # Check session limits
            if len(self.active_sessions) >= self.max_concurrent_sessions:
                debug_log(f"Maximum concurrent sessions reached: {self.max_concurrent_sessions}", "BRIDGE")
                return False
            
            # Create session
            session = TelegramSession(
                session_id=session_id,
                chat_id=chat_id,
                project_directory=project_directory,
                start_time=datetime.now(),
                last_activity=datetime.now(),
                active_mcp_calls=set(),
                pending_responses={},
                user_context=user_context or {}
            )
            
            self.active_sessions[session_id] = session
            
            # Send session start notification
            await self._send_session_notification(session_id, "🎯 New MCP Session Started", {
                "session_id": session_id,
                "project_directory": project_directory,
                "start_time": session.start_time.isoformat()
            })
            
            debug_log(f"Created Telegram session: {session_id}", "BRIDGE")
            return True
            
        except Exception as e:
            debug_log(f"Failed to create session {session_id}: {e}", "BRIDGE")
            return False
    
    async def end_session(self, session_id: str) -> bool:
        """
        End a Telegram session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                debug_log(f"Session not found: {session_id}", "BRIDGE")
                return False
            
            # Send session end notification
            duration = datetime.now() - session.start_time
            await self._send_session_notification(session_id, "🏁 MCP Session Completed", {
                "session_id": session_id,
                "duration_minutes": int(duration.total_seconds() / 60),
                "mcp_calls_count": len(session.active_mcp_calls),
                "end_time": datetime.now().isoformat()
            })
            
            # Cleanup session data
            del self.active_sessions[session_id]
            self.pending_feedback.pop(session_id, None)
            
            # Cleanup message correlations
            to_remove = [msg_id for msg_id, call_id in self.message_correlation.items() 
                        if call_id in session.active_mcp_calls]
            for msg_id in to_remove:
                del self.message_correlation[msg_id]
            
            debug_log(f"Ended Telegram session: {session_id}", "BRIDGE")
            return True
            
        except Exception as e:
            debug_log(f"Failed to end session {session_id}: {e}", "BRIDGE")
            return False
    
    async def send_mcp_message_to_telegram(self,
                                         session_id: str,
                                         mcp_call_id: str,
                                         message: str,
                                         metadata: Optional[Dict[str, Any]] = None) -> Optional[List[int]]:
        """
        Send an MCP message to Telegram with intelligent chunking.

        Args:
            session_id: Session identifier
            mcp_call_id: MCP call identifier
            message: Message content
            metadata: Additional metadata

        Returns:
            List of Telegram message IDs if sent successfully
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                debug_log(f"Session not found for MCP message: {session_id}", "BRIDGE")
                return None

            # Chunk the message intelligently
            chunks = self.message_chunker.chunk_message(message)

            # If message is large, create a summary chunk first
            if len(chunks) > 3:
                summary_chunk = self.message_chunker.create_summary_chunk(chunks, message)
                chunks.insert(0, summary_chunk)

            telegram_msg_ids = []

            # Send each chunk
            for i, chunk in enumerate(chunks):
                chunk_message = chunk.to_telegram_message(include_metadata=True)

                # Send chunk to Telegram
                result = await self.telegram_manager.send_message(chunk_message, parse_mode=None)

                if result:
                    telegram_msg_id = result['message_id']
                    telegram_msg_ids.append(telegram_msg_id)

                    # Store correlation for each chunk
                    chunk_call_id = f"{mcp_call_id}_chunk_{i}"
                    self.message_correlation[str(telegram_msg_id)] = chunk_call_id
                    session.active_mcp_calls.add(chunk_call_id)

                    # Small delay between chunks to avoid rate limiting
                    if i < len(chunks) - 1:
                        await asyncio.sleep(0.5)
                else:
                    debug_log(f"Failed to send chunk {i+1}/{len(chunks)}", "BRIDGE")
                    break

            if telegram_msg_ids:
                session.update_activity()

                # Create bridge message for the complete message
                bridge_msg = BridgeMessage(
                    id=str(uuid.uuid4()),
                    message_type=MessageType.MCP_TO_TELEGRAM,
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    content=message,
                    metadata={
                        **(metadata or {}),
                        "chunks_sent": len(telegram_msg_ids),
                        "total_chunks": len(chunks),
                        "telegram_message_ids": telegram_msg_ids
                    },
                    telegram_message_id=telegram_msg_ids[0] if telegram_msg_ids else None,
                    mcp_call_id=mcp_call_id
                )

                # Notify handlers
                await self._notify_message_handlers(bridge_msg)

                # Send WebSocket update
                await self._send_websocket_update({
                    "type": "mcp_message_sent",
                    "session_id": session_id,
                    "telegram_message_ids": telegram_msg_ids,
                    "mcp_call_id": mcp_call_id,
                    "chunks_sent": len(telegram_msg_ids)
                })

                debug_log(f"Sent MCP message to Telegram in {len(telegram_msg_ids)} chunks: {telegram_msg_ids}", "BRIDGE")
                return telegram_msg_ids

            return None

        except Exception as e:
            debug_log(f"Failed to send MCP message to Telegram: {e}", "BRIDGE")
            return None
    
    async def handle_telegram_response(self, 
                                     telegram_message: Dict[str, Any]) -> bool:
        """
        Handle a response from Telegram and route it to MCP.
        
        Args:
            telegram_message: Telegram message data
            
        Returns:
            True if handled successfully
        """
        try:
            chat_id = str(telegram_message.get('chat', {}).get('id', ''))
            message_text = telegram_message.get('text', '')
            reply_to_message_id = telegram_message.get('reply_to_message', {}).get('message_id')
            
            # Find session by chat_id
            session = None
            session_id = None
            for sid, sess in self.active_sessions.items():
                if sess.chat_id == chat_id:
                    session = sess
                    session_id = sid
                    break
            
            if not session:
                debug_log(f"No active session found for chat: {chat_id}", "BRIDGE")
                return False
            
            # Find MCP call correlation
            mcp_call_id = None
            if reply_to_message_id:
                mcp_call_id = self.message_correlation.get(str(reply_to_message_id))
            
            # Store feedback for MCP system
            feedback_data = {
                "interactive_feedback": message_text,
                "telegram_message_id": telegram_message.get('message_id'),
                "timestamp": datetime.now().isoformat(),
                "mcp_call_id": mcp_call_id,
                "user_id": telegram_message.get('from', {}).get('id')
            }
            
            self.pending_feedback[session_id] = feedback_data
            session.update_activity()
            
            # Create bridge message
            bridge_msg = BridgeMessage(
                id=str(uuid.uuid4()),
                message_type=MessageType.TELEGRAM_TO_MCP,
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                content=message_text,
                metadata=feedback_data,
                telegram_message_id=telegram_message.get('message_id'),
                mcp_call_id=mcp_call_id,
                user_id=str(telegram_message.get('from', {}).get('id', ''))
            )
            
            # Notify handlers
            await self._notify_message_handlers(bridge_msg)
            
            # Send WebSocket update
            await self._send_websocket_update({
                "type": "telegram_response_received",
                "session_id": session_id,
                "message_text": message_text,
                "mcp_call_id": mcp_call_id
            })
            
            debug_log(f"Handled Telegram response for session: {session_id}", "BRIDGE")
            return True
            
        except Exception as e:
            debug_log(f"Failed to handle Telegram response: {e}", "BRIDGE")
            return False
    
    def get_pending_feedback(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get pending feedback for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Feedback data if available
        """
        return self.pending_feedback.get(session_id)
    
    def clear_pending_feedback(self, session_id: str):
        """Clear pending feedback for a session"""
        self.pending_feedback.pop(session_id, None)
    
    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status and statistics"""
        return {
            "status": self.status.value,
            "is_running": self.is_running,
            "active_sessions": len(self.active_sessions),
            "pending_feedback": len(self.pending_feedback),
            "message_correlations": len(self.message_correlation),
            "websocket_connections": len(self.websocket_connections),
            "config": {
                "session_timeout_minutes": self.session_timeout_minutes,
                "max_concurrent_sessions": self.max_concurrent_sessions,
                "enable_auto_forwarding": self.enable_auto_forwarding
            }
        }
    
    async def _handle_mcp_event(self, log_entry: MCPLogEntry):
        """Handle MCP events from logging middleware"""
        try:
            if not self.enable_auto_forwarding or self.status != BridgeStatus.CONNECTED:
                return
            
            # Only forward specific event types
            if log_entry.event_type not in [MCPEventType.TOOL_CALL_START, 
                                          MCPEventType.TOOL_CALL_END, 
                                          MCPEventType.TOOL_CALL_ERROR]:
                return
            
            # Find active session (for now, use the first active session)
            # In a real implementation, you'd correlate by session_id
            if not self.active_sessions:
                return
            
            session_id = list(self.active_sessions.keys())[0]
            session = self.active_sessions[session_id]
            
            # Format message for Telegram
            telegram_message = log_entry.to_telegram_message(
                include_details=self.message_format_config.get('include_details', True)
            )
            
            # Send to Telegram
            await self.send_mcp_message_to_telegram(
                session_id=session_id,
                mcp_call_id=f"{log_entry.tool_name}_{log_entry.timestamp}",
                message=telegram_message,
                metadata={
                    "event_type": log_entry.event_type.value,
                    "tool_name": log_entry.tool_name,
                    "success": log_entry.success
                }
            )
            
        except Exception as e:
            debug_log(f"Error handling MCP event: {e}", "BRIDGE")
    
    async def _telegram_polling_task(self):
        """Background task for polling Telegram messages"""
        try:
            while self.is_running:
                try:
                    # Get updates from Telegram
                    updates = await self.telegram_manager.get_updates(timeout=10)
                    
                    for update in updates:
                        if 'message' in update:
                            await self.handle_telegram_response(update['message'])
                    
                    # Small delay to prevent excessive polling
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    debug_log(f"Error in Telegram polling: {e}", "BRIDGE")
                    await asyncio.sleep(5)  # Wait longer on error
                    
        except Exception as e:
            debug_log(f"Telegram polling task failed: {e}", "BRIDGE")
    
    async def _session_cleanup_task(self):
        """Background task for cleaning up expired sessions"""
        try:
            while self.is_running:
                try:
                    current_time = datetime.now()
                    expired_sessions = []
                    
                    for session_id, session in self.active_sessions.items():
                        if session.is_expired(self.session_timeout_minutes):
                            expired_sessions.append(session_id)
                    
                    for session_id in expired_sessions:
                        debug_log(f"Cleaning up expired session: {session_id}", "BRIDGE")
                        await self.end_session(session_id)
                    
                    # Run cleanup every 5 minutes
                    await asyncio.sleep(300)
                    
                except Exception as e:
                    debug_log(f"Error in session cleanup: {e}", "BRIDGE")
                    await asyncio.sleep(60)  # Wait longer on error
                    
        except Exception as e:
            debug_log(f"Session cleanup task failed: {e}", "BRIDGE")
    
    async def _send_system_notification(self, message: str, metadata: Dict[str, Any]):
        """Send a system notification to Telegram"""
        try:
            if self.status == BridgeStatus.CONNECTED:
                await self.telegram_manager.send_message(message, parse_mode=None)
                
                # Create bridge message
                bridge_msg = BridgeMessage(
                    id=str(uuid.uuid4()),
                    message_type=MessageType.SYSTEM_NOTIFICATION,
                    timestamp=datetime.now().isoformat(),
                    content=message,
                    metadata=metadata
                )
                
                await self._notify_message_handlers(bridge_msg)
                
        except Exception as e:
            debug_log(f"Failed to send system notification: {e}", "BRIDGE")
    
    async def _send_session_notification(self, session_id: str, message: str, metadata: Dict[str, Any]):
        """Send a session-specific notification"""
        try:
            session = self.active_sessions.get(session_id)
            if session and self.status == BridgeStatus.CONNECTED:
                await self.telegram_manager.send_message(message, parse_mode=None)
                
                # Create bridge message
                bridge_msg = BridgeMessage(
                    id=str(uuid.uuid4()),
                    message_type=MessageType.SESSION_UPDATE,
                    timestamp=datetime.now().isoformat(),
                    session_id=session_id,
                    content=message,
                    metadata=metadata
                )
                
                await self._notify_message_handlers(bridge_msg)
                
        except Exception as e:
            debug_log(f"Failed to send session notification: {e}", "BRIDGE")
    
    async def _notify_message_handlers(self, bridge_msg: BridgeMessage):
        """Notify all registered message handlers"""
        try:
            handlers = self.message_handlers.get(bridge_msg.message_type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(bridge_msg)
                    else:
                        handler(bridge_msg)
                except Exception as e:
                    debug_log(f"Error in message handler: {e}", "BRIDGE")
                    
        except Exception as e:
            debug_log(f"Error notifying message handlers: {e}", "BRIDGE")
    
    async def _send_websocket_update(self, data: Dict[str, Any]):
        """Send update to all connected WebSocket clients"""
        try:
            if not self.websocket_connections:
                return
            
            message = json.dumps(data)
            disconnected = set()
            
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.add(websocket)
            
            # Remove disconnected WebSockets
            for websocket in disconnected:
                self.websocket_connections.discard(websocket)
                
        except Exception as e:
            debug_log(f"Error sending WebSocket update: {e}", "BRIDGE")


# Global bridge instance
_global_bridge: Optional[MCPTelegramBridge] = None


def get_bridge() -> Optional[MCPTelegramBridge]:
    """Get the global bridge instance"""
    return _global_bridge


def initialize_bridge(telegram_manager: TelegramBotManager,
                     logging_middleware: MCPLoggingMiddleware,
                     config: Optional[Dict[str, Any]] = None) -> MCPTelegramBridge:
    """Initialize the global bridge instance"""
    global _global_bridge
    
    _global_bridge = MCPTelegramBridge(
        telegram_manager=telegram_manager,
        logging_middleware=logging_middleware,
        config=config
    )
    
    debug_log("Global MCP-Telegram bridge initialized", "BRIDGE")
    return _global_bridge


# Convenience functions
async def start_bridge() -> bool:
    """Start the global bridge"""
    bridge = get_bridge()
    if bridge:
        return await bridge.start()
    return False


async def stop_bridge():
    """Stop the global bridge"""
    bridge = get_bridge()
    if bridge:
        await bridge.stop()


async def create_telegram_session(session_id: str, 
                                chat_id: str, 
                                project_directory: str,
                                user_context: Optional[Dict[str, Any]] = None) -> bool:
    """Create a new Telegram session"""
    bridge = get_bridge()
    if bridge:
        return await bridge.create_session(session_id, chat_id, project_directory, user_context)
    return False


async def end_telegram_session(session_id: str) -> bool:
    """End a Telegram session"""
    bridge = get_bridge()
    if bridge:
        return await bridge.end_session(session_id)
    return False


def get_telegram_feedback(session_id: str) -> Optional[Dict[str, Any]]:
    """Get pending Telegram feedback for a session"""
    bridge = get_bridge()
    if bridge:
        return bridge.get_pending_feedback(session_id)
    return None


def clear_telegram_feedback(session_id: str):
    """Clear pending Telegram feedback for a session"""
    bridge = get_bridge()
    if bridge:
        bridge.clear_pending_feedback(session_id)