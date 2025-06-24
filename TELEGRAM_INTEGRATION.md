# MCP Feedback Enhanced - Telegram Integration

## Overview

Complete bidirectional integration between MCP (Model Context Protocol) servers and Telegram, enabling VSCode extensions to communicate with users via Telegram chat. Provides real-time feedback collection, session management, and comprehensive monitoring.

## Architecture

```
VSCode Extension ↔ MCP Server ↔ Telegram Bridge ↔ Telegram Bot ↔ User Chat
```

## Core Components

### 1. Telegram Bot Manager (`src/mcp_feedback_enhanced/utils/telegram_manager.py`)
- **Purpose**: Handles Telegram Bot API communication
- **Features**: Rate limiting, message chunking, webhook support, connection management
- **Key Methods**: `send_message()`, `start()`, `stop()`, `test_connection()`

### 2. MCP-Telegram Bridge (`src/mcp_feedback_enhanced/utils/mcp_telegram_bridge.py`)
- **Purpose**: Correlates MCP calls with Telegram sessions
- **Features**: Session management, message correlation, auto-forwarding, bidirectional flow
- **Key Methods**: `create_session()`, `send_mcp_message_to_telegram()`, `get_bridge_status()`

### 3. Message Chunking System (`src/mcp_feedback_enhanced/utils/message_chunker.py`)
- **Purpose**: Intelligently splits long messages for Telegram's 4096 character limit
- **Features**: Content-aware splitting, code block preservation, markdown preservation, navigation
- **Algorithm**: Preserves paragraphs, code blocks, and logical boundaries

### 4. Configuration Management (`src/mcp_feedback_enhanced/utils/config_manager.py`)
- **Purpose**: Secure configuration with encryption for sensitive data
- **Features**: Environment variable support, validation, runtime updates, encryption
- **Security**: Fernet encryption for bot tokens, masked logging

### 5. Logging Middleware (`src/mcp_feedback_enhanced/utils/logging_middleware.py`)
- **Purpose**: Comprehensive event tracking and logging
- **Features**: Tool call tracking, Telegram formatting, statistics, search
- **Integration**: Automatic forwarding to Telegram, dashboard integration

### 6. Web Dashboard (`src/mcp_feedback_enhanced/web/routes/telegram_routes.py`)
- **Purpose**: Real-time monitoring and management interface
- **Features**: Live status, session management, log viewer, configuration panel
- **Access**: `http://localhost:8080/telegram/dashboard`

## Key Features

### Bidirectional Communication
- **Outbound**: VSCode → MCP → Telegram (requests, notifications)
- **Inbound**: Telegram → MCP → VSCode (responses, feedback)
- **Correlation**: Automatic session-based message correlation

### Message Processing
- **Chunking**: Intelligent content-aware message splitting
- **Formatting**: Markdown and code block preservation
- **Navigation**: Chunk indicators and previews
- **Rate Limiting**: Telegram API compliance

### Session Management
- **Auto-creation**: Sessions created per MCP call
- **Timeout**: Configurable session expiration
- **Cleanup**: Automatic expired session cleanup
- **Tracking**: Real-time session monitoring

### Security
- **Encryption**: Bot tokens encrypted with Fernet
- **Validation**: Configuration validation and constraints
- **Masking**: Sensitive data masked in logs
- **Environment**: Environment variable override support

## Configuration

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
TELEGRAM_ENABLED="true"
TELEGRAM_ENABLE_BRIDGE="true"
MCP_WEB_UI_PORT="8080"
```

### Configuration File Structure
```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "encrypted_token",
    "chat_id": "507491548",
    "enable_bridge": true,
    "enable_auto_forwarding": true,
    "enable_chunking": true,
    "max_chunk_size": 3000,
    "session_timeout_minutes": 30,
    "max_concurrent_sessions": 5
  }
}
```

## API Endpoints

### Telegram Dashboard Routes
- `GET /telegram/dashboard` - Main dashboard interface
- `GET /telegram/api/status` - Bridge status and metrics
- `GET /telegram/api/sessions` - Active session list
- `POST /telegram/api/sessions/action` - Session management
- `GET /telegram/api/logs` - Message logs with filtering
- `GET /telegram/api/config` - Configuration management
- `WebSocket /telegram/ws` - Real-time updates

## Usage

### Basic Integration
```python
from mcp_feedback_enhanced.utils.mcp_telegram_bridge import get_bridge

# Send message to Telegram
bridge = get_bridge()
await bridge.send_mcp_message_to_telegram(
    session_id="session_123",
    mcp_call_id="call_456",
    message="Hello from MCP!",
    metadata={"source": "vscode"}
)
```

### Session Management
```python
# Create session
session_id = await bridge.create_session(
    session_id="unique_id",
    chat_id="507491548",
    project_directory="/path/to/project"
)

# End session
await bridge.end_session(session_id)
```

### Configuration Updates
```python
from mcp_feedback_enhanced.utils.config_manager import get_config_manager

config = get_config_manager()
config.update_telegram_config(
    enable_chunking=True,
    max_chunk_size=3000
)
```

## File Structure

```
src/mcp_feedback_enhanced/
├── utils/
│   ├── telegram_manager.py          # Telegram Bot API interface
│   ├── mcp_telegram_bridge.py       # MCP-Telegram correlation
│   ├── message_chunker.py           # Message splitting logic
│   ├── config_manager.py            # Configuration management
│   └── logging_middleware.py        # Event tracking
├── web/
│   ├── routes/telegram_routes.py    # Dashboard API routes
│   └── templates/telegram_dashboard.html  # Dashboard UI
└── server.py                        # Main server integration
```

## Testing

### Test Files
- `test_telegram_integration.py` - Complete integration test
- `test_config_manager.py` - Configuration system test
- `test_mcp_telegram_bridge.py` - Bridge functionality test
- `test_message_chunker.py` - Chunking system test
- `live_telegram_uat.py` - Live user acceptance test

### Running Tests
```bash
# Individual component tests
uv run python test_telegram_integration.py
uv run python test_config_manager.py

# Live integration test
uv run python live_telegram_uat.py

# Bidirectional communication test
uv run python simple_bidirectional_test.py
```

## Deployment

### Production Setup
1. Set environment variables for bot token and chat ID
2. Configure `TELEGRAM_ENABLED=true`
3. Start MCP server with Telegram integration
4. Access dashboard at configured port
5. Monitor via real-time dashboard

### Security Considerations
- Bot tokens are automatically encrypted
- Sensitive data masked in logs
- Configuration validation prevents invalid settings
- Rate limiting prevents API abuse

## Monitoring

### Dashboard Features
- Real-time bridge status and metrics
- Active session management with controls
- Message log viewer with search and filtering
- Configuration panel with validation
- WebSocket-based live updates

### Key Metrics
- Bridge connection status
- Active session count
- Message correlation count
- Pending feedback count
- Processing statistics

## Why This Architecture

### Design Decisions
- **Bridge Pattern**: Decouples MCP from Telegram specifics
- **Session Correlation**: Enables stateful conversations
- **Message Chunking**: Handles Telegram's character limits
- **Configuration Encryption**: Secures sensitive credentials
- **Real-time Dashboard**: Provides operational visibility
- **Middleware Logging**: Enables debugging and monitoring

### Benefits
- **Seamless Integration**: Works with any MCP-compatible tool
- **Production Ready**: Comprehensive error handling and monitoring
- **Secure**: Encrypted configuration and masked logging
- **Scalable**: Session management and rate limiting
- **Maintainable**: Clear separation of concerns and modular design
