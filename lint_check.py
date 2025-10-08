#!/usr/bin/env python3
"""
Comprehensive Code Linting and MCP Compatibility Check
======================================================

This script performs manual linting and checks MCP compatibility.
"""

import sys
import os
import ast
import importlib.util
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_syntax_errors(file_path):
    """Check for Python syntax errors"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_imports(file_path):
    """Check if all imports can be resolved"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        importlib.import_module(alias.name)
                    except ImportError:
                        # Check if it's a local import
                        if not alias.name.startswith('mcp_feedback_enhanced'):
                            issues.append(f"Cannot import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        importlib.import_module(node.module)
                    except ImportError:
                        if not node.module.startswith('mcp_feedback_enhanced'):
                            issues.append(f"Cannot import from: {node.module}")
    
    except Exception as e:
        issues.append(f"Error checking imports: {e}")
    
    return issues

def check_bridge_references(file_path):
    """Check for remaining bridge references"""
    bridge_terms = [
        'get_bridge', 'initialize_bridge', 'create_telegram_session', 
        'end_telegram_session', 'mcp_telegram_bridge', 'BridgeStatus',
        'MessageType', 'BridgeMessage', 'TelegramSession'
    ]
    
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for term in bridge_terms:
            if term in content:
                issues.append(f"Found bridge reference: {term}")
    
    except Exception as e:
        issues.append(f"Error checking bridge references: {e}")
    
    return issues

def lint_python_files():
    """Lint all Python files in the project"""
    print("🔍 Performing Manual Code Linting")
    print("=" * 50)
    
    src_path = Path("src/mcp_feedback_enhanced")
    python_files = list(src_path.rglob("*.py"))
    
    total_files = len(python_files)
    syntax_errors = 0
    import_issues = 0
    bridge_issues = 0
    
    for file_path in python_files:
        print(f"\n📄 Checking: {file_path}")
        
        # Check syntax
        syntax_ok, syntax_error = check_syntax_errors(file_path)
        if not syntax_ok:
            print(f"  ❌ Syntax: {syntax_error}")
            syntax_errors += 1
        else:
            print("  ✅ Syntax: OK")
        
        # Check imports
        import_issues_list = check_imports(file_path)
        if import_issues_list:
            print(f"  ⚠️  Imports: {len(import_issues_list)} issues")
            for issue in import_issues_list[:3]:  # Show first 3
                print(f"    - {issue}")
            import_issues += len(import_issues_list)
        else:
            print("  ✅ Imports: OK")
        
        # Check bridge references
        bridge_issues_list = check_bridge_references(file_path)
        if bridge_issues_list:
            print(f"  ❌ Bridge refs: {len(bridge_issues_list)} found")
            for issue in bridge_issues_list:
                print(f"    - {issue}")
            bridge_issues += len(bridge_issues_list)
        else:
            print("  ✅ Bridge refs: Clean")
    
    print("\n" + "=" * 50)
    print("📊 Linting Summary:")
    print(f"  Files checked: {total_files}")
    print(f"  Syntax errors: {syntax_errors}")
    print(f"  Import issues: {import_issues}")
    print(f"  Bridge references: {bridge_issues}")
    
    return syntax_errors == 0 and bridge_issues == 0

def test_mcp_imports():
    """Test core MCP imports"""
    print("\n🧪 Testing MCP Core Imports")
    print("=" * 50)
    
    imports_to_test = [
        ('mcp_feedback_enhanced.server', 'main'),
        ('mcp_feedback_enhanced.utils.telegram_manager', 'send_telegram_notification'),
        ('mcp_feedback_enhanced.web.routes.telegram_routes', 'setup_telegram_routes'),
        ('mcp_feedback_enhanced.utils.config_manager', 'get_config_manager'),
    ]
    
    success_count = 0
    
    for module_name, function_name in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                print(f"  ✅ {module_name}.{function_name}")
                success_count += 1
            else:
                print(f"  ❌ {module_name}.{function_name} - function not found")
        except ImportError as e:
            print(f"  ❌ {module_name} - import failed: {e}")
        except Exception as e:
            print(f"  ❌ {module_name} - error: {e}")
    
    print(f"\n📊 Import Test Results: {success_count}/{len(imports_to_test)} successful")
    return success_count == len(imports_to_test)

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Code Linting")
    
    lint_success = lint_python_files()
    import_success = test_mcp_imports()
    
    overall_success = lint_success and import_success
    
    print("\n" + "=" * 60)
    print("🏁 Final Results:")
    print(f"  Code Linting: {'✅ PASS' if lint_success else '❌ FAIL'}")
    print(f"  Import Tests: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"  Overall: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
    
    sys.exit(0 if overall_success else 1)
