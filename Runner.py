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
from libs.simulation import *
import libs.VUEtoPy as VUEtoPy

#YARP and "iSpike" helpers
import libs.pYARP
import libs.pySpike

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
    parser.add_argument('--output-dir',
        help = 'Override config-defined output dir',
        dest = 'forced_output')
    parser.add_argument('--disable-sensory',
        action = 'store_true',
        help = 'Disable all the sensory neurons (force not to use gazebo)',
        dest = 'disable_sensory',
        default = False
    )
    saving = parser.add_mutually_exclusive_group()
    saving.add_argument('--save-all',
        action = 'store_true',
        help = 'Save all neurons (override config)',
        dest = 'save_all',
        default = False)
    saving.add_argument('--save-none',
        action = 'store_true',
        help = 'Don\'t save membrane potential (override config). Faster',
        dest = 'save_none',
        default = False)
    parser.add_argument('--replace-variables',
        help = '''Fast change variables marked with %% Use --replace-help for other infos''',
        dest = 'replaced'
    )
    parser.add_argument('--replace-help',
        action = 'store_true',
        help = '''Show replace-variables usage and exit.''',
        dest = 'replace_help'
    )
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
    images.add_argument( '--membrane-only',
        action= 'store_true',
        help = 'Show membrane potential onlt',
        dest = 'SHOW_MEMBRANE_ONLY'
    )
    parser.add_argument('--analyze',
        action = 'store_true',
        help = 'Run all available analysis at the end of the simulation')

    args = parser.parse_args()
    config_name, force_run, steps, save_all, save_none, disable_sensory\
  = args.network_file, args.force_run, args.steps, args.save_all,\
   args.save_none, args.disable_sensory
    if args.replace_help:
        '''Well... I don't know how to implement this right now.
        (config file is imported with "import". )'''
        exit('''--replace-variables can be used to replace any value
        that gets evaluated in the config file. Those values must be marked with
        % (ie. %VAR_A%) and can be replaced here (ie. with: VAR_A=0.02,VAR_B=0.2)''')

    if steps:
        try:
            if 'm' in steps:
                steps = float(steps.strip('m')) * 60 * 1000
            elif 's' in steps:
                steps = float(steps.strip('s')) * 1000
        except ValueError:
            exit("Steps parameter can contain either 'm' (minutes) or 's' (seconds)")
        general_config.steps = int(steps)

    # Load user-defined config file
    if ".vue" in config_name:
        print("Converting input VUE to py")
        VUEtoPy.VUEtoPyConverter(config_name)
        config_name = "".join((config_name.split(".")[:-1]))
        config_name += ".py"
    try:
        config = imp.load_source('*', config_name)
        script_dir = os.getcwd()
    except SyntaxError:
        print("Config file: Syntax Error")
        raise
    except:
        print("DEBUG: Unknown error")
        raise

    if save_all:
        config.save = range(0, len(config.neurons[0]))
    elif save_none:
        config.save = []

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
        if disable_sensory:
            config.sensory_neurons = [[], []]
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
                #Show spiking: #FIX
                if general_config._SHOW_IMAGE_ON_SAVE or args.SHOW_ALL or args.SHOW_SPIKES_ONLY:
                    if general_config._SHOW_SPIKES or args.SHOW_SPIKES_ONLY or args.SHOW_ALL:
                        loaded_img = importer(old_output)
                        showSourceImage("." + general_config_hash + config_hash + '.png')
                    #FIXME: fix the following, to save is not defined. Where to read all?
                    #if general_config._SHOW_MEMBRANE or args.SHOW_ALL:
                    #    for neuron in to_save:
                    #        loaded_img = importer(old_output + '_membrane' + str(neuron) + '.png')
                    #        showSourceImage(loaded_img)

            bypass = True and not force_run
        if args.GPU == None:
            GPU = general_config._GPU
        else:
            GPU = args.GPU

    if not bypass:
        net = nemo.Network()
        iz = net.add_neuron_type('Izhikevich')
        #km = net.add_neuron_type('Kuramoto')

        nemo_config = nemo.Configuration()

        #TODO: for small networks, cpu is faster, use it (if config permits)
        if GPU:
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
            except TypeError: #Is already a list :)
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

        sensory_neuron_list = config.sensory_neurons

        #create the array of neuron that get passed to pySpike/pYARP
        sensory_neurons_map_in = []
        count = 0
        for sensory_array_in in sensory_neuron_list[0]: #for every input
            sensory_neurons_map_in.append({})
            n_number = sensory_array_in[0]
            a, b, c, d, s, u, v = sensory_array_in[2][0]
            for nn in range(0, n_number):
                nidx +=1
                net.add_neuron(iz, nidx, a, b, c, d, s, u, v)
                dest = sensory_array_in[3]
                delay, weights, plastic = sensory_array_in[4]
                net.add_synapse(nidx, dests, delay, weights, plastic)
                sensory_neurons_map_in[count][nidx] =  nn
            count += 1

        nsens_port_map = []
        for sensory_array_out in sensory_neuron_list[1]:
            port_name = sensory_array_out[0]
            out_dof = sensory_array_out[1]
            sens_conn_out = sensory_array_out[2]
            n_number = len(sens_conn_out)
            #TODO: add other params needed
            nsens_port_map.append([port_name, out_dof, sens_conn_out])

        conf = nemo.Configuration()
        sim = nemo.Simulation(net, conf)

        start = time.time()

        to_save = config.save
        output_firings, membrane_output, config.step_input, angles =\
        simulation(
            Nsim = sim,
            save = to_save,
            steps = general_config.steps,
            stims = config.step_input,
            fspikes = config.step_spike,
            sensory_in = sensory_neurons_map_in,
            sensory_out = nsens_port_map
        ) #Returns step_input too, cause it can be edited by the yarp interaction

        end = time.time()

        #TODO: if this is slow for big networks, replace with pickle
        saveKey(general_config_hash + config_hash, output_firings)
        saveKey(general_config_hash + config_hash + '_membrane', membrane_output)
        #Save spiking:
        saveSourceImage(output_firings, '.' + general_config_hash + config_hash + '.png')
        for neuron in to_save:
            stims = []
            n = 0
            for n in range(0, general_config.steps):
                if n in config.step_input:
                    found = False
                    for s in config.step_input[n]:
                        if s[0] == neuron:
                            stims.append(s[1])
                            found = True
                    if not found:
                        stims.append(0)
                else:
                    stims.append(0)

            saveRawImage(membraneImage((membrane_output[neuron], stims), title = config.name + ' - neuron ' + str(neuron)),
                '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')
        for neuron in to_save:
            saveRawImage(membraneImage((membrane_output[neuron], stims), close = False, title = config.name),
                '.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '_Mixed.png', close = False)
        #TODO: add "angles" (is a list of lists of angles for every sensory neuron)
        saveKey(general_config_hash + config_hash + '_angles', angles)
        print("Output file is: %s" % (general_config._history_dir + '/' + '.' + general_config_hash + config_hash))
        #Show spiking:
        if general_config._SHOW_IMAGE_ON_SAVE or args.SHOW_ALL or args.SHOW_SPIKES_ONLY or args.SHOW_MEMBRANE_ONLY:
            if (general_config._SHOW_SPIKES or args.SHOW_SPIKES_ONLY or args.SHOW_ALL) and not args.SHOW_MEMBRANE_ONLY:
                showSourceImage("." + general_config_hash + config_hash + '.png')
            if general_config._SHOW_MEMBRANE or args.SHOW_ALL or args.SHOW_MEMBRANE_ONLY:
                for neuron in to_save:
                    showSourceImage('.' + general_config_hash + config_hash + '_membrane' + str(neuron) + '.png')

    total_time = end - start
    step_time = total_time / general_config.steps
    history = open("history.log", 'a') #Update the history with results timing
    history.write("%f, %s, %s, %s, %f, %f\n" % (time.time(),
                                        "GPU" if GPU else "CPU",
                                        general_config_hash,
                                        config_hash,
                                        total_time,
                                        step_time))
    history.close()
    print("Run Analysis with: python Analyze.py --general-hash %s --config-hash %s --all" % (general_config_hash, config_hash))
    #Debug stats
    if general_config._DEBUG:
        print("DEBUG: total_time = %f" % (total_time))
        print("DEBUG: step_time = %f" % (step_time))
    if args.analyze:
        import subprocess
        subprocess.call("cd %s; python Analyze.py --general-hash %s --config-hash %s --all" % (script_dir, general_config_hash, config_hash), shell = True)
