#!/usr/bin/env python3
"""
Telegram Integration Routes (Simplified)
========================================

FastAPI routes for Telegram integration, providing basic configuration testing
and management using direct API calls (bridge system removed).

Key Features:
- Telegram connection testing
- Configuration validation
- Direct API integration

Author: MCP Feedback Enhanced Team
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ...debug import web_debug_log as debug_log
from ...utils.config_manager import is_telegram_enabled, get_telegram_config
from ...utils.telegram_manager import TelegramBotManager


def setup_telegram_routes(app, web_manager):
    """Setup simplified Telegram integration routes (bridge system removed)"""
    router = APIRouter(prefix="/telegram", tags=["telegram"])
    
    @router.get("/api/status")
    async def get_telegram_status():
        """Get basic Telegram integration status (bridge system removed)"""
        try:
            # Check if Telegram is enabled
            telegram_enabled = is_telegram_enabled()
            telegram_config = get_telegram_config() if telegram_enabled else None
            
            return JSONResponse({
                "telegram_enabled": telegram_enabled,
                "status": "direct_api" if telegram_enabled else "disabled",
                "config_summary": {
                    "bot_configured": bool(telegram_config and telegram_config.bot_token),
                    "chat_configured": bool(telegram_config and telegram_config.chat_id),
                } if telegram_config else {
                    "bot_configured": False,
                    "chat_configured": False,
                }
            })
            
        except Exception as e:
            debug_log(f"Error getting Telegram status: {e}")
            raise HTTPException(status_code=500, detail="Failed to get status")
    
    @router.post("/api/test-connection")
    async def test_telegram_connection():
        """Test Telegram bot connection using direct API"""
        try:
            # Check if Telegram is configured
            if not is_telegram_enabled():
                raise HTTPException(status_code=503, detail="Telegram not configured")
            
            # Get Telegram configuration
            config = get_telegram_config()
            if not config:
                raise HTTPException(status_code=503, detail="Telegram configuration not found")
            
            if not config.bot_token or not config.chat_id:
                raise HTTPException(status_code=503, detail="Telegram configuration incomplete (missing bot_token or chat_id)")
            
            # Test connection using TelegramBotManager directly
            async with TelegramBotManager(config.bot_token, config.chat_id) as bot:
                success, message = await bot.test_connection()
            
            return JSONResponse({
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            debug_log(f"Error testing Telegram connection: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to test connection: {str(e)}")
    
    # Add the router to the app
    app.include_router(router)
    
    return router
