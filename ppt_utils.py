"""
Utility functions for PowerPoint manipulation using python-pptx.

This module provides a comprehensive set of functions to create and manipulate
PowerPoint presentations programmatically. It wraps the python-pptx library
with higher-level functions that simplify common operations.

Key features:
- Create, open, and save presentations
- Add and format slides with various layouts
- Manipulate text, including titles, placeholders, and textboxes
- Add and format shapes, images, tables, and charts
- Set document properties

Usage examples:
    # Create a new presentation
    pres = create_presentation()
    
    # Add a title slide
    slide, layout = add_slide(pres, 0)
    set_title(slide, "Presentation Title")
    
    # Add a content slide with bullet points
    slide, layout = add_slide(pres, 1)
    set_title(slide, "Key Points")
    placeholder = slide.placeholders[1]  # Content placeholder
    add_bullet_points(placeholder, ["Point 1", "Point 2", "Point 3"])
    
    # Save the presentation
    save_presentation(pres, "my_presentation.pptx")
"""
import base64
import io
from typing import Any

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


def try_multiple_approaches(operation_name, approaches):
    """
    Try multiple approaches to perform an operation, returning the first successful result.
    
    Args:
        operation_name: Name of the operation for error reporting
        approaches: List of (approach_func, description) tuples to try
        
    Returns:
        Tuple of (result, None) if any approach succeeded, or (None, error_messages) if all failed
    """
    error_messages = []

    for approach_func, description in approaches:
        try:
            result = approach_func()
            return result, None
        except Exception as e:
            error_messages.append(f"{description}: {str(e)}")

    return None, f"Failed to {operation_name} after trying multiple approaches: {'; '.join(error_messages)}"

def safe_operation(operation_name, operation_func, error_message=None, *args, **kwargs):
    """
    Execute an operation safely with standard error handling.
    
    Args:
        operation_name: Name of the operation for error reporting
        operation_func: Function to execute
        error_message: Custom error message (optional)
        *args, **kwargs: Arguments to pass to the operation function
        
    Returns:
        A tuple (result, error) where error is None if operation was successful
    """
    try:
        result = operation_func(*args, **kwargs)
        return result, None
    except ValueError as e:
        error_msg = error_message or f"Invalid input for {operation_name}: {str(e)}"
        return None, error_msg
    except TypeError as e:
        error_msg = error_message or f"Type error in {operation_name}: {str(e)}"
        return None, error_msg
    except Exception as e:
        error_msg = error_message or f"Failed to execute {operation_name}: {str(e)}"
        return None, error_msg

# ---- Presentation Functions ----

def open_presentation(file_path: str) -> Presentation:
    """
    Open an existing PowerPoint presentation.
    
    Args:
        file_path: Path to the PowerPoint file
        
    Returns:
        A Presentation object
    """
    return Presentation(file_path)

def create_presentation() -> Presentation:
    """
    Create a new PowerPoint presentation.
    
    Returns:
        A new Presentation object
    """
    return Presentation()

def save_presentation(presentation: Presentation, file_path: str) -> str:
    """
    Save a PowerPoint presentation to a file.
    
    Args:
        presentation: The Presentation object
        file_path: Path where the file should be saved
        
    Returns:
        The file path where the presentation was saved
    """
    presentation.save(file_path)
    return file_path

def presentation_to_base64(presentation: Presentation) -> str:
    """
    Convert a presentation to a base64 encoded string.
    
    Args:
        presentation: The Presentation object
        
    Returns:
        Base64 encoded string of the presentation
    """
    ppt_bytes = io.BytesIO()
    presentation.save(ppt_bytes)
    ppt_bytes.seek(0)
    return base64.b64encode(ppt_bytes.read()).decode('utf-8')

def base64_to_presentation(base64_string: str) -> Presentation:
    """
    Create a presentation from a base64 encoded string.
    
    Args:
        base64_string: Base64 encoded string of a presentation
        
    Returns:
        A Presentation object
    """
    ppt_bytes = io.BytesIO(base64.b64decode(base64_string))
    return Presentation(ppt_bytes)

# ---- Slide Functions ----

def add_slide(presentation: Presentation, layout_index: int = 1) -> tuple:
    """
    Add a slide to the presentation.
    
    Args:
        presentation: The Presentation object
        layout_index: Index of the slide layout to use (default is 1, typically a title and content slide)
        
    Returns:
        A tuple containing the slide and its layout
    """
    layout = presentation.slide_layouts[layout_index]
    slide = presentation.slides.add_slide(layout)
    return slide, layout

def get_slide_layouts(presentation: Presentation) -> list[dict]:
    """
    Get all available slide layouts in the presentation.
    
    Args:
        presentation: The Presentation object
        
    Returns:
        A list of dictionaries with layout information
    """
    layouts = []
    for i, layout in enumerate(presentation.slide_layouts):
        layout_info = {
            "index": i,
            "name": layout.name,
            "placeholder_count": len(layout.placeholders)
        }
        layouts.append(layout_info)
    return layouts

# ---- Placeholder Functions ----

def get_placeholders(slide) -> list[dict]:
    """
    Get all placeholders in a slide.
    
    Args:
        slide: The slide object
        
    Returns:
        A list of dictionaries with placeholder information
    """
    placeholders = []
    for placeholder in slide.placeholders:
        placeholder_info = {
            "idx": placeholder.placeholder_format.idx,
            "type": placeholder.placeholder_format.type,
            "name": placeholder.name,
            "shape_type": placeholder.shape_type
        }
        placeholders.append(placeholder_info)
    return placeholders

def set_title(slide, title: str) -> None:
    """
    Set the title of a slide.
    
    Args:
        slide: The slide object
        title: The title text
    """
    if slide.shapes.title:
        slide.shapes.title.text = title

def populate_placeholder(slide, placeholder_idx: int, text: str) -> None:
    """
    Populate a placeholder with text.
    
    Args:
        slide: The slide object
        placeholder_idx: The index of the placeholder
        text: The text to add
    """
    placeholder = slide.placeholders[placeholder_idx]
    placeholder.text = text

def add_bullet_points(placeholder, bullet_points: list[str]) -> None:
    """
    Add bullet points to a placeholder.
    
    Args:
        placeholder: The placeholder object
        bullet_points: List of bullet point texts
    """
    text_frame = placeholder.text_frame
    text_frame.clear()

    for i, point in enumerate(bullet_points):
        p = text_frame.add_paragraph()
        p.text = point
        p.level = 0

        # Only add line breaks between bullet points, not after the last one
        if i < len(bullet_points) - 1:
            p.line_spacing = 1.0

# ---- Text Functions ----

def add_textbox(slide, left: float, top: float, width: float, height: float, text: str) -> Any:
    """
    Add a textbox to a slide.
    
    Args:
        slide: The slide object
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        text: Text content
        
    Returns:
        The created textbox shape
    """
    textbox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    textbox.text_frame.text = text
    return textbox

def format_text(text_frame, font_size: int = None, font_name: str = None,
                bold: bool = None, italic: bool = None, color: tuple[int, int, int] = None,
                alignment: str = None) -> None:
    """
    Format text in a text frame.
    
    Args:
        text_frame: The text frame to format
        font_size: Font size in points
        font_name: Font name
        bold: Whether text should be bold
        italic: Whether text should be italic
        color: RGB color tuple (r, g, b)
        alignment: Text alignment ('left', 'center', 'right', 'justify')
    """
    alignment_map = {
        'left': PP_ALIGN.LEFT,
        'center': PP_ALIGN.CENTER,
        'right': PP_ALIGN.RIGHT,
        'justify': PP_ALIGN.JUSTIFY
    }

    for paragraph in text_frame.paragraphs:
        if alignment and alignment in alignment_map:
            paragraph.alignment = alignment_map[alignment]

        for run in paragraph.runs:
            font = run.font

            if font_size is not None:
                font.size = Pt(font_size)

            if font_name is not None:
                font.name = font_name

            if bold is not None:
                font.bold = bold

            if italic is not None:
                font.italic = italic

            if color is not None:
                r, g, b = color
                font.color.rgb = RGBColor(r, g, b)

# ---- Image Functions ----

def add_image(slide, image_path: str, left: float, top: float, width: float = None, height: float = None) -> Any:
    """
    Add an image to a slide.
    
    Args:
        slide: The slide object
        image_path: Path to the image file
        left: Left position in inches
        top: Top position in inches
        width: Width in inches (optional)
        height: Height in inches (optional)
        
    Returns:
        The created picture shape
    """
    if width and height:
        picture = slide.shapes.add_picture(
            image_path, Inches(left), Inches(top), Inches(width), Inches(height)
        )
    else:
        picture = slide.shapes.add_picture(
            image_path, Inches(left), Inches(top)
        )
    return picture

def add_image_from_base64(slide, base64_string: str, left: float, top: float,
                          width: float = None, height: float = None) -> Any:
    """
    Add an image from a base64 encoded string to a slide.
    
    Args:
        slide: The slide object
        base64_string: Base64 encoded image string
        left: Left position in inches
        top: Top position in inches
        width: Width in inches (optional)
        height: Height in inches (optional)
        
    Returns:
        The created picture shape
    """
    image_data = base64.b64decode(base64_string)
    image_stream = io.BytesIO(image_data)

    if width and height:
        picture = slide.shapes.add_picture(
            image_stream, Inches(left), Inches(top), Inches(width), Inches(height)
        )
    else:
        picture = slide.shapes.add_picture(
            image_stream, Inches(left), Inches(top)
        )
    return picture

# ---- Table Functions ----

def add_table(slide, rows: int, cols: int, left: float, top: float, width: float, height: float) -> Any:
    """
    Add a table to a slide.
    
    Args:
        slide: The slide object
        rows: Number of rows
        cols: Number of columns
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        
    Returns:
        The created table shape
    """
    table = slide.shapes.add_table(
        rows, cols, Inches(left), Inches(top), Inches(width), Inches(height)
    ).table
    return table

def set_cell_text(table, row: int, col: int, text: str) -> None:
    """
    Set text in a table cell.
    
    Args:
        table: The table object
        row: Row index
        col: Column index
        text: Text content
    """
    cell = table.cell(row, col)
    cell.text = text

def format_table_cell(cell, font_size: int = None, font_name: str = None,
                     bold: bool = None, italic: bool = None,
                     color: tuple[int, int, int] = None,
                     bg_color: tuple[int, int, int] = None,
                     alignment: str = None,
                     vertical_alignment: str = None) -> None:
    """
    Format a table cell.
    
    Args:
        cell: The table cell to format
        font_size: Font size in points
        font_name: Font name
        bold: Whether text should be bold
        italic: Whether text should be italic
        color: RGB color tuple for text (r, g, b)
        bg_color: RGB color tuple for background (r, g, b)
        alignment: Text alignment ('left', 'center', 'right', 'justify')
        vertical_alignment: Vertical alignment ('top', 'middle', 'bottom')
    """
    alignment_map = {
        'left': PP_ALIGN.LEFT,
        'center': PP_ALIGN.CENTER,
        'right': PP_ALIGN.RIGHT,
        'justify': PP_ALIGN.JUSTIFY
    }

    vertical_alignment_map = {
        'top': MSO_VERTICAL_ANCHOR.TOP,
        'middle': MSO_VERTICAL_ANCHOR.MIDDLE,
        'bottom': MSO_VERTICAL_ANCHOR.BOTTOM
    }

    # Format text
    text_frame = cell.text_frame

    if vertical_alignment and vertical_alignment in vertical_alignment_map:
        text_frame.vertical_anchor = vertical_alignment_map[vertical_alignment]

    for paragraph in text_frame.paragraphs:
        if alignment and alignment in alignment_map:
            paragraph.alignment = alignment_map[alignment]

        for run in paragraph.runs:
            font = run.font

            if font_size is not None:
                font.size = Pt(font_size)

            if font_name is not None:
                font.name = font_name

            if bold is not None:
                font.bold = bold

            if italic is not None:
                font.italic = italic

            if color is not None:
                r, g, b = color
                font.color.rgb = RGBColor(r, g, b)

    # Set background color
    if bg_color is not None:
        r, g, b = bg_color
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(r, g, b)

# ---- Shape Functions ----

def add_shape(slide, shape_type: str, left: float, top: float, width: float, height: float) -> Any:
    """
    Add an auto shape to a slide.
    
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
    # Ensure shape_type is a string
    shape_type_str = str(shape_type)
    shape_type_lower = shape_type_str.lower()

    # Define shape type mapping with correct enum values
    shape_type_map = {
        'rectangle': MSO_SHAPE.RECTANGLE,
        'rounded_rectangle': MSO_SHAPE.ROUNDED_RECTANGLE,
        'oval': MSO_SHAPE.OVAL,
        'diamond': MSO_SHAPE.DIAMOND,
        'triangle': MSO_SHAPE.ISOSCELES_TRIANGLE,  # Changed from TRIANGLE to ISOSCELES_TRIANGLE
        'isosceles_triangle': MSO_SHAPE.ISOSCELES_TRIANGLE,
        'right_triangle': MSO_SHAPE.RIGHT_TRIANGLE,
        'pentagon': MSO_SHAPE.PENTAGON,
        'hexagon': MSO_SHAPE.HEXAGON,
        'heptagon': MSO_SHAPE.HEPTAGON,
        'octagon': MSO_SHAPE.OCTAGON,
        'star': MSO_SHAPE.STAR_5_POINTS,
        'arrow': MSO_SHAPE.ARROW,
        'cloud': MSO_SHAPE.CLOUD,
        'heart': MSO_SHAPE.HEART,
        'lightning_bolt': MSO_SHAPE.LIGHTNING_BOLT,
        'sun': MSO_SHAPE.SUN,
        'moon': MSO_SHAPE.MOON,
        'smiley_face': MSO_SHAPE.SMILEY_FACE,
        'no_symbol': MSO_SHAPE.NO_SYMBOL,
        'flowchart_process': MSO_SHAPE.FLOWCHART_PROCESS,
        'flowchart_decision': MSO_SHAPE.FLOWCHART_DECISION,
        'flowchart_data': MSO_SHAPE.FLOWCHART_DATA,
        'flowchart_document': MSO_SHAPE.FLOWCHART_DOCUMENT,
        'flowchart_predefined_process': MSO_SHAPE.FLOWCHART_PREDEFINED_PROCESS,
        'flowchart_internal_storage': MSO_SHAPE.FLOWCHART_INTERNAL_STORAGE,
        'flowchart_connector': MSO_SHAPE.FLOWCHART_CONNECTOR
    }

    # Check if shape type is valid before trying to use it
    if shape_type_lower not in shape_type_map:
        available_shapes = ', '.join(sorted(shape_type_map.keys()))
        raise ValueError(f"Unsupported shape type: '{shape_type}'. Available shape types: {available_shapes}")

    # Get the shape enum value
    shape_enum = shape_type_map[shape_type_lower]

    # Create the shape with better error handling
    try:
        shape = slide.shapes.add_shape(
            shape_enum, Inches(left), Inches(top), Inches(width), Inches(height)
        )
        return shape
    except Exception as e:
        # More detailed error for debugging
        raise ValueError(f"Could not create shape '{shape_type}' (enum: {shape_enum.__class__.__name__}.{shape_enum.name}): {str(e)}")

def format_shape(shape, fill_color: tuple[int, int, int] = None,
                line_color: tuple[int, int, int] = None, line_width: float = None) -> None:
    """
    Format a shape.
    
    Args:
        shape: The shape object
        fill_color: RGB color tuple for fill (r, g, b)
        line_color: RGB color tuple for outline (r, g, b)
        line_width: Line width in points
    """
    if fill_color is not None:
        r, g, b = fill_color
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor(r, g, b)

    if line_color is not None:
        r, g, b = line_color
        shape.line.color.rgb = RGBColor(r, g, b)

    if line_width is not None:
        shape.line.width = Pt(line_width)

# ---- Chart Functions ----

def add_chart(slide, chart_type: str, left: float, top: float, width: float, height: float,
             categories: list[str], series_names: list[str], series_values: list[list[float]]) -> Any:
    """
    Add a chart to a slide.
    
    Args:
        slide: The slide object
        chart_type: Type of chart ('column', 'bar', 'line', 'pie')
        left: Left position in inches
        top: Top position in inches
        width: Width in inches
        height: Height in inches
        categories: List of category names
        series_names: List of series names
        series_values: List of lists containing values for each series
        
    Returns:
        The created chart
    """
    chart_type_map = {
        'column': XL_CHART_TYPE.COLUMN_CLUSTERED,
        'stacked_column': XL_CHART_TYPE.COLUMN_STACKED,
        'bar': XL_CHART_TYPE.BAR_CLUSTERED,
        'stacked_bar': XL_CHART_TYPE.BAR_STACKED,
        'line': XL_CHART_TYPE.LINE,
        'line_markers': XL_CHART_TYPE.LINE_MARKERS,
        'pie': XL_CHART_TYPE.PIE,
        'doughnut': XL_CHART_TYPE.DOUGHNUT,
        'area': XL_CHART_TYPE.AREA,
        'stacked_area': XL_CHART_TYPE.AREA_STACKED,
        'scatter': XL_CHART_TYPE.XY_SCATTER,
        'radar': XL_CHART_TYPE.RADAR,
        'radar_markers': XL_CHART_TYPE.RADAR_MARKERS
    }

    chart_type_enum = chart_type_map.get(chart_type.lower(), XL_CHART_TYPE.COLUMN_CLUSTERED)

    # Create chart data
    chart_data = CategoryChartData()
    chart_data.categories = categories

    for i, series_name in enumerate(series_names):
        chart_data.add_series(series_name, series_values[i])

    # Add chart to slide
    graphic_frame = slide.shapes.add_chart(
        chart_type_enum, Inches(left), Inches(top), Inches(width), Inches(height), chart_data
    )

    return graphic_frame.chart

def format_chart(chart, has_legend: bool = True, legend_position: str = 'right',
                has_data_labels: bool = False, title: str = None) -> None:
    """
    Format a chart.
    
    Args:
        chart: The chart object
        has_legend: Whether to show the legend
        legend_position: Position of the legend ('right', 'left', 'top', 'bottom')
        has_data_labels: Whether to show data labels
        title: Chart title
    """
    # Set chart title
    if title:
        chart.has_title = True
        chart.chart_title.text_frame.text = title
    else:
        chart.has_title = False

    # Configure legend
    chart.has_legend = has_legend
    if has_legend:
        position_map = {
            'right': 2,  # XL_LEGEND_POSITION.RIGHT
            'left': 3,   # XL_LEGEND_POSITION.LEFT
            'top': 1,    # XL_LEGEND_POSITION.TOP
            'bottom': 4  # XL_LEGEND_POSITION.BOTTOM
        }
        chart.legend.position = position_map.get(legend_position.lower(), 2)

    # Configure data labels
    for series in chart.series:
        series.has_data_labels = has_data_labels

# ---- Document Properties Functions ----

def set_core_properties(presentation: Presentation, title: str = None, subject: str = None,
                       author: str = None, keywords: str = None, comments: str = None) -> None:
    """
    Set core document properties.
    
    Args:
        presentation: The Presentation object
        title: Document title
        subject: Document subject
        author: Document author
        keywords: Document keywords
        comments: Document comments
    """
    core_props = presentation.core_properties

    if title is not None:
        core_props.title = title

    if subject is not None:
        core_props.subject = subject

    if author is not None:
        core_props.author = author

    if keywords is not None:
        core_props.keywords = keywords

    if comments is not None:
        core_props.comments = comments

def get_core_properties(presentation: Presentation) -> dict:
    """
    Get core document properties.
    
    Args:
        presentation: The Presentation object
        
    Returns:
        Dictionary of core properties
    """
    core_props = presentation.core_properties

    return {
        'title': core_props.title,
        'subject': core_props.subject,
        'author': core_props.author,
        'keywords': core_props.keywords,
        'comments': core_props.comments,
        'category': core_props.category,
        'created': core_props.created,
        'modified': core_props.modified,
        'last_modified_by': core_props.last_modified_by
    }
