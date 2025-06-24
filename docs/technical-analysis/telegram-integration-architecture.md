# Telegram Bot Integration Architecture Design

## Executive Summary

This document defines the comprehensive architecture for integrating Telegram Bot API with the existing MCP Feedback Enhanced system, enabling remote monitoring and bidirectional communication through user-configurable Telegram bots.

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Feedback Enhanced                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   MCP Server    │    │   Web UI        │    │   Telegram   │ │
│  │   (server.py)   │    │   (main.py)     │    │   Integration│ │
│  │                 │    │                 │    │              │ │
│  │ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌──────────┐ │ │
│  │ │ Tool Calls  │ │    │ │ WebSocket   │ │    │ │ Bot      │ │ │
│  │ │ Middleware  │◄┼────┼►│ Manager     │◄┼────┼►│ Manager  │ │ │
│  │ └─────────────┘ │    │ └─────────────┘ │    │ └──────────┘ │ │
│  └─────────────────┘    └─────────────────┘    └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │    Telegram Bot API     │
                    │                         │
                    │  ┌─────────────────┐   │
                    │  │ User's Telegram │   │
                    │  │ Chat/Channel    │   │
                    │  └─────────────────┘   │
                    └─────────────────────────┘
```

## Component Design

### 1. TelegramBotManager Class

#### Core Responsibilities
- **Message Sending**: Send formatted messages to Telegram
- **Message Receiving**: Handle incoming messages from Telegram
- **Authentication**: Manage bot tokens and chat ID validation
- **Rate Limiting**: Respect Telegram API limits
- **Error Handling**: Robust error recovery and logging

#### Class Structure
```python
class TelegramBotManager:
    def __init__(self, bot_token: str, chat_id: str, config: dict):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.config = config
        self.session = aiohttp.ClientSession()
        self.rate_limiter = RateLimiter()
        self.message_chunker = MessageChunker()
        
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool
    async def send_chunked_message(self, text: str, max_length: int = 4096) -> list[str]
    async def send_file(self, file_path: str, caption: str = None) -> bool
    async def get_updates(self, offset: int = None) -> list[dict]
    async def test_connection(self) -> tuple[bool, str]
    async def validate_chat_access(self) -> tuple[bool, str]
```

### 2. MCPLoggingMiddleware Class

#### Integration Points
- **Tool Call Interception**: Capture all MCP tool executions
- **Response Logging**: Record tool responses and outputs
- **Session Correlation**: Link logs to specific MCP sessions
- **Real-time Forwarding**: Send logs to Telegram in real-time

#### Implementation Strategy
```python
class MCPLoggingMiddleware:
    def __init__(self, telegram_manager: TelegramBotManager):
        self.telegram_manager = telegram_manager
        self.session_context = {}
        self.log_buffer = []
        
    async def log_tool_call(self, tool_name: str, params: dict, session_id: str):
        """Log tool call initiation"""
        
    async def log_tool_response(self, tool_name: str, response: any, session_id: str):
        """Log tool execution results"""
        
    async def forward_to_telegram(self, log_entry: dict):
        """Forward log entry to Telegram with formatting"""
```

### 3. MCPTelegramBridge Class

#### Bidirectional Communication Flow
```
MCP Tool Call → Middleware → Format → Telegram → User
     ↑                                            ↓
User Response ← WebSocket ← Bridge ← Parse ← Telegram
```

#### Bridge Responsibilities
- **Message Correlation**: Track conversation threads
- **Session Management**: Maintain context across interactions
- **Response Routing**: Route Telegram responses back to MCP
- **State Synchronization**: Keep WebSocket and Telegram in sync

#### Class Structure
```python
class MCPTelegramBridge:
    def __init__(self, telegram_manager: TelegramBotManager, websocket_manager):
        self.telegram_manager = telegram_manager
        self.websocket_manager = websocket_manager
        self.active_sessions = {}
        self.message_correlation = {}
        
    async def forward_mcp_to_telegram(self, session_id: str, message: dict):
        """Forward MCP feedback request to Telegram"""
        
    async def handle_telegram_response(self, update: dict):
        """Process incoming Telegram message and route to MCP"""
        
    async def correlate_conversation(self, telegram_message_id: str, session_id: str):
        """Link Telegram messages to MCP sessions"""
```

## Message Flow Design

### 1. MCP → Telegram Flow

```
1. AI Assistant calls interactive_feedback tool
2. MCPLoggingMiddleware intercepts the call
3. Tool executes normally (Web UI opens)
4. Middleware captures tool parameters and response
5. MCPTelegramBridge formats message for Telegram
6. TelegramBotManager sends chunked message to user
7. User receives notification on Telegram
```

### 2. Telegram → MCP Flow

```
1. User responds via Telegram
2. TelegramBotManager receives webhook/polling update
3. MCPTelegramBridge processes the response
4. Bridge correlates response to active MCP session
5. Response is forwarded to WebSocket infrastructure
6. Web UI receives the response and processes it
7. MCP tool completes with user's feedback
```

## Data Structures

### 1. Configuration Schema
```json
{
  "telegram": {
    "enabled": false,
    "bot_token": "",
    "chat_id": "",
    "webhook_url": "",
    "polling_enabled": true,
    "message_format": {
      "include_session_id": true,
      "include_timestamp": true,
      "include_project_path": false,
      "max_message_length": 4096
    },
    "security": {
      "encrypt_sensitive_data": true,
      "allowed_commands": ["start", "help", "status"],
      "rate_limit": {
        "messages_per_minute": 20,
        "burst_limit": 5
      }
    }
  }
}
```

### 2. Message Format Schema
```json
{
  "session_id": "uuid",
  "timestamp": "ISO8601",
  "type": "tool_call|tool_response|user_feedback",
  "tool_name": "interactive_feedback",
  "project_directory": "/path/to/project",
  "summary": "AI work summary",
  "content": {
    "text": "message content",
    "images": ["base64_data"],
    "commands": ["executed commands"]
  },
  "correlation_id": "telegram_message_id"
}
```

## Security Considerations

### 1. Authentication & Authorization
- **Bot Token Security**: Encrypted storage, environment variable support
- **Chat ID Validation**: Verify user has access to specified chat
- **Command Whitelist**: Restrict allowed Telegram commands
- **Rate Limiting**: Prevent abuse and API quota exhaustion

### 2. Data Privacy
- **Sensitive Data Filtering**: Remove passwords, tokens from logs
- **Encryption**: Encrypt stored configuration and logs
- **Access Control**: Restrict file system access in logs
- **Audit Trail**: Log all Telegram interactions for security review

### 3. Error Handling
- **Graceful Degradation**: Continue MCP operation if Telegram fails
- **Retry Logic**: Exponential backoff for failed API calls
- **Circuit Breaker**: Disable Telegram if repeated failures occur
- **Fallback Mechanisms**: Use WebSocket if Telegram unavailable

## Integration Points

### 1. WebSocket Infrastructure Integration
```python
# Extend existing WebSocketManager
class EnhancedWebSocketManager(WebSocketManager):
    def __init__(self, telegram_bridge: MCPTelegramBridge):
        super().__init__()
        self.telegram_bridge = telegram_bridge
        
    async def handle_feedback_submission(self, data: dict):
        # Existing WebSocket logic
        result = await super().handle_feedback_submission(data)
        
        # Forward to Telegram if enabled
        if self.telegram_bridge.is_enabled():
            await self.telegram_bridge.forward_mcp_to_telegram(
                data['session_id'], 
                result
            )
        
        return result
```

### 2. Settings Manager Integration
```python
# Extend existing SettingsManager
class EnhancedSettingsManager(SettingsManager):
    def __init__(self):
        super().__init__()
        self.telegram_settings = TelegramSettings()
        
    def get_telegram_config(self) -> dict:
        """Get Telegram configuration with security validation"""
        
    def update_telegram_config(self, config: dict) -> bool:
        """Update Telegram settings with validation"""
        
    def test_telegram_connection(self) -> tuple[bool, str]:
        """Test Telegram bot connectivity"""
```

## User Interface Design

### 1. Settings Panel Extension
```html
<!-- Add to existing settings panel -->
<div class="settings-section" id="telegramSettings">
    <h3>📱 Telegram Integration</h3>
    
    <div class="setting-group">
        <label class="setting-label">
            <input type="checkbox" id="telegramEnabled"> Enable Telegram Integration
        </label>
    </div>
    
    <div class="setting-group" id="telegramConfig">
        <label for="botToken">Bot Token:</label>
        <input type="password" id="botToken" placeholder="Enter your bot token">
        
        <label for="chatId">Chat ID:</label>
        <input type="text" id="chatId" placeholder="Enter chat ID or @username">
        
        <button id="testConnection" class="btn btn-secondary">Test Connection</button>
    </div>
    
    <div class="setting-group">
        <h4>Message Format</h4>
        <label><input type="checkbox" id="includeSessionId"> Include Session ID</label>
        <label><input type="checkbox" id="includeTimestamp"> Include Timestamp</label>
        <label><input type="checkbox" id="includeProjectPath"> Include Project Path</label>
    </div>
</div>
```

### 2. Status Indicators
```html
<!-- Add to connection status area -->
<div class="telegram-status">
    <span class="status-indicator" id="telegramStatus">
        <span class="status-dot"></span>
        <span class="status-text">Telegram: Disconnected</span>
    </span>
</div>
```

## Message Chunking Strategy

### 1. Smart Chunking Algorithm
```python
class MessageChunker:
    def __init__(self, max_length: int = 4096):
        self.max_length = max_length
        
    def chunk_message(self, text: str, preserve_formatting: bool = True) -> list[str]:
        """
        Intelligent message chunking that:
        - Preserves markdown formatting
        - Keeps code blocks intact
        - Maintains readability across chunks
        - Adds chunk indicators (1/3, 2/3, 3/3)
        """
        
    def chunk_code_block(self, code: str, language: str = "") -> list[str]:
        """Special handling for code blocks"""
        
    def add_chunk_headers(self, chunks: list[str], total: int) -> list[str]:
        """Add chunk numbering and navigation"""
```

### 2. Content Type Handling
- **Text Messages**: Smart line breaking, preserve paragraphs
- **Code Blocks**: Maintain syntax highlighting, add language tags
- **File Paths**: Truncate long paths, preserve important parts
- **Error Messages**: Highlight critical information
- **Images**: Send as files with descriptions

## Performance Considerations

### 1. Asynchronous Operations
- **Non-blocking**: All Telegram operations are async
- **Concurrent Processing**: Handle multiple sessions simultaneously
- **Queue Management**: Buffer messages during high load
- **Background Tasks**: Use asyncio for periodic operations

### 2. Resource Management
- **Connection Pooling**: Reuse HTTP connections
- **Memory Management**: Limit log buffer size
- **Cleanup Tasks**: Periodic cleanup of old sessions
- **Rate Limiting**: Respect API quotas and limits

## Error Recovery Strategies

### 1. Network Failures
- **Exponential Backoff**: Retry with increasing delays
- **Circuit Breaker**: Disable after repeated failures
- **Offline Mode**: Queue messages for later delivery
- **Health Checks**: Periodic connectivity testing

### 2. API Errors
- **Token Validation**: Detect invalid/expired tokens
- **Permission Errors**: Handle chat access issues
- **Rate Limiting**: Respect 429 responses
- **Malformed Requests**: Validate before sending

## Implementation Phases

### Phase 1: Core Infrastructure
1. TelegramBotManager implementation
2. Basic message sending/receiving
3. Configuration management
4. Settings UI integration

### Phase 2: MCP Integration
1. MCPLoggingMiddleware development
2. Tool call interception
3. Response forwarding
4. Session correlation

### Phase 3: Bidirectional Bridge
1. MCPTelegramBridge implementation
2. Response routing to WebSocket
3. Conversation threading
4. State synchronization

### Phase 4: Advanced Features
1. Message chunking optimization
2. File upload support
3. Command processing
4. Analytics and monitoring

## Testing Strategy

### 1. Unit Testing
- TelegramBotManager API interactions
- Message chunking algorithms
- Configuration validation
- Error handling scenarios

### 2. Integration Testing
- MCP tool call interception
- WebSocket message routing
- End-to-end message flow
- Security validation

### 3. User Acceptance Testing
- Real Telegram bot setup
- Multiple chat configurations
- Performance under load
- Error recovery validation

## Conclusion

This architecture provides a robust, secure, and scalable foundation for integrating Telegram with the MCP Feedback Enhanced system. The design maintains separation of concerns, ensures backward compatibility, and provides comprehensive error handling while enabling powerful remote monitoring capabilities.

The modular approach allows for incremental implementation and testing, ensuring system stability throughout the development process.