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
    if not "--" in a:
        a = '\'%s\'' % a
    new_args.append(a)

#Get the output dir, or set it to batch if none defined
output_dir = "batch"
if not "--history-dir" in new_args:
    new_args.append("--history-dir")
    new_args.append(output_dir)
else:
    output_dir = new_args[new_args.index("--history-dir")+1]
if "'" in output_dir:
    output_dir = string.replace(output_dir,"'", "")
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

#fix parentheses:
real_commands = [ i for i in commands if not missing(i) ]
#set just to be sure no duplicate runs
real_commands = set(real_commands)


#TODO:
#Save "real_commands" hash to file + iter number (every 10?)
#to allow loop recovery for long loops
#FIXME: remove "--show-image" etc to prevent different hashes of same config
session_hash = hashDict(real_commands)


#Start
is_folder (output_dir)

print("We'll use %s as output dir" % (output_dir))

#Let's run the simulations (surely not the best way, but does the job)
#TODO: add the loop inside Runner?
start = time.time()
try:
    run = import_history(output_dir + "/" + session_hash + "_batch")
    recover_from_lap = run["cycle"]
    print("You already run this sym, recovering from %s"
          % (recover_from_lap))
except IOError:
    print("First time you run this exact sim")
    recover_from_lap = 0
    pass

last_save_time = time.time()
next_sleep = False
forced_quit = False
lap = 0
laps = len(real_commands)
print ("We are going to run %s simulations!" % (laps))
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
            now = time.time()
            time_diff = now - last_save_time
            last_save_time = now
            print "\n\n\n-----------------------------------\n\n\n\nSAVING\n\n\n"
            print("This round mean step time: %s" % (time_diff / config.BATCH_SAVE_EVERY))
            write_batch_log(str(session_hash) + "_batch", lap, output_dir)
            print "-------------------"
    except KeyboardInterrupt:
        if not forced_quit:
            write_batch_log(session_hash, lap, output_dir)
            next_sleep = True
            print ("Forced saving! Press CTRL-C again (on cue) to quit")
        else:
            #save 2 lap less to be sure sims have not been interrupted
            write_batch_log(str(session_hash) + "_batch", lap - 2, output_dir)

            exit("Forced QUIT")

print("Batch runned successfully!")
end = time.time()

#subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
