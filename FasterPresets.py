#!/bin/python2
from random import random

def typicalN( #DO NOT TOUCH
    a = 0.02,
    b = 0.2,
    c = -65,
    d = 2,
    u = False, #default calculated down here
    v = -65 #Don't know too
    ):
    if not u:
        u = b * v
    return [a, b, c, d, u, v]

def typicalS (d = 1, w = 10, l = False):
    #return fixing unsupported values
    return (d if d >= 1 else 1, w, True if l else False)
