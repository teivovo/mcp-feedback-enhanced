# MCP Feedback Enhanced - Architecture Documentation

## System Overview

MCP Feedback Enhanced is a comprehensive feedback collection system with intelligent auto-submit capabilities, message-type rules management, and responsive web interface. The system follows a modular architecture with clear separation of concerns.

## Core Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│                    MCP Server Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Interactive    │  │  Rules Engine   │  │   System    │ │
│  │   Feedback      │  │    Backend      │  │    Info     │ │
│  │     Tool        │  │                 │  │    Tool     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Web UI Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Frontend      │  │  Rules Manager  │  │   Session   │ │
│  │   Interface     │  │      UI         │  │  Manager    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Storage Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Rules         │  │   Session       │  │   Settings  │ │
│  │   Storage       │  │   Storage       │  │   Storage   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Module Architecture

### Backend Components

#### 1. MCP Server (`server.py`)
- **Purpose**: Main MCP protocol implementation
- **Responsibilities**:
  - Tool registration and handling
  - Request/response processing
  - Error handling and logging
  - Rules engine integration

#### 2. Rules Engine (`utils/rules_engine.py`)
- **Purpose**: Core rules processing and application
- **Components**:
  - `MessageTypeRulesEngine`: Main engine class
  - Rule matching algorithms
  - Priority resolution system
  - Configuration merging logic

#### 3. Rules Storage (`utils/rules_storage.py`)
- **Purpose**: Persistent storage management
- **Features**:
  - JSON-based storage with atomic operations
  - Backup management and cleanup
  - Thread-safe operations
  - Data validation and migration

#### 4. Error Handler (`utils/error_handler.py`)
- **Purpose**: Centralized error handling
- **Features**:
  - Error categorization and logging
  - User-friendly error messages
  - Context preservation
  - Recovery mechanisms

### Frontend Components

#### 1. Rules Manager (`static/js/modules/rules-manager.js`)
- **Purpose**: Rules management interface
- **Features**:
  - Accordion-based project grouping
  - Visual rule editor
  - Real-time testing panel
  - Form validation and submission

#### 2. UI Manager (`static/js/modules/ui-manager.js`)
- **Purpose**: Main UI coordination
- **Responsibilities**:
  - Component initialization
  - Event coordination
  - State management
  - Responsive behavior

#### 3. Session Manager (`static/js/modules/session-manager.js`)
- **Purpose**: Session state management
- **Features**:
  - WebSocket connection handling
  - Session persistence
  - State synchronization
  - Cleanup operations

### Web Layer

#### 1. Main Routes (`web/routes/main_routes.py`)
- **Purpose**: HTTP API endpoints
- **Endpoints**:
  - `/api/rules` - Rules CRUD operations
  - `/api/rules/test` - Rule testing
  - `/api/session-status` - Session management
  - `/api/settings` - Configuration management

#### 2. Template System (`web/templates/feedback.html`)
- **Purpose**: Main web interface
- **Features**:
  - Responsive design
  - Tab-based navigation
  - Module loading system
  - Internationalization support

## Data Flow

### Rule Application Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server    │───▶│  Rules Engine   │
│                 │    │                 │    │                 │
│ interactive_    │    │ 1. Receive      │    │ 1. Load rules   │
│ feedback()      │    │    request      │    │ 2. Match rules  │
│                 │    │ 2. Extract      │    │ 3. Apply config │
│ + message_type  │    │    parameters   │    │ 4. Return       │
│ + project_dir   │    │ 3. Call rules   │    │    merged       │
│                 │    │    engine       │    │    config       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │◀───│  Launch Web     │◀───│  Applied        │
│                 │    │  Feedback UI    │    │  Configuration  │
│ 1. Display      │    │                 │    │                 │
│    interface    │    │ 1. Use applied  │    │ - auto_submit   │
│ 2. Apply rules  │    │    config       │    │ - timeout       │
│ 3. Collect      │    │ 2. Configure    │    │ - response_text │
│    feedback     │    │    interface    │    │ - template_id   │
│                 │    │ 3. Handle       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Rules Management Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Rules UI       │───▶│   API Routes    │───▶│  Rules Storage  │
│                 │    │                 │    │                 │
│ 1. User         │    │ 1. Validate     │    │ 1. Atomic       │
│    interaction  │    │    request      │    │    write        │
│ 2. Form         │    │ 2. Process      │    │ 2. Backup       │
│    validation   │    │    data         │    │    creation     │
│ 3. API call     │    │ 3. Call         │    │ 3. Cache        │
│                 │    │    storage      │    │    invalidation │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Update     │◀───│   Response      │◀───│   Storage       │
│                 │    │                 │    │   Result        │
│ 1. Update       │    │ 1. Success/     │    │                 │
│    display      │    │    error        │    │ 1. File         │
│ 2. Refresh      │    │    status       │    │    updated      │
│    rules list   │    │ 2. Updated      │    │ 2. Backup       │
│ 3. Show         │    │    data         │    │    created      │
│    feedback     │    │ 3. Validation   │    │ 3. Cache        │
│                 │    │    results      │    │    cleared      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Storage Architecture

### Rules Storage Format

```json
{
  "version": "1.0.0",
  "created_at": "2025-01-05T10:30:00Z",
  "updated_at": "2025-01-05T15:45:00Z",
  "rules": [
    {
      "id": "unique_rule_id",
      "name": "Rule Name",
      "description": "Rule description",
      "message_type": "error_report",
      "rule_type": "auto_submit_override",
      "value": true,
      "timeout_override": 300,
      "project_filter": {
        "type": "all"
      },
      "priority": 100,
      "enabled": true,
      "created_at": "2025-01-05T10:30:00Z",
      "updated_at": "2025-01-05T15:45:00Z"
    }
  ],
  "metadata": {
    "total_rules": 1,
    "enabled_rules": 1,
    "last_backup": "2025-01-05T15:40:00Z"
  }
}
```

### File System Structure

```
~/.config/mcp-feedback-enhanced/
├── rules/
│   ├── rules.json              # Main rules storage
│   ├── backups/
│   │   ├── rules_backup_20250105_154000.json
│   │   └── rules_backup_20250105_153000.json
│   └── cache/
│       └── rules_cache.json    # Performance cache
├── sessions/
│   ├── session_history.json   # Session storage
│   └── active_sessions.json   # Active sessions
└── settings/
    ├── ui_settings.json       # UI preferences
    └── app_settings.json      # Application settings
```

## Security Architecture

### Data Protection

1. **Local Storage Only**: All data stored locally, no external transmission
2. **File Permissions**: Restricted file access (600 permissions)
3. **Input Validation**: Comprehensive validation at all entry points
4. **Sanitization**: XSS protection and data sanitization
5. **Backup Encryption**: Optional backup encryption support

### Access Control

1. **Local Access**: Web UI accessible only on localhost
2. **Session Management**: Secure session handling with timeouts
3. **API Authentication**: Internal API with request validation
4. **File System**: Protected configuration directory

## Performance Architecture

### Optimization Strategies

1. **Caching System**:
   - Rules cache with file modification time tracking
   - UI component caching
   - API response caching

2. **Lazy Loading**:
   - Module loading on demand
   - UI components initialized when needed
   - Rules loaded only when required

3. **Efficient Algorithms**:
   - Optimized rule matching with early termination
   - Priority-based sorting with minimal comparisons
   - Pattern matching with compiled regex caching

4. **Memory Management**:
   - Automatic cleanup of unused resources
   - Garbage collection optimization
   - Memory leak prevention

### Performance Metrics

- **Rule Evaluation**: < 1ms for typical rule sets (< 100 rules)
- **UI Rendering**: < 100ms for complete interface initialization
- **Storage Operations**: < 10ms for read/write operations
- **Memory Usage**: < 5MB for typical configurations
- **Startup Time**: < 500ms for complete system initialization

## Scalability Considerations

### Current Limits

- **Rules**: Optimized for < 1000 rules per system
- **Projects**: Supports unlimited project patterns
- **Sessions**: Handles multiple concurrent sessions
- **Storage**: JSON format suitable for < 10MB data

### Future Scalability

1. **Database Backend**: Migration path to SQLite/PostgreSQL
2. **Distributed Storage**: Support for shared rule repositories
3. **Caching Layer**: Redis integration for high-performance caching
4. **API Scaling**: RESTful API ready for horizontal scaling

## Integration Points

### MCP Protocol Integration

1. **Tool Registration**: Standard MCP tool registration
2. **Parameter Handling**: Extended parameter support
3. **Response Format**: Standard MCP response format
4. **Error Handling**: MCP-compliant error responses

### External System Integration

1. **Telegram**: Optional Telegram bot integration
2. **File Systems**: Cross-platform file system support
3. **Browsers**: Modern browser compatibility
4. **Development Tools**: IDE and editor integration support

## Deployment Architecture

### Development Environment

```
Development Machine
├── Python Environment (3.8+)
├── MCP Server Process
├── Web UI Server (FastAPI)
├── File System Storage
└── Browser Interface
```

### Production Environment

```
Production Server
├── MCP Server (systemd service)
├── Web UI (reverse proxy)
├── Storage (persistent volume)
├── Backup System (automated)
└── Monitoring (logs/metrics)
```

## Monitoring and Observability

### Logging Architecture

1. **Structured Logging**: JSON-formatted logs with context
2. **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
3. **Log Rotation**: Automatic log rotation and cleanup
4. **Error Tracking**: Centralized error collection and analysis

### Metrics Collection

1. **Performance Metrics**: Response times, throughput, resource usage
2. **Business Metrics**: Rule usage, session statistics, user interactions
3. **System Metrics**: Memory usage, file system operations, cache hit rates
4. **Error Metrics**: Error rates, failure patterns, recovery times

### Health Checks

1. **System Health**: File system access, memory usage, process status
2. **Service Health**: MCP server status, web UI availability, API responsiveness
3. **Data Health**: Storage integrity, backup status, cache consistency
4. **Integration Health**: External service connectivity, dependency status

## Future Architecture Considerations

### Planned Enhancements

1. **Microservices**: Split into independent services
2. **Event-Driven**: Implement event-driven architecture
3. **Real-Time**: WebSocket-based real-time updates
4. **Multi-Tenant**: Support for multiple organizations
5. **Cloud Native**: Kubernetes deployment support

### Technology Evolution

1. **Frontend**: Migration to modern frameworks (React/Vue)
2. **Backend**: Async/await optimization
3. **Storage**: NoSQL database integration
4. **API**: GraphQL API implementation
5. **Security**: OAuth2/OIDC integration
