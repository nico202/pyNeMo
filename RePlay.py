#!/bin/python2
#Compatible with python3
#Load config, history
from general_config import _history_dir, commit_version
from sys import exit

import time, datetime
from InAndOut import importer
#Load history
try:
    history = [ #Makes a list of lists of every runned sim
        line.strip().replace(",", "").split() for line in
        open(_history_dir + '/history.log', 'r').readlines() ]

except IOError:
    exit("History file missing!?")

#_history_dir, commit_version

now = time.time(); results = False
n = 0
used_hash = {"config":[], "general":[]}
mapping = {}
for sim_hist in history:
    if sim_hist[2] not in used_hash["general"]:
        used_hash["config"].append(sim_hist[2])
    elif sim_hist[3] not in used_hash["config"]:
        used_hash["general"].append(sim_hist[2])
    else:
        n += 1
        break
    general_config_name, config_name = sim_hist[2:4]
    membrane_file = _history_dir + '/.' + general_config_name + config_name
    general_config_file = _history_dir + '/.' + general_config_name
    config_file = _history_dir + '/.' + config_name

    #Import configs
    config = importer(config_file)
    general_config = importer(general_config_file)
    commit_version, steps = general_config["commit_version"], general_config["steps"]
    neurons = config["neurons"][0]
    synapse_number = len([
        b for sub in [s[1] for s in config["synapses"]] for b in sub
    ])

    if float(sim_hist[0]) + 10000 > now:
        results = True
        print("[%s] %s, steps = %d, # of neurons: %d, # of synapses: %d" % (
            n,
            datetime.datetime.fromtimestamp(int(float(sim_hist[0]))).strftime('%Y-%m-%d %H:%M:%S'),
            steps,
            len(neurons),
            synapse_number
            )
        )
        n += 1
if results:
    choose = int(input("Which one?: "))
    print(history[choose])
else:
    print("No result for defined criteria")
