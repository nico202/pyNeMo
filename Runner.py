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
import argparse
from sys import exit, stderr

from libs.InAndOut import *

if __name__ == "__main__":
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            if message == "too few arguments":
                message = "You must provide a network file!"
            stderr.write('error: %s\n' % message)
            self.print_help()
            exit(2)

    parser = MyParser(description='Run NeMo simulations')
    parser.add_argument('network_file', help = 'Network file to use')
    parser.add_argument('--force',
        action = 'store_true',
        help = 'Bypass previously computed simulation; run it again (debugging)',
        dest = 'force_run')
    parser.add_argument('--steps',
        help = 'Steps to run. Default loaded in general config\nDefault ms. Can use s and m (ie. 10s, 3m)',
        dest = 'steps')

    processing = parser.add_mutually_exclusive_group()
    processing.add_argument('--gpu',
        action='store_true',
        help = 'Overwrite config GPU settings (force GPU)',
        dest = 'GPU',
        default = None
    )
    processing.add_argument('--cpu',
        action='store_false',
        help = 'Overwrite config GPU settings (force CPU)',
        dest = 'GPU'
    )

    images = parser.add_mutually_exclusive_group()
    images.add_argument( '--show-all',
        action= 'store_true',
        help = 'Force show saved images',
        dest = 'SHOW_ALL'
    )
    images.add_argument( '--spikes-only',
        action= 'store_true',
        help = 'Show spikes image only',
        dest = 'SHOW_SPIKES_ONLY'
    )
    images.add_argument( '--show-none',
        action= 'store_false',
        help = 'Don\'t show images upon creation. Useful for batch',
        dest = 'SHOW_IMAGE'
    )

    args = parser.parse_args()
    config_name, force_run, steps = args.network_file, args.force_run, args.steps

    if steps:
        try:
            if 'm' in steps:
                steps = int(steps.strip('m')) * 60 * 1000
            elif 's' in steps:
                steps = int(steps.strip('s')) * 1000
        except ValueError:
            exit("Steps parameter can contain either 'm' (minutes) or 's' (seconds)")
        general_config.steps = int(steps)

    # Load user-defined config file
    try:
        config = imp.load_source('*', config_name)
        script_dir = os.getcwd()
    except SyntaxError:
        exit("Config file: Syntax Error")
    except:
        print("DEBUG: Unknown error")
        raise

    try:
        net_name = config.name
    except AttributeError:
        print("Having a name in the network will be mandatory in the first version. Fix it NOW")

    start = 0.0; end = 0.0 #Initialize it here to enable bypass
    bypass = False
    if startup_check(general_config._history_dir):
        os.chdir(general_config._history_dir)
        config_key, config_hash = hashIt(config)
        general_config_key, general_config_hash = hashIt(general_config)

        #If any of the following False, we can bypass the computation and print previously-saved run
        if not force_run:
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
                    loaded_img = importer(old_output)
                    saveSourceImage(loaded_img, old_output + ".png")
                    showSourceImage(old_output + ".png")
                bypass = True and not force_run
        if args.GPU == None:
            GPU = general_config._GPU
        else:
            GPU = args.GPU

    if not bypass:
        net = nemo.Network()
        iz = net.add_neuron_type('Izhikevich')
        nemo_config = nemo.Configuration()

        #TODO: for small networks, cpu is faster, use it (if config permits)
        if general_config._GPU:
            try:
                nemo_config.set_cuda_backend(general_config._BACKEND_NUMBER)
                GPU = True
            except RuntimeError:
                print("No CUDA-GPU found: using CPU instead")
                GPU = False
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
            net.add_synapse(source, dests, delay, weights, plastic)

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
        #Save spiking:
        saveSourceImage(output_firings, '.' + general_config_hash + config_hash + '.png')
        for neuron in to_save:
            saveRawImage(membraneImage(membrane_output[neuron]),
                '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')
        for neuron in to_save:
            saveRawImage(membraneImage(membrane_output[neuron], close = False),
                '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '_Mixed.png', close = False)


        print("Output file is: %s" % (general_config._history_dir + '/' + '.' + general_config_hash + config_hash))
        #Show spiking:
        if general_config._SHOW_IMAGE_ON_SAVE or args.SHOW_ALL or args.SHOW_SPIKES_ONLY:
            if general_config._SHOW_SPIKES or args.SHOW_SPIKES_ONLY or args.SHOW_ALL:
                showSourceImage("." + general_config_hash + config_hash + '.png')
            if general_config._SHOW_MEMBRANE or args.SHOW_ALL:
                for neuron in to_save:
                    showSourceImage('.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')

    total_time = end - start
    step_time = total_time / general_config.steps
    history = open("history.log", 'a') #Update the history with results timing
    history.write("%f, %s, %s, %s %f, %f\n" % (time.time(),
                                        "GPU" if GPU else "CPU",
                                        general_config_hash,
                                        config_hash,
                                        total_time,
                                        step_time))
    history.close()
    #Debug stats
    if general_config._DEBUG:
        print("DEBUG: total_time = %f" % (total_time))
        print("DEBUG: step_time = %f" % (step_time))
