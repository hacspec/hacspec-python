#!/usr/bin/python3

from hacspec.speclib import *
from check_test import *
from check_test_fail import *
from sys import exit

# Run spec checker tests


def main():
    test_lists()
    fail_lists()


if __name__ == "__main__":
    main()
