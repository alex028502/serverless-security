import sys

from os.path import abspath

assert abspath(sys.argv[1]) == abspath(sys.argv[2]), sys.argv[1:3]
