#!/usr/bin/env python3
"""
Telegram Integration Routes
===========================

FastAPI routes for Telegram integration dashboard, providing real-time monitoring,
configuration management, and session control for the MCP-Telegram bridge.

Key Features:
- Real-time bridge status monitoring
- Live message log viewer with chunking visualization
- Active session management interface
- Configuration panel for Telegram settings
- WebSocket integration for live updates
- Message history and search functionality
- Session analytics and statistics

Author: MCP Feedback Enhanced Team
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from ...debug import web_debug_log as debug_log
from ...utils.config_manager import get_config_manager, is_telegram_enabled, get_telegram_config
from ...utils.mcp_telegram_bridge import get_bridge
from ...utils.logging_middleware import get_middleware


# Pydantic models for API requests/responses
class TelegramConfigUpdate(BaseModel):
    """Model for Telegram configuration updates"""
    enabled: Optional[bool] = None
    enable_bridge: Optional[bool] = None
    enable_auto_forwarding: Optional[bool] = None
    enable_chunking: Optional[bool] = None
    include_session_id: Optional[bool] = None
    include_timestamp: Optional[bool] = None
    include_project_path: Optional[bool] = None
    include_details: Optional[bool] = None
    max_chunk_size: Optional[int] = None
    preserve_code_blocks: Optional[bool] = None
    preserve_markdown: Optional[bool] = None
    add_navigation: Optional[bool] = None
    add_previews: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    max_concurrent_sessions: Optional[int] = None


class SessionAction(BaseModel):
    """Model for session management actions"""
    action: str  # "end", "extend", "cleanup"
    session_id: Optional[str] = None


class MessageSearch(BaseModel):
    """Model for message search requests"""
    query: Optional[str] = None
    event_type: Optional[str] = None
    tool_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: int = 50


def setup_telegram_routes(app, web_manager):
    """Setup Telegram integration routes"""
    router = APIRouter(prefix="/telegram", tags=["telegram"])
    
    # WebSocket connections for real-time updates
    telegram_websockets: List[WebSocket] = []
    
    @router.get("/dashboard", response_class=HTMLResponse)
    async def telegram_dashboard(request: Request):
        """Render Telegram integration dashboard"""
        try:
            # Check if Telegram is enabled
            telegram_enabled = is_telegram_enabled()
            
            # Get configuration
            config_manager = get_config_manager()
            telegram_config = get_telegram_config() if config_manager else None
            
            # Get bridge status
            bridge = get_bridge()
            bridge_status = bridge.get_bridge_status() if bridge else {
                "status": "disconnected",
                "is_running": False,
                "active_sessions": 0,
                "pending_feedback": 0,
                "message_correlations": 0,
                "websocket_connections": 0
            }
            
            # Get recent logs
            middleware = get_middleware()
            recent_logs = []
            if middleware:
                logs = middleware.get_recent_logs(20)
                recent_logs = [
                    {
                        "timestamp": log.timestamp,
                        "event_type": log.event_type.value,
                        "tool_name": log.tool_name,
                        "success": log.success,
                        "duration_ms": log.duration_ms,
                        "session_id": log.session_id
                    }
                    for log in logs
                ]
            
            return web_manager.templates.TemplateResponse(
                "telegram_dashboard.html",
                {
                    "request": request,
                    "telegram_enabled": telegram_enabled,
                    "telegram_config": telegram_config.to_dict() if telegram_config else {},
                    "bridge_status": bridge_status,
                    "recent_logs": recent_logs,
                    "page_title": "Telegram Integration Dashboard"
                }
            )
            
        except Exception as e:
            debug_log(f"Error rendering Telegram dashboard: {e}")
            raise HTTPException(status_code=500, detail="Failed to load dashboard")
    
    @router.get("/api/status")
    async def get_telegram_status():
        """Get current Telegram integration status"""
        try:
            # Get configuration status
            telegram_enabled = is_telegram_enabled()
            config_manager = get_config_manager()
            telegram_config = get_telegram_config() if config_manager else None
            
            # Get bridge status
            bridge = get_bridge()
            bridge_status = bridge.get_bridge_status() if bridge else {
                "status": "disconnected",
                "is_running": False,
                "active_sessions": 0,
                "pending_feedback": 0,
                "message_correlations": 0,
                "websocket_connections": 0
            }
            
            # Get middleware statistics
            middleware = get_middleware()
            middleware_stats = middleware.get_statistics() if middleware else {}
            
            return JSONResponse({
                "telegram_enabled": telegram_enabled,
                "bridge_status": bridge_status,
                "middleware_stats": middleware_stats,
                "config_summary": {
                    "bot_configured": bool(telegram_config and telegram_config.bot_token),
                    "chat_configured": bool(telegram_config and telegram_config.chat_id),
                    "auto_forwarding": telegram_config.enable_auto_forwarding if telegram_config else False,
                    "chunking_enabled": telegram_config.enable_chunking if telegram_config else False
                } if telegram_config else {}
            })
            
        except Exception as e:
            debug_log(f"Error getting Telegram status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get status")
    
    @router.get("/api/sessions")
    async def get_telegram_sessions():
        """Get active Telegram sessions"""
        try:
            bridge = get_bridge()
            if not bridge:
                return JSONResponse({"sessions": []})
            
            sessions_data = []
            for session_id, session in bridge.active_sessions.items():
                sessions_data.append({
                    "session_id": session_id,
                    "chat_id": session.chat_id,
                    "project_directory": session.project_directory,
                    "start_time": session.start_time.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "active_mcp_calls": len(session.active_mcp_calls),
                    "pending_responses": len(session.pending_responses),
                    "user_context": session.user_context,
                    "is_expired": session.is_expired(bridge.session_timeout_minutes)
                })
            
            return JSONResponse({"sessions": sessions_data})
            
        except Exception as e:
            debug_log(f"Error getting Telegram sessions: {e}")
            raise HTTPException(status_code=500, detail="Failed to get sessions")
    
    @router.post("/api/sessions/action")
    async def manage_telegram_session(action: SessionAction):
        """Manage Telegram sessions (end, extend, cleanup)"""
        try:
            bridge = get_bridge()
            if not bridge:
                raise HTTPException(status_code=503, detail="Telegram bridge not available")
            
            if action.action == "end" and action.session_id:
                success = await bridge.end_session(action.session_id)
                return JSONResponse({
                    "success": success,
                    "message": f"Session {action.session_id} ended" if success else "Failed to end session"
                })
            
            elif action.action == "cleanup":
                # Cleanup expired sessions
                expired_count = 0
                for session_id, session in list(bridge.active_sessions.items()):
                    if session.is_expired(bridge.session_timeout_minutes):
                        await bridge.end_session(session_id)
                        expired_count += 1
                
                return JSONResponse({
                    "success": True,
                    "message": f"Cleaned up {expired_count} expired sessions"
                })
            
            elif action.action == "extend" and action.session_id:
                session = bridge.active_sessions.get(action.session_id)
                if session:
                    session.update_activity()
                    return JSONResponse({
                        "success": True,
                        "message": f"Session {action.session_id} activity updated"
                    })
                else:
                    raise HTTPException(status_code=404, detail="Session not found")
            
            else:
                raise HTTPException(status_code=400, detail="Invalid action or missing session_id")
                
        except HTTPException:
            raise
        except Exception as e:
            debug_log(f"Error managing Telegram session: {e}")
            raise HTTPException(status_code=500, detail="Failed to manage session")
    
    @router.get("/api/logs")
    async def get_telegram_logs(
        limit: int = 50,
        event_type: Optional[str] = None,
        tool_name: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Get MCP logs with filtering"""
        try:
            middleware = get_middleware()
            if not middleware:
                return JSONResponse({"logs": []})
            
            # Get logs with filtering
            all_logs = middleware.get_recent_logs(limit * 2)  # Get more to allow filtering
            
            filtered_logs = []
            for log in all_logs:
                # Apply filters
                if event_type and log.event_type.value != event_type:
                    continue
                if tool_name and log.tool_name != tool_name:
                    continue
                if session_id and log.session_id != session_id:
                    continue
                
                # Convert to dict
                log_data = {
                    "timestamp": log.timestamp,
                    "event_type": log.event_type.value,
                    "tool_name": log.tool_name,
                    "session_id": log.session_id,
                    "duration_ms": log.duration_ms,
                    "success": log.success,
                    "error_message": log.error_message,
                    "metadata": log.metadata
                }
                
                # Add Telegram message formatting if available
                try:
                    telegram_message = log.to_telegram_message(include_details=False)
                    log_data["telegram_preview"] = telegram_message[:200] + "..." if len(telegram_message) > 200 else telegram_message
                except:
                    log_data["telegram_preview"] = None
                
                filtered_logs.append(log_data)
                
                if len(filtered_logs) >= limit:
                    break
            
            return JSONResponse({"logs": filtered_logs})
            
        except Exception as e:
            debug_log(f"Error getting Telegram logs: {e}")
            raise HTTPException(status_code=500, detail="Failed to get logs")
    
    @router.post("/api/logs/search")
    async def search_telegram_logs(search: MessageSearch):
        """Search MCP logs with advanced filtering"""
        try:
            middleware = get_middleware()
            if not middleware:
                return JSONResponse({"logs": [], "total": 0})
            
            # Get all logs for searching
            all_logs = middleware.get_recent_logs(1000)  # Get more for comprehensive search
            
            filtered_logs = []
            for log in all_logs:
                # Apply filters
                if search.event_type and log.event_type.value != search.event_type:
                    continue
                if search.tool_name and log.tool_name != search.tool_name:
                    continue
                
                # Time range filtering
                if search.start_time:
                    try:
                        start_dt = datetime.fromisoformat(search.start_time.replace('Z', '+00:00'))
                        log_dt = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
                        if log_dt < start_dt:
                            continue
                    except:
                        pass
                
                if search.end_time:
                    try:
                        end_dt = datetime.fromisoformat(search.end_time.replace('Z', '+00:00'))
                        log_dt = datetime.fromisoformat(log.timestamp.replace('Z', '+00:00'))
                        if log_dt > end_dt:
                            continue
                    except:
                        pass
                
                # Text search in content
                if search.query:
                    query_lower = search.query.lower()
                    searchable_text = f"{log.tool_name or ''} {log.error_message or ''} {json.dumps(log.metadata or {})}"
                    if query_lower not in searchable_text.lower():
                        continue
                
                # Convert to dict
                log_data = {
                    "timestamp": log.timestamp,
                    "event_type": log.event_type.value,
                    "tool_name": log.tool_name,
                    "session_id": log.session_id,
                    "duration_ms": log.duration_ms,
                    "success": log.success,
                    "error_message": log.error_message,
                    "metadata": log.metadata
                }
                
                filtered_logs.append(log_data)
                
                if len(filtered_logs) >= search.limit:
                    break
            
            return JSONResponse({
                "logs": filtered_logs,
                "total": len(filtered_logs),
                "query": search.dict()
            })
            
        except Exception as e:
            debug_log(f"Error searching Telegram logs: {e}")
            raise HTTPException(status_code=500, detail="Failed to search logs")
    
    @router.get("/api/config")
    async def get_telegram_config():
        """Get current Telegram configuration"""
        try:
            config_manager = get_config_manager()
            if not config_manager:
                raise HTTPException(status_code=503, detail="Configuration manager not available")
            
            # Get safe config (sensitive data masked)
            safe_config = config_manager.get_safe_config_summary()
            
            return JSONResponse({
                "config": safe_config,
                "telegram_enabled": is_telegram_enabled(),
                "validation_status": "valid"  # Could add validation logic here
            })
            
        except Exception as e:
            debug_log(f"Error getting Telegram config: {e}")
            raise HTTPException(status_code=500, detail="Failed to get configuration")
    
    @router.post("/api/config")
    async def update_telegram_config(config_update: TelegramConfigUpdate):
        """Update Telegram configuration"""
        try:
            config_manager = get_config_manager()
            if not config_manager:
                raise HTTPException(status_code=503, detail="Configuration manager not available")
            
            # Convert to dict and filter None values
            update_data = {k: v for k, v in config_update.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No configuration updates provided")
            
            # Update configuration
            success = config_manager.update_telegram_config(**update_data)
            
            if success:
                # Broadcast configuration update to WebSocket clients
                await broadcast_to_telegram_websockets({
                    "type": "config_updated",
                    "message": "Telegram configuration updated successfully",
                    "updated_fields": list(update_data.keys())
                })
                
                return JSONResponse({
                    "success": True,
                    "message": "Configuration updated successfully",
                    "updated_fields": list(update_data.keys())
                })
            else:
                raise HTTPException(status_code=400, detail="Failed to update configuration")
                
        except ValueError as e:
            # Configuration validation error
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            debug_log(f"Error updating Telegram config: {e}")
            raise HTTPException(status_code=500, detail="Failed to update configuration")
    
    @router.post("/api/test-connection")
    async def test_telegram_connection():
        """Test Telegram bot connection"""
        try:
            bridge = get_bridge()
            if not bridge:
                raise HTTPException(status_code=503, detail="Telegram bridge not available")
            
            # Test connection through telegram manager
            success, message = await bridge.telegram_manager.test_connection()
            
            return JSONResponse({
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            debug_log(f"Error testing Telegram connection: {e}")
            raise HTTPException(status_code=500, detail="Failed to test connection")
    
    @router.websocket("/ws")
    async def telegram_websocket(websocket: WebSocket):
        """WebSocket endpoint for real-time Telegram updates"""
        await websocket.accept()
        telegram_websockets.append(websocket)
        debug_log(f"Telegram WebSocket connected, total: {len(telegram_websockets)}")
        
        try:
            # Send initial status
            await websocket.send_json({
                "type": "connected",
                "message": "Connected to Telegram dashboard",
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep connection alive and handle incoming messages
            while True:
                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                    
                    # Handle different message types
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.now().isoformat()
                        })
                    elif message.get("type") == "request_status":
                        # Send current status
                        bridge = get_bridge()
                        status = bridge.get_bridge_status() if bridge else {"status": "disconnected"}
                        await websocket.send_json({
                            "type": "status_update",
                            "data": status,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    await websocket.send_json({
                        "type": "keepalive",
                        "timestamp": datetime.now().isoformat()
                    })
                
        except WebSocketDisconnect:
            debug_log("Telegram WebSocket disconnected")
        except Exception as e:
            debug_log(f"Telegram WebSocket error: {e}")
        finally:
            if websocket in telegram_websockets:
                telegram_websockets.remove(websocket)
            debug_log(f"Telegram WebSocket removed, remaining: {len(telegram_websockets)}")
    
    async def broadcast_to_telegram_websockets(message: Dict[str, Any]):
        """Broadcast message to all connected Telegram WebSocket clients"""
        if not telegram_websockets:
            return
        
        message["timestamp"] = datetime.now().isoformat()
        disconnected = []
        
        for websocket in telegram_websockets:
            try:
                await websocket.send_json(message)
            except Exception as e:
                debug_log(f"Failed to send to Telegram WebSocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            if websocket in telegram_websockets:
                telegram_websockets.remove(websocket)
    
    # Add the router to the app
    app.include_router(router)
    
    # Store broadcast function for external use
    app.broadcast_to_telegram_websockets = broadcast_to_telegram_websockets
    
    debug_log("Telegram integration routes setup complete")
    
    return router