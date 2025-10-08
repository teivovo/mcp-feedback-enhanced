# Development Commands

## Testing Commands
```bash
# Functional testing
make test-func                    # Standard functional testing
make test-web                     # Web UI testing (continuous running)
make test-desktop-func            # Desktop application functional testing

# Unit testing
make test                         # Run all unit tests
make test-fast                    # Fast testing (skip slow tests)
make test-cov                     # Test with coverage report

# Direct commands
python -m mcp_feedback_enhanced test              # Standard functional testing
python -m mcp_feedback_enhanced test --web        # Web UI testing
python -m mcp_feedback_enhanced test --desktop    # Desktop testing
```

## Code Quality
```bash
make check                        # Complete code quality check
make quick-check                  # Quick check with auto-fix
make lint                         # Run linting with Ruff
make format                       # Format code with Ruff
make type-check                   # Run type checking with mypy
```

## Development Setup
```bash
make dev-setup                    # Complete development setup
make install-dev                  # Install development dependencies
make install-hooks                # Install pre-commit hooks
```

## Desktop Application
```bash
make build-desktop                # Build desktop application (debug)
make build-desktop-release        # Build desktop application (release)
make test-desktop                 # Test desktop application
make clean-desktop                # Clean desktop build artifacts
```