#!/usr/bin/env python2
import subprocess
import numpy as np
import time
import os

import re
import string

from libs.IO import is_folder, hashDict, write_batch_log
from plugins.importer import import_history
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
output_dir = "batch"
if not "--history-dir" in new_args:
    new_args.append("--history-dir")
    new_args.append(output_dir)
else:
    output_dir = new_args[new_args.index("--history-dir")+1]

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
        and not "--save-spikes" in new_args
):
    ask("You are not saving the spikes image.")

if (
        config.BATCH_CONFIRM_SHOW_IMAGE
        and all([
            not "--no-show-membrane" in new_args or not "--no-show-spikes" in new_args
            , not "--no-show-images" in new_args
])):
    ask("You are showing images", "Use \"--no-show-images\" and run the batch again")

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
#set just to be sure no duplicate runs
real_commands = set([ i for i in commands if not missing(i) ])

#TODO:
#Save "real_commands" hash to file + iter number (every 10?)
#to allow loop recovery for long loops
session_hash = hashDict(real_commands)


#Start
is_folder (output_dir)

print("We'll use %s as output dir" % (output_dir))

#Let's run the simulations (surely not the best way, but does the job)
#TODO: add the loop inside Runner?
start = time.time()
try:
    run = import_history(output_dir + "/" + session_hash)
    recover_from_lap = run["cycle"]
    print("You already run this sym, recovering from %s"
          % (recover_from_lap))
except IOError:
    print("First time you run this exact sim")
    recover_from_lap = 0
    pass

next_sleep = False
forced_quit = False
lap = 0
laps = len(real_commands)
for com in real_commands:
    try:
        if lap < recover_from_lap:
            lap += 1
            continue
        if next_sleep:
            forced_quit = True
            print("Press CTRL-C NOW! (trice) to quit")
            time.sleep(5)
            forced_quit = False
            next_sleep = False
        print ("Lap %s / %s" % (lap , laps))
        subprocess.call("%s Runner.py %s" % (python, com), shell = True)
        lap +=1
        #save only every X laps and on keyboard interrupt
        if not lap % config.BATCH_SAVE_EVERY: 
            print "\n\n\n-----------------------------------\n\n\n\nSAVING\n\n\n"
            write_batch_log(session_hash, lap, output_dir)
            print "-------------------"
            print session_hash
            print lap
            print output_dir
    except KeyboardInterrupt:
        if not forced_quit:
            write_batch_log(session_hash, lap, output_dir)
            next_sleep = True
            print ("Forced saving! Press CTRL-C again (on cue) to quit")
        else:
            #save 2 lap less to be sure sims have not been interrupted
            write_batch_log(session_hash, lap - 2, output_dir)

            exit("Forced QUIT")

end = time.time()

#subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
