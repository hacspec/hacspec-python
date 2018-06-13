import sys
import threading

def print_dot():
    t = threading.Timer(1, print_dot)
    t.daemon = True
    t.start()
    print(".", end="")
    sys.stdout.flush()
    return t

def exit(r, t):
    t.cancel()
    sys.exit(r)
