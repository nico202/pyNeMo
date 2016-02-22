from sys import exit
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
        if not found: exit("Could not find required module: %s" % (module))

def load_network_file (network_file, vue_prehook):
    import imp
    try:
             
        config = imp.load_source('*',
                                 try_load_vue (network_file, vue_prehook))
    #    script_dir = os.getcwd()
    except SyntaxError:
        print("Config file: Syntax Error")
        raise
    except IOError:
        print("Error: network file (%s) does not exists" % (network_file))
        raise
        exit()
    except NameError:
        print("This VUE contains undefined variables (is it for a batch?)")
        raise
    except:
        print("DEBUG: Unknown error")
        raise
    return config

def try_load_vue(config_name, prehook = ""): #FIXME: relative path etc
    if ".vue" in config_name:
        import libs.VUEtoPy as VUEtoPy
        #TODO: verbosity fix
        print("Converting input VUE to py")
        VUEtoPy.VUEtoPyConverter(config_name, prehook)
        config_name = "".join((config_name.split(".")[:-1]))
        config_name += ".py"
    return "./" + config_name

def import_network (
        (network_file, vue_prehook)
        , (use_cuda, cuda_backend_number)
        , (disable_sensory)
):
    '''
    Pass the network file to load_network_file, then:
    * Add neurons and synapses to Nemo
    
    returns [ nemo_simulation, to_save ]
    '''
    network_config = load_network_file (network_file, vue_prehook)

    import nemo
    nemo_net = nemo.Network()
    nemo_config = nemo.Configuration()
    
    nemo_select_backend (nemo_config, (use_cuda, cuda_backend_number))

    #Add network neurons
    nemo_add_neurons (nemo_net, network_config.neurons[0])
    nidx = len(network_config.neurons[0]) #Used to coninue numeration on sensory

    #Add networks synapses
    nemo_add_synapses (nemo_net, network_config.synapses)

    #Create the simulation
    nemo_simulation = nemo.Simulation(nemo_net, nemo_config)

    return ([
        nemo_simulation #0
        , ( #1
            network_config.save
            , len(network_config.neurons[0])
            , network_config.step_input
            , network_config.sensory_neurons
            , network_config.neurons
            , network_config.synapses
            , network_config.name
        )
    ]
    )

def nemo_add_neurons (net, neuron_list, start_id = 0):
    iz = net.add_neuron_type('Izhikevich')
    #TODO: edit conifg file to allow this?
    #km = net.add_neuron_type('Kuramoto')
    for nidx in range( len( neuron_list ) ):
        n_id = nidx + start_id
        a, b, c, d, s, u, v = neuron_list[nidx]
        net.add_neuron(iz, n_id, a, b, c, d, s, u, v)

def nemo_add_synapses (net, synaspes_list):
    for sidx in range(len(synaspes_list)):
        source, dests, synaptic_prop = synaspes_list[sidx]
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


def nemo_select_backend (
        nemo_config
        , (use_cuda, backend_number)
):
    if use_cuda:
        try:
            nemo_config.set_cuda_backend(backend_number)
        except RuntimeError:
            #FIXME: verbosity
            print("No CUDA-GPU found: using CPU instead")
            nemo_config.set_cpu_backend()
            
        else:
            nemo_config.set_cpu_backend()

def saveKey(filename, values, out_dir = "."):
    import os.path
    is_folder (out_dir)
    output_name = out_dir + '/' + filename
    if not os.path.isfile(output_name):
        try:
            output = open(output_name, 'w')
            output.write("%s" % values)
            output.close()
        except:
            print("Probem writing file?! DEBUG me")
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

def is_folder(output_dir = ".store"):
    import os.path
    output_dir = str(output_dir)
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

def write_log(uniqueId, output_dir = "history", name = "history.log"):
    import time
    history = open(output_dir + "/" + name, 'a') #Update the history
    history.write("%f, %s\n" % (time.time(), uniqueId))
    history.close()

def membraneImage(values, title = False, close = True, scales = []): #TODO: Add stimulation trace
    '''
        Output an image of the membrane potential from a list of Membrane values.
        zoom = (stretch_x, stretch_y) means the stretch that is applied to x and y axes
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    Vm_list=  values
    if close:
        plt.clf()
        plt.cla()
    x = len(Vm_list)
    x = np.array(range (0, x))
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
def rgb(triplet):
    return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]
