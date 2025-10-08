# MCP Feedback Enhanced - Project Overview

## Purpose
Enhanced MCP (Model Context Protocol) server for interactive user feedback and command execution in AI-assisted development. Provides dual interface support (Web UI and Desktop Application) with intelligent environment detection and cross-platform compatibility.

## Tech Stack
- **Backend**: Python 3.11+ with FastMCP framework
- **Web Framework**: FastAPI with WebSocket support
- **Desktop App**: Tauri-based cross-platform application
- **Image Processing**: Supports PNG, JPG, JPEG, GIF, BMP, WebP
- **Communication**: WebSocket for real-time feedback, Telegram integration

## Key Features
- Dual interface (Web UI + Desktop App)
- Interactive feedback collection with image upload
- Telegram bidirectional communication
- Session management and tracking
- Smart environment detection (SSH Remote, WSL)
- Audio notifications and responsive design

## Architecture
- **Frontend**: Web UI with drag & drop image upload
- **Backend**: FastAPI server with WebSocket endpoints
- **MCP Integration**: FastMCP tools for AI interaction
- **Image Pipeline**: WebFeedbackSession → process_images → FastMCP Image objects