#!/usr/bin/env python2

import subprocess
import numpy as np
import time
import os
from libs.IO import is_folder
from sys import argv

#Net config
try:
    net = argv[1]
except IndexError:
    net = "nets/better2neurons.vue" #Must be a vue

name = "iterate_small_values_a-b20"

iterated_variable = "_stim_a"
simulation_steps = 10000
disable_sensory = True
show = "None"

#Batch config
min = 0
max = 12
step_size = 0.1


#Start
is_folder ("batch")
if not name:
    unique_id = time.time()
else:
    unique_id = name
output_dir = "batch/" + str(unique_id)
is_folder (output_dir)
print("We'll use %s as output dir" % (output_dir))

steps = np.arange (min, max, step_size)
print("I'm gonna run: %s symulations! Be prapared" % (len(steps)))

#Let's run the simulations (surely not the best way, but does the job)
start = time.time()

lap = 0
for value in steps:
    lap_start = time.time()
    subprocess.call("python Runner.py %s --steps %s --disable-sensory --vue-prehook '%s=%s' --no-show-images --history-dir %s" %
                    ( net, simulation_steps, iterated_variable, value, output_dir),
                    shell = True)
    lap_end = time.time()
    cycle_time = lap_end - lap_start
    lap +=1

end = time.time()

subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
