#!/usr/bin/env python3
"""
Verification script to ensure all fix components are in place
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("MCP Backend Crash Fix - Verification Script")
print("=" * 80)
print()

project_root = Path(__file__).parent
errors = []
warnings = []
success = []

# Check documentation files
print("Checking documentation files...")
docs = [
    "START_HERE.md",
    "WAKE_UP_SUMMARY.md",
    "PROBLEM_SOLVED.md",
    "FIX_VALIDATION_REPORT.md",
    "ARCHITECTURE_DIAGRAM.md",
    "TESTING_CHECKLIST.md",
    "FILES_CREATED_SUMMARY.md",
    "FINAL_REPORT.md",
    "VISUAL_SUMMARY.txt"
]

for doc in docs:
    path = project_root / doc
    if path.exists():
        size = path.stat().st_size
        success.append(f"  OK: {doc} ({size} bytes)")
    else:
        errors.append(f"  MISSING: {doc}")

# Check test scripts
print("\nChecking test scripts...")
tests = [
    "test_crash_simulation.py",
    "test_e2e_with_tool_call.py",
    "test_dev_wrapper.py",
    "test_backend_direct.py"
]

for test in tests:
    path = project_root / test
    if path.exists():
        size = path.stat().st_size
        success.append(f"  OK: {test} ({size} bytes)")
    else:
        errors.append(f"  MISSING: {test}")

# Check test output
print("\nChecking test output files...")
outputs = [
    "crash_sim_output.txt",
    "backend_test_output.txt"
]

for output in outputs:
    path = project_root / output
    if path.exists():
        size = path.stat().st_size
        success.append(f"  OK: {output} ({size} bytes)")
    else:
        warnings.append(f"  NOT FOUND: {output} (will be created when tests run)")

# Check code changes
print("\nChecking code changes...")
code_file = project_root / "src" / "mcp_feedback_enhanced" / "dev_wrapper.py"
if code_file.exists():
    with open(code_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for key changes
    checks = [
        ("read_backend_stderr", "Stderr reader thread"),
        ("backend_stderr_thread", "Stderr thread variable"),
        ("spawn_failure_count", "Crash loop prevention"),
        ("backend_crash_", "Crash log creation"),
        ("backend_stderr_", "Stderr log creation"),
    ]
    
    for check_str, description in checks:
        if check_str in content:
            success.append(f"  OK: {description} found")
        else:
            errors.append(f"  MISSING: {description} not found in code")
    
    size = code_file.stat().st_size
    success.append(f"  OK: dev_wrapper.py ({size} bytes)")
else:
    errors.append(f"  MISSING: {code_file}")

# Check logs directory
print("\nChecking logs directory...")
logs_dir = project_root / "logs"
if logs_dir.exists():
    success.append(f"  OK: logs/ directory exists")
    
    # Count log files
    runtime_logs = list(logs_dir.glob("devwrapper_runtime_*.log"))
    if runtime_logs:
        success.append(f"  OK: {len(runtime_logs)} runtime log(s) found")
    else:
        warnings.append(f"  INFO: No runtime logs yet (will be created when server runs)")
else:
    warnings.append(f"  INFO: logs/ directory will be created when server runs")

# Print results
print("\n" + "=" * 80)
print("VERIFICATION RESULTS")
print("=" * 80)

if success:
    print(f"\nSUCCESS ({len(success)} items):")
    for item in success:
        print(item)

if warnings:
    print(f"\nWARNINGS ({len(warnings)} items):")
    for item in warnings:
        print(item)

if errors:
    print(f"\nERRORS ({len(errors)} items):")
    for item in errors:
        print(item)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if errors:
    print(f"\nStatus: INCOMPLETE")
    print(f"  Success: {len(success)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Errors: {len(errors)}")
    print("\nPlease fix the errors above before testing.")
    sys.exit(1)
else:
    print(f"\nStatus: COMPLETE")
    print(f"  Success: {len(success)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Errors: 0")
    print("\nAll fix components are in place!")
    print("\nNext steps:")
    print("  1. Read START_HERE.md for overview")
    print("  2. Run test_crash_simulation.py to verify fix")
    print("  3. Follow TESTING_CHECKLIST.md for full testing")
    sys.exit(0)

