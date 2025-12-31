"""
Core utility functions for PowerPoint MCP Server.
Basic operations and error handling.
"""
from typing import Any, Callable, List, Tuple, Optional
import codecs


def ensure_unicode_text(text: str) -> str:
    """
    Ensure text is properly decoded as unicode.

    This handles cases where unicode escape sequences (like \\u00fc for ü)
    are passed as literal strings instead of actual unicode characters.
    This can happen when JSON is serialized with ensure_ascii=True or
    when text passes through systems that escape unicode.

    Args:
        text: The input text that may contain escaped unicode sequences

    Returns:
        Text with proper unicode characters
    """
    if not isinstance(text, str):
        return text

    # Check if text contains unicode escape sequences like \u00fc
    # These would appear as literal backslash-u in the string
    if '\\u' in text:
        try:
            # Decode unicode escape sequences
            text = codecs.decode(text, 'unicode_escape')
        except (UnicodeDecodeError, ValueError):
            # If decoding fails, return original text
            pass

    return text


def try_multiple_approaches(operation_name: str, approaches: List[Tuple[Callable, str]]) -> Tuple[Any, Optional[str]]:
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


def safe_operation(operation_name: str, operation_func: Callable, error_message: Optional[str] = None, *args, **kwargs) -> Tuple[Any, Optional[str]]:
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