"""
Telegram Bot Manager for MCP Feedback Enhanced
==============================================

Comprehensive Telegram Bot API integration with message sending, receiving,
formatting, chunking, and error handling capabilities.
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote

import aiohttp

from ..debug import debug_log


class TelegramRateLimiter:
    """Rate limiter for Telegram Bot API to respect API limits."""
    
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window (default: 30)
            time_window: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """
        Acquire permission to make an API call.
        
        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            now = time.time()
            
            # Remove old requests outside the time window
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < self.time_window]
            
            # Check if we can make a new request
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_retry_after(self) -> int:
        """
        Calculate retry delay for rate limited requests.
        
        Returns:
            Seconds to wait before next request
        """
        if not self.requests:
            return 0
        
        oldest_request = min(self.requests)
        return max(0, int(self.time_window - (time.time() - oldest_request)))


class TelegramMessageChunker:
    """Smart message chunker for Telegram's 4096 character limit."""
    
    def __init__(self, max_length: int = 4096):
        """
        Initialize message chunker.
        
        Args:
            max_length: Maximum message length (default: 4096 for Telegram)
        """
        self.max_length = max_length
    
    def chunk_message(self, text: str, preserve_formatting: bool = True) -> List[str]:
        """
        Intelligently chunk a message while preserving formatting.
        
        Args:
            text: Text to chunk
            preserve_formatting: Whether to preserve markdown formatting
            
        Returns:
            List of message chunks
        """
        if len(text) <= self.max_length:
            return [text]
        
        chunks = []
        
        if preserve_formatting:
            chunks = self._chunk_with_formatting(text)
        else:
            chunks = self._chunk_simple(text)
        
        # Add chunk indicators
        if len(chunks) > 1:
            chunks = self._add_chunk_indicators(chunks)
        
        return chunks
    
    def _chunk_with_formatting(self, text: str) -> List[str]:
        """Chunk text while preserving markdown formatting."""
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            # Check if adding this paragraph would exceed limit
            test_chunk = current_chunk + ('\n\n' if current_chunk else '') + paragraph
            
            if len(test_chunk) <= self.max_length:
                current_chunk = test_chunk
            else:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # Handle large paragraphs
                if len(paragraph) > self.max_length:
                    # Split large paragraph by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    for sentence in sentences:
                        test_chunk = current_chunk + (' ' if current_chunk else '') + sentence
                        
                        if len(test_chunk) <= self.max_length:
                            current_chunk = test_chunk
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            
                            # Handle very long sentences
                            if len(sentence) > self.max_length:
                                chunks.extend(self._chunk_simple(sentence))
                                current_chunk = ""
                            else:
                                current_chunk = sentence
                else:
                    current_chunk = paragraph
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _chunk_simple(self, text: str) -> List[str]:
        """Simple text chunking by character count."""
        chunks = []
        
        for i in range(0, len(text), self.max_length):
            chunk = text[i:i + self.max_length]
            chunks.append(chunk)
        
        return chunks
    
    def _add_chunk_indicators(self, chunks: List[str]) -> List[str]:
        """Add chunk indicators to messages."""
        total = len(chunks)
        
        if total <= 1:
            return chunks
        
        result = []
        for i, chunk in enumerate(chunks, 1):
            indicator = f"📄 Part {i}/{total}\n\n"
            
            # Ensure chunk with indicator doesn't exceed limit
            if len(indicator + chunk) <= self.max_length:
                result.append(indicator + chunk)
            else:
                # If adding indicator would exceed limit, put it separately
                result.append(f"📄 Part {i}/{total}")
                result.append(chunk)
        
        return result
    
    def chunk_code_block(self, code: str, language: str = "") -> List[str]:
        """
        Special handling for code blocks to maintain syntax highlighting.
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
            
        Returns:
            List of code block chunks
        """
        code_prefix = f"```{language}\n"
        code_suffix = "\n```"
        
        # Calculate available space for code content
        available_length = self.max_length - len(code_prefix) - len(code_suffix)
        
        if len(code) <= available_length:
            return [f"{code_prefix}{code}{code_suffix}"]
        
        chunks = []
        lines = code.split('\n')
        current_chunk = ""
        
        for line in lines:
            test_chunk = current_chunk + ('\n' if current_chunk else '') + line
            
            if len(test_chunk) <= available_length:
                current_chunk = test_chunk
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(f"{code_prefix}{current_chunk}{code_suffix}")
                    current_chunk = ""
                
                # Handle very long lines
                if len(line) > available_length:
                    # Split long line
                    for i in range(0, len(line), available_length):
                        line_chunk = line[i:i + available_length]
                        chunks.append(f"{code_prefix}{line_chunk}{code_suffix}")
                else:
                    current_chunk = line
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(f"{code_prefix}{current_chunk}{code_suffix}")
        
        return chunks


class TelegramBotManager:
    """
    Comprehensive Telegram Bot manager for MCP Feedback Enhanced.
    
    Handles message sending, receiving, formatting, chunking, and error handling
    with proper rate limiting and Telegram API compliance.
    """
    
    def __init__(self, bot_token: str, chat_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Telegram Bot Manager.
        
        Args:
            bot_token: Telegram Bot API token
            chat_id: Target chat ID for messages
            config: Optional configuration dictionary
        """
        self.bot_token = bot_token
        self.chat_id = str(chat_id)
        self.config = config or {}
        
        # API configuration
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Components
        self.rate_limiter = TelegramRateLimiter(
            max_requests=self.config.get('rate_limit_requests', 30),
            time_window=self.config.get('rate_limit_window', 60)
        )
        self.message_chunker = TelegramMessageChunker(
            max_length=self.config.get('max_message_length', 4096)
        )
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # State tracking
        self.last_update_id = 0
        self.is_polling = False
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()
    
    async def start(self):
        """Initialize the bot manager."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        debug_log(f"TelegramBotManager started for chat {self.chat_id}")
    
    async def stop(self):
        """Clean up resources."""
        self.is_polling = False
        
        if self.session:
            await self.session.close()
            self.session = None
        
        debug_log("TelegramBotManager stopped")
    
    async def send_message(
        self, 
        text: str, 
        parse_mode: str = "MarkdownV2",
        disable_web_page_preview: bool = True,
        reply_to_message_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to the configured chat.
        
        Args:
            text: Message text
            parse_mode: Telegram parse mode (MarkdownV2, Markdown, HTML, or None)
            disable_web_page_preview: Whether to disable link previews
            reply_to_message_id: Message ID to reply to
            
        Returns:
            Telegram API response or None if failed
        """
        if not await self.rate_limiter.acquire():
            retry_after = self.rate_limiter.get_retry_after()
            debug_log(f"Rate limited, waiting {retry_after} seconds")
            await asyncio.sleep(retry_after)
            return await self.send_message(text, parse_mode, disable_web_page_preview, reply_to_message_id)
        
        url = f"{self.api_base_url}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        
        try:
            async with self.session.post(url, json=payload) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("ok"):
                    debug_log(f"Message sent successfully: {result['result']['message_id']}")
                    return result["result"]
                else:
                    error_msg = result.get("description", "Unknown error")
                    debug_log(f"Failed to send message: {error_msg}")
                    return None
                    
        except Exception as e:
            debug_log(f"Exception sending message: {e}")
            return None
    
    async def send_chunked_message(
        self, 
        text: str, 
        parse_mode: str = "MarkdownV2",
        preserve_formatting: bool = True
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Send a large message in chunks if necessary.
        
        Args:
            text: Message text
            parse_mode: Telegram parse mode
            preserve_formatting: Whether to preserve formatting when chunking
            
        Returns:
            List of Telegram API responses
        """
        chunks = self.message_chunker.chunk_message(text, preserve_formatting)
        results = []
        
        for i, chunk in enumerate(chunks):
            # Add small delay between chunks to avoid rate limiting
            if i > 0:
                await asyncio.sleep(0.5)
            
            result = await self.send_message(chunk, parse_mode)
            results.append(result)
        
        return results
    
    async def send_code_block(
        self, 
        code: str, 
        language: str = "",
        caption: str = ""
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Send code with proper formatting and chunking.
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
            caption: Optional caption for the code
            
        Returns:
            List of Telegram API responses
        """
        results = []
        
        # Send caption first if provided
        if caption:
            caption_result = await self.send_message(caption)
            results.append(caption_result)
        
        # Send code in chunks
        code_chunks = self.message_chunker.chunk_code_block(code, language)
        
        for i, chunk in enumerate(code_chunks):
            if i > 0 or caption:  # Add delay if not first message
                await asyncio.sleep(0.5)
            
            result = await self.send_message(chunk, parse_mode=None)  # No parse mode for code blocks
            results.append(result)
        
        return results
    
    async def send_file(
        self, 
        file_path: str, 
        caption: str = "",
        parse_mode: str = "MarkdownV2"
    ) -> Optional[Dict[str, Any]]:
        """
        Send a file to the chat.
        
        Args:
            file_path: Path to the file to send
            caption: Optional caption for the file
            parse_mode: Parse mode for the caption
            
        Returns:
            Telegram API response or None if failed
        """
        if not await self.rate_limiter.acquire():
            retry_after = self.rate_limiter.get_retry_after()
            await asyncio.sleep(retry_after)
            return await self.send_file(file_path, caption, parse_mode)
        
        url = f"{self.api_base_url}/sendDocument"
        
        try:
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.chat_id)
                data.add_field('document', file, filename=file_path.split('/')[-1])
                
                if caption:
                    data.add_field('caption', caption)
                    if parse_mode:
                        data.add_field('parse_mode', parse_mode)
                
                async with self.session.post(url, data=data) as response:
                    result = await response.json()
                    
                    if response.status == 200 and result.get("ok"):
                        debug_log(f"File sent successfully: {result['result']['message_id']}")
                        return result["result"]
                    else:
                        error_msg = result.get("description", "Unknown error")
                        debug_log(f"Failed to send file: {error_msg}")
                        return None
                        
        except Exception as e:
            debug_log(f"Exception sending file: {e}")
            return None
    
    async def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Get updates from Telegram using long polling.
        
        Args:
            offset: Update offset for pagination
            timeout: Long polling timeout
            
        Returns:
            List of updates
        """
        url = f"{self.api_base_url}/getUpdates"
        
        params = {
            "timeout": timeout,
            "allowed_updates": ["message"]
        }
        
        if offset is not None:
            params["offset"] = offset
        
        try:
            async with self.session.get(url, params=params) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("ok"):
                    return result.get("result", [])
                else:
                    error_msg = result.get("description", "Unknown error")
                    debug_log(f"Failed to get updates: {error_msg}")
                    return []
                    
        except Exception as e:
            debug_log(f"Exception getting updates: {e}")
            return []
    
    async def test_connection(self) -> Tuple[bool, str]:
        """
        Test the bot connection and permissions.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Test bot info
            url = f"{self.api_base_url}/getMe"
            
            async with self.session.get(url) as response:
                result = await response.json()
                
                if not (response.status == 200 and result.get("ok")):
                    error_msg = result.get("description", "Invalid bot token")
                    return False, f"Bot token validation failed: {error_msg}"
                
                bot_info = result["result"]
                bot_username = bot_info.get("username", "Unknown")
                
                # Test chat access by sending a test message
                test_message = f"🤖 Connection test successful!\nBot: @{bot_username}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                message_result = await self.send_message(test_message, parse_mode=None)
                
                if message_result:
                    return True, f"Connection successful! Bot @{bot_username} can send messages to chat {self.chat_id}"
                else:
                    return False, f"Bot @{bot_username} cannot send messages to chat {self.chat_id}. Please check chat ID and bot permissions."
                    
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    async def start_polling(self, message_handler=None) -> None:
        """
        Start polling for updates.
        
        Args:
            message_handler: Optional callback function for handling messages
        """
        self.is_polling = True
        debug_log("Started Telegram polling")
        
        while self.is_polling:
            try:
                updates = await self.get_updates(offset=self.last_update_id + 1)
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    
                    if "message" in update and message_handler:
                        try:
                            await message_handler(update["message"])
                        except Exception as e:
                            debug_log(f"Error in message handler: {e}")
                
                # Small delay to prevent excessive API calls
                await asyncio.sleep(1)
                
            except Exception as e:
                debug_log(f"Error in polling loop: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    def stop_polling(self):
        """Stop the polling loop."""
        self.is_polling = False
        debug_log("Stopped Telegram polling")
    
    def format_mcp_message(
        self, 
        tool_name: str, 
        summary: str, 
        session_id: str = "",
        project_directory: str = "",
        include_session_id: bool = True,
        include_timestamp: bool = True,
        include_project_path: bool = False
    ) -> str:
        """
        Format an MCP tool call for Telegram.
        
        Args:
            tool_name: Name of the MCP tool
            summary: Tool summary/description
            session_id: MCP session ID
            project_directory: Project directory path
            include_session_id: Whether to include session ID
            include_timestamp: Whether to include timestamp
            include_project_path: Whether to include project path
            
        Returns:
            Formatted message string
        """
        lines = []
        
        # Header
        lines.append("🤖 **MCP Tool Call**")
        lines.append("")
        
        # Tool information
        lines.append(f"**Tool:** `{tool_name}`")
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"**Time:** {timestamp}")
        
        if include_session_id and session_id:
            lines.append(f"**Session:** `{session_id[:8]}...`")
        
        if include_project_path and project_directory:
            # Truncate long paths
            if len(project_directory) > 50:
                path_display = "..." + project_directory[-47:]
            else:
                path_display = project_directory
            lines.append(f"**Project:** `{path_display}`")
        
        lines.append("")
        
        # Summary
        lines.append("**Summary:**")
        lines.append(summary)
        
        lines.append("")
        lines.append("---")
        lines.append("💬 Please provide your feedback...")
        
        return "\n".join(lines)
    
    @staticmethod
    def escape_markdown_v2(text: str) -> str:
        """
        Escape special characters for MarkdownV2 format.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Characters that need escaping in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    @staticmethod
    def validate_bot_token(token: str) -> bool:
        """
        Validate Telegram bot token format.
        
        Args:
            token: Bot token to validate
            
        Returns:
            True if token format is valid
        """
        # Telegram bot token format: <bot_id>:<bot_secret>
        # bot_id is numeric, bot_secret is alphanumeric with underscores and hyphens
        pattern = r'^\d+:[A-Za-z0-9_-]+$'
        return bool(re.match(pattern, token))
    
    @staticmethod
    def validate_chat_id(chat_id: str) -> bool:
        """
        Validate chat ID format.
        
        Args:
            chat_id: Chat ID to validate
            
        Returns:
            True if chat ID format is valid
        """
        # Chat ID can be numeric (positive or negative) or username starting with @
        if chat_id.startswith('@'):
            # Username format: @username (alphanumeric and underscores)
            return bool(re.match(r'^@[A-Za-z0-9_]+$', chat_id))
        else:
            # Numeric chat ID (can be negative for groups)
            return bool(re.match(r'^-?\d+$', chat_id))


# Convenience functions for easy usage
async def send_telegram_message(
    bot_token: str, 
    chat_id: str, 
    message: str,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Convenience function to send a single Telegram message.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Target chat ID
        message: Message to send
        **kwargs: Additional arguments for send_message
        
    Returns:
        Telegram API response or None
    """
    async with TelegramBotManager(bot_token, chat_id) as bot:
        return await bot.send_message(message, **kwargs)


async def test_telegram_connection(bot_token: str, chat_id: str) -> Tuple[bool, str]:
    """
    Convenience function to test Telegram connection.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Target chat ID
        
    Returns:
        Tuple of (success, message)
    """
    async with TelegramBotManager(bot_token, chat_id) as bot:
        return await bot.test_connection()