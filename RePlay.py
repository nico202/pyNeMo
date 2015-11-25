#!/bin/python2

#Load config, history
from general_config import _history_dir, commit_version
from sys import exit

import time

#Load history
try:
    history = [ #Makes a list of lists of every runned sim
        line.strip().replace(",", "").split() for line in
        open(_history_dir + '/history.log', 'r').readlines() ]

except IOError:
    exit("History file missing!?")

#_history_dir, commit_version

now = time.time()
for sim_hist in history:
    if sim_hist[0] > now + 1000:
        print sim_hist
