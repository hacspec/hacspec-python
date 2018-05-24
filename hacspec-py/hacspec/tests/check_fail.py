# Testing spec checker. Negative tests

@typechecked
def fail_lists() -> None:
    y = [0, 1] # This should fail
