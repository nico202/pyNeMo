#!/usr/bin/python2
#Simulation
import nemo
import random
import time

#Config
import os
import imp #import the network config
import general_config

#Various
from sys import argv, exit

from InAndOut import *

if __name__ == "__main__":
    # Load user-defined config file
    try:
        config_name = argv[1]
        config = imp.load_source('*', config_name)
        script_dir = os.getcwd()
    except SyntaxError:
        exit("Config file: Syntax Error")
    except IndexError:
        print("You must provide a config file!")
        exit("Usage: %s network.py" % (argv[0]))
    except:
        print("DEBUG: Unknown error")
        raise

    #"--force" argument. Disable computation bypass
    try:
        force_run = argv[2]
        if force_run == "--force":
            force_run = True
        else:
            force_run = False
    except:
        force_run = False

    start = 0.0; end = 0.0 #Initialize it here to enable bypass
    bypass = False
    if startup_check(general_config._history_dir):
        os.chdir(general_config._history_dir)
        config_key, config_hash = hashIt(config)
        general_config_key, general_config_hash = hashIt(general_config)
        history = open("history.log", 'a')
        history.write("%f, %s, %s, %s, " % (time.time(),
                                            "GPU" if general_config._GPU else "CPU",
                                            general_config_hash,
                                            config_hash))
        history.close()

        #If any of the following False, we can bypass the computation and print previously-saved run
        if not any([
            saveKey(general_config_hash, general_config_key),
            saveKey(config_hash, config_key),
            saveFile(script_dir + '/' + "general_config.py", general_config_hash),
            saveFile(script_dir + '/' + config_name, config_hash), #TODO: FIX this.
            not os.path.isfile('./.' + general_config_hash + config_hash)
        ]):
            old_output = '.' + general_config_hash + config_hash
            if general_config._OUTPUT:
                print open(old_output, 'r').readlines()
            else:
                print("Simulation has previously been executed!")
                print("Watch the file %s" % (general_config._history_dir + '/' + old_output))
                bypass = True and not force_run

    if not bypass:
        net = nemo.Network()
        iz = net.add_neuron_type('Izhikevich')
        nemo_config = nemo.Configuration()

        #TODO: for small networks, cpu is faster, use it (if config permits)
        if general_config._GPU:
            try:
                nemo_config.set_cuda_backend(general_config._BACKEND_NUMBER)
            except RuntimeError:
                print("No CUDA-GPU found: using CPU instead")
                nemo_config.set_cpu_backend()
        else:
            nemo_config.set_cpu_backend()
        # Neurons
        neuron_list = config.neurons[0]
        for nidx in range(len(neuron_list)):
            a, b, c, d, s, u, v = neuron_list[nidx]
            net.add_neuron(iz, nidx, a, b, c, d, s, u, v)

        #Synapses
        for sidx in range(len(config.synapses)):
            source, dests, synaptic_prop = config.synapses[sidx]
            delay, weights, plastic = synaptic_prop
            try: #dests is a single value or a list?
                dests = int(dests)
                dests = [ dests ]
            except TypeError:
                pass

            try: #if weight length is 1, apply it to all synapses
                weights = int(weights)
                weights = [ weights ]
            except TypeError: #Already an array
                pass

            if ( len(weights) != len(dests) ):
                if ( len(weights) == 1 ):
                    #List of weight matching number of outpu nurons
                    weights = weights * len(dests)
                else:
                    exit("Malformed synapse line %d" % (sidx + 1))

            net.add_synapse(source, dests, delay, weights, plastic);

        conf = nemo.Configuration()
        sim = nemo.Simulation(net, conf)

        start = time.time()

        t = general_config.steps or -1 #if == 0, run indefinitely
        tot = t

        output_firings = {}
        membrane_output = {}

        if general_config._OUTPUT: #I keep them separate to reduce the overhead
            while not t == 0:
                general_config.steps
                fired = sim.step()
                t -= 1
                if (t < 0):
                    T = abs(t)
                else:
                    T = tot - t
                print T, ":", fired
        else:
            try:
                to_save = config.save
            except:
                to_save = []
            for i in to_save:
                membrane_output[i] = [] #We save the dict containing neurons_Vm
            if to_save: #Every optimization here matters
                while not t == 0:
                    fired = sim.step()
                    for neuron in to_save: #Save membrane potential
                        membrane_output[neuron].append(sim.get_membrane_potential(neuron))
                    output_firings[t] = [ i for i in fired ]
                    t -= 1
            else:
                while not t == 0:
                    general_config.steps
                    fired = sim.step()
                    output_firings[t] = [ i for i in fired ]
                    t -= 1
        end = time.time()

        #TODO: if this is slow for big networks, replace with pickle
        saveKey(general_config_hash + config_hash, output_firings)
        saveKey(general_config_hash + config_hash + '_membrane', membrane_output)

    total_time = end - start
    step_time = total_time / general_config.steps
    history = open("history.log", 'a') #Update the history with results timing
    history.write("%f, %f\n" % (total_time, step_time))
    history.close()

    #Debug stats
    if general_config._DEBUG:
        print("DEBUG: total_time = %f" % (total_time))
        print("DEBUG: step_time = %f" % (step_time))
