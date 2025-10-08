#!/usr/bin/env python3
"""
Fix Image Processing Issues in MCP Feedback Enhanced

This script applies the necessary fixes to the server.py file to resolve
the FastMCP Image import and usage issues.

Usage:
    python fix_image_processing.py

Fixes Applied:
1. Fix FastMCP Image import
2. Replace FastMCPImage with Image
3. Ensure proper data format handling
4. Add validation and error handling
"""

import os
import re
import shutil
from pathlib import Path


def backup_file(file_path: Path) -> Path:
    """Create a backup of the original file"""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path


def fix_imports(content: str) -> str:
    """Fix the FastMCP imports to include Image"""
    # Find the fastmcp import line and add Image
    import_pattern = r'from fastmcp import FastMCP'
    replacement = 'from fastmcp import FastMCP, Image'

    if 'from fastmcp import FastMCP, Image' in content:
        print("FastMCP Image import already correct")
        return content
    elif 'from fastmcp import FastMCP' in content:
        content = re.sub(import_pattern, replacement, content)
        print("Fixed FastMCP import to include Image")
    else:
        print("WARNING: FastMCP import not found - may need manual intervention")

    return content


def fix_fastmcp_image_usage(content: str) -> str:
    """Replace FastMCPImage with Image throughout the file"""
    # Replace FastMCPImage class references
    replacements = [
        (r'FastMCPImage', 'Image'),
        (r'list\[FastMCPImage \| str\]', 'list[Image | str]'),
        (r'isinstance\(.*?, FastMCPImage\)', lambda m: m.group(0).replace('FastMCPImage', 'Image')),
    ]

    changes_made = 0
    for pattern, replacement in replacements:
        if callable(replacement):
            # For complex replacements
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                changes_made += len(matches)
        else:
            # For simple string replacements
            old_content = content
            content = re.sub(pattern, replacement, content)
            if content != old_content:
                changes_made += content.count(replacement) - old_content.count(replacement)

    if changes_made > 0:
        print(f"Fixed {changes_made} FastMCPImage references")
    else:
        print("No FastMCPImage references found to fix")

    return content


def add_image_validation(content: str) -> str:
    """Add proper image validation and error handling"""
    # Look for the image creation section in interactive_feedback
    image_creation_pattern = r'(# 創建 FastMCP Image 對象\s*)(fastmcp_image = Image\(data=img_data, format=format_str\))'
    
    replacement = r'''\1try:
                        # Validate image data before creating Image object
                        if not isinstance(img_data, bytes):
                            debug_log(f"圖片 {i} 數據類型錯誤: {type(img_data)}")
                            continue
                        
                        if len(img_data) == 0:
                            debug_log(f"圖片 {i} 數據為空")
                            continue
                        
                        # Create FastMCP Image object with proper validation
                        \2
                        
                        # Validate the created image object
                        if not hasattr(fastmcp_image, 'data') or not hasattr(fastmcp_image, 'format'):
                            debug_log(f"圖片 {i} Image 對象創建不完整")
                            continue
                            
                    except Exception as img_creation_error:
                        debug_log(f"圖片 {i} Image 對象創建失敗: {img_creation_error}")
                        continue'''
    
    if re.search(image_creation_pattern, content):
        content = re.sub(image_creation_pattern, replacement, content, flags=re.MULTILINE)
        print("✅ Added image validation and error handling")
    else:
        print("⚠️ Image creation pattern not found - validation not added")
    
    return content


def fix_class_definition(content: str) -> str:
    """Remove or fix the FastMCPImage class definition if it exists"""
    # Look for FastMCPImage class definition
    class_pattern = r'class FastMCPImage:.*?(?=\n\n|\nclass|\ndef|\n@|\Z)'
    
    if re.search(class_pattern, content, re.DOTALL):
        content = re.sub(class_pattern, '', content, flags=re.DOTALL)
        print("✅ Removed FastMCPImage class definition")
    else:
        print("✅ No FastMCPImage class definition found")
    
    return content


def validate_fixes(content: str) -> bool:
    """Validate that all fixes have been applied correctly"""
    issues = []

    # Check for correct import
    if 'from fastmcp import FastMCP, Image' not in content:
        issues.append("FastMCP Image import not found")

    # Check for remaining FastMCPImage references
    if 'FastMCPImage' in content:
        issues.append("FastMCPImage references still exist")

    # Check for Image usage
    if 'Image(data=' not in content:
        issues.append("Image object creation not found")

    if issues:
        print("Validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("All fixes validated successfully")
        return True


def main():
    """Main function to apply fixes"""
    print("MCP Feedback Enhanced - Image Processing Fix Script")
    print("=" * 60)
    
    # Find the server.py file
    server_file = Path("src/mcp_feedback_enhanced/server.py")
    
    if not server_file.exists():
        print(f"ERROR: Server file not found: {server_file}")
        print("Please run this script from the project root directory")
        return False

    print(f"Found server file: {server_file}")

    # Create backup
    backup_path = backup_file(server_file)

    try:
        # Read the current content
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"Read {len(content)} characters from server.py")

        # Apply fixes
        print("\nApplying fixes...")
        content = fix_imports(content)
        content = fix_fastmcp_image_usage(content)
        content = fix_class_definition(content)
        content = add_image_validation(content)

        # Validate fixes
        print("\nValidating fixes...")
        if not validate_fixes(content):
            print("ERROR: Validation failed - restoring backup")
            shutil.copy2(backup_path, server_file)
            return False

        # Write the fixed content
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nSUCCESS: Applied fixes to {server_file}")
        print(f"Backup saved as: {backup_path}")

        # Show summary
        print("\nSummary of fixes applied:")
        print("   - Fixed FastMCP import to include Image")
        print("   - Replaced FastMCPImage with Image")
        print("   - Added image validation and error handling")
        print("   - Removed any FastMCPImage class definitions")

        print("\nNext steps:")
        print("   1. Run the test script: python test_image_processing.py")
        print("   2. Test image upload functionality")
        print("   3. Verify fixes work with the main server")
        
        return True

    except Exception as e:
        print(f"ERROR: Error applying fixes: {e}")
        print("Restoring backup...")
        shutil.copy2(backup_path, server_file)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
