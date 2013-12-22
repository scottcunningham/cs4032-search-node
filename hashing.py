#!/usr/bin/python2

from numpy import int32, asscalar
import warnings
warnings.simplefilter("ignore", RuntimeWarning)

def HashCode(input_string):
        code = int32(0)
        for char in input_string:
                code = (code * int32((31))) + int32(ord(char))
        return asscalar(abs(code))
