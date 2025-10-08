# API Endpoints Test Suite Documentation

## Overview

The API Endpoints Test Suite provides comprehensive automated testing for all Auto-Submit UI Enhancement API endpoints. This test suite validates CRUD operations, request/response handling, error scenarios, security measures, and performance characteristics of the REST API.

## Test Suite Components

### 1. Main Test Files

- **`test_api_endpoints.py`** - Main test suite with comprehensive API testing
- **`test_api_scenarios.json`** - Test scenarios and mock data for various test cases
- **`API_TEST_DOCUMENTATION.md`** - This documentation file

### 2. Test Categories

#### A. Core API Endpoints Tests (`APIEndpointsTestSuite`)
- **GET /api/rules** - Retrieve all rules with pagination and filtering
- **POST /api/rules/test** - Test rule matching against message types and project paths
- **POST /api/rules** - Create new rules with validation
- **PUT /api/rules/{id}** - Update existing rules
- **DELETE /api/rules/{id}** - Delete rules by ID
- **GET /api/rules/{id}** - Retrieve individual rules by ID

#### B. Data Validation Tests (`APIValidationTests`)
- **Valid Rule Creation** - Tests creation of properly formatted rules
- **Invalid Rule Handling** - Tests rejection of malformed or invalid rules
- **Edge Cases** - Tests boundary conditions and special characters
- **Unicode Support** - Tests handling of international characters and emojis

#### C. Security Tests (`APISecurityTests`)
- **SQL Injection Protection** - Tests against SQL injection attempts
- **XSS Protection** - Tests against cross-site scripting attempts
- **Path Traversal Protection** - Tests against directory traversal attacks
- **Input Sanitization** - Tests proper handling of malicious input

#### D. Performance Tests (`APIPerformanceTests`)
- **Response Time Testing** - Validates API response times under normal load
- **Bulk Request Performance** - Tests performance with high-volume requests
- **Memory Usage Monitoring** - Tracks memory consumption during operations
- **Concurrent Request Handling** - Tests API behavior under concurrent load

## API Endpoints Tested

### Rules Management API

#### GET /api/rules
- **Purpose**: Retrieve all rules with metadata
- **Response Format**: JSON with rules array, total count, and enabled count
- **Test Coverage**: Response structure, data integrity, performance
- **Performance Target**: < 100ms response time

#### POST /api/rules/test
- **Purpose**: Test rule matching for given message type and project path
- **Request Format**: JSON with message_type and project_path
- **Response Format**: JSON with matching rules and metadata
- **Test Coverage**: Rule matching logic, project filtering, performance
- **Performance Target**: < 100ms response time

#### POST /api/rules
- **Purpose**: Create new rules
- **Request Format**: JSON with complete rule definition
- **Validation**: Required fields, data types, business logic constraints
- **Test Coverage**: Valid creation, validation errors, security
- **Performance Target**: < 200ms response time

#### PUT /api/rules/{id}
- **Purpose**: Update existing rules
- **Request Format**: JSON with updated rule fields
- **Test Coverage**: Successful updates, not found errors, validation
- **Performance Target**: < 200ms response time

#### DELETE /api/rules/{id}
- **Purpose**: Delete rules by ID
- **Test Coverage**: Successful deletion, not found errors, security
- **Performance Target**: < 100ms response time

#### GET /api/rules/{id}
- **Purpose**: Retrieve individual rule by ID
- **Test Coverage**: Successful retrieval, not found errors, security
- **Performance Target**: < 50ms response time

## Test Data and Scenarios

### Valid Test Rules
```json
{
  "id": "test_auto_submit_rule",
  "name": "Test Auto Submit Rule",
  "description": "Test rule for automatic submission",
  "message_type": "error_report",
  "rule_type": "auto_submit_override",
  "value": true,
  "timeout_override": 300,
  "project_filter": {"type": "all"},
  "priority": 100,
  "enabled": true
}
```

### Invalid Test Cases
- Missing required fields (name, message_type, rule_type)
- Invalid rule types
- Invalid priority values (< 1 or > 1000)
- Invalid project filter types
- Empty or null values

### Security Test Cases
- SQL injection attempts in rule IDs
- XSS attempts in rule names and descriptions
- Path traversal attempts in endpoints
- Oversized payloads

### Performance Test Scenarios
- Single request performance measurement
- Bulk request testing (100+ requests)
- Concurrent request handling (10+ simultaneous)
- Memory usage monitoring during operations

## Usage Instructions

### Running All Tests
```bash
python test_api_endpoints.py
```

### Running with Verbose Output
```bash
python test_api_endpoints.py --verbose
```

### Running Performance Tests Only
```bash
python test_api_endpoints.py --performance-only
```

### Running Specific Endpoint Tests
```bash
python test_api_endpoints.py --endpoint /api/rules
```

## Test Framework Architecture

### Mock API Implementation
The test suite includes a complete mock FastAPI application that simulates the real API behavior:
- Proper HTTP status codes
- Request validation
- Error handling
- Security measures
- Performance characteristics

### Test Client Integration
Uses FastAPI's TestClient for:
- HTTP request simulation
- Response validation
- Performance measurement
- Error handling testing

### Data Validation Framework
Comprehensive validation testing for:
- Required field validation
- Data type validation
- Business rule validation
- Security input validation

## Performance Benchmarks

### Response Time Targets
- **GET operations**: < 100ms
- **POST operations**: < 200ms
- **PUT operations**: < 200ms
- **DELETE operations**: < 100ms

### Throughput Targets
- **Concurrent requests**: 95% success rate with 10+ simultaneous requests
- **Bulk operations**: < 50ms average per request for 100+ requests
- **Memory usage**: < 10MB increase for 1000 requests

### Performance Monitoring
- Real-time response time measurement
- Memory usage tracking
- Concurrent request success rate monitoring
- Performance regression detection

## Error Handling Validation

### HTTP Status Codes Tested
- **200 OK**: Successful operations
- **400 Bad Request**: Invalid input data
- **404 Not Found**: Non-existent resources
- **405 Method Not Allowed**: Invalid HTTP methods
- **413 Payload Too Large**: Oversized requests

### Error Response Format
```json
{
  "status": "error",
  "message": "Descriptive error message",
  "details": "Additional error context"
}
```

## Security Testing

### Input Validation
- SQL injection prevention
- XSS attack prevention
- Path traversal protection
- Input sanitization verification

### Security Headers
- Content-Type validation
- Request size limits
- Rate limiting (when implemented)

## Integration with CI/CD

### Automated Testing
The test suite is designed for integration with continuous integration pipelines:
- Exit codes indicate test success/failure
- JSON output for automated parsing
- Performance metrics for monitoring
- Security validation for compliance

### Test Reports
- Detailed test execution logs
- Performance metrics and trends
- Security validation results
- Error analysis and debugging information

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure FastAPI and required dependencies are installed
2. **Test Failures**: Check mock API implementation and test data
3. **Performance Issues**: Verify system resources and test environment
4. **Security Test Failures**: Review input validation and error handling

### Debug Mode
Enable verbose output for detailed test execution information:
```bash
python test_api_endpoints.py --verbose
```

### Test Data Validation
Verify test scenarios JSON file syntax and structure:
```bash
python -m json.tool test_api_scenarios.json
```

## Extending the Test Suite

### Adding New Endpoints
1. Add endpoint to mock FastAPI app
2. Create test methods in appropriate test class
3. Add test scenarios to JSON file
4. Update documentation

### Adding New Test Categories
1. Create new test class inheriting from unittest.TestCase
2. Add class to test runner configuration
3. Implement setUp and tearDown methods
4. Add comprehensive test methods

### Performance Testing
1. Define performance targets
2. Implement measurement logic
3. Add assertions for performance validation
4. Include in automated reporting

## Maintenance and Updates

### Regular Maintenance Tasks
- Update test data to reflect API changes
- Review and update performance targets
- Add tests for new security vulnerabilities
- Optimize test execution time

### Version Compatibility
- Test suite is designed to be backward compatible
- Update mock API to match real API changes
- Maintain test data format consistency
- Document breaking changes

This comprehensive test suite ensures the reliability, security, and performance of all API endpoints while providing detailed validation and monitoring capabilities.
