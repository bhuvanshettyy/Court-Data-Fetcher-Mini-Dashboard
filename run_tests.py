#!/usr/bin/env python3
"""
Test runner script for Court Data Fetcher
"""

import sys
import os
import subprocess
import pytest

def run_tests():
    """Run the test suite"""
    print("Running tests for Court Data Fetcher...")
    
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with specific options
    args = [
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=utils",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml"
    ]
    
    try:
        result = subprocess.run(args, check=True)
        print("✅ All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 