#!/usr/bin/env python
"""
Security test script to verify path traversal protection.
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.core_utils import sanitize_path

def test_path_sanitization():
    """Test the path sanitization function."""
    print("Testing path sanitization...")
    print("-" * 60)
    
    # Test 1: Normal relative path (should pass)
    try:
        result = sanitize_path("test.pptx")
        print(f"✓ Test 1 PASSED: Normal relative path")
        print(f"  Input: 'test.pptx'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✗ Test 1 FAILED: {e}")
    
    print()
    
    # Test 2: Path traversal attempt (should fail)
    try:
        result = sanitize_path("../../../../etc/passwd")
        print(f"✗ Test 2 FAILED: Path traversal was not blocked!")
        print(f"  Input: '../../../../etc/passwd'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✓ Test 2 PASSED: Path traversal blocked")
        print(f"  Input: '../../../../etc/passwd'")
        print(f"  Error: {e}")
    
    print()
    
    # Test 3: Subdirectory path (should pass)
    try:
        result = sanitize_path("templates/test.pptx")
        print(f"✓ Test 3 PASSED: Subdirectory path")
        print(f"  Input: 'templates/test.pptx'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✗ Test 3 FAILED: {e}")
    
    print()
    
    # Test 4: Absolute path with allow_absolute=True (should pass)
    try:
        result = sanitize_path("/tmp/test.pptx", allow_absolute=True)
        print(f"✓ Test 4 PASSED: Absolute path with allow_absolute=True")
        print(f"  Input: '/tmp/test.pptx'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✗ Test 4 FAILED: {e}")
    
    print()
    
    # Test 5: Absolute path without allow_absolute (should be converted to relative)
    try:
        result = sanitize_path("/tmp/test.pptx", allow_absolute=False)
        print(f"✓ Test 5 PASSED: Absolute path converted to relative")
        print(f"  Input: '/tmp/test.pptx'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✗ Test 5 FAILED: {e}")
    
    print()
    
    # Test 6: Path with .. in the middle (should fail if it escapes)
    try:
        result = sanitize_path("templates/../../../etc/passwd")
        print(f"✗ Test 6 FAILED: Path traversal with .. was not blocked!")
        print(f"  Input: 'templates/../../../etc/passwd'")
        print(f"  Output: {result}")
    except ValueError as e:
        print(f"✓ Test 6 PASSED: Path traversal with .. blocked")
        print(f"  Input: 'templates/../../../etc/passwd'")
        print(f"  Error: {e}")
    
    print()
    print("-" * 60)
    print("Security tests completed!")

if __name__ == "__main__":
    test_path_sanitization()
