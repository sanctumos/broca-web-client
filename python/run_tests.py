#!/usr/bin/env python3
"""
Comprehensive Test Runner for Web Chat Bridge Flask API
Runs unit, integration, and e2e tests with coverage reporting
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Exit Code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print("\nSTDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"\n❌ FAILED: {description}")
        return False
    else:
        print(f"\n✅ SUCCESS: {description}")
        return True
    
    return result.returncode == 0

def main():
    """Main test runner"""
    print("🚀 Web Chat Bridge Flask API - Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('tests'):
        print("❌ Error: 'tests' directory not found. Please run from the python/ directory.")
        sys.exit(1)
    
    # Install test dependencies
    print("\n📦 Installing test dependencies...")
    if not run_command("pip install -r requirements.txt", "Install dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    unit_success = run_command(
        "python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov/unit",
        "Unit Tests with Coverage"
    )
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_success = run_command(
        "python -m pytest tests/integration/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov/integration",
        "Integration Tests with Coverage"
    )
    
    # Run e2e tests
    print("\n🌐 Running End-to-End Tests...")
    e2e_success = run_command(
        "python -m pytest tests/e2e/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov/e2e",
        "End-to-End Tests with Coverage"
    )
    
    # Run all tests together for overall coverage
    print("\n📊 Running All Tests for Overall Coverage...")
    overall_success = run_command(
        "python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov/overall --cov-report=xml",
        "All Tests with Overall Coverage"
    )
    
    # Generate coverage summary
    print("\n📈 Generating Coverage Summary...")
    coverage_success = run_command(
        "python -m coverage report",
        "Coverage Report"
    )
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST SUITE SUMMARY")
    print("="*60)
    
    results = {
        "Unit Tests": unit_success,
        "Integration Tests": integration_success,
        "End-to-End Tests": e2e_success,
        "Overall Coverage": overall_success,
        "Coverage Report": coverage_success
    }
    
    all_passed = True
    for test_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_type:25} {status}")
        if not success:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! 100% Coverage Achieved!")
        print("\n📁 Coverage reports generated in:")
        print("   - htmlcov/unit/")
        print("   - htmlcov/integration/")
        print("   - htmlcov/e2e/")
        print("   - htmlcov/overall/")
        print("   - coverage.xml")
    else:
        print("❌ Some tests failed. Please review the output above.")
        sys.exit(1)
    
    print("\n🚀 Test suite completed successfully!")

if __name__ == "__main__":
    main()
