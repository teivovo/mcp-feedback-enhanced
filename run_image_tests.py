#!/usr/bin/env python3
"""
Comprehensive Test Runner for Image Processing Fixes

This script orchestrates the complete testing process:
1. Applies fixes to the server.py file
2. Runs the independent test server on port 8772
3. Provides testing instructions and validation

Usage:
    python run_image_tests.py [--fix-only] [--test-only] [--port PORT]

Options:
    --fix-only    Only apply fixes, don't run tests
    --test-only   Only run tests, don't apply fixes
    --port PORT   Use custom port (default: 8772)
"""

import argparse
import asyncio
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


class ImageTestRunner:
    """Orchestrates the complete image processing testing workflow"""
    
    def __init__(self, port: int = 8772):
        self.port = port
        self.project_root = Path(__file__).parent
        
    def apply_fixes(self) -> bool:
        """Apply fixes to the server.py file"""
        print("🔧 Step 1: Applying image processing fixes...")
        
        fix_script = self.project_root / "fix_image_processing.py"
        if not fix_script.exists():
            print(f"❌ Fix script not found: {fix_script}")
            return False
        
        try:
            result = subprocess.run([
                sys.executable, str(fix_script)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running fix script: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        print("📦 Checking dependencies...")
        
        required_packages = ['fastmcp', 'fastapi', 'uvicorn']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Please install them with: uv sync --dev")
            return False
        
        return True
    
    async def run_test_server(self) -> bool:
        """Run the independent test server"""
        print(f"🚀 Step 2: Starting test server on port {self.port}...")
        
        test_script = self.project_root / "test_image_processing.py"
        if not test_script.exists():
            print(f"❌ Test script not found: {test_script}")
            return False
        
        try:
            # Import and run the test server
            sys.path.insert(0, str(self.project_root))
            from test_image_processing import ImageProcessingTester
            
            tester = ImageProcessingTester(port=self.port)
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                url = f"http://localhost:{self.port}"
                print(f"🌐 Opening browser: {url}")
                webbrowser.open(url)
            
            import threading
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Run the server
            await tester.run_server()
            return True
            
        except Exception as e:
            print(f"❌ Error running test server: {e}")
            return False
    
    def show_testing_instructions(self):
        """Show comprehensive testing instructions"""
        print("\n" + "="*60)
        print("🧪 IMAGE PROCESSING TESTING INSTRUCTIONS")
        print("="*60)
        
        print(f"""
📋 Testing Checklist:

1. 🌐 BROWSER INTERFACE (http://localhost:{self.port})
   ✅ Upload images via drag & drop
   ✅ Upload images via file selector
   ✅ Test multiple image formats (PNG, JPG, GIF)
   ✅ Test different image sizes
   
2. 🧪 PIPELINE TESTING
   ✅ Click "Test Image Processing Pipeline"
   ✅ Verify all images process successfully
   ✅ Check for any error messages
   
3. 🔧 MCP TOOL TESTING
   ✅ Click "Test MCP Tool"
   ✅ Verify FastMCP Image objects are created
   ✅ Check that images are displayed correctly
   
4. 📊 VALIDATION CHECKS
   ✅ All uploaded images should show green checkmarks
   ✅ No red error messages in results
   ✅ Images should be visible in the response
   ✅ File sizes and formats should be correct

🎯 SUCCESS CRITERIA:
   - All images process without errors
   - FastMCP Image objects are created successfully
   - Images are displayed correctly in the test interface
   - No "FastMCPImage" undefined errors

❌ COMMON ISSUES TO WATCH FOR:
   - "FastMCPImage is not defined" errors
   - Base64 decode failures
   - Image format detection issues
   - WebSocket connection problems

🔄 IF ISSUES FOUND:
   1. Note the specific error messages
   2. Check the browser console for additional errors
   3. Stop the server (Ctrl+C)
   4. Review and fix the issues
   5. Re-run this test script
        """)
    
    def show_next_steps(self):
        """Show next steps after testing"""
        print("\n" + "="*60)
        print("🎯 NEXT STEPS AFTER TESTING")
        print("="*60)
        
        print("""
1. 🧪 IF TESTS PASS:
   ✅ The fixes are working correctly
   ✅ You can now test with the main MCP server
   ✅ Image processing should work in VS Code/Cursor
   
2. 🔧 INTEGRATION WITH MAIN SERVER:
   ✅ The fixes have been applied to src/mcp_feedback_enhanced/server.py
   ✅ Restart your MCP server to pick up the changes
   ✅ Test image upload through the main interface
   
3. 📱 TELEGRAM TESTING (Later):
   ✅ Once WebUI images work, test Telegram integration
   ✅ Verify bidirectional image communication
   
4. 🚀 PRODUCTION DEPLOYMENT:
   ✅ Run full test suite: make test
   ✅ Check code quality: make check
   ✅ Update version if needed
        """)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Image Processing Test Runner")
    parser.add_argument("--fix-only", action="store_true", help="Only apply fixes")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    parser.add_argument("--port", type=int, default=8772, help="Test server port")
    
    args = parser.parse_args()
    
    runner = ImageTestRunner(port=args.port)
    
    print("🧪 MCP Feedback Enhanced - Image Processing Test Runner")
    print("=" * 60)
    
    # Check dependencies first
    if not runner.check_dependencies():
        return False
    
    success = True
    
    # Apply fixes unless test-only mode
    if not args.test_only:
        if not runner.apply_fixes():
            print("❌ Failed to apply fixes")
            return False
        print("✅ Fixes applied successfully")
    
    # Run tests unless fix-only mode
    if not args.fix_only:
        runner.show_testing_instructions()
        
        print(f"\n🚀 Starting test server on port {args.port}...")
        print("Press Ctrl+C to stop the server when testing is complete")
        
        try:
            await runner.run_test_server()
        except KeyboardInterrupt:
            print("\n🛑 Test server stopped by user")
        except Exception as e:
            print(f"❌ Test server error: {e}")
            success = False
        
        runner.show_next_steps()
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        exit(0)
