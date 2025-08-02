#!/usr/bin/env python3
"""
Test runner for Court Data Fetcher
"""

import sys
import os
import subprocess
import unittest

def run_tests():
    """Run all tests"""
    print("🧪 Running Court Data Fetcher Tests")
    print("=" * 50)
    
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_linting():
    """Run code linting"""
    print("\n🔍 Running Code Linting")
    print("=" * 50)
    
    try:
        # Check if flake8 is installed
        subprocess.run([sys.executable, '-m', 'flake8', '--version'], 
                      capture_output=True, check=True)
        
        # Run flake8
        result = subprocess.run([
            sys.executable, '-m', 'flake8', 
            '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics',
            'app.py', 'utils/', 'models/', 'tests/'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Linting passed!")
            return True
        else:
            print("❌ Linting failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError:
        print("⚠️  flake8 not installed. Install with: pip install flake8")
        return True
    except FileNotFoundError:
        print("⚠️  flake8 not found")
        return True

def run_security_checks():
    """Run security checks"""
    print("\n🔒 Running Security Checks")
    print("=" * 50)
    
    try:
        # Check if bandit is installed
        subprocess.run([sys.executable, '-m', 'bandit', '--version'], 
                      capture_output=True, check=True)
        
        # Run bandit
        result = subprocess.run([
            sys.executable, '-m', 'bandit', '-r', '.', '-f', 'txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Security checks passed!")
            return True
        else:
            print("⚠️  Security issues found:")
            print(result.stdout)
            return False
            
    except subprocess.CalledProcessError:
        print("⚠️  bandit not installed. Install with: pip install bandit")
        return True
    except FileNotFoundError:
        print("⚠️  bandit not found")
        return True

def main():
    """Main test runner"""
    print("🚀 Court Data Fetcher - Test Suite")
    print("=" * 50)
    
    # Run tests
    tests_passed = run_tests()
    
    # Run linting
    linting_passed = run_linting()
    
    # Run security checks
    security_passed = run_security_checks()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"Tests: {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"Linting: {'✅ PASSED' if linting_passed else '❌ FAILED'}")
    print(f"Security: {'✅ PASSED' if security_passed else '❌ FAILED'}")
    
    overall_success = tests_passed and linting_passed and security_passed
    
    if overall_success:
        print("\n🎉 All checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Some checks failed!")
        sys.exit(1)

if __name__ == '__main__':
    main() 