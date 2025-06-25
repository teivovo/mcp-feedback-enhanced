# Changelog

All notable changes to MCP Feedback Enhanced will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Auto-Submit UI Enhancement Project** - Complete message-type rules system with intelligent auto-submit behavior
- **Message-Type Rules Engine** - Backend rules engine with persistent storage and priority-based conflict resolution
- **Rules Management UI** - Comprehensive web interface for managing message-type rules with project grouping
- **MCP Protocol Extension** - Extended interactive_feedback tool with message_type parameter for configurable behaviors
- **Project Grouping System** - Accordion-based interface for organizing rules by project patterns
- **Responsive UI Overhaul** - Complete responsive design improvements with mobile-friendly interface
- **Enhanced Audio System** - Improved audio permission handling with browser autoplay restrictions support
- **Smart Auto-Scroll** - Intelligent auto-scroll functionality with user position detection
- **Project Context Display** - Enhanced project and agent context information display

### Enhanced
- **Header Layout** - Responsive header design with CSS Grid system and proper breakpoints
- **Template Selection** - Redesigned auto-submit template selection popup with better UX
- **Connection Monitor** - Improved connection status display with responsive design
- **Settings Management** - Enhanced settings interface with better organization
- **Error Handling** - Comprehensive error handling framework with user-friendly messages
- **Performance** - Optimized rendering and interaction handling for better user experience

### Technical Improvements
- **Modular Architecture** - Improved JavaScript module organization and loading
- **CSS Variables** - Consistent theming with CSS custom properties
- **API Design** - RESTful API endpoints for rules management operations
- **Storage System** - JSON-based persistent storage with atomic operations and backup management
- **Validation Framework** - Comprehensive rule validation and error handling
- **Testing Suite** - Complete test files for backend engine and frontend UI

### Fixed
- **Responsive Issues** - Fixed header cramping and layout breaks on mobile devices
- **Audio Playback** - Resolved browser autoplay restrictions with proper permission handling
- **Scroll Behavior** - Fixed auto-scroll interrupting user reading experience
- **Template UX** - Improved template selection interaction model
- **Connection Display** - Fixed connection monitor responsive design issues

## [Previous Versions]

### [1.0.0] - Initial Release
- Basic MCP feedback collection functionality
- Web UI interface for feedback submission
- Image upload and processing capabilities
- Command execution and logging
- Session management
- Telegram integration support
- Multi-language support (English/Chinese)
- Basic settings management

---

## Project Structure

### Core Components
- **Backend Rules Engine** (`src/mcp_feedback_enhanced/utils/rules_engine.py`)
- **Rules Storage** (`src/mcp_feedback_enhanced/utils/rules_storage.py`)
- **Frontend Rules Manager** (`src/mcp_feedback_enhanced/web/static/js/modules/rules-manager.js`)
- **API Routes** (`src/mcp_feedback_enhanced/web/routes/main_routes.py`)
- **Enhanced Server** (`src/mcp_feedback_enhanced/server.py`)

### Key Features
1. **Message-Type Rules System**
   - Auto-submit overrides based on message types
   - Response headers and footers customization
   - Timeout overrides for specific scenarios
   - Template overrides for different contexts
   - Custom configuration merging

2. **Project Grouping**
   - All Projects: Universal rules
   - Specific Projects: Pattern-based targeting
   - Exclude Projects: Exclusion patterns
   - Regex Patterns: Advanced pattern matching

3. **Rule Types**
   - `auto_submit_override`: Controls automatic submission
   - `timeout_override`: Modifies timeout values
   - `response_header`: Prepends text to responses
   - `response_footer`: Appends text to responses
   - `template_override`: Changes template selection
   - `custom_config`: Arbitrary configuration merging

### Default Rules
- **Error Report Auto-Submit**: 5-minute auto-submit for error reports
- **Testing Auto-Submit**: 7.5-minute auto-submit for testing results
- **Deployment Auto-Submit**: 5-minute auto-submit for deployment confirmations
- **Code Review Header**: Standard header for code review responses
- **Security Footer**: Security disclaimer for security-related responses

### API Endpoints
- `GET /api/rules` - Retrieve all rules
- `POST /api/rules/test` - Test rule matching
- `POST /api/rules` - Create new rule
- `PUT /api/rules/{id}` - Update existing rule
- `DELETE /api/rules/{id}` - Delete rule

### Testing
- **Backend Testing**: `test_rules_engine.html`
- **Frontend Testing**: `test_rules_management_ui.html`
- **Integration Testing**: Built into main application

---

## Migration Guide

### From Previous Versions
1. **Backup Settings**: Export existing settings before upgrading
2. **Update Dependencies**: Ensure all required modules are installed
3. **Database Migration**: Rules storage will be automatically initialized
4. **Configuration**: Review and update configuration files as needed
5. **Testing**: Use provided test files to verify functionality

### Breaking Changes
- **MCP Tool Signature**: `interactive_feedback` now accepts optional `message_type` parameter
- **Module Loading**: New rules management module added to loading sequence
- **API Changes**: New API endpoints added for rules management

### Compatibility
- **Backward Compatible**: Existing functionality remains unchanged
- **Optional Features**: All new features are optional and don't affect existing workflows
- **Graceful Degradation**: System works without rules configuration

---

## Development

### Building
```bash
# Install dependencies
pip install -e .

# Run tests
python -m pytest tests/

# Start development server
python -m mcp_feedback_enhanced.web.main
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript
- Maintain consistent CSS formatting
- Add comprehensive documentation

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original MCP Feedback Enhanced by Fábio Ferreira
- Enhanced by Minidoracat with Web UI, image support, and environment detection
- Auto-Submit UI Enhancement project implementation
- Community contributors and testers
