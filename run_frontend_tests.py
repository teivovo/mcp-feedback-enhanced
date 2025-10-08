#!/usr/bin/env python3
"""
Frontend UI Components Test Runner
==================================

Automated test runner for the frontend UI components using headless browser automation.
This script validates the frontend test suite functionality and generates test reports.
"""

import json
import os
import sys
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class FrontendTestRunner:
    """Frontend test runner using Selenium WebDriver"""
    
    def __init__(self):
        self.driver = None
        self.test_results = []
        self.start_time = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with headless options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized successfully")
            return True
            
        except WebDriverException as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            print("💡 Please ensure Chrome and ChromeDriver are installed")
            return False
    
    def load_test_page(self):
        """Load the frontend test page"""
        try:
            test_file = Path(__file__).parent / "test_frontend_ui_components.html"
            if not test_file.exists():
                print(f"❌ Test file not found: {test_file}")
                return False
            
            file_url = f"file:///{test_file.absolute().as_posix()}"
            print(f"🌐 Loading test page: {file_url}")
            
            self.driver.get(file_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "test-suite-container"))
            )
            
            print("✅ Test page loaded successfully")
            return True
            
        except TimeoutException:
            print("❌ Timeout waiting for test page to load")
            return False
        except Exception as e:
            print(f"❌ Error loading test page: {e}")
            return False
    
    def wait_for_test_framework(self):
        """Wait for the test framework to initialize"""
        try:
            # Wait for test framework to be available
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return window.testFramework !== undefined")
            )
            
            print("✅ Test framework initialized")
            return True
            
        except TimeoutException:
            print("❌ Timeout waiting for test framework to initialize")
            return False
    
    def run_test_suite(self, test_name):
        """Run a specific test suite"""
        try:
            print(f"🧪 Running {test_name} tests...")
            
            # Execute the test function
            self.driver.execute_script(f"window.testFramework.{test_name}()")
            
            # Wait a moment for tests to complete
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error running {test_name}: {e}")
            return False
    
    def get_test_results(self):
        """Get test results from the page"""
        try:
            # Get test statistics
            total_tests = self.driver.execute_script("return document.getElementById('totalTests').textContent")
            passed_tests = self.driver.execute_script("return document.getElementById('passedTests').textContent")
            failed_tests = self.driver.execute_script("return document.getElementById('failedTests').textContent")
            success_rate = self.driver.execute_script("return document.getElementById('successRate').textContent")
            
            # Get test log
            test_log = self.driver.execute_script("return document.getElementById('testLog').textContent")
            test_results = self.driver.execute_script("return document.getElementById('testResults').textContent")
            
            return {
                'total_tests': int(total_tests) if total_tests.isdigit() else 0,
                'passed_tests': int(passed_tests) if passed_tests.isdigit() else 0,
                'failed_tests': int(failed_tests) if failed_tests.isdigit() else 0,
                'success_rate': success_rate,
                'test_log': test_log,
                'test_results': test_results
            }
            
        except Exception as e:
            print(f"❌ Error getting test results: {e}")
            return None
    
    def run_all_tests(self):
        """Run all frontend test suites"""
        print("🚀 Starting Frontend UI Components Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        
        if not self.setup_driver():
            return False
        
        if not self.load_test_page():
            return False
        
        if not self.wait_for_test_framework():
            return False
        
        # Run all test suites
        test_suites = [
            'runRulesManagerTests',
            'runAccordionTests', 
            'runFormValidationTests',
            'runResponsiveTests',
            'runUIInteractionTests',
            'runKeyboardNavigationTests',
            'runAccessibilityTests'
        ]
        
        for suite in test_suites:
            if not self.run_test_suite(suite):
                print(f"⚠️ Failed to run {suite}")
        
        # Wait for all tests to complete
        time.sleep(3)
        
        # Get final results
        results = self.get_test_results()
        if results:
            self.print_results(results)
            self.save_results(results)
            return results['failed_tests'] == 0
        
        return False
    
    def print_results(self, results):
        """Print test results to console"""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        print("\n" + "=" * 60)
        print("📋 Frontend Test Suite Results")
        print("=" * 60)
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"🧪 Total tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed_tests']}")
        print(f"❌ Failed: {results['failed_tests']}")
        print(f"🎯 Success rate: {results['success_rate']}")
        
        if results['failed_tests'] > 0:
            print(f"\n❌ Test failures detected:")
            print(results['test_results'])
    
    def save_results(self, results):
        """Save test results to file"""
        try:
            report = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'test_suite': 'Frontend UI Components',
                'duration': time.time() - self.start_time if self.start_time else 0,
                'results': results
            }
            
            report_file = f"frontend_test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"📊 Test report saved: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Failed to save test report: {e}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            print("🧹 WebDriver cleaned up")


def main():
    """Main test runner function"""
    runner = FrontendTestRunner()
    
    try:
        success = runner.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        return 1
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1
        
    finally:
        runner.cleanup()


if __name__ == "__main__":
    # Check if Selenium is available
    try:
        import selenium
        print(f"🔧 Selenium version: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium not installed. Install with: pip install selenium")
        print("💡 Also ensure Chrome and ChromeDriver are installed")
        sys.exit(1)
    
    sys.exit(main())
