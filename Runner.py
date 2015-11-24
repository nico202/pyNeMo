import nemo
import random
import time

import os

import general_config
import hashlib          #We use it to check different configurations

from sys import argv, exit

#those can be exported to a module for future use
def startup_check(output_dir = ".store"):
    if not os.path.isdir(output_dir):
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except:
                exit("Unknown error creating folder")
            return True
        else:
            exit("Destination must be a folder! Check your config")
    else:
        return True

def hashIt(module): #We use this to check if configuration changed
    key_string = str({key: value for key, value in module.__dict__.iteritems()
        if not (key.startswith('__') or key.startswith('_'))})

    return key_string, hashlib.sha1(key_string).hexdigest()

def saveKey(name, values):
    output_name = '.' + name
    if not os.path.isfile(output_name):
        try:
            output = open(output_name, 'a')
            output.write(values)
            output.close()
        except:
            exit("Probem writing file?! DEBUG me")
    return True


if __name__ == "__main__":
    # Load user-defined config file
    try:
        config = argv[1]
        config = __import__(config.split(".")[0])
    except SyntaxError:
        exit("Config file: Syntax Error")
    except:
        exit("You must provide a config file!")

    if startup_check(general_config.history_dir):
        os.chdir(general_config.history_dir)
        config_key, config_hash = hashIt(config)
        general_config_key, general_config_hash = hashIt(general_config)
        history = open("history.log", 'a')
        history.write("%f, %s, %s\n" % (time.time(), general_config_hash, config_hash))
        history.close()

        if (general_config.DEBUG and
        saveKey(general_config_hash, general_config_key)
        and saveKey(config_hash, config_key)):
            print ("DEBUG: config has been saved")



    #TODO: create an array of all the config. Hash it and save it.

    net = nemo.Network()
    iz = net.add_neuron_type('Izhikevich')

    # Neurons
    for nidx in range(len(config.neurons)):
        a, b, c, d = config.neurons[nidx]
        net.add_neuron(iz, nidx, a, b, c, d, 5.0, 0.2*c, c);

    #Synapses
    for sidx in range(len(config.synapses)):
        source, dests, learning, weights, boh = config.synapses[sidx]
        try: #dests is a single value or a list?
            dests = int(dests)
            dests = [ dests ]
        except TypeError:
            pass

        try: #if weight length is 1, apply it to all synapses
            weights = int(weights)
            weights = [ weights ]
        except TypeError:
            pass

        if ( len(weights) != len(dests) ):
            if ( len(weights) == 1 ):
                weights = weights * len(dests)
            else:
                exit("Malformed synapse line %d" % (sidx + 1))

        net.add_synapse(source, dests, 1, weights, False);

    conf = nemo.Configuration()
    sim = nemo.Simulation(net, conf)

    start = time.time()
    t = general_config.steps or -1 #if == 0, run indefinitely
    tot = t

    if general_config.OUTPUT: #I keep them separate to reduce the overhead
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
        while not t == 0:
            general_config.steps
            fired = sim.step()
            t -= 1

    end = time.time()

    print("DEBUG: total_time = %f" % (end - start))
    print("DEBUG: step_time = %f" % ((end - start) / general_config.steps))
