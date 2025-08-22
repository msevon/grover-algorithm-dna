#!/usr/bin/env python3
"""
Test Runner for Grover Algorithm Project
========================================

This script runs all tests in the project to ensure everything is working correctly.
"""

import sys
import os
import subprocess
import time

def run_test(test_file, description):
    """Run a specific test file and report results."""
    print(f"\n🧪 Running {description}...")
    print("-" * 50)
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=60)
        test_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} PASSED ({test_time:.2f}s)")
            return True
        else:
            print(f"❌ {description} FAILED")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} TIMEOUT (60s)")
        return False
    except Exception as e:
        print(f"💥 {description} ERROR: {e}")
        return False

def main():
    """Run all tests in the project."""
    print("🚀 Grover Algorithm Project - Test Suite")
    print("=" * 50)
    
    # Add src directory to path for imports
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
    sys.path.insert(0, src_path)
    
    # Add cpp directory to path for C++ module
    cpp_path = os.path.join(os.path.dirname(__file__), '..', 'cpp')
    sys.path.insert(0, cpp_path)
    
    tests = [
        ("test_accelerator.py", "C++ Accelerator Tests"),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_file, description in tests:
        if run_test(test_file, description):
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The project is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
