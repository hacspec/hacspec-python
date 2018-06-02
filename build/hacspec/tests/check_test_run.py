#!/usr/bin/python3

from hacspec.speclib import *
from check import *
from check_fail import *
from sys import exit

# Run spec checker tests


def main(x: int) -> None:
    test_lists()
    fail_lists()


if __name__ == "__main__":
    main(0)
