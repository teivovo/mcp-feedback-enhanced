#!/usr/bin/env python3
"""
MCP Logging Middleware
======================

Comprehensive logging middleware for capturing all MCP tool calls and responses
without interfering with the JSON-RPC protocol. This middleware serves as the
data source for Telegram integration and remote monitoring.

Key Features:
- Non-intrusive MCP protocol monitoring
- Structured logging for Telegram forwarding
- Tool call and response capture
- Performance monitoring
- Error tracking and analysis
- Configurable log levels and formats

Author: MCP Feedback Enhanced Team
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from ..debug import debug_log


class LogLevel(Enum):
    """Log levels for MCP middleware"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MCPEventType(Enum):
    """Types of MCP events to log"""
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    TOOL_CALL_ERROR = "tool_call_error"
    RESPONSE_SENT = "response_sent"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SYSTEM_INFO = "system_info"


@dataclass
class MCPLogEntry:
    """Structured log entry for MCP events"""
    timestamp: str
    event_type: MCPEventType
    tool_name: Optional[str] = None
    session_id: Optional[str] = None
    project_directory: Optional[str] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        return result

    def to_json(self) -> str:
        """Convert log entry to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def to_telegram_message(self, include_details: bool = True) -> str:
        """Format log entry for Telegram message"""
        lines = []
        
        # Header with emoji based on event type
        emoji_map = {
            MCPEventType.TOOL_CALL_START: "🔧",
            MCPEventType.TOOL_CALL_END: "✅",
            MCPEventType.TOOL_CALL_ERROR: "❌",
            MCPEventType.RESPONSE_SENT: "📤",
            MCPEventType.SESSION_START: "🚀",
            MCPEventType.SESSION_END: "🏁",
            MCPEventType.SYSTEM_INFO: "ℹ️"
        }
        
        emoji = emoji_map.get(self.event_type, "📋")
        lines.append(f"{emoji} **MCP Event: {self.event_type.value.replace('_', ' ').title()}**")
        lines.append("")
        
        # Basic information
        if self.tool_name:
            lines.append(f"**Tool:** `{self.tool_name}`")
        
        lines.append(f"**Time:** {self.timestamp}")
        
        if self.session_id:
            session_short = self.session_id[:8] + "..." if len(self.session_id) > 8 else self.session_id
            lines.append(f"**Session:** `{session_short}`")
        
        if self.project_directory:
            # Truncate long paths
            if len(self.project_directory) > 50:
                path_display = "..." + self.project_directory[-47:]
            else:
                path_display = self.project_directory
            lines.append(f"**Project:** `{path_display}`")
        
        # Status and performance
        status = "✅ Success" if self.success else "❌ Failed"
        lines.append(f"**Status:** {status}")
        
        if self.duration_ms is not None:
            if self.duration_ms < 1000:
                duration_str = f"{self.duration_ms:.1f}ms"
            else:
                duration_str = f"{self.duration_ms/1000:.2f}s"
            lines.append(f"**Duration:** {duration_str}")
        
        # Error information
        if not self.success and self.error_message:
            lines.append("")
            lines.append("**Error:**")
            # Truncate very long error messages
            error_msg = self.error_message
            if len(error_msg) > 200:
                error_msg = error_msg[:197] + "..."
            lines.append(f"```\n{error_msg}\n```")
        
        # Additional details if requested
        if include_details:
            if self.request_data:
                lines.append("")
                lines.append("**Request Data:**")
                request_str = json.dumps(self.request_data, ensure_ascii=False, indent=2)
                if len(request_str) > 300:
                    request_str = request_str[:297] + "..."
                lines.append(f"```json\n{request_str}\n```")
            
            if self.response_data and self.success:
                lines.append("")
                lines.append("**Response:**")
                response_str = json.dumps(self.response_data, ensure_ascii=False, indent=2)
                if len(response_str) > 300:
                    response_str = response_str[:297] + "..."
                lines.append(f"```json\n{response_str}\n```")
        
        return "\n".join(lines)


class MCPLoggingMiddleware:
    """
    Comprehensive MCP logging middleware for capturing tool calls and responses.
    
    This middleware operates transparently without interfering with the MCP
    JSON-RPC protocol, providing structured logging for Telegram integration.
    """
    
    def __init__(self, 
                 log_level: LogLevel = LogLevel.INFO,
                 enable_telegram_forwarding: bool = False,
                 max_log_entries: int = 1000,
                 include_request_data: bool = True,
                 include_response_data: bool = True):
        """
        Initialize the MCP logging middleware.
        
        Args:
            log_level: Minimum log level to capture
            enable_telegram_forwarding: Whether to enable Telegram forwarding
            max_log_entries: Maximum number of log entries to keep in memory
            include_request_data: Whether to include request data in logs
            include_response_data: Whether to include response data in logs
        """
        self.log_level = log_level
        self.enable_telegram_forwarding = enable_telegram_forwarding
        self.max_log_entries = max_log_entries
        self.include_request_data = include_request_data
        self.include_response_data = include_response_data
        
        # Log storage
        self.log_entries: List[MCPLogEntry] = []
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        
        # Statistics
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_duration_ms': 0.0,
            'session_count': 0
        }
        
        # Event handlers
        self.event_handlers: Dict[MCPEventType, List[Callable]] = {
            event_type: [] for event_type in MCPEventType
        }
        
        # Telegram forwarding callback
        self.telegram_callback: Optional[Callable[[MCPLogEntry], None]] = None
        
        debug_log("MCPLoggingMiddleware initialized", "MIDDLEWARE")
    
    def add_event_handler(self, event_type: MCPEventType, handler: Callable[[MCPLogEntry], None]):
        """Add an event handler for specific MCP events"""
        self.event_handlers[event_type].append(handler)
        debug_log(f"Added event handler for {event_type.value}", "MIDDLEWARE")
    
    def set_telegram_callback(self, callback: Callable[[MCPLogEntry], None]):
        """Set the callback function for Telegram forwarding"""
        self.telegram_callback = callback
        debug_log("Telegram callback set", "MIDDLEWARE")
    
    def _generate_call_id(self, tool_name: str, timestamp: str) -> str:
        """Generate a unique call ID for tracking"""
        return f"{tool_name}_{timestamp}_{id(self)}"
    
    def _add_log_entry(self, entry: MCPLogEntry):
        """Add a log entry and manage storage limits"""
        self.log_entries.append(entry)
        
        # Maintain max log entries limit
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]
        
        # Trigger event handlers
        for handler in self.event_handlers.get(entry.event_type, []):
            try:
                handler(entry)
            except Exception as e:
                debug_log(f"Error in event handler: {e}", "MIDDLEWARE")
        
        # Telegram forwarding
        if self.enable_telegram_forwarding and self.telegram_callback:
            try:
                if asyncio.iscoroutinefunction(self.telegram_callback):
                    # Schedule the coroutine to run in the event loop
                    asyncio.create_task(self.telegram_callback(entry))
                else:
                    self.telegram_callback(entry)
            except Exception as e:
                debug_log(f"Error in Telegram forwarding: {e}", "MIDDLEWARE")
        
        debug_log(f"Logged {entry.event_type.value} for tool {entry.tool_name}", "MIDDLEWARE")
    
    def log_tool_call_start(self, 
                           tool_name: str,
                           request_data: Optional[Dict[str, Any]] = None,
                           session_id: Optional[str] = None,
                           project_directory: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Log the start of a tool call.
        
        Returns:
            call_id: Unique identifier for this call
        """
        timestamp = datetime.now().isoformat()
        call_id = self._generate_call_id(tool_name, timestamp)
        
        # Store active call info
        self.active_calls[call_id] = {
            'tool_name': tool_name,
            'start_time': time.time(),
            'session_id': session_id,
            'project_directory': project_directory,
            'metadata': metadata
        }
        
        # Create log entry
        entry = MCPLogEntry(
            timestamp=timestamp,
            event_type=MCPEventType.TOOL_CALL_START,
            tool_name=tool_name,
            session_id=session_id,
            project_directory=project_directory,
            request_data=request_data if self.include_request_data else None,
            metadata=metadata
        )
        
        self._add_log_entry(entry)
        self.stats['total_calls'] += 1
        
        return call_id
    
    def log_tool_call_end(self, 
                         call_id: str,
                         response_data: Optional[Dict[str, Any]] = None,
                         success: bool = True) -> None:
        """Log the successful completion of a tool call"""
        if call_id not in self.active_calls:
            debug_log(f"Unknown call_id: {call_id}", "MIDDLEWARE")
            return
        
        call_info = self.active_calls.pop(call_id)
        end_time = time.time()
        duration_ms = (end_time - call_info['start_time']) * 1000
        
        # Create log entry
        entry = MCPLogEntry(
            timestamp=datetime.now().isoformat(),
            event_type=MCPEventType.TOOL_CALL_END,
            tool_name=call_info['tool_name'],
            session_id=call_info.get('session_id'),
            project_directory=call_info.get('project_directory'),
            duration_ms=duration_ms,
            success=success,
            response_data=response_data if self.include_response_data else None,
            metadata=call_info.get('metadata')
        )
        
        self._add_log_entry(entry)
        
        # Update statistics
        if success:
            self.stats['successful_calls'] += 1
        else:
            self.stats['failed_calls'] += 1
        self.stats['total_duration_ms'] += duration_ms
    
    def log_tool_call_error(self, 
                           call_id: str,
                           error_message: str,
                           error_details: Optional[Dict[str, Any]] = None) -> None:
        """Log an error during tool call execution"""
        if call_id not in self.active_calls:
            debug_log(f"Unknown call_id for error: {call_id}", "MIDDLEWARE")
            return
        
        call_info = self.active_calls.pop(call_id)
        end_time = time.time()
        duration_ms = (end_time - call_info['start_time']) * 1000
        
        # Create log entry
        entry = MCPLogEntry(
            timestamp=datetime.now().isoformat(),
            event_type=MCPEventType.TOOL_CALL_ERROR,
            tool_name=call_info['tool_name'],
            session_id=call_info.get('session_id'),
            project_directory=call_info.get('project_directory'),
            duration_ms=duration_ms,
            success=False,
            error_message=error_message,
            metadata={
                **(call_info.get('metadata') or {}),
                **(error_details or {})
            }
        )
        
        self._add_log_entry(entry)
        
        # Update statistics
        self.stats['failed_calls'] += 1
        self.stats['total_duration_ms'] += duration_ms
    
    def log_session_start(self, 
                         session_id: str,
                         project_directory: Optional[str] = None,
                         user_agent: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log the start of a new MCP session"""
        entry = MCPLogEntry(
            timestamp=datetime.now().isoformat(),
            event_type=MCPEventType.SESSION_START,
            session_id=session_id,
            project_directory=project_directory,
            user_agent=user_agent,
            metadata=metadata
        )
        
        self._add_log_entry(entry)
        self.stats['session_count'] += 1
    
    def log_session_end(self, 
                       session_id: str,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log the end of an MCP session"""
        entry = MCPLogEntry(
            timestamp=datetime.now().isoformat(),
            event_type=MCPEventType.SESSION_END,
            session_id=session_id,
            metadata=metadata
        )
        
        self._add_log_entry(entry)
    
    def log_system_info(self, 
                       info_data: Dict[str, Any],
                       session_id: Optional[str] = None) -> None:
        """Log system information events"""
        entry = MCPLogEntry(
            timestamp=datetime.now().isoformat(),
            event_type=MCPEventType.SYSTEM_INFO,
            session_id=session_id,
            response_data=info_data
        )
        
        self._add_log_entry(entry)
    
    def get_recent_logs(self, 
                       count: int = 10,
                       event_type: Optional[MCPEventType] = None,
                       tool_name: Optional[str] = None) -> List[MCPLogEntry]:
        """Get recent log entries with optional filtering"""
        filtered_logs = self.log_entries
        
        if event_type:
            filtered_logs = [log for log in filtered_logs if log.event_type == event_type]
        
        if tool_name:
            filtered_logs = [log for log in filtered_logs if log.tool_name == tool_name]
        
        return filtered_logs[-count:] if count > 0 else filtered_logs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        avg_duration = (
            self.stats['total_duration_ms'] / self.stats['total_calls']
            if self.stats['total_calls'] > 0 else 0
        )
        
        success_rate = (
            self.stats['successful_calls'] / self.stats['total_calls'] * 100
            if self.stats['total_calls'] > 0 else 0
        )
        
        return {
            **self.stats,
            'average_duration_ms': avg_duration,
            'success_rate_percent': success_rate,
            'active_calls': len(self.active_calls),
            'log_entries_count': len(self.log_entries)
        }
    
    def clear_logs(self) -> None:
        """Clear all stored log entries"""
        self.log_entries.clear()
        debug_log("Log entries cleared", "MIDDLEWARE")
    
    def export_logs(self, 
                   format_type: str = "json",
                   include_details: bool = True) -> str:
        """
        Export logs in various formats.
        
        Args:
            format_type: Export format ("json", "telegram", "csv")
            include_details: Whether to include detailed information
            
        Returns:
            Formatted log data as string
        """
        if format_type == "json":
            return json.dumps([entry.to_dict() for entry in self.log_entries], 
                            ensure_ascii=False, indent=2)
        
        elif format_type == "telegram":
            messages = []
            for entry in self.log_entries:
                messages.append(entry.to_telegram_message(include_details))
            return "\n\n---\n\n".join(messages)
        
        elif format_type == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'timestamp', 'event_type', 'tool_name', 'session_id',
                'duration_ms', 'success', 'error_message'
            ])
            
            # Data rows
            for entry in self.log_entries:
                writer.writerow([
                    entry.timestamp,
                    entry.event_type.value,
                    entry.tool_name or '',
                    entry.session_id or '',
                    entry.duration_ms or '',
                    entry.success,
                    entry.error_message or ''
                ])
            
            return output.getvalue()
        
        else:
            raise ValueError(f"Unsupported format type: {format_type}")


# Global middleware instance
_global_middleware: Optional[MCPLoggingMiddleware] = None


def get_middleware() -> MCPLoggingMiddleware:
    """Get the global middleware instance"""
    global _global_middleware
    if _global_middleware is None:
        _global_middleware = MCPLoggingMiddleware()
    return _global_middleware


def initialize_middleware(config: Optional[Dict[str, Any]] = None) -> MCPLoggingMiddleware:
    """Initialize the global middleware with configuration"""
    global _global_middleware
    
    config = config or {}
    
    _global_middleware = MCPLoggingMiddleware(
        log_level=LogLevel(config.get('log_level', 'info')),
        enable_telegram_forwarding=config.get('enable_telegram_forwarding', False),
        max_log_entries=config.get('max_log_entries', 1000),
        include_request_data=config.get('include_request_data', True),
        include_response_data=config.get('include_response_data', True)
    )
    
    debug_log("Global middleware initialized", "MIDDLEWARE")
    return _global_middleware


# Convenience functions for common operations
def log_tool_start(tool_name: str, **kwargs) -> str:
    """Convenience function to log tool call start"""
    return get_middleware().log_tool_call_start(tool_name, **kwargs)


def log_tool_end(call_id: str, **kwargs) -> None:
    """Convenience function to log tool call end"""
    get_middleware().log_tool_call_end(call_id, **kwargs)


def log_tool_error(call_id: str, error_message: str, **kwargs) -> None:
    """Convenience function to log tool call error"""
    get_middleware().log_tool_call_error(call_id, error_message, **kwargs)


def log_session_start(session_id: str, **kwargs) -> None:
    """Convenience function to log session start"""
    get_middleware().log_session_start(session_id, **kwargs)


def log_session_end(session_id: str, **kwargs) -> None:
    """Convenience function to log session end"""
    get_middleware().log_session_end(session_id, **kwargs)


# Decorator for automatic tool call logging
def log_mcp_tool(tool_name: Optional[str] = None):
    """
    Decorator to automatically log MCP tool calls.
    
    Usage:
        @log_mcp_tool("my_tool")
        async def my_tool_function(arg1, arg2):
            return result
    """
    def decorator(func):
        actual_tool_name = tool_name or func.__name__
        
        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                call_id = log_tool_start(actual_tool_name, request_data={
                    'args': args,
                    'kwargs': kwargs
                })
                
                try:
                    result = await func(*args, **kwargs)
                    log_tool_end(call_id, response_data={'result': result})
                    return result
                except Exception as e:
                    log_tool_error(call_id, str(e), error_details={
                        'exception_type': type(e).__name__,
                        'traceback': traceback.format_exc()
                    })
                    raise
            
            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs):
                call_id = log_tool_start(actual_tool_name, request_data={
                    'args': args,
                    'kwargs': kwargs
                })
                
                try:
                    result = func(*args, **kwargs)
                    log_tool_end(call_id, response_data={'result': result})
                    return result
                except Exception as e:
                    log_tool_error(call_id, str(e), error_details={
                        'exception_type': type(e).__name__,
                        'traceback': traceback.format_exc()
                    })
                    raise
            
            return sync_wrapper
    
    return decorator