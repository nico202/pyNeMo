#!/usr/bin/env python2

#"Front-end" for the real script

#Argparse
import argparse
from sys import exit, stderr

#Timing
import time

#Config
import os.path

#Own helpers
from libs.IO import time_to_steps
from libs.IO import dependency_check
from libs.IO import import_network
from libs.IO import saveKey, hashDict, write_log
from libs.IO import saveFile

from libs.simulations import main_simulation_run
from libs.pYARP import RobotYARP
if __name__ == "__main__":
    #Check dependencyes:
    required_modules = [
        "nemo"
        , "scipy"
        , "yarp" #FIXME: not needed if no sensory
#       , "pygazebo"
        , "shutil"
    ]
    dependency_check(required_modules)

    #The parser. Read command line arguments
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            if message == "Too few arguments":
                message = "You must provide a network file!"
            stderr.write('Error: %s\n' % message)
            self.print_help()
            exit(2)

    parser = MyParser(description='Run NeMo+YARP+Gazebo simulations')

    parser.add_argument('network_file', help = 'Network file to use')

    parser.add_argument('--steps'
                        , help = 'Steps to run. Default loaded in general config\
                        \nDefault ms. Can use s and m (ie. 100, 10s, 3m)'
                        , dest = 'steps'
                        , default = None
    )

    parser.add_argument('--history-dir'
                        , help = 'Override config-defined output dir'
                        , dest = 'history_dir'
                        , default = False
    )

    processor = parser.add_mutually_exclusive_group()
    processor.add_argument('--cuda'
                            , action='store_true'
                            , help = 'Overwrite config cuda settings (force cuda)'
                            , dest = 'use_cuda'
                            , default = None
    )
    processor.add_argument('--cpu'
                            , action='store_false'
                            , help = 'Overwrite config GPU settings (force CPU)'
                            , dest = 'use_cuda'
    )
    parser.add_argument('--cuda-backend'
                        , help = 'Override cuda processor number'
                        , dest = 'cuda_backend'
                        , default = 0
    )

    parser.add_argument('--control'
                        , help = 'Name of the robot to control'
                        , dest = 'control_robot'
                        , default = '/doublePendulumGazebo/body'
    )

    parser.add_argument('--robot-mode' #TODO: Read docs + ADD TO HASH
                        , help = 'Control mode: Torque, Position ...'
                        , dest = 'robot_mode'
                        , default = 'Torque'
    )

    parser.add_argument('--no-reset' #TODO: implement
                        , help = 'Reset robot position to it\'s home'
                        , dest = 'reset_position'
                        , action = 'store_true'
                        , default = True
    )

    parser.add_argument('--vue-prehook'
                        , help = 'Add python commands before a vue script variable definition'
                        , dest = 'vue_prehook'
                        , default = "#No prehooks"
    )

    parser.add_argument('--vue-posthook'
                        , help = 'Add python commands after a vue script variable definition'
                        , dest = 'vue_posthook'
                        , default = "#No posthooks"
    )

    parser.add_argument('--disable-sensory'
                        , help = 'Disable sensory neurons (those which reads/write to yarp)'
                        , dest = 'disable_sensory'
                        , default = False
                        , action = 'store_true'
    )
    #IMAGES
    parser.add_argument('--no-show-images'
                        , help = 'Don\'t show images'
                        , dest = 'show_images'
                        , default = True
                        , action = 'store_false'
    )
    parser.add_argument('--no-show-membrane'
                        , help = 'Don\'t show membrane images'
                        , dest = 'show_membrane'
                        , default = True
                        , action = 'store_false'
    )
    parser.add_argument('--no-show-spikes'
                        , help = 'Don\'t show spikes images'
                        , dest = 'show_spikes'
                        , default = True
                        , action = 'store_false'
    )
    parser.add_argument('--save-spikes'
                        , help = 'Save spikes images'
                        , dest = 'save_spikes'
                        , default = False
                        , action = 'store_true'
    )

    parser.add_argument('--analyze-spikes-frequency'
                        , help = 'Return frequency of spikes data'
                        , dest = 'analyze_spikes_frequency'
                        , default = False
                        , action = 'store_true'
    )

    #Load all the parameters (choose if/when read from CLI/config.py)
    use_config = True if os.path.isfile("config.py") else False
    if use_config: import config

    #Parse args
    args = parser.parse_args()

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
    networks =\
        import_network (
            (network_file, (vue_prehook, vue_posthook))
            , (use_cuda, cuda_backend)
            , (disable_sensory))

    nemo_simulation = networks[0]
    to_save = networks[1][0]
    neuron_number = networks[1][1]
    stimuli_dict = networks[1][2]

    if not disable_sensory:
        sensory_neurons_in, sensory_neurons_out  = networks[1][3]
    else:
        sensory_neurons_in = []
        sensory_neurons_out = []
    
    neurons = networks[1][4]
    synapses = networks[1][5]
    network_name = networks[1][6]

    #Save Config
    dict_config = {
        "neurons":neurons
        ,"sensory_neurons":(sensory_neurons_in, sensory_neurons_out)
        , "save": to_save
        , "step_input": stimuli_dict
        , "synapses": synapses
        , "name": network_name
    }
    config_dict_hash = hashDict(dict_config)
    saveKey(config_dict_hash + "_input", dict_config, output_dir)
    saveFile(args.network_file, output_dir + "/" + config_dict_hash + "_input.py")

    #Define robot
    if (sensory_neurons_in or sensory_neurons_out):
        robot = RobotYARP ()
    else:
        robot = None

    #Time the simulation
    start_time = time.time()

    #TODO: Reset robot original position? (and maybe gz-world status?)
    #robot.reset_all()
    
    #Actually run the simulation
    output = main_simulation_run(
        general_config
        , (nemo_simulation, (to_save, neuron_number), stimuli_dict)
        , (robot)
        , (sensory_neurons_in, sensory_neurons_out)
    )

    #Get the total run time
    end_time = time.time()
    general_config = {"steps": output["ran_steps"]} #Add various robot params
    #Save/process output + input
    uniqueId = hashDict(general_config)\
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
            (args.show_images or args.save_spikes)
            and
            any([
                args.show_membrane
                , args.show_spikes
                , args.save_spikes
            ])):
        print("Processing images...")
        from plugins.images import IO as ImageIO
        if args.show_spikes or args.save_spikes:
            ImageIO.ImageFromSpikes(output["NeMo"][1]
                        #used only if save true
                        , file_path = output_dir + "/" + uniqueId + "_spikes.png"
                        , show = all([args.show_spikes, args.show_images])
                        , save = args.save_spikes
            )
        if args.show_membrane:
            ImageIO.ImageFromMembranes(output["NeMo"][0])

#Analysis:
if args.analyze_spikes_frequency: #TODO: write all conditions etc
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray

    for i in spikesDictToArray(output["NeMo"][1]):
        #print spikes.neuronSpikesToSquare(i)
#        print len(spikes.neuronSpikesToSquare(i))
#        print sum(spikes.neuronSpikesToSquare(i))
        mean = spikes.squareMeans(spikes.neuronSpikesToSquare(i))
        print "ANALYSIS not working yet"
#        print mean
#        print 1. / mean[0] * 1000.
#        print 1. / mean[1] * 1000.
        
print("All done, thanks!")
