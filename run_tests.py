#!/usr/bin/env python3
"""
run_tests.py
============
Master test suite runner for Electric Vehicle Market Analysis platform.
Executes test_routes.py, test_database.py, and test_data_quality.py.
Outputs structured performance and pass/fail summary.
"""

import sys
import unittest
import time

def main():
    print("\n" + "="*70)
    print(" ELECTRIC VEHICLE MARKET ANALYSIS — MASTER TEST SUITE")
    print("="*70 + "\n")

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Discover and add test cases
    suite.addTests(loader.discover("tests", pattern="test_*.py"))

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("\n" + "="*70)
    print(" TEST EXECUTION SUMMARY")
    print("="*70)
    print(f" Total Tests Run:   {result.testsRun}")
    print(f" Total Passed:      {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f" Total Failures:    {len(result.failures)}")
    print(f" Total Errors:      {len(result.errors)}")
    print(f" Elapsed Time:      {elapsed:.3f} seconds")
    print("="*70 + "\n")

    if not result.wasSuccessful():
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
