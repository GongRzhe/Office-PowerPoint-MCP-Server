"""
Core utility functions for PowerPoint MCP Server.
Basic operations and error handling.
"""
from typing import Any, Callable, List, Tuple, Optional
import os
import pathlib


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


def sanitize_path(file_path: str, base_dir: Optional[str] = None, allow_absolute: bool = False) -> str:
    """
    Sanitize a file path to prevent path traversal attacks.
    
    This function resolves the absolute path and ensures it's within a safe directory.
    By default, it restricts paths to the current working directory or a specified base directory.
    
    Args:
        file_path: The file path to sanitize
        base_dir: The base directory to restrict paths to (defaults to current working directory)
        allow_absolute: If True, allows absolute paths outside base_dir (use with caution)
        
    Returns:
        The sanitized absolute path
        
    Raises:
        ValueError: If the path attempts to traverse outside the allowed directory
    """
    # Get the base directory (default to current working directory)
    if base_dir is None:
        base_dir = os.getcwd()
    
    # Resolve to absolute path
    base_path = pathlib.Path(base_dir).resolve()
    
    # Handle the file path
    file_path_obj = pathlib.Path(file_path)
    
    # If absolute paths are allowed and this is an absolute path, return it as-is
    if allow_absolute and file_path_obj.is_absolute():
        return str(file_path_obj.resolve())
    
    # Resolve the file path relative to base directory
    if file_path_obj.is_absolute():
        # If absolute path but not allowed, treat as relative by taking just the name
        resolved_path = (base_path / file_path_obj.name).resolve()
    else:
        resolved_path = (base_path / file_path_obj).resolve()
    
    # Check if the resolved path is within the base directory
    try:
        resolved_path.relative_to(base_path)
    except ValueError:
        raise ValueError(
            f"Path traversal detected: '{file_path}' resolves to '{resolved_path}' "
            f"which is outside the allowed directory '{base_path}'"
        )
    
    return str(resolved_path)
