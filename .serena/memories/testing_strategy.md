# Comprehensive Testing Strategy for Image Processing

## Objective
Test and fix image sending from WebUI to MCP feedback server without requiring VS Code restarts.

## Testing Environment
- **Test Port**: 8772 (keeping 8771 for main communication)
- **Scope**: Focus on WebUI image processing first, Telegram later
- **Approach**: Independent test server with comprehensive pipeline testing

## Phase 1: Independent Test Server Setup
1. Create standalone test server on port 8772
2. Set up minimal MCP server with corrected image handling
3. Create test web UI connecting to test server
4. Isolate testing from main server operations

## Phase 2: Image Processing Pipeline Testing
1. **Frontend Testing**: Test drag & drop, clipboard paste image upload
2. **Data Format Testing**: Verify base64 encoding/decoding at each stage
3. **Session Processing**: Test WebFeedbackSession._process_images() method
4. **Server Processing**: Test server.py image processing functions
5. **FastMCP Integration**: Test Image object creation and serialization

## Phase 3: End-to-End Validation
1. Upload test images through WebUI
2. Trace data flow through each processing stage
3. Verify final output format for MCP consumption
4. Test multiple image formats (PNG, JPG, GIF, etc.)

## Phase 4: Fix Implementation & Integration
1. Identify and fix specific pipeline issues
2. Implement fixes maintaining backward compatibility
3. Validate fixes with comprehensive test cases
4. Test integration with main server