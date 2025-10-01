#!/usr/bin/env python3
"""
Test runner script for the wedding mirror assistant
"""

import sys
import subprocess
import os

def run_tests():
    """Run all tests and return exit code"""
    # Change to the tests directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    print("🧪 Running Wedding Mirror Assistant Tests")
    print("=" * 50)
    
    # Run pytest with verbose output
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-v",  # verbose
            "-s",  # don't capture output
            "--tb=short",  # shorter traceback format
            "."  # run all tests in current directory
        ], capture_output=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)