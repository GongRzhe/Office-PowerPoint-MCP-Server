#!/usr/bin/env python
"""
MCP Server for PowerPoint manipulation using python-pptx.
"""
import os
import json
import tempfile
from typing import Dict, List, Optional, Any, Union
from mcp.server.fastmcp import FastMCP
import argparse

import ppt_utils

# Initialize the FastMCP server
app = FastMCP(
    name="ppt-mcp-server",
    description="MCP Server for PowerPoint manipulation using python-pptx",
    version="1.0.0"
)

# Global state to store presentations in memory
presentations = {}
current_presentation_id = None

# ---- Helper Functions ----

def get_current_presentation():
    """Get the current presentation object or raise an error if none is loaded."""
    if current_presentation_id is None or current_presentation_id not in presentations:
        raise ValueError("No presentation is currently loaded. Please create or open a presentation first.")
    return presentations[current_presentation_id]

def validate_parameters(params):
    """
    Validate parameters against constraints.
    
    Args:
        params: Dictionary of parameter name: (value, constraints) pairs
        
    Returns:
        (True, None) if all valid, or (False, error_message) if invalid
    """
    for param_name, (value, constraints) in params.items():
        for constraint_func, error_msg in constraints:
            if not constraint_func(value):
                return False, f"Parameter '{param_name}': {error_msg}"
    return True, None

def is_positive(value):
    """Check if a value is positive."""
    return value > 0

def is_non_negative(value):
    """Check if a value is non-negative."""
    return value >= 0

def is_in_range(min_val, max_val):
    """Create a function that checks if a value is in a range."""
    return lambda x: min_val <= x <= max_val

def is_in_list(valid_list):
    """Create a function that checks if a value is in a list."""
    return lambda x: x in valid_list

def is_valid_rgb(color_list):
    """Check if a color list is a valid RGB tuple."""
    if not isinstance(color_list, list) or len(color_list) != 3:
        return False
    return all(isinstance(c, int) and 0 <= c <= 255 for c in color_list)

def add_shape_direct(slide, shape_type: str, left: float, top: float, width: float, height: float) -> Any:
    """
    Add an auto shape to a slide using direct integer values instead of enum objects.
    
    This implementation provides a reliable alternative that bypasses potential 
    enum-related issues in the python-pptx library.
    
    Args:
        slide: The slide object
        shape_type: Shape type string (e.g., 'rectangle', 'oval', 'triangle')
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        
    Returns:
        The created shape
    """
    from pptx.util import Inches
    
    # Direct mapping of shape types to their integer values
    # These values are directly from the MS Office VBA documentation
    shape_type_map = {
        'rectangle': 1,
        'rounded_rectangle': 2, 
        'oval': 9,
        'diamond': 4,
        'triangle': 5,  # This is ISOSCELES_TRIANGLE
        'right_triangle': 6,
        'pentagon': 56,
        'hexagon': 10,
        'heptagon': 11,
        'octagon': 12,
        'star': 12,  # This is STAR_5_POINTS (value 12)
        'arrow': 13,
        'cloud': 35,
        'heart': 21,
        'lightning_bolt': 22,
        'sun': 23,
        'moon': 24,
        'smiley_face': 17,
        'no_symbol': 19,
        'flowchart_process': 112,
        'flowchart_decision': 114,
        'flowchart_data': 115,
        'flowchart_document': 119
    }
    
    # Check if shape type is valid before trying to use it
    shape_type_lower = str(shape_type).lower()
    if shape_type_lower not in shape_type_map:
        available_shapes = ', '.join(sorted(shape_type_map.keys()))
        raise ValueError(f"Unsupported shape type: '{shape_type}'. Available shape types: {available_shapes}")
    
    # Get the integer value for the shape type
    shape_value = shape_type_map[shape_type_lower]
    
    # Create the shape using the direct integer value
    try:
        # The integer value is passed directly to add_shape
        shape = slide.shapes.add_shape(
            shape_value, Inches(left), Inches(top), Inches(width), Inches(height)
        )
        return shape
    except Exception as e:
        raise ValueError(f"Failed to create '{shape_type}' shape using direct value {shape_value}: {str(e)}")

# ---- Presentation Tools ----

@app.tool()
def create_presentation(id: Optional[str] = None) -> Dict:
    """Create a new PowerPoint presentation."""
    global current_presentation_id
    
    # Create a new presentation
    pres = ppt_utils.create_presentation()
    
    # Generate an ID if not provided
    if id is None:
        id = f"presentation_{len(presentations) + 1}"
    
    # Store the presentation
    presentations[id] = pres
    current_presentation_id = id
    
    return {
        "presentation_id": id,
        "message": f"Created new presentation with ID: {id}",
        "slide_count": len(pres.slides)
    }

@app.tool()
def open_presentation(file_path: str, id: Optional[str] = None) -> Dict:
    """Open an existing PowerPoint presentation from a file."""
    global current_presentation_id
    
    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "error": f"File not found: {file_path}"
        }
    
    # Open the presentation
    try:
        pres = ppt_utils.open_presentation(file_path)
    except Exception as e:
        return {
            "error": f"Failed to open presentation: {str(e)}"
        }
    
    # Generate an ID if not provided
    if id is None:
        id = f"presentation_{len(presentations) + 1}"
    
    # Store the presentation
    presentations[id] = pres
    current_presentation_id = id
    
    return {
        "presentation_id": id,
        "message": f"Opened presentation from {file_path} with ID: {id}",
        "slide_count": len(pres.slides)
    }

@app.tool()
def save_presentation(file_path: str, presentation_id: Optional[str] = None) -> Dict:
    """Save a presentation to a file."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    # Save the presentation
    try:
        saved_path = ppt_utils.save_presentation(presentations[pres_id], file_path)
        return {
            "message": f"Presentation saved to {saved_path}",
            "file_path": saved_path
        }
    except Exception as e:
        return {
            "error": f"Failed to save presentation: {str(e)}"
        }

@app.tool()
def get_presentation_info(presentation_id: Optional[str] = None) -> Dict:
    """Get information about a presentation."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Get slide layouts
    layouts = ppt_utils.get_slide_layouts(pres)
    
    # Get core properties
    core_props = ppt_utils.get_core_properties(pres)
    
    return {
        "presentation_id": pres_id,
        "slide_count": len(pres.slides),
        "slide_layouts": layouts,
        "core_properties": core_props
    }

@app.tool()
def set_core_properties(
    title: Optional[str] = None,
    subject: Optional[str] = None,
    author: Optional[str] = None,
    keywords: Optional[str] = None,
    comments: Optional[str] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Set core document properties."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Set core properties
    try:
        ppt_utils.set_core_properties(
            pres, title=title, subject=subject, author=author, 
            keywords=keywords, comments=comments
        )
        
        # Get updated properties
        updated_props = ppt_utils.get_core_properties(pres)
        
        return {
            "message": "Core properties updated successfully",
            "core_properties": updated_props
        }
    except Exception as e:
        return {
            "error": f"Failed to set core properties: {str(e)}"
        }

# ---- Slide Tools ----

@app.tool()
def add_slide(
    layout_index: int = 1,
    title: Optional[str] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add a new slide to the presentation."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Validate layout index
    if layout_index < 0 or layout_index >= len(pres.slide_layouts):
        return {
            "error": f"Invalid layout index: {layout_index}. Available layouts: 0-{len(pres.slide_layouts) - 1}",
            "available_layouts": ppt_utils.get_slide_layouts(pres)
        }
    
    # Add the slide
    slide, error = ppt_utils.safe_operation(
        "add_slide",
        lambda: ppt_utils.add_slide(pres, layout_index)
    )
    
    if error:
        return {"error": error}
    
    # Set the title if provided
    if title and slide[0].shapes.title:
        _, error = ppt_utils.safe_operation(
            "set_title",
            lambda: ppt_utils.set_title(slide[0], title)
        )
        if error:
            return {
                "warning": f"Slide created but failed to set title: {error}",
                "slide_index": len(pres.slides) - 1,
                "layout_name": slide[1].name
            }
    
    # Get placeholders
    placeholders, error = ppt_utils.safe_operation(
        "get_placeholders",
        lambda: ppt_utils.get_placeholders(slide[0])
    )
    
    if error:
        placeholders = []
    
    return {
        "message": f"Added slide with layout '{slide[1].name}'",
        "slide_index": len(pres.slides) - 1,
        "layout_name": slide[1].name,
        "placeholders": placeholders
    }

@app.tool()
def get_slide_info(slide_index: int, presentation_id: Optional[str] = None) -> Dict:
    """Get information about a specific slide."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    # Get placeholders
    placeholders = ppt_utils.get_placeholders(slide)
    
    # Get shapes information
    shapes_info = []
    for i, shape in enumerate(slide.shapes):
        shape_info = {
            "index": i,
            "name": shape.name,
            "shape_type": str(shape.shape_type),
            "width": shape.width.inches,
            "height": shape.height.inches,
            "left": shape.left.inches,
            "top": shape.top.inches
        }
        shapes_info.append(shape_info)
    
    return {
        "slide_index": slide_index,
        "placeholders": placeholders,
        "shapes": shapes_info
    }

@app.tool()
def populate_placeholder(
    slide_index: int,
    placeholder_idx: int,
    text: str,
    presentation_id: Optional[str] = None
) -> Dict:
    """Populate a placeholder with text."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    try:
        # Check if placeholder exists
        if placeholder_idx not in [p.placeholder_format.idx for p in slide.placeholders]:
            return {
                "error": f"Placeholder with index {placeholder_idx} not found in slide {slide_index}"
            }
        
        # Populate the placeholder
        ppt_utils.populate_placeholder(slide, placeholder_idx, text)
        
        return {
            "message": f"Populated placeholder {placeholder_idx} in slide {slide_index}"
        }
    except Exception as e:
        return {
            "error": f"Failed to populate placeholder: {str(e)}"
        }

@app.tool()
def add_bullet_points(
    slide_index: int,
    placeholder_idx: int,
    bullet_points: List[str],
    presentation_id: Optional[str] = None
) -> Dict:
    """Add bullet points to a placeholder."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    try:
        # Check if placeholder exists
        if placeholder_idx not in [p.placeholder_format.idx for p in slide.placeholders]:
            return {
                "error": f"Placeholder with index {placeholder_idx} not found in slide {slide_index}"
            }
        
        # Get the placeholder
        placeholder = slide.placeholders[placeholder_idx]
        
        # Add bullet points
        ppt_utils.add_bullet_points(placeholder, bullet_points)
        
        return {
            "message": f"Added {len(bullet_points)} bullet points to placeholder {placeholder_idx} in slide {slide_index}"
        }
    except Exception as e:
        return {
            "error": f"Failed to add bullet points: {str(e)}"
        }

# ---- Text Tools ----

@app.tool()
def add_textbox(
    slide_index: int,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    font_size: Optional[int] = None,
    font_name: Optional[str] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[List[int]] = None,
    alignment: Optional[str] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add a textbox to a slide."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    try:
        # Add the textbox
        textbox = ppt_utils.add_textbox(slide, left, top, width, height, text)
        
        # Format the text if formatting options are provided
        if any([font_size, font_name, bold, italic, color, alignment]):
            ppt_utils.format_text(
                textbox.text_frame,
                font_size=font_size,
                font_name=font_name,
                bold=bold,
                italic=italic,
                color=tuple(color) if color else None,
                alignment=alignment
            )
        
        return {
            "message": f"Added textbox to slide {slide_index}",
            "shape_index": len(slide.shapes) - 1
        }
    except Exception as e:
        return {
            "error": f"Failed to add textbox: {str(e)}"
        }

# ---- Image Tools ----

@app.tool()
def add_image(
    slide_index: int,
    image_path: str,
    left: float,
    top: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add an image to a slide with graceful error recovery."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    # Check if image file exists
    if not os.path.exists(image_path):
        # Try to find the image by searching in common directories
        common_dirs = ['.', './images', './assets', './resources']
        image_name = os.path.basename(image_path)
        
        for directory in common_dirs:
            potential_path = os.path.join(directory, image_name)
            if os.path.exists(potential_path):
                image_path = potential_path
                break
        else:
            return {
                "error": f"Image file not found: {image_path}. Searched in {', '.join(common_dirs)}"
            }
    
    # Define multiple approaches to add the image
    def add_with_size():
        return ppt_utils.add_image(slide, image_path, left, top, width, height)
        
    def add_without_size():
        return ppt_utils.add_image(slide, image_path, left, top)
    
    def add_with_pil():
        from PIL import Image
        img = Image.open(image_path)
        img_width, img_height = img.size
        
        # Calculate aspect ratio and use it to determine missing dimension
        aspect_ratio = img_width / img_height
        
        if width is not None and height is None:
            h = width / aspect_ratio
            return ppt_utils.add_image(slide, image_path, left, top, width, h)
        elif height is not None and width is None:
            w = height * aspect_ratio
            return ppt_utils.add_image(slide, image_path, left, top, w, height)
        else:
            return ppt_utils.add_image(slide, image_path, left, top, width, height)
    
    approaches = [
        (add_with_size, "Adding image with specified dimensions"),
        (add_without_size, "Adding image with original dimensions"),
        (add_with_pil, "Adding image with calculated dimensions using PIL")
    ]
    
    picture, error = ppt_utils.try_multiple_approaches("add image", approaches)
    
    if error:
        return {
            "error": error
        }
    
    return {
        "message": f"Added image to slide {slide_index}",
        "shape_index": len(slide.shapes) - 1,
        "width": picture.width.inches,
        "height": picture.height.inches
    }

@app.tool()
def add_image_from_base64(
    slide_index: int,
    base64_string: str,
    left: float,
    top: float,
    width: Optional[float] = None,
    height: Optional[float] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add an image from a base64 encoded string to a slide."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    try:
        # Add the image
        picture = ppt_utils.add_image_from_base64(slide, base64_string, left, top, width, height)
        
        return {
            "message": f"Added image to slide {slide_index}",
            "shape_index": len(slide.shapes) - 1,
            "width": picture.width.inches,
            "height": picture.height.inches
        }
    except Exception as e:
        return {
            "error": f"Failed to add image: {str(e)}"
        }

# ---- Table Tools ----

@app.tool()
def add_table(
    slide_index: int,
    rows: int,
    cols: int,
    left: float,
    top: float,
    width: float,
    height: float,
    data: Optional[List[List[str]]] = None,
    presentation_id: Optional[str] = None,
    filename: Optional[str] = None  # Added to satisfy MCP framework validation
) -> Dict:
    """Add a table to a slide with comprehensive parameter validation."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Validate parameters
    valid, error = validate_parameters({
        "rows": (rows, [(is_positive, "must be a positive integer")]),
        "cols": (cols, [(is_positive, "must be a positive integer")]),
        "left": (left, [(is_non_negative, "must be non-negative")]),
        "top": (top, [(is_non_negative, "must be non-negative")]),
        "width": (width, [(is_positive, "must be positive")]),
        "height": (height, [(is_positive, "must be positive")]),
    })
    
    if not valid:
        return {"error": error}
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    # Validate data if provided
    if data is not None:
        if not isinstance(data, list):
            return {"error": "Data must be a list of rows"}
        
        for i, row in enumerate(data):
            if not isinstance(row, list):
                return {"error": f"Row {i} must be a list of cell values"}
    
    try:
        # Add the table
        table, error = ppt_utils.safe_operation(
            "add_table",
            lambda: ppt_utils.add_table(slide, rows, cols, left, top, width, height)
        )
        
        if error:
            return {"error": error}
        
        # Populate the table if data is provided
        warnings = []
        if data:
            for row_idx, row_data in enumerate(data):
                if row_idx >= rows:
                    warnings.append(f"Ignored excess data: table has only {rows} rows but data has {len(data)} rows")
                    break
                    
                for col_idx, cell_text in enumerate(row_data):
                    if col_idx >= cols:
                        warnings.append(f"Ignored excess data in row {row_idx}: table has only {cols} columns")
                        break
                        
                    _, cell_error = ppt_utils.safe_operation(
                        f"set_cell_text(row={row_idx}, col={col_idx})",
                        lambda: ppt_utils.set_cell_text(table, row_idx, col_idx, str(cell_text))
                    )
                    
                    if cell_error:
                        warnings.append(cell_error)
        
        result = {
            "message": f"Added {rows}x{cols} table to slide {slide_index}",
            "shape_index": len(slide.shapes) - 1
        }
        
        if warnings:
            result["warnings"] = warnings
            
        return result
    except Exception as e:
        return {
            "error": f"Failed to add table: {str(e)}"
        }

@app.tool()
def format_table_cell(
    slide_index: int,
    shape_index: int,
    row: int,
    col: int,
    font_size: Optional[int] = None,
    font_name: Optional[str] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[List[int]] = None,
    bg_color: Optional[List[int]] = None,
    alignment: Optional[str] = None,
    vertical_alignment: Optional[str] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Format a table cell with comprehensive error handling and parameter validation.
    
    This function applies formatting to a cell in a table on a slide. It provides options
    for text formatting (font size, name, style, color), cell background color, and
    text alignment.
    
    Args:
        slide_index: Index of the slide containing the table (0-based)
        shape_index: Index of the table shape on the slide (0-based)
        row: Row index of the cell to format (0-based)
        col: Column index of the cell to format (0-based)
        font_size: Font size in points
        font_name: Font name/family (e.g., 'Arial', 'Calibri')
        bold: Whether text should be bold (True/False)
        italic: Whether text should be italic (True/False)
        color: RGB color list for text [R, G, B] (0-255 for each value)
        bg_color: RGB color list for cell background [R, G, B] (0-255 for each value)
        alignment: Text alignment ('left', 'center', 'right', 'justify')
        vertical_alignment: Vertical text alignment ('top', 'middle', 'bottom')
        presentation_id: ID of the presentation to use (uses current presentation if not specified)
    
    Returns:
        Dict with keys:
            - message: Success message
            - error: Error message if operation failed
            - warning: Warning message if some formatting was applied but some failed
    
    Examples:
        To format a header cell with bold text and gray background:
            format_table_cell(0, 1, 0, 1, font_size=14, bold=True, bg_color=[200, 200, 200])
            
        To center text in a cell:
            format_table_cell(0, 1, 2, 3, alignment="center", vertical_alignment="middle")
    """
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    # Check if shape index is valid
    if shape_index < 0 or shape_index >= len(slide.shapes):
        return {
            "error": f"Invalid shape index: {shape_index}. Available shapes: 0-{len(slide.shapes) - 1}"
        }
    
    shape = slide.shapes[shape_index]
    
    # Validate parameters
    valid_alignments = ['left', 'center', 'right', 'justify']
    valid_vertical_alignments = ['top', 'middle', 'bottom']
    
    validations = {}
    
    if font_size is not None:
        validations["font_size"] = (font_size, [(is_positive, "must be a positive integer")])
    
    if alignment is not None:
        validations["alignment"] = (alignment.lower(), [(lambda x: x in valid_alignments, 
                                    f"must be one of {', '.join(valid_alignments)}")])
    
    if vertical_alignment is not None:
        validations["vertical_alignment"] = (vertical_alignment.lower(), 
                                           [(lambda x: x in valid_vertical_alignments, 
                                             f"must be one of {', '.join(valid_vertical_alignments)}")])
    
    if color is not None:
        validations["color"] = (color, [(is_valid_rgb, "must be a valid RGB list [R, G, B] with values 0-255")])
    
    if bg_color is not None:
        validations["bg_color"] = (bg_color, [(is_valid_rgb, "must be a valid RGB list [R, G, B] with values 0-255")])
    
    if validations:
        valid, error = validate_parameters(validations)
        if not valid:
            return {"error": error}
    
    try:
        # Check if shape is a table
        if not hasattr(shape, 'table'):
            # Try to recover if this is a graphic frame containing a table
            if hasattr(shape, 'graphic') and hasattr(shape.graphic, 'graphicData'):
                # This might be a table in a graphic frame
                warnings = ["Shape is not directly a table, attempting to extract table from graphic frame"]
                # Further recovery logic would be needed here
                return {
                    "error": "Shape at index {shape_index} is not a table",
                    "warning": "If this is a table, it might be in a graphic frame which requires different handling"
                }
            else:
                return {
                    "error": f"Shape at index {shape_index} is not a table"
                }
        
        table = shape.table
        
        # Check if row and column indices are valid
        if row < 0 or row >= len(table.rows):
            return {
                "error": f"Invalid row index: {row}. Available rows: 0-{len(table.rows) - 1}"
            }
            
        if col < 0 or col >= len(table.columns):
            return {
                "error": f"Invalid column index: {col}. Available columns: 0-{len(table.columns) - 1}"
            }
        
        # Get the cell
        cell = table.cell(row, col)
        
        # Format the cell with error handling
        warnings = []
        
        # Try multiple formatting operations and collect any warnings
        try:
            ppt_utils.format_table_cell(
                cell,
                font_size=font_size,
                font_name=font_name,
                bold=bold,
                italic=italic,
                color=tuple(color) if color else None,
                bg_color=tuple(bg_color) if bg_color else None,
                alignment=alignment,
                vertical_alignment=vertical_alignment
            )
        except Exception as e:
            # Try individual formatting operations to recover
            formatting_ops = [
                (lambda: ppt_utils.format_text(cell.text_frame, font_size=font_size, font_name=font_name, 
                                              bold=bold, italic=italic, 
                                              color=tuple(color) if color else None,
                                              alignment=alignment),
                 "text formatting"),
                
                (lambda: cell.fill.solid() if bg_color else None, "background preparation"),
                
                (lambda: setattr(cell.fill.fore_color, 'rgb', 
                                tuple(bg_color)) if bg_color else None, 
                 "background color"),
                
                (lambda: setattr(cell.text_frame, 'vertical_anchor', 
                                ppt_utils.vertical_alignment_map.get(vertical_alignment)) 
                 if vertical_alignment else None,
                 "vertical alignment")
            ]
            
            for op_func, op_name in formatting_ops:
                try:
                    op_func()
                except Exception as sub_e:
                    warnings.append(f"Failed to apply {op_name}: {str(sub_e)}")
        
        result = {
            "message": f"Formatted cell at row {row}, column {col} in table at shape index {shape_index} on slide {slide_index}"
        }
        
        if warnings:
            result["warnings"] = warnings
            
        return result
    except Exception as e:
        return {
            "error": f"Failed to format table cell: {str(e)}"
        }

# ---- Shape Tools ----

@app.tool()
def add_shape(
    slide_index: int,
    shape_type: str,
    left: float,
    top: float,
    width: float,
    height: float,
    fill_color: Optional[List[int]] = None,
    line_color: Optional[List[int]] = None,
    line_width: Optional[float] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add an auto shape to a slide.
    
    This function adds a shape to a slide in the presentation. It supports various shape types
    and allows customization of fill color, line color, and line width.
    
    Args:
        slide_index: Index of the slide to add the shape to (0-based)
        shape_type: Type of shape to add. Supported types include:
            - Basic shapes: 'rectangle', 'rounded_rectangle', 'oval', 'triangle', 'diamond'
            - Polygons: 'pentagon', 'hexagon', 'heptagon', 'octagon'
            - Stars and arrows: 'star', 'arrow'
            - Misc: 'cloud', 'heart', 'lightning_bolt', 'sun', 'moon', 'smiley_face', 'no_symbol'
            - Flowchart: 'flowchart_process', 'flowchart_decision', 'flowchart_data'
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        fill_color: RGB color list for shape fill [R, G, B] (0-255 for each value)
        line_color: RGB color list for shape outline [R, G, B] (0-255 for each value)
        line_width: Width of the shape outline in points
        presentation_id: ID of the presentation to use (uses current presentation if not specified)
    """
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    try:
        # Use the direct implementation that bypasses the enum issues
        shape = add_shape_direct(slide, shape_type, left, top, width, height)
        
        # Format the shape if formatting options are provided
        if any([fill_color, line_color, line_width]):
            ppt_utils.format_shape(
                shape,
                fill_color=tuple(fill_color) if fill_color else None,
                line_color=tuple(line_color) if line_color else None,
                line_width=line_width
            )
        
        return {
            "message": f"Added {shape_type} shape to slide {slide_index}",
            "shape_index": len(slide.shapes) - 1
        }
    except ValueError as e:
        # Specific handling for validation errors
        return {
            "error": str(e)
        }
    except Exception as e:
        return {
            "error": f"Failed to add shape '{shape_type}': {str(e)}"
        }

# ---- Chart Tools ----

@app.tool()
def add_chart(
    slide_index: int,
    chart_type: str,
    left: float,
    top: float,
    width: float,
    height: float,
    categories: List[str],
    series_names: List[str],
    series_values: List[List[float]],
    has_legend: bool = True,
    legend_position: str = "right",
    has_data_labels: bool = False,
    title: Optional[str] = None,
    presentation_id: Optional[str] = None
) -> Dict:
    """Add a chart to a slide with comprehensive error handling."""
    # Use the specified presentation or the current one
    pres_id = presentation_id if presentation_id is not None else current_presentation_id
    
    if pres_id is None or pres_id not in presentations:
        return {
            "error": "No presentation is currently loaded or the specified ID is invalid"
        }
    
    pres = presentations[pres_id]
    
    # Check if slide index is valid
    if slide_index < 0 or slide_index >= len(pres.slides):
        return {
            "error": f"Invalid slide index: {slide_index}. Available slides: 0-{len(pres.slides) - 1}"
        }
    
    slide = pres.slides[slide_index]
    
    # Validate chart type
    valid_chart_types = [
        'column', 'stacked_column', 'bar', 'stacked_bar', 'line', 
        'line_markers', 'pie', 'doughnut', 'area', 'stacked_area', 
        'scatter', 'radar', 'radar_markers'
    ]
    if chart_type.lower() not in valid_chart_types:
        return {
            "error": f"Invalid chart type: '{chart_type}'. Valid types are: {', '.join(valid_chart_types)}"
        }
    
    # Validate series data
    if len(series_names) != len(series_values):
        return {
            "error": f"Number of series names ({len(series_names)}) must match number of series values ({len(series_values)})"
        }
    
    # Validate categories list
    if not categories:
        return {
            "error": "Categories list cannot be empty"
        }
    
    # Validate that all series have the same number of values as categories
    for i, values in enumerate(series_values):
        if len(values) != len(categories):
            return {
                "error": f"Series '{series_names[i]}' has {len(values)} values but there are {len(categories)} categories"
            }
    
    try:
        # Add the chart
        chart, error = ppt_utils.safe_operation(
            "add_chart",
            lambda: ppt_utils.add_chart(
                slide, chart_type, left, top, width, height,
                categories, series_names, series_values
            )
        )
        
        if error:
            return {"error": error}
        
        # Format the chart
        _, error = ppt_utils.safe_operation(
            "format_chart",
            lambda: ppt_utils.format_chart(
                chart,
                has_legend=has_legend,
                legend_position=legend_position,
                has_data_labels=has_data_labels,
                title=title
            )
        )
        
        if error:
            return {
                "warning": f"Chart created but failed to format: {error}",
                "shape_index": len(slide.shapes) - 1
            }
        
        return {
            "message": f"Added {chart_type} chart to slide {slide_index}",
            "shape_index": len(slide.shapes) - 1
        }
    except Exception as e:
        return {
            "error": f"Failed to add chart: {str(e)}"
        }

# ---- Main Execution ----
def main(transport: str = "stdio", port: int = 8000):
    if transport == "http":
        import asyncio
        # Set the port for HTTP transport
        app.settings.port = port
        # Start the FastMCP server with HTTP transport
        try:
            app.run(transport='streamable-http')
        except asyncio.exceptions.CancelledError:
            print("Server stopped by user.")
        except KeyboardInterrupt:
            print("Server stopped by user.")
        except Exception as e:
            print(f"Error starting server: {e}")

    else:
        # Run the FastMCP server
        app.run(transport='stdio')

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Server for PowerPoint manipulation using python-pptx")

    parser.add_argument(
        "-t",
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "http"],
        help="Transport method for the MCP server (default: stdio)"
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to run the MCP server on (default: 8000)"
    )
    args = parser.parse_args()
    main(args.transport, args.port)