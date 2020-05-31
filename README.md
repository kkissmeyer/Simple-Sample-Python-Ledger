# Simple-Sample-Python-Ledger
Ledger Written in Python 3 

Test Exercise Code

This code is developed for the ledger transactions / account balance coding exercise in python

Files:

ledger.py: This module contains the Classes that implement the solution to the exercise. 
          It provides account balances both in Cached and Reduced (calculated) mode. 
          Balances for a date are calculated for the end of the day, and include all transactions through that date.
          See ledger_test_driver for sample usage code. The module is intended to demonstrate the use of Python classes and
          inheritance, lists, arrays, collections, tuples and general object-oriented design that encapsulates internal logic.
          It includes a test driver with regression input and tests, as well as random test generator.
          
sortedcollection.py: This module contains a community insert based sort collection class. I use this class in ledger.py

sortcollection_test_driver.py: This module is a test driver for the SortedCollection class. It was provided with the community class.

ledger_test_driver.py: This module imports ledger.py and runs regression and random transaction and balance tests against its classes. 
                      It accepts an argument for the number of random test transactions to run. It tallies the passes and fails and uses
                      cprofile to print stats on the test run
                      
run_test.bat: Windows batch file calls ledger_test_driver with an argument for the number of random tests to execute, and redirects stdout and stderr to ledger_test_driver.txt

run_ledger_test.sh:  bash shell script that runs ledger_test_driver with a command line argument for the number of random tests to execute, and redicts stdout and stderr to ledger_test_driver.txt

Enjoy!
          
