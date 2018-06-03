# Testing spec checker. Negative tests

from hacspec.speclib import *

@typechecked
def fail_lists() -> None:
    y = [0, 1] # This should fail
