"""
This module defines various useful functions used for Input and Output
like loading the config file, checking dependencies, various conversions etc.
"""

#Transform input time to ms (steps):
#  example: 100 = 100 (ms)
#  example: 30s = 30000 (ms)
#  example: 10m = 600000 (ms)
def time_to_steps(input_time):
    try:
        if 'm' in input_time: #minutes
            steps = float(input_time.strip('m')) * 60 * 1000
        elif 's' in input_time: #Seconds
            steps = float(input_time.strip('s')) * 1000
        else:
            steps = input_time
    except ValueError:
        exit("Steps parameter can contain either 'm' (minutes) or 's' (seconds)")
    except TypeError:
        return None

    return int(steps)

#Dependency check: check if all required module are present
#(without actually importing them)
def dependency_check(modules):
    import imp
    for module in modules:
        try:
            imp.find_module(module)
            found = True
        except ImportError:
            found = False
        if not found:
            exit("Could not find required module: %s" % (module))

def load_network_file(network_file, hooks):
    import imp
    #Ultra-important. Prevent the creation of pyc files, that get imported by imp
    #... preventing the reload of the source, leading to wrong input -> wrong output
    #... in batch runs
    ###############################
    import sys
    sys.dont_write_bytecode = True
    ###############################
    try:
        config_name = try_load_vue(network_file, hooks)
        config = imp.load_source('*', config_name)
    except SyntaxError:
        cprint("Config file: Syntax Error", 'fail')
        raise
    except IOError:
        cprint("Error: network file (%s) does not exists" % (network_file), 'fail')
        exit()
    except NameError:
        cprint("This VUE contains undefined variables (is it for a batch?)", 'fail')
        raise
    except:
        cprint("DEBUG: Unknown error", 'fail')
        raise
    return config, config_name

def try_load_vue(config_name, hooks=("", "")): #FIXME: relative path etc
    if ".vue" in config_name:
        import libs.VUEtoPy as VUEtoPy
        #TODO: verbosity fix
        cprint("Converting input VUE to py", 'info')
        VUEtoPy.VUEtoPyConverter(config_name, hooks)
        config_name = "".join((config_name.split(".")[:-1]))
        config_name += ".py"
    return "./" + config_name

def import_network(
        (network_file, hooks),
        (use_cuda, cuda_backend_number),
        (disable_sensory) #FIXME: use this
):
    '''
    Pass the network file to load_network_file, then:
    * Add neurons and synapses to Nemo

    returns [ nemo_simulation, to_save ]
    '''
    network_config, network_name = load_network_file(network_file, hooks)

    import nemo
    nemo_net = nemo.Network()
    nemo_config = nemo.Configuration()

    nemo_select_backend(nemo_config, (use_cuda, cuda_backend_number))

    #Add network neurons
    nemo_add_neurons(nemo_net, network_config.neurons[0])

    #Add networks synapses
    nemo_add_synapses(nemo_net, network_config.synapses)

    #Create the simulation
    nemo_simulation = nemo.Simulation(nemo_net, nemo_config)

    return ([
        nemo_simulation, #0
        ( #1
            network_config.save,
            #Used to coninue numeration on sensor
            len(network_config.neurons[0]),
            network_config.step_input,
            network_config.sensory_neurons,
            network_config.neurons,
            network_config.synapses,
            network_config.name
        )
    ]), network_name

def nemo_add_neurons(net, neuron_list, start_id=0):
    iz = net.add_neuron_type('Izhikevich')
    #TODO: edit conifg file to allow this?
    #km = net.add_neuron_type('Kuramoto')
    for nidx, neuron in enumerate(neuron_list):
        n_id = nidx + start_id
        a, b, c, d, s, u, v = neuron
        net.add_neuron(iz, n_id, a, b, c, d, s, u, v)

def nemo_add_synapses(net, synaspes_list):
    for sidx, synapse in enumerate(synaspes_list):
        source, dests, synaptic_prop = synapse
        delay, weights, plastic = synaptic_prop
        try: #dests is a single value or a list?
            dests = int(dests)
            dests = [dests]
        except TypeError: #Is already a list :)
            pass

        try: #if weight length is 1, apply it to all synapses
            weights = int(weights)
            weights = [weights]
        except TypeError: #Already an array
            pass

        if len(weights) != len(dests):
            if len(weights) == 1:
                #List of weight matching number of outpu nurons
                weights = weights * len(dests)
            else:
                exit("Malformed synapse line %d" % (sidx + 1))

        net.add_synapse(source, dests, delay, weights, plastic)


def nemo_select_backend(
        nemo_config,
        (use_cuda, backend_number)
):
    if use_cuda:
        try:
            nemo_config.set_cuda_backend(backend_number)
        except RuntimeError:
            #FIXME: verbosity
            print "No CUDA-GPU found: using CPU instead"
            nemo_config.set_cpu_backend()
        else:
            nemo_config.set_cpu_backend()

def saveKey(filename,
            values,
            out_dir=".",
            compress=True,
            compress_format="gzip",
            force_write=False):
    '''
    Saves a dict to a file.
    If compress enabled, saves to gz (compress less then bz2 but faster)
    '''
    import os.path
    filename = str(filename)
    out_dir = str(out_dir)
    is_folder(out_dir)
    output_name = out_dir + '/' + filename
    values = str(values)
    if not os.path.isfile(output_name) or force_write:
        try:
            if compress:
                if compress_format in ["gzip", "gz"]:
                    import gzip
                    with gzip.open(output_name + ".gz", 'wb') as f:
                        f.write(values)
                elif compress_format in ["bzip2", "bzip", "bz2"]:
                    import bz2
                    file_out = bz2.BZ2File(output_name + ".bz2", 'wb')
                    try:
                        file_out.write(values)
                    finally:
                        file_out.close()
                    values = bz2.compress("%s" % values)
            else:
                output = open(output_name, 'w')
                output.write("%s" % values)
                output.close()
        except:
            print "Probem writing file?! DEBUG me"
            raise
        return True
    else:
        return False

def hashIt(module): #We use this to check if configuration changed
    import hashlib
    key_string = str({key: value for key, value in module.__dict__.iteritems()
                      if not (key.startswith('__') or key.startswith('_'))})

    return key_string, str(hashlib.sha1(key_string).hexdigest())

def hashDict(dictionary):
    import hashlib
    return str(hashlib.sha1(str(dictionary)).hexdigest())

def is_folder(output_dir=".store"):
    #FIXME: allow recursive creation
    import os.path
    output_dir = str(output_dir)
    if not os.path.isdir(output_dir):
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except:
                print "Unknown error creating folder"
                raise
            return True
        else:
            exit("Destination must be a folder! Check your config")
    else:
        return True

def write_log(uniqueId, output_dir="history", name="history.log"):
    import time
    history = open(output_dir + "/" + name, 'a') #Update the history
    history.write("%f, %s\n" % (time.time(), uniqueId))
    history.close()

def write_batch_log(sessionId, cycle, output_dir="batch"):
    print cycle, output_dir, sessionId
    save = {
        "cycle":cycle
    } #Do we need something else?
    saveKey(str(sessionId), save, output_dir, compress=False, force_write=True)

def membraneImage(values,
                  title=False,
                  close=True,
                  scales=None):
    """
        Output an image of the membrane potential from a list of Membrane values.
        zoom = (stretch_x, stretch_y) means the stretch that is applied to x and y axes
    """
    #https://docs.python.org/2/tutorial/controlflow.html#default-argument-values
    if not scales:
        scales = []
    #TODO: Add stimulation trace
    import matplotlib.pyplot as plt
    import numpy as np
    Vm_list = values
    if close:
        plt.clf()
        plt.cla()
    x = len(Vm_list)
    x = np.array(range(0, x))
    fig, ax1 = plt.subplots()
    ax1.plot(x, np.array(Vm_list))
    ax1.set_xlabel('time (ms)')
    ax1.set_ylabel('Membrane Potential\n(mV)')
    if title:
        plt.title(title)
    plt.show()
    return plt

#COLORS
_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}
LOWERCASE, UPPERCASE = 'x', 'X'
MAP = {0: "R", 1: "G", 2: "B"}
COLORS=[[ 0.08,  0.80,  0.3], [ 0.68531278,  0.89077202,0.47581724], [ 0.80060385,  0.5,  0.1], [ 0.85033402,0.51683594,  0.11595041], [ 0.69312674,  0.66558017,  0.19565276], [0.09279514,  0.29094335,  0.85578709], [ 0.12722716,  0.62390063,  0.6649016 ], [ 0.91393435,  0.40349173,  0.10641532], [ 0.75184848,  0.79743901,  0.52527901], [ 0.44535098,  0.97818332,  0.03139634], [ 0.57541834,  0.22390996,  0.92280031], [ 0.22892716,  0.24278792,  0.8204559 ], [ 0.19601175,  0.79459385,  0.48783126], [ 0.10710888,  0.30693979,  0.01899005], [ 0.35588286,  0.18795917,  0.14780942], [ 0.80756219,  0.56990641,  0.00645912], [ 0.65984658,  0.12283337,  0.78819321], [ 0.17601197,  0.78862402,  0.78049605], [ 0.57904688,  0.31030127,  0.65775516],[ 0.25918713,  0.40173477,  0.19886916]]

def rgb(triplet):
    return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]

def cprint(text, color="okblue", debug=False):
    colors = {
        'okblue': '\033[94m',
        'info': '\033[94m',
        'okgreen': '\033[92m',
        'endc': '\033[0m',
        'warning': '\033[93m',
        'fail': '\033[91m',
        'red': '\033[91m' #=fail
    }
    if not debug:# or debug: #change if enable debug
        print colors[color]+text+colors['endc']

def saveFile(file_source, file_dest):
    '''
    Copy file #TODO: Enable compression (bz2/_lzma_)
    '''
    from shutil import copy2
    from os.path import isfile
    output_name = file_dest
    if not isfile(output_name):
        try:
            copy2(file_source, file_dest)
        except:
            print "Probem copying file?! DEBUG me"
            raise
    else:
        return False

def read_output(f, path, idx=0, total=0):
    import imp
    #Move import_istory to libs.IO?
    from plugins.importer import import_history
    from os.path import isfile, join

    fail = False
    print "[%s/%s]\tUsing file: %s" % (idx, total, f)
    #_input.bz2 could be used, but is more difficult to extract, and is heavier
    input_file = join(path, f.split("_")[1]) + "_input.py"
    try:
        input_conf = imp.load_source('*', input_file)
    except IOError: #File _input.py missing, save name to file, will try later?
        broken = open('ANALYSIS_FAILED.csv', 'a')
        broken.write("%s,%s\n" % (f.split("_")[0], f.split("_")[1]))
        broken.close()
        cprint("FAILED, SKIPPING", 'fail')
        fail = True
    except SyntaxError:
        broken = open('CONVERT_VUE_TO_PY.csv', 'a')
        broken.write("%s,%s\n" % (f.split("_")[0], f.split("_")[1]))
        broken.close()
        cprint("FAILED, SKIPPING", 'fail')
        fail = True
    input_conf = vars(input_conf)
    remove = ["step_input", "_S", "_N", "_stimuli", "_typicalN"]
    input_conf_clear = {}
    for var in input_conf:
        if var not in remove and not var.startswith("__"):
            input_conf_clear[var] = input_conf[var]
    data = import_history(join(path, f), compressed=True) #FIXME: allow uncompressed

    return data, input_conf_clear if not fail else False

def list_all(path, start_from, end_to):
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(path) if isfile(join(path, f))]

    #FIXME: allow uncompressed
    outputs = list(set([f for f in files if "_output" in f]))

    #Filter out unwanted runs
    outputs = outputs[start_from:end_to] if end_to else outputs[start_from:]
    total = len(outputs) + start_from

    return outputs, total

def ask(msg
        , exit_msg="Change your cli params then!"
        , sure="Are you sure? [y/n]"):
    action = "z"
    while action.capitalize() not in ["Y", "N"]:
        action = raw_input(msg + "\n" + sure +": ")
        if action.capitalize() == "Y":
            break
        else:
            cprint(exit_msg, 'warning')
            exit()

def reset_world(): #TODO: move to own function (like in IO.py)
    '''
    Reset gazebo world. Replaces reset_all
    '''
    import subprocess
    subprocess.call(["gz", "world", "-r"])
    return True
