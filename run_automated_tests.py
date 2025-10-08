#!/usr/bin/env python3
"""
Automated Test Runner and Reporting System
==========================================

Unified test runner that coordinates all test suites, executes them automatically,
and generates comprehensive reports with results, performance metrics, and recommendations.

Usage:
    python run_automated_tests.py
    python run_automated_tests.py --suite backend
    python run_automated_tests.py --parallel
    python run_automated_tests.py --report-format html
    python run_automated_tests.py --ci-mode
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add the project root to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_report_generator import TestReportGenerator
except ImportError:
    print("⚠️ Test report generator not available, using basic reporting")
    TestReportGenerator = None


class AutomatedTestRunner:
    """Main automated test runner class"""
    
    def __init__(self, config_file: str = "test_automation_config.json"):
        """Initialize the test runner"""
        self.config = self.load_config(config_file)
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.report_generator = TestReportGenerator() if TestReportGenerator else None
        
        # Test suites configuration
        self.test_suites = {
            "backend": {
                "script": "test_backend_rules_engine.py",
                "description": "Backend Rules Engine Test Suite",
                "dependencies": [],
                "timeout": 300,
                "critical": True
            },
            "frontend": {
                "script": "test_frontend_ui_components.py",
                "description": "Frontend UI Components Test Suite",
                "dependencies": [],
                "timeout": 180,
                "critical": True
            },
            "api": {
                "script": "test_api_endpoints.py",
                "description": "API Endpoints Test Suite",
                "dependencies": [],
                "timeout": 120,
                "critical": True
            },
            "integration": {
                "script": "test_integration_workflows.py",
                "description": "Integration Workflow Test Suite",
                "dependencies": ["backend", "frontend", "api"],
                "timeout": 300,
                "critical": True
            },
            "performance": {
                "script": "test_performance_benchmarks.py",
                "description": "Performance Benchmarking Suite",
                "dependencies": ["backend", "api"],
                "timeout": 600,
                "critical": False
            }
        }
    
    def load_config(self, config_file: str) -> Dict:
        """Load test automation configuration"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config file {config_file} not found, using defaults")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "execution": {
                "parallel_execution": False,
                "max_workers": 3,
                "continue_on_failure": True,
                "timeout_multiplier": 1.0
            },
            "reporting": {
                "formats": ["json", "html"],
                "output_directory": "./test_reports",
                "include_performance_metrics": True,
                "include_coverage_analysis": False,
                "generate_recommendations": True
            },
            "ci_cd": {
                "exit_on_failure": True,
                "generate_junit_xml": True,
                "upload_artifacts": False,
                "notify_on_failure": False
            },
            "quality_gates": {
                "minimum_pass_rate": 95.0,
                "maximum_performance_degradation": 20.0,
                "required_coverage": 80.0
            }
        }
    
    def get_execution_order(self, selected_suites: List[str]) -> List[str]:
        """Determine execution order based on dependencies"""
        ordered = []
        remaining = selected_suites.copy()
        
        while remaining:
            # Find suites with no unmet dependencies
            ready = []
            for suite in remaining:
                dependencies = self.test_suites[suite].get("dependencies", [])
                if all(dep in ordered or dep not in selected_suites for dep in dependencies):
                    ready.append(suite)
            
            if not ready:
                # Circular dependency or missing dependency
                print(f"⚠️ Cannot resolve dependencies for: {remaining}")
                ready = remaining  # Execute remaining suites anyway
            
            # Add ready suites to execution order
            for suite in ready:
                ordered.append(suite)
                remaining.remove(suite)
        
        return ordered
    
    def execute_test_suite(self, suite_name: str) -> Dict:
        """Execute a single test suite"""
        suite_config = self.test_suites[suite_name]
        script_path = suite_config["script"]
        timeout = suite_config["timeout"] * self.config["execution"]["timeout_multiplier"]
        
        print(f"🧪 Executing {suite_config['description']}...")
        
        start_time = time.time()
        
        try:
            # Check if script exists
            if not os.path.exists(script_path):
                return {
                    "suite": suite_name,
                    "status": "error",
                    "message": f"Test script not found: {script_path}",
                    "execution_time": 0,
                    "tests_run": 0,
                    "tests_passed": 0,
                    "tests_failed": 0,
                    "errors": 1
                }
            
            # Execute test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            execution_time = time.time() - start_time
            
            # Parse test results from output
            test_stats = self.parse_test_output(result.stdout, result.stderr)
            
            return {
                "suite": suite_name,
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests_run": test_stats.get("tests_run", 0),
                "tests_passed": test_stats.get("tests_passed", 0),
                "tests_failed": test_stats.get("tests_failed", 0),
                "errors": test_stats.get("errors", 0),
                "performance_metrics": test_stats.get("performance_metrics", {}),
                "message": f"Completed in {execution_time:.2f}s"
            }
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "suite": suite_name,
                "status": "timeout",
                "execution_time": execution_time,
                "message": f"Test suite timed out after {timeout}s",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "errors": 1
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "suite": suite_name,
                "status": "error",
                "execution_time": execution_time,
                "message": f"Execution error: {str(e)}",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "errors": 1
            }
    
    def parse_test_output(self, stdout: str, stderr: str) -> Dict:
        """Parse test output to extract statistics and metrics"""
        stats = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": 0,
            "performance_metrics": {}
        }
        
        # Parse unittest output
        lines = stdout.split('\n') + stderr.split('\n')
        
        for line in lines:
            # Look for test result summaries
            if "Ran " in line and " test" in line:
                try:
                    parts = line.split()
                    stats["tests_run"] = int(parts[1])
                except (IndexError, ValueError):
                    pass
            
            elif "FAILED (failures=" in line or "FAILED (errors=" in line:
                # Parse failure/error counts
                if "failures=" in line:
                    try:
                        failures = line.split("failures=")[1].split(",")[0].split(")")[0]
                        stats["tests_failed"] = int(failures)
                    except (IndexError, ValueError):
                        pass
                
                if "errors=" in line:
                    try:
                        errors = line.split("errors=")[1].split(",")[0].split(")")[0]
                        stats["errors"] = int(errors)
                    except (IndexError, ValueError):
                        pass
            
            elif "OK" in line and stats["tests_run"] > 0:
                # All tests passed
                stats["tests_passed"] = stats["tests_run"]
            
            # Look for performance metrics
            elif "📊" in line and "time:" in line:
                try:
                    # Extract performance metrics from output
                    metric_line = line.split("📊")[1].strip()
                    if ":" in metric_line:
                        key, value = metric_line.split(":", 1)
                        stats["performance_metrics"][key.strip()] = value.strip()
                except (IndexError, ValueError):
                    pass
        
        # Calculate passed tests if not explicitly found
        if stats["tests_passed"] == 0 and stats["tests_run"] > 0:
            stats["tests_passed"] = stats["tests_run"] - stats["tests_failed"] - stats["errors"]
        
        return stats
    
    def execute_parallel(self, suites: List[str]) -> Dict[str, Dict]:
        """Execute test suites in parallel"""
        max_workers = self.config["execution"]["max_workers"]
        results = {}
        
        # Group suites by dependency level for parallel execution
        execution_groups = self.group_by_dependencies(suites)
        
        for group in execution_groups:
            print(f"🔄 Executing group: {', '.join(group)}")
            
            with ThreadPoolExecutor(max_workers=min(max_workers, len(group))) as executor:
                # Submit all suites in current group
                future_to_suite = {
                    executor.submit(self.execute_test_suite, suite): suite 
                    for suite in group
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_suite):
                    suite = future_to_suite[future]
                    try:
                        result = future.result()
                        results[suite] = result
                        
                        status_icon = "✅" if result["status"] == "success" else "❌"
                        print(f"{status_icon} {suite}: {result['message']}")
                        
                    except Exception as e:
                        results[suite] = {
                            "suite": suite,
                            "status": "error",
                            "message": f"Execution failed: {str(e)}",
                            "execution_time": 0,
                            "tests_run": 0,
                            "tests_passed": 0,
                            "tests_failed": 0,
                            "errors": 1
                        }
                        print(f"❌ {suite}: Execution failed: {str(e)}")
            
            # Check if we should continue after failures
            if not self.config["execution"]["continue_on_failure"]:
                failed_suites = [s for s, r in results.items() if r["status"] != "success"]
                if failed_suites:
                    print(f"🛑 Stopping execution due to failures in: {', '.join(failed_suites)}")
                    break
        
        return results
    
    def execute_sequential(self, suites: List[str]) -> Dict[str, Dict]:
        """Execute test suites sequentially"""
        results = {}
        execution_order = self.get_execution_order(suites)
        
        for suite in execution_order:
            result = self.execute_test_suite(suite)
            results[suite] = result
            
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"{status_icon} {suite}: {result['message']}")
            
            # Check if we should continue after failure
            if result["status"] != "success" and not self.config["execution"]["continue_on_failure"]:
                print(f"🛑 Stopping execution due to failure in {suite}")
                break
        
        return results
    
    def group_by_dependencies(self, suites: List[str]) -> List[List[str]]:
        """Group suites by dependency levels for parallel execution"""
        groups = []
        remaining = suites.copy()
        processed = set()
        
        while remaining:
            current_group = []
            
            for suite in remaining[:]:
                dependencies = self.test_suites[suite].get("dependencies", [])
                # Check if all dependencies are already processed or not in selected suites
                if all(dep in processed or dep not in suites for dep in dependencies):
                    current_group.append(suite)
                    remaining.remove(suite)
            
            if not current_group:
                # Handle circular dependencies by adding remaining suites
                current_group = remaining[:]
                remaining = []
            
            groups.append(current_group)
            processed.update(current_group)
        
        return groups
    
    def run_tests(self, selected_suites: Optional[List[str]] = None, parallel: bool = False) -> Dict:
        """Run the selected test suites"""
        if selected_suites is None:
            selected_suites = list(self.test_suites.keys())
        
        # Validate selected suites
        invalid_suites = [s for s in selected_suites if s not in self.test_suites]
        if invalid_suites:
            raise ValueError(f"Invalid test suites: {invalid_suites}")
        
        print("🚀 Starting Automated Test Execution")
        print("=" * 60)
        print(f"📋 Selected suites: {', '.join(selected_suites)}")
        print(f"🔄 Execution mode: {'Parallel' if parallel else 'Sequential'}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Execute test suites
        if parallel and self.config["execution"]["parallel_execution"]:
            suite_results = self.execute_parallel(selected_suites)
        else:
            suite_results = self.execute_sequential(selected_suites)
        
        self.end_time = time.time()
        
        # Compile overall results
        self.results = {
            "execution_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration": self.end_time - self.start_time,
                "execution_mode": "parallel" if parallel else "sequential",
                "selected_suites": selected_suites
            },
            "suite_results": suite_results,
            "summary": self.generate_summary(suite_results),
            "quality_gates": self.check_quality_gates(suite_results),
            "recommendations": self.generate_recommendations(suite_results)
        }
        
        return self.results

    def generate_summary(self, suite_results: Dict[str, Dict]) -> Dict:
        """Generate test execution summary"""
        total_suites = len(suite_results)
        successful_suites = sum(1 for r in suite_results.values() if r["status"] == "success")
        failed_suites = sum(1 for r in suite_results.values() if r["status"] in ["failed", "error", "timeout"])

        total_tests = sum(r.get("tests_run", 0) for r in suite_results.values())
        total_passed = sum(r.get("tests_passed", 0) for r in suite_results.values())
        total_failed = sum(r.get("tests_failed", 0) for r in suite_results.values())
        total_errors = sum(r.get("errors", 0) for r in suite_results.values())

        success_rate = (successful_suites / total_suites * 100) if total_suites > 0 else 0
        test_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        return {
            "total_suites": total_suites,
            "successful_suites": successful_suites,
            "failed_suites": failed_suites,
            "suite_success_rate": success_rate,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "test_pass_rate": test_pass_rate,
            "total_execution_time": self.end_time - self.start_time if self.start_time and self.end_time else 0
        }

    def check_quality_gates(self, suite_results: Dict[str, Dict]) -> Dict:
        """Check quality gates and return pass/fail status"""
        summary = self.generate_summary(suite_results)
        gates = self.config["quality_gates"]

        quality_results = {
            "pass_rate_gate": {
                "required": gates["minimum_pass_rate"],
                "actual": summary["test_pass_rate"],
                "passed": summary["test_pass_rate"] >= gates["minimum_pass_rate"]
            },
            "critical_suites_gate": {
                "description": "All critical test suites must pass",
                "passed": True,
                "failed_critical_suites": []
            }
        }

        # Check critical suites
        for suite_name, result in suite_results.items():
            if self.test_suites[suite_name].get("critical", False) and result["status"] != "success":
                quality_results["critical_suites_gate"]["passed"] = False
                quality_results["critical_suites_gate"]["failed_critical_suites"].append(suite_name)

        # Overall quality gate status
        quality_results["overall_passed"] = all(
            gate["passed"] for gate in quality_results.values()
            if isinstance(gate, dict) and "passed" in gate
        )

        return quality_results

    def generate_recommendations(self, suite_results: Dict[str, Dict]) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []

        # Analyze failed suites
        failed_suites = [name for name, result in suite_results.items() if result["status"] != "success"]

        if failed_suites:
            recommendations.append(f"🔧 Fix failing test suites: {', '.join(failed_suites)}")

            # Specific recommendations based on suite type
            for suite in failed_suites:
                if suite == "backend":
                    recommendations.append("🔍 Review backend rules engine implementation and storage operations")
                elif suite == "frontend":
                    recommendations.append("🎨 Check frontend UI components and JavaScript functionality")
                elif suite == "api":
                    recommendations.append("🌐 Validate API endpoints and request/response handling")
                elif suite == "integration":
                    recommendations.append("🔗 Examine cross-component communication and data flow")
                elif suite == "performance":
                    recommendations.append("⚡ Optimize performance bottlenecks and resource usage")

        # Performance recommendations
        slow_suites = [
            name for name, result in suite_results.items()
            if result.get("execution_time", 0) > self.test_suites[name]["timeout"] * 0.8
        ]

        if slow_suites:
            recommendations.append(f"🐌 Optimize slow test suites: {', '.join(slow_suites)}")

        # Quality gate recommendations
        summary = self.generate_summary(suite_results)
        if summary["test_pass_rate"] < self.config["quality_gates"]["minimum_pass_rate"]:
            recommendations.append(f"📈 Improve test pass rate from {summary['test_pass_rate']:.1f}% to {self.config['quality_gates']['minimum_pass_rate']}%")

        # General recommendations
        if summary["total_errors"] > 0:
            recommendations.append("🐛 Investigate and fix test execution errors")

        if not recommendations:
            recommendations.append("🎉 All tests passing! Consider adding more comprehensive test coverage")

        return recommendations

    def save_results(self, output_dir: str = None) -> List[str]:
        """Save test results in configured formats"""
        if output_dir is None:
            output_dir = self.config["reporting"]["output_directory"]

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        if "json" in self.config["reporting"]["formats"]:
            json_file = os.path.join(output_dir, f"test_results_{timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            saved_files.append(json_file)

        # Generate HTML report
        if "html" in self.config["reporting"]["formats"] and self.report_generator:
            html_file = os.path.join(output_dir, f"test_report_{timestamp}.html")
            self.report_generator.generate_html_report(self.results, html_file)
            saved_files.append(html_file)

        # Generate JUnit XML for CI/CD
        if self.config["ci_cd"]["generate_junit_xml"]:
            xml_file = os.path.join(output_dir, f"junit_results_{timestamp}.xml")
            self.generate_junit_xml(xml_file)
            saved_files.append(xml_file)

        return saved_files

    def generate_junit_xml(self, output_file: str):
        """Generate JUnit XML format for CI/CD integration"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom

        testsuites = Element("testsuites")

        for suite_name, result in self.results["suite_results"].items():
            testsuite = SubElement(testsuites, "testsuite")
            testsuite.set("name", suite_name)
            testsuite.set("tests", str(result.get("tests_run", 0)))
            testsuite.set("failures", str(result.get("tests_failed", 0)))
            testsuite.set("errors", str(result.get("errors", 0)))
            testsuite.set("time", str(result.get("execution_time", 0)))

            # Add individual test cases (simplified)
            if result["status"] == "success":
                testcase = SubElement(testsuite, "testcase")
                testcase.set("name", f"{suite_name}_suite")
                testcase.set("classname", suite_name)
                testcase.set("time", str(result.get("execution_time", 0)))
            else:
                testcase = SubElement(testsuite, "testcase")
                testcase.set("name", f"{suite_name}_suite")
                testcase.set("classname", suite_name)
                testcase.set("time", str(result.get("execution_time", 0)))

                if result["status"] == "failed":
                    failure = SubElement(testcase, "failure")
                    failure.set("message", result.get("message", "Test suite failed"))
                    failure.text = result.get("stderr", "")
                elif result["status"] == "error":
                    error = SubElement(testcase, "error")
                    error.set("message", result.get("message", "Test suite error"))
                    error.text = result.get("stderr", "")

        # Write XML file
        rough_string = tostring(testsuites, 'utf-8')
        reparsed = minidom.parseString(rough_string)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))

    def print_summary(self):
        """Print test execution summary to console"""
        if not self.results:
            print("❌ No test results available")
            return

        summary = self.results["summary"]
        quality_gates = self.results["quality_gates"]

        print("\n" + "=" * 60)
        print("📋 Automated Test Execution Summary")
        print("=" * 60)

        # Execution info
        exec_info = self.results["execution_info"]
        print(f"⏱️  Total execution time: {summary['total_execution_time']:.2f} seconds")
        print(f"🔄 Execution mode: {exec_info['execution_mode']}")
        print(f"📅 Completed at: {exec_info['end_time']}")

        # Suite results
        print(f"\n📊 Test Suite Results:")
        print(f"✅ Successful suites: {summary['successful_suites']}/{summary['total_suites']} ({summary['suite_success_rate']:.1f}%)")
        print(f"❌ Failed suites: {summary['failed_suites']}")

        # Test results
        print(f"\n🧪 Individual Test Results:")
        print(f"✅ Tests passed: {summary['total_passed']}")
        print(f"❌ Tests failed: {summary['total_failed']}")
        print(f"💥 Test errors: {summary['total_errors']}")
        print(f"🎯 Pass rate: {summary['test_pass_rate']:.1f}%")

        # Quality gates
        print(f"\n🚪 Quality Gates:")
        for gate_name, gate_result in quality_gates.items():
            if isinstance(gate_result, dict) and "passed" in gate_result:
                status = "✅ PASS" if gate_result["passed"] else "❌ FAIL"
                print(f"  {status} {gate_name}")

        overall_status = "✅ PASS" if quality_gates["overall_passed"] else "❌ FAIL"
        print(f"\n🎯 Overall Quality Gate: {overall_status}")

        # Recommendations
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in self.results["recommendations"]:
                print(f"  {rec}")

        # Suite details
        print(f"\n📋 Suite Details:")
        for suite_name, result in self.results["suite_results"].items():
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"  {status_icon} {suite_name}: {result['message']} ({result['execution_time']:.2f}s)")


def main():
    """Main entry point for the automated test runner"""
    parser = argparse.ArgumentParser(description="Automated Test Runner and Reporting System")
    parser.add_argument("--suite", "-s", action="append", help="Specific test suite(s) to run")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run tests in parallel")
    parser.add_argument("--config", "-c", default="test_automation_config.json", help="Configuration file")
    parser.add_argument("--output-dir", "-o", help="Output directory for reports")
    parser.add_argument("--report-format", "-f", action="append", choices=["json", "html", "xml"], help="Report format(s)")
    parser.add_argument("--ci-mode", action="store_true", help="CI/CD mode (exit with error code on failure)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        # Initialize test runner
        runner = AutomatedTestRunner(args.config)

        # Override configuration with command line arguments
        if args.output_dir:
            runner.config["reporting"]["output_directory"] = args.output_dir

        if args.report_format:
            runner.config["reporting"]["formats"] = args.report_format

        if args.ci_mode:
            runner.config["ci_cd"]["exit_on_failure"] = True
            runner.config["execution"]["continue_on_failure"] = False

        # Run tests
        selected_suites = args.suite if args.suite else None
        results = runner.run_tests(selected_suites, args.parallel)

        # Print summary
        runner.print_summary()

        # Save reports
        saved_files = runner.save_results()
        if saved_files:
            print(f"\n📄 Reports saved:")
            for file_path in saved_files:
                print(f"  📁 {file_path}")

        # Exit with appropriate code for CI/CD
        if args.ci_mode and not results["quality_gates"]["overall_passed"]:
            print("\n❌ Quality gates failed - exiting with error code")
            sys.exit(1)

        print("\n🎉 Test execution completed successfully!")

    except Exception as e:
        print(f"❌ Test runner failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
