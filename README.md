# Office-PowerPoint-MCP-Server
[![smithery badge](https://smithery.ai/badge/@GongRzhe/Office-PowerPoint-MCP-Server)](https://smithery.ai/server/@GongRzhe/Office-PowerPoint-MCP-Server)
![](https://badge.mcpx.dev?type=server 'MCP Server')

A MCP (Model Context Protocol) server for PowerPoint manipulation using python-pptx. This server provides tools for creating, editing, and manipulating PowerPoint presentations through the MCP protocol.

### Example

#### Pormpt

<img width="1280" alt="650f4cc5d0f1ea4f3b1580800cb0deb" src="https://github.com/user-attachments/assets/90633c97-f373-4c85-bc9c-a1d7b891c344" />

#### Output

<img width="1640" alt="084f1cf4bc7e4fcd4890c8f94f536c1" src="https://github.com/user-attachments/assets/420e63a0-15a4-46d8-b149-1408d23af038" />

#### Demo's GIF -> (./public/demo.mp4)

![demo](./public/demo.gif)

## Features

- Round-trip any Open XML presentation (.pptx file) including all its elements
- Add slides
- Populate text placeholders, for example to create a bullet slide
- Add image to slide at arbitrary position and size
- Add textbox to a slide; manipulate text font size and bold
- Add table to a slide
- Add auto shapes (e.g. polygons, flowchart shapes, etc.) to a slide
- Add and manipulate column, bar, line, and pie charts
- Access and change core document properties such as title and subject

## Installation

### Installing via Smithery

To install PowerPoint Manipulation Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@GongRzhe/Office-PowerPoint-MCP-Server):

```bash
npx -y @smithery/cli install @GongRzhe/Office-PowerPoint-MCP-Server --client claude
```

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation Options

#### Option 1: Using the Setup Script (Recommended)

The easiest way to set up the PowerPoint MCP Server is using the provided setup script, which automates the installation process:

```bash
python setup_mcp.py
```

This script will:
- Check prerequisites
- Offer installation options:
  - Install from PyPI (recommended for most users)
  - Set up local development environment
- Install required dependencies
- Generate the appropriate MCP configuration file
- Provide instructions for integrating with Claude Desktop

The script offers different paths based on your environment:
- If you have `uvx` installed, it will configure using UVX (recommended)
- If the server is already installed, it provides configuration options
- If the server is not installed, it offers installation methods

#### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GongRzhe/Office-PowerPoint-MCP-Server.git
   cd Office-PowerPoint-MCP-Server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make the server executable:
   ```bash
   chmod +x ppt_mcp_server.py
   ```

## Usage

Display help text:
```bash
python ppt_mcp_server.py -h
```

### Starting the Stdio Server

Run the stdio server:

```bash
python ppt_mcp_server.py
```

### Starting the Streamable-Http Server

Run the streamable-http server on port 8000:

```bash
python ppt_mcp_server.py --transport http --port 8000
```

Run in Docker
```bash
docker build -t ppt_mcp_server .
docker run -d --rm -p 8000:8000 ppt_mcp_server -t http
```


### MCP Configuration

#### Option 1: Local Python Server

Add the server to your MCP settings configuration file:

```json
{
  "mcpServers": {
    "ppt": {
      "command": "python",
      "args": ["/path/to/ppt_mcp_server.py"],
      "env": {}
    }
  }
}
```

#### Option 2: Using UVX (No Local Installation Required)

If you have `uvx` installed, you can run the server directly from PyPI without local installation:

```json
{
  "mcpServers": {
    "ppt": {
      "command": "uvx",
      "args": [
        "--from", "office-powerpoint-mcp-server", "ppt_mcp_server"
      ],
      "env": {}
    }
  }
}
```

## Available Tools

### Presentation Tools

- **create_presentation**: Create a new PowerPoint presentation
- **open_presentation**: Open an existing PowerPoint presentation from a file
- **save_presentation**: Save the current presentation to a file
- **get_presentation_info**: Get information about the current presentation
- **set_core_properties**: Set core document properties of the current presentation

### Slide Tools

- **add_slide**: Add a new slide to the current presentation
- **get_slide_info**: Get information about a specific slide
- **populate_placeholder**: Populate a placeholder with text
- **add_bullet_points**: Add bullet points to a placeholder

### Text Tools

- **add_textbox**: Add a textbox to a slide

### Image Tools

- **add_image**: Add an image to a slide
- **add_image_from_base64**: Add an image from a base64 encoded string to a slide

### Table Tools

- **add_table**: Add a table to a slide
- **format_table_cell**: Format a table cell

### Shape Tools

- **add_shape**: Add an auto shape to a slide

### Chart Tools

- **add_chart**: Add a chart to a slide

## Examples

### Creating a New Presentation

```python
# Create a new presentation
result = use_mcp_tool(
    server_name="ppt",
    tool_name="create_presentation",
    arguments={}
)
presentation_id = result["presentation_id"]

# Add a title slide
result = use_mcp_tool(
    server_name="ppt",
    tool_name="add_slide",
    arguments={
        "layout_index": 0,  # Title slide layout
        "title": "My Presentation",
        "presentation_id": presentation_id
    }
)
slide_index = result["slide_index"]

# Populate subtitle placeholder
result = use_mcp_tool(
    server_name="ppt",
    tool_name="populate_placeholder",
    arguments={
        "slide_index": slide_index,
        "placeholder_idx": 1,  # Subtitle placeholder
        "text": "Created with PowerPoint MCP Server",
        "presentation_id": presentation_id
    }
)

# Save the presentation
result = use_mcp_tool(
    server_name="ppt",
    tool_name="save_presentation",
    arguments={
        "file_path": "my_presentation.pptx",
        "presentation_id": presentation_id
    }
)
```

### Adding a Chart

```python
# Add a chart slide
result = use_mcp_tool(
    server_name="ppt",
    tool_name="add_slide",
    arguments={
        "layout_index": 1,  # Content slide layout
        "title": "Sales Data",
        "presentation_id": presentation_id
    }
)
slide_index = result["slide_index"]

# Add a column chart
result = use_mcp_tool(
    server_name="ppt",
    tool_name="add_chart",
    arguments={
        "slide_index": slide_index,
        "chart_type": "column",
        "left": 1.0,
        "top": 2.0,
        "width": 8.0,
        "height": 4.5,
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "series_names": ["2023", "2024"],
        "series_values": [
            [100, 120, 140, 160],
            [110, 130, 150, 170]
        ],
        "has_legend": True,
        "legend_position": "bottom",
        "has_data_labels": True,
        "title": "Quarterly Sales",
        "presentation_id": presentation_id
    }
)
```

## License

MIT
