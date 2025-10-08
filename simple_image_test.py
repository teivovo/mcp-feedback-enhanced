#!/usr/bin/env python3
"""
Simple test for MCP image processing
"""

import sys
import base64
import traceback
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_fastmcp_import():
    """Test FastMCP Image import"""
    print("Testing FastMCP Image import...")
    try:
        from fastmcp.utilities.types import Image as MCPImage
        print(f"[PASS] FastMCP Image imported: {MCPImage}")
        return MCPImage
    except Exception as e:
        print(f"[FAIL] FastMCP Image import failed: {e}")
        return None

def test_image_loading():
    """Test loading the test image"""
    print("Testing image loading...")
    try:
        with open("tests/image/test_image.png", "rb") as f:
            image_bytes = f.read()
        print(f"[PASS] Image loaded: {len(image_bytes)} bytes")
        return image_bytes
    except Exception as e:
        print(f"[FAIL] Image loading failed: {e}")
        return None

def test_mcp_image_creation(MCPImage, image_bytes):
    """Test creating MCPImage"""
    print("Testing MCPImage creation...")
    try:
        if not MCPImage or not image_bytes:
            print("[SKIP] Prerequisites failed")
            return None
        
        mcp_image = MCPImage(data=image_bytes, format="png")
        print(f"[PASS] MCPImage created: {type(mcp_image)}")
        return mcp_image
    except Exception as e:
        print(f"[FAIL] MCPImage creation failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return None

def test_process_images_function(image_bytes):
    """Test the actual process_images function"""
    print("Testing process_images function...")
    try:
        if not image_bytes:
            print("[SKIP] No image data")
            return None
        
        from mcp_feedback_enhanced.server import process_images
        
        # Simulate processed image data from web UI
        processed_images = [{
            "name": "test_image.png",
            "data": image_bytes,
            "type": "image/png",
            "size": len(image_bytes)
        }]
        
        result = process_images(processed_images)
        print(f"[PASS] process_images returned: {len(result)} images")
        print(f"Result types: {[type(img).__name__ for img in result]}")
        return result
    except Exception as e:
        print(f"[FAIL] process_images failed: {e}")
        print(f"Error details: {traceback.format_exc()}")
        return None

def main():
    print("Simple MCP Image Processing Test")
    print("=" * 40)
    
    # Test 1: Import
    MCPImage = test_fastmcp_import()
    
    # Test 2: Load image
    image_bytes = test_image_loading()
    
    # Test 3: Create MCPImage
    mcp_image = test_mcp_image_creation(MCPImage, image_bytes)
    
    # Test 4: Test process_images function
    process_result = test_process_images_function(image_bytes)
    
    # Summary
    print("\nTest Summary:")
    print(f"FastMCP Import: {'PASS' if MCPImage else 'FAIL'}")
    print(f"Image Loading: {'PASS' if image_bytes else 'FAIL'}")
    print(f"MCPImage Creation: {'PASS' if mcp_image else 'FAIL'}")
    print(f"process_images: {'PASS' if process_result else 'FAIL'}")

if __name__ == "__main__":
    main()
