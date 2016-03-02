#!/usr/bin/env python2
import subprocess
import numpy as np
import time
import os

import re
import string

from libs.IO import is_folder, hashDict
import config

from sys import argv, exit

print ("\n\n\n\n\n\n\n----------------")

name = False

python = "python" #Python command

new_args = []
for a in argv:
    if not "-" in a:
        a = '\'%s\'' % a
    new_args.append(a)

#Get the output dir, or set it to batch if none defined
if not "--history-dir" in argv:
    argv.append("--history-dir")
    argv.append("batch")
else:
    output_dir = argv[argv.index("--history-dir")+1]

def ask(msg, exit_msg =  "Change your cli params then!", sure = "Are you sure? [y/n]"):
    from sys import exit
    action = "z"
    while action.capitalize() not in ["Y","N"]:
        action = raw_input(msg + "\n" + sure +": ")
        if action.capitalize() == "Y":
            break
        else:
            exit(exit_msg)
    
if (
        config.BATCH_CONFIRM_NO_SAVE_IMAGE
        and not "--save-spikes" in argv
):
    ask("You are not saving the spikes image.")

if (
        config.BATCH_CONFIRM_SHOW_IMAGE
        and all([
            not "--no-show-membrane" in argv or not "--no-show-spikes" in argv
            , not "--no-show-images" in argv
])):
    ask("You are showing images", "Use \"--no-show-images\" and run the batch again")

exit()
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

#TODO:
#Save "real_commands" hash to file + iter number (every 10?)
#to allow loop recovery for long loops
session_hash = hashDict(real_commands)


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

#subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
