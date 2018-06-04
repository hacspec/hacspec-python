from specs.argon2i import *

from test_vectors.argon2i_test_vectors import *
from sys import exit
from tests.testlib import print_dot, exit

def main():
    t = print_dot()
    for i, vec in enumerate(argon2i_test_vectors):
        p = bytes.from_hex(vec['p'])
        s = bytes.from_hex(vec['s'])
        x = bytes.from_hex(vec['x'])
        k = bytes.from_hex(vec['k'])
        lanes = lanes_t(vec['lanes'])
        t_len = t_len_t(vec['t_len'])
        m = size_nat_t(nat(vec['m']))
        iterations = size_nat_t(nat(vec['iterations']))
        expected = bytes.from_hex(vec['output'])
        computed = argon2i(p,s,lanes,t_len,m,iterations,x,k)
        # computed = array([])
        if computed == expected:
            print("Argon2i Test {} passed.".format(i+1))
            exit(0, t)
        else:
            print("Argon2i Test {} failed.".format(i+1))
            print("expected hash:",bytes.to_hex(expected))
            print("computed hash:",bytes.to_hex(computed))
            exit(1, t)


if __name__ == "__main__":
    main()
