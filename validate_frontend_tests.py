#!/usr/bin/env python3
"""
Frontend UI Components Test Validator
=====================================

Validates the frontend test suite files and structure without requiring browser automation.
Performs static analysis of the test files to ensure they are properly structured and complete.
"""

import json
import os
import re
import sys
from pathlib import Path


class FrontendTestValidator:
    """Validator for frontend test suite files"""
    
    def __init__(self):
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
    def log_result(self, test_name, status, details=""):
        """Log validation result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details
        }
        self.validation_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {details}")
        
        if status == "FAIL":
            self.errors.append(f"{test_name}: {details}")
        elif status == "WARN":
            self.warnings.append(f"{test_name}: {details}")
    
    def validate_html_structure(self):
        """Validate the HTML test file structure"""
        html_file = Path("test_frontend_ui_components.html")
        
        if not html_file.exists():
            self.log_result("HTML File Existence", "FAIL", "test_frontend_ui_components.html not found")
            return False
        
        try:
            content = html_file.read_text(encoding='utf-8')
            
            # Check for required elements
            required_elements = [
                r'<title>.*Frontend UI Components.*</title>',
                r'class="test-suite-container"',
                r'class="test-controls"',
                r'class="test-results"',
                r'class="test-summary"',
                r'id="testLog"',
                r'id="testResults"',
                r'id="testSummary"',
                r'id="hiddenTestArea"'
            ]
            
            for element in required_elements:
                if not re.search(element, content, re.IGNORECASE):
                    self.log_result("HTML Structure", "FAIL", f"Missing required element: {element}")
                    return False
            
            # Check for test control buttons
            test_buttons = [
                r'onclick="runRulesManagerTests\(\)"',
                r'onclick="runAccordionTests\(\)"',
                r'onclick="runFormValidationTests\(\)"',
                r'onclick="runAllTests\(\)"'
            ]
            
            for button in test_buttons:
                if not re.search(button, content):
                    self.log_result("HTML Controls", "WARN", f"Missing test button: {button}")
            
            # Check for CSS styles
            if 'test-success' not in content or 'test-error' not in content:
                self.log_result("HTML Styling", "WARN", "Missing test status CSS classes")
            
            self.log_result("HTML Structure", "PASS", "All required HTML elements present")
            return True
            
        except Exception as e:
            self.log_result("HTML File Reading", "FAIL", f"Error reading HTML file: {e}")
            return False
    
    def validate_javascript_structure(self):
        """Validate the JavaScript test framework structure"""
        js_file = Path("test_frontend_automation.js")
        
        if not js_file.exists():
            self.log_result("JavaScript File Existence", "FAIL", "test_frontend_automation.js not found")
            return False
        
        try:
            content = js_file.read_text(encoding='utf-8')
            
            # Check for main framework class
            if 'function FrontendTestFramework()' not in content:
                self.log_result("JavaScript Framework", "FAIL", "FrontendTestFramework class not found")
                return False
            
            # Check for required methods
            required_methods = [
                'initialize',
                'runTest',
                'updateResults',
                'testRulesManagerInit',
                'testAccordionFunctionality',
                'testFormValidation',
                'testResponsiveDesign',
                'testUIInteractions',
                'testKeyboardNavigation',
                'testAccessibility',
                'runAllTests',
                'clearResults',
                'generateReport'
            ]
            
            missing_methods = []
            for method in required_methods:
                if f'.{method} = function(' not in content and f'.prototype.{method} = function(' not in content:
                    missing_methods.append(method)
            
            if missing_methods:
                self.log_result("JavaScript Methods", "FAIL", f"Missing methods: {', '.join(missing_methods)}")
                return False
            
            # Check for test suites
            test_suites = [
                'runRulesManagerTests',
                'runAccordionTests',
                'runFormValidationTests',
                'runResponsiveTests',
                'runUIInteractionTests',
                'runKeyboardNavigationTests',
                'runAccessibilityTests'
            ]
            
            missing_suites = []
            for suite in test_suites:
                if f'.{suite} = function(' not in content and f'.prototype.{suite} = function(' not in content:
                    missing_suites.append(suite)
            
            if missing_suites:
                self.log_result("JavaScript Test Suites", "FAIL", f"Missing test suites: {', '.join(missing_suites)}")
                return False
            
            # Check for global export
            if 'window.FrontendTestFramework = FrontendTestFramework' not in content:
                self.log_result("JavaScript Export", "FAIL", "Framework not exported to global scope")
                return False
            
            self.log_result("JavaScript Structure", "PASS", "All required JavaScript components present")
            return True
            
        except Exception as e:
            self.log_result("JavaScript File Reading", "FAIL", f"Error reading JavaScript file: {e}")
            return False
    
    def validate_test_coverage(self):
        """Validate test coverage and completeness"""
        js_file = Path("test_frontend_automation.js")
        
        if not js_file.exists():
            return False
        
        try:
            content = js_file.read_text(encoding='utf-8')
            
            # Count test methods
            test_methods = re.findall(r'\.test\w+\s*=\s*function\(', content)
            test_count = len(test_methods)
            
            if test_count < 10:
                self.log_result("Test Coverage", "WARN", f"Only {test_count} test methods found, consider adding more")
            else:
                self.log_result("Test Coverage", "PASS", f"{test_count} test methods found")
            
            # Check for error handling
            error_handling_patterns = [
                r'try\s*{',
                r'catch\s*\(',
                r'\.success\s*:\s*false',
                r'return\s*{\s*success:\s*false'
            ]
            
            error_handling_count = 0
            for pattern in error_handling_patterns:
                error_handling_count += len(re.findall(pattern, content))
            
            if error_handling_count < 5:
                self.log_result("Error Handling", "WARN", "Limited error handling detected")
            else:
                self.log_result("Error Handling", "PASS", "Adequate error handling present")
            
            # Check for mock data
            if 'mockRules' in content or 'testData' in content:
                self.log_result("Test Data", "PASS", "Mock test data found")
            else:
                self.log_result("Test Data", "WARN", "No mock test data found")
            
            return True
            
        except Exception as e:
            self.log_result("Test Coverage Analysis", "FAIL", f"Error analyzing test coverage: {e}")
            return False
    
    def validate_dependencies(self):
        """Validate external dependencies and references"""
        html_file = Path("test_frontend_ui_components.html")
        
        if not html_file.exists():
            return False
        
        try:
            content = html_file.read_text(encoding='utf-8')
            
            # Check for CSS dependencies
            css_refs = re.findall(r'href="([^"]+\.css)"', content)
            for css_ref in css_refs:
                css_path = Path(css_ref)
                if not css_path.exists():
                    self.log_result("CSS Dependencies", "WARN", f"CSS file not found: {css_ref}")
                else:
                    self.log_result("CSS Dependencies", "PASS", f"CSS file found: {css_ref}")
            
            # Check for JavaScript dependencies
            js_refs = re.findall(r'src="([^"]+\.js)"', content)
            for js_ref in js_refs:
                js_path = Path(js_ref)
                if not js_path.exists():
                    self.log_result("JavaScript Dependencies", "WARN", f"JS file not found: {js_ref}")
                else:
                    self.log_result("JavaScript Dependencies", "PASS", f"JS file found: {js_ref}")
            
            return True
            
        except Exception as e:
            self.log_result("Dependencies Check", "FAIL", f"Error checking dependencies: {e}")
            return False
    
    def validate_accessibility_features(self):
        """Validate accessibility features in the test suite"""
        html_file = Path("test_frontend_ui_components.html")
        
        if not html_file.exists():
            return False
        
        try:
            content = html_file.read_text(encoding='utf-8')
            
            # Check for accessibility attributes
            accessibility_features = [
                r'aria-label=',
                r'aria-describedby=',
                r'role=',
                r'alt=',
                r'tabindex='
            ]
            
            found_features = []
            for feature in accessibility_features:
                if re.search(feature, content, re.IGNORECASE):
                    found_features.append(feature.replace('=', ''))
            
            if found_features:
                self.log_result("Accessibility Features", "PASS", f"Found: {', '.join(found_features)}")
            else:
                self.log_result("Accessibility Features", "WARN", "No accessibility attributes found in HTML")
            
            # Check for accessibility tests in JavaScript
            js_file = Path("test_frontend_automation.js")
            if js_file.exists():
                js_content = js_file.read_text(encoding='utf-8')
                if 'testAccessibility' in js_content:
                    self.log_result("Accessibility Tests", "PASS", "Accessibility test methods found")
                else:
                    self.log_result("Accessibility Tests", "WARN", "No accessibility test methods found")
            
            return True
            
        except Exception as e:
            self.log_result("Accessibility Validation", "FAIL", f"Error validating accessibility: {e}")
            return False
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🔍 Frontend UI Components Test Suite Validation")
        print("=" * 60)
        
        # Run all validation checks
        validations = [
            self.validate_html_structure,
            self.validate_javascript_structure,
            self.validate_test_coverage,
            self.validate_dependencies,
            self.validate_accessibility_features
        ]
        
        all_passed = True
        for validation in validations:
            if not validation():
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 Validation Summary")
        print("=" * 60)
        
        total_tests = len(self.validation_results)
        passed_tests = len([r for r in self.validation_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.validation_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.validation_results if r['status'] == 'WARN'])
        
        print(f"🧪 Total validations: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warnings}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"🎯 Success rate: {success_rate:.1f}%")
        
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️ Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if failed_tests == 0:
            print(f"\n🎉 All validations passed! Frontend test suite is ready.")
        else:
            print(f"\n🔧 Please fix the errors above before running the test suite.")
        
        return failed_tests == 0


def main():
    """Main validation function"""
    validator = FrontendTestValidator()
    
    try:
        success = validator.run_validation()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        return 1
        
    except Exception as e:
        print(f"💥 Unexpected error during validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
