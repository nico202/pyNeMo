#!/usr/bin/env python2
import subprocess
import numpy as np
import time
import os

import re
import string

from libs.runParser import parse_args

from libs.IO import is_folder, hashDict, write_batch_log, saveKey
from libs.IO import cprint
from plugins.importer import import_history
import config

from sys import argv, exit

from libs.simulations import main_simulation_run
from libs.IO import import_network

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
            cprint(exit_msg, 'warning')
            exit()
    
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

#Save args to file
l = open("batch_history.log", 'a')
l.write("%s, %s" % (output_dir, args))
l.close()

ranges = True
def missing(input_string):
    #TODO: check [ number + , + number + , + number ]
    ranges = re.findall("\[(.*?)\]", input_string)
    if ranges:
        return ranges[0]
    else:
        return False

def substituteRanges(input_strings, commands):
    if not commands:
        commands = []
    for input_string in input_strings:
        ranges = missing(input_string)
        if ranges:
            start, stop, step = [float(n) for n in ranges.split(',')]
            steps = np.linspace (start, stop, (abs(stop-start)/step)+1)
            for s in steps:
                command = string.replace(input_string, "["+ranges+"]", str(s))
                commands.append(command)
        else:
            commands.append(input_string)
            return commands

    return substituteRanges(commands, commands)

commands = substituteRanges([args], [])

#fix parentheses:
commands = [ i for i in commands if not missing(i) ]

#set just to be sure no duplicate runs
real_commands = set(commands)

#TODO:
#FIXME: remove "--show-image" etc to prevent different hashes of same config
session_hash = str(hashDict(real_commands))

#Save commands list
is_folder("./commands")
commands_file = "./commands/" + session_hash + "_commands"
cprint ("Saving %s commands to file: %s" % (len(real_commands), commands_file), 'info')
saveKey(commands_file, commands)
cprint("Running in 5s", "warning")
time.sleep(5)

#Start
is_folder (output_dir)

cprint("We'll use %s as output dir" % (output_dir), 'info')

#Let's run the simulations (surely not the best way, but does the job)
#TODO: add the loop inside Runner?
start = time.time()
try:
    run = import_history(output_dir + "/" + session_hash + "_batch")
    recover_from_lap = run["cycle"]
    cprint("You already run this sym, recovering from %s"
           % (recover_from_lap), 'okblue')
except IOError:
    print("First time you run this exact sim")
    recover_from_lap = 0
    pass

last_save_time = time.time()
start_time = last_save_time
next_sleep = False
forced_quit = False
lap = 0
laps = len(real_commands)
cprint ("We are going to run %s simulations!" % (laps), 'okblue')

for com in real_commands:
    try:
        if lap < recover_from_lap:
            lap += 1
            continue
        if next_sleep:
            forced_quit = True
            cprint("Press CTRL-C NOW! (trice) to quit", 'warning')
            time.sleep(5)
            forced_quit = False
            next_sleep = False
        #Start. Take time
        start_time = time.time()
        print ("Lap %s / %s" % (lap , laps))
        ##Replace subprocess: call it directly to save time
        parser = parse_args()
        args = parser.parse_args(com.split()) #That way is 100% compatible with the old os call
        
        #Load all the parameters (choose if/when read from CLI/config.py)
        use_config = True if os.path.isfile("config.py") else False
        if use_config: import config
        
        network_file = args.network_file.strip("'")

        config_steps = config.STEPS if use_config else 0
        steps = time_to_steps(args.steps) if args.steps != None else config_steps
        
        config_history = config.HISTORY_DIR if use_config else 0
        output_dir = args.history_dir or config_history
        
        config_cuda = config.TRY_CUDA if use_config else 0
        use_cuda = args.use_cuda if args.use_cuda != None else config_cuda
        
        config_cuda_backend = config.CUDA_BACKEND if use_config else 0
        cuda_backend = args.cuda_backend or config_cuda_backend
        try:
            cuda_backend = int(cuda_backend)
        except ValueError:
            exit("Error, wrong cuda_backend format. Must be a int")
            
        vue_prehook = args.vue_prehook
        vue_posthook = args.vue_posthook
            
        #Robot args
        control_robot = args.control_robot
        robot_mode = args.robot_mode #FIXME
        
        disable_sensory = args.disable_sensory
        
        ########################################

        #L1
        networks, config_file_name =\
                import_network (
                    (network_file, (vue_prehook, vue_posthook))
                    , (use_cuda, cuda_backend)
                    , (disable_sensory))

        #L1
        nemo_simulation = networks[0]
        to_save = networks[1][0]
        neuron_number = networks[1][1]
        stimuli_dict = networks[1][2]
        
        #L2
        if (sensory_neurons_in or sensory_neurons_out):
            from libs.pYARP import RobotYARP #Import only if strictly needed
            robot = RobotYARP ()
        else:
            robot = None

        #L3
        if not disable_sensory: #CLI
            sensory_neurons_in, sensory_neurons_out  = networks[1][3]
        else:
            sensory_neurons_in = []
            sensory_neurons_out = []

        output = main_simulation_run(
            {
                "steps": steps
                , "use_cuda": use_cuda
                , "cuda_backend": cuda_backend
            }#general_config
            , (nemo_simulation, (to_save, neuron_number), stimuli_dict) #L1
            , (robot) #L2
            , (sensory_neurons_in, sensory_neurons_out) #L3
        )

        general_config_out = {"steps": output["ran_steps"]} #Add various robot params
        #Save/process output + input
        uniqueId = hashDict(general_config_out)\
                   + "_" + hashDict(dict_config)
        
        #Step is included in the output
        saveKey(uniqueId + "_output", output, output_dir)
        
        #Save the log
        write_log(uniqueId, output_dir = output_dir)
        
        lap +=1
        #save only every X laps and on keyboard interrupt
        if not lap % config.BATCH_SAVE_EVERY:
            now = time.time()
            time_diff = now - last_save_time
            last_save_time = now
            cprint("\n\n\n-----------------------------------\n\n\n\nSAVING\n\n\n")
            cprint("This round mean step time: %s" % (time_diff / config.BATCH_SAVE_EVERY))
            write_batch_log(session_hash + "_batch", lap, output_dir)
            cprint("-------------------")
        else:
            end_time = time.time()
            cprint ("Realtime ratio: %sX" % (output["ran_steps"]/((start_time - end_time)*1000)), 'info')
        
    except KeyboardInterrupt:
        if not forced_quit:
            write_batch_log(session_hash + "_batch", lap, output_dir)
            next_sleep = True
            cprint ("Forced saving! Press CTRL-C again (on cue) to quit", 'warning')
        else:
            #save 2 lap less to be sure sims have not been interrupted
            write_batch_log(str(session_hash) + "_batch", lap - 2, output_dir)
            cprint("Forced QUIT", 'error')
            exit()

run_time = time.time() - start_time
cprint("Batch runned successfully in %s!" % (run_time), 'okgreen')
end = time.time()

#subprocess.call("notify-send 'pyNeMo' 'batch process ended!'", shell = True)
