# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server for PowerPoint manipulation using python-pptx. The server provides AI models with the ability to create, edit, and manipulate PowerPoint presentations through standardized MCP tools.

### Core Architecture

The project follows a simple two-module architecture:

- **`ppt_mcp_server.py`**: Main MCP server implementation using FastMCP framework
  - Handles MCP protocol communication
  - Manages presentation state in memory (`presentations` dict)
  - Implements all MCP tool endpoints
  - Provides error handling and parameter validation
- **`ppt_utils.py`**: Utility functions wrapping python-pptx operations
  - Low-level PowerPoint manipulation functions
  - Error recovery mechanisms for common python-pptx issues
  - Direct shape creation bypassing enum problems

### Key Design Patterns

1. **In-Memory State Management**: Presentations are stored in a global `presentations` dictionary with unique IDs, allowing multiple presentations to be worked on simultaneously.

2. **Error Recovery**: The codebase implements robust error handling with fallback approaches, particularly for shape creation where enum issues are common.

3. **Parameter Validation**: Comprehensive validation using constraint functions to ensure data integrity before operations.

4. **Safe Operations**: Wrapper functions that catch and handle exceptions gracefully, returning structured error responses.

## Common Development Commands

### Setup and Installation (uv workflow - recommended for development)
```bash
# Install dependencies and create virtual environment
uv sync

# Install the project in development mode
uv pip install -e .

# Install additional dev dependencies
uv add --dev pytest black ruff mypy
```

### Legacy Setup (for users/deployment)
```bash
# Automated setup (recommended)
python setup_mcp.py

# Manual setup with virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Install from PyPI
pip install office-powerpoint-mcp-server
```

For complete setup instructions including IDE integration, troubleshooting, and advanced configuration, see the main [README.md](README.md) file.

### Running the Server
```bash
# Local development (with uv)
uv run python ppt_mcp_server.py

# Local development (traditional)
python ppt_mcp_server.py

# Via UVX (if installed from PyPI)
uvx --from office-powerpoint-mcp-server ppt_mcp_server
```

### Development Tools
```bash
# Code formatting
uv run black .

# Linting
uv run ruff check .
uv run ruff check --fix .

# Type checking
uv run mypy .

# Testing
uv run pytest

# All checks at once
uv run black . && uv run ruff check --fix . && uv run mypy . && uv run pytest
```

### Testing
```bash
# Manual testing via MCP protocol (stdio)
uv run python ppt_mcp_server.py

# Run tests
uv run pytest

# The server responds to MCP messages on stdin/stdout
```

### Building and Packaging
```bash
# Build package
uv build

# Install in development mode
uv pip install -e .
```

## MCP Configuration

The server can be configured in multiple ways for Claude Desktop:

1. **UVX (Recommended)**: Uses `mcp-config.json` with uvx command
2. **Local Development**: Points to local Python interpreter and script
3. **PyPI Module**: Uses installed package as Python module

Configuration is generated automatically by `setup_mcp.py`.

## Important Implementation Notes

### Shape Creation
The codebase includes a custom `add_shape_direct()` function that bypasses python-pptx enum issues by using direct integer values for shape types. This is more reliable than the standard enum-based approach.

### Presentation Lifecycle
- Presentations must be created or opened before other operations
- Use `current_presentation_id` for implicit presentation context
- All operations validate presentation existence before proceeding

### Error Handling Strategy
- Operations return `{"error": "message"}` for failures
- Use `safe_operation()` wrapper for consistent error handling
- Implement fallback approaches for common failure scenarios

### Dependencies
- `python-pptx`: Core PowerPoint manipulation
- `mcp[cli]`: MCP server framework
- Python 3.6+ required (though 3.10+ recommended per README)