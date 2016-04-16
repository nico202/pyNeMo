#!/usr/bin/env python2

#"Front-end" for the real script

from sys import exit, stderr

#Timing
import time

#Config
import os.path

#Own helpers
from libs.runParser import parse_args

from libs.IO import time_to_steps
from libs.IO import dependency_check
from libs.IO import import_network
from libs.IO import saveKey, hashDict, write_log
from libs.IO import saveFile

from libs.simulations import main_simulation_run
from libs.pYARP import RobotYARP

import config
if __name__ == "__main__":
    #Check dependencyes:
    required_modules = [
        "nemo"
        , "scipy"
#        , "yarp" #FIXME: not needed if no sensory
#       , "pygazebo"
        , "shutil"
    ]
    dependency_check(required_modules)

    #IMPORT PARSER
    parser = parse_args()
    #Parse args
    args = parser.parse_args()

    #Load all the parameters (choose if/when read from CLI/config.py)
    use_config = True if os.path.isfile("config.py") else False
    if use_config: import config

    network_file = args.network_file

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

    #Create general_config, the configuration that will be passed to our simulation
    general_config = {
        "steps":steps
        , "use_cuda": use_cuda
        , "cuda_backend": cuda_backend
    }

    #Import the network, tranform it to a valid nemo.Network object
    if ".py" in network_file and (vue_prehook != "#No prehooks"
                                  or vue_posthook != "#No posthooks"):
        exit("Refusing to run with hooks on py file (not supported yet")
    
    
    networks, config_file_name =\
        import_network(
            (network_file, (vue_prehook, vue_posthook))
            , (use_cuda, cuda_backend)
            , (disable_sensory))

    nemo_simulation = networks[0]
    to_save = networks[1][0]
    neuron_number = networks[1][1]
    stimuli_dict = networks[1][2]

    if not disable_sensory:
        sensory_neurons_in, sensory_neurons_out = networks[1][3]
    else:
        sensory_neurons_in = []
        sensory_neurons_out = []
    
    neurons = networks[1][4]
    synapses = networks[1][5]
    network_name = networks[1][6]
    
    #Save Config
    dict_config = {
        "neurons":neurons
        , "sensory_neurons":(sensory_neurons_in, sensory_neurons_out)
        , "save": to_save
        , "step_input": stimuli_dict
        , "synapses": synapses
        , "name": network_name
    }
    config_dict_hash = hashDict(dict_config)
    saveKey(config_dict_hash + "_input"
            , dict_config
            , output_dir)
    
    saveFile(
        config_file_name
        , output_dir + "/" + config_dict_hash + "_input.py")

    #Define robot
    if (sensory_neurons_in or sensory_neurons_out):
        robot = RobotYARP(mode=args.robot_mode)
    else:
        robot = None
    #TODO: Reset robot original position? (and maybe gz-world status?)
    if args.reset_position or args.reset_only:
        robot.reset_all() #Use both right now. Strange gz reset
        robot.reset_world() #FIXME: wrong class?
        if args.reset_only:
            exit("Resetting done, exiting (remove --reset-and-exit to continue)")

    #Time the simulation
    start_time = time.time()

    #Actually run the simulation
    output = main_simulation_run(
        general_config
        , (nemo_simulation
           , (to_save, neuron_number)
           , stimuli_dict)
        , (robot)
        , (sensory_neurons_in
           , sensory_neurons_out)
    )

    #Get the total run time
    end_time = time.time()
    general_config_out = {"steps": output["ran_steps"]} #Add various robot params
    #Save/process output + input
    uniqueId = hashDict(general_config_out)\
               + "_" + hashDict(dict_config)

    #Step is included in the output
    saveKey(uniqueId + "_output", output, output_dir)

    #Save the log
    write_log(uniqueId, output_dir = output_dir)

    #Print some statistic
    #TODO: verbosity
    print ("\n\nSession: %s" % (uniqueId))
    total_time = end_time - start_time
    print("-------------------\n\
Total run time: %s\n\
Realtime ratio: %sX\n\
Steps: %s"
          % (
              total_time
              , output["ran_steps"]/(total_time*1000)
              , output["ran_steps"]
          )
    )
    print("-------------------\n")
    #Show images
    if (
            (args.show_images or args.save_spikes or args.angle_images)
            and
            any([
                args.show_membrane
                , args.show_spikes
                , args.save_spikes
                , args.angle_images
            ])):
        print("Processing images...")
        from plugins.images import IO as ImageIO
        if args.show_spikes or args.save_spikes:
            ImageIO.ImageFromSpikes(output["NeMo"][1]
                        #used only if save true
                        , file_path=output_dir + "/" + uniqueId + "_spikes.png"
                        , show=all([args.show_spikes, args.show_images])
                        , save=args.save_spikes
            )
        if args.show_membrane:
            ImageIO.ImageFromMembranes(output["NeMo"][0])
        if args.angle_images:
            ImageIO.ImageFromAngles(
                (output["YARP"]["read"],
                output["YARP"]["wrote"])#FIXME: should be pyspike
                , file_path=output_dir + "/" + uniqueId + "_angles.png")

#Analysis:
if args.analyze_spikes_frequency: #TODO: write all conditions etc
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray
    neuron_number = 0
    print len (spikesDictToArray(output["NeMo"][1]))
    for i in spikesDictToArray(output["NeMo"][1]):
#        print "ANALYSIS not working yet"
        freq = spikes.getFreq(spikes.squareToBitSeq(spikes.neuronSpikesToSquare(i)))
        if freq:
            print ("Neuron: %s, freqs: %s, %s"
                   %
                   (neuron_number, 1./freq[0]*1000, 1./freq[1]*1000))
        neuron_number += 1
        
print("All done, thanks!")
