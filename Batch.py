#!/usr/bin/env python2
import subprocess
import numpy as np
import time
import os

import re
import string

from libs.IO import is_folder
from sys import argv, exit

print ("\n\n\n\n\n\n\n----------------")

name = False

python = "python" #Python command

new_args = []
for a in argv:
    if not "-" in a:
        a = '\'%s\'' % a
    new_args.append(a)

args = " ".join(new_args[1:])

commands = []

ranges = True

def missing(input_string):
    ranges = re.findall("\[(.*?)\]", input_string)
    return ranges

def substituteRanges(input_strings, commands):
    if not commands:
        commands = []
    for input_string in input_strings:
        ranges = missing(input_string)
        if ranges:
            r = ranges[0]
            start, stop, step = [float(n) for n in r.split(',')]
            steps = np.arange (start, stop, step)
            for s in steps:
                command = string.replace(input_string, "["+r+"]", str(s))
                commands.append(command)
        else:
            return commands

    return substituteRanges(commands, commands)

commands = substituteRanges([args], [])
real_commands = [ i for i in commands if not missing(i) ]

#Start
is_folder ("batch")
if not name:
    unique_id = time.time()
else:
    unique_id = name

output_dir = "batch/" + str(unique_id)

is_folder (output_dir)

print("We'll use %s as output dir" % (output_dir))

#Let's run the simulations (surely not the best way, but does the job)
start = time.time()

lap = 0

for com in real_commands:
    lap_start = time.time()
    subprocess.call("%s Runner.py %s" % (python, com), shell = True)
    lap_end = time.time()
    cycle_time = lap_end - lap_start
    lap +=1

end = time.time()

subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
