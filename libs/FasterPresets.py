#!/bin/python2
from random import random

#On function defined here, the "_" is mandatory

def _typicalN( #DO NOT TOUCH
    a = 0.02,   # time scale of recovery variable (u)
    b = 0.2,    # sensitivity of recovery variable (u) on subtreshold
    c = -65,    # after-spike reset value
    d = 2,      # after-spike recovery variable (u)
    s = 3,      # input bias picked from gaussian [0, s)
    u = False,  # default calculated down here
    v = -65     # Initial membrane potential
    ):
    if not u:
        u = b * v
    return [(a, b, c, d, s, u, v)]

def _typicalS (d = 1, w = 10, l = False): #TODO: not tested
    #return fixing unsupported values
    return [(d if d >= 1 else 1, w, True if l else False)]
