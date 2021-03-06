''' The parser. Shared between Runner.py and Batch.py (v2)'''
import argparse
def parse_args():
    #The parser. Read command line arguments
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            from sys import stderr, exit
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
                        , default = 'Position' #TODO: Decide default (before v1)
    )
    parser.add_argument('--no-home-position'
                        , help = 'Don\'t reset robot position to it\'s home'
                        , dest = 'reset_position'
                        , action = 'store_false'
                        , default = True
    )
    parser.add_argument('--reset-and-exit'
                        , help = 'Move to home, then exit. Don\'t simulate anything'
                        , dest = 'reset_only'
                        , action = 'store_true'
                        , default = False
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
    parser.add_argument('--save-membrane'
                        , help = 'Save membrane data (SLOW!)'
                        , dest = 'save_membrane'
                        , default = False
                        , action = 'store_true'
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
    parser.add_argument('--angle-images'
                        , help = 'Show angle images'
                        , dest = 'angle_images'
                        , default = False
                        , action = 'store_true'
    )
    parser.add_argument('--dont-save-anything'
                        , help = 'Experimental: don\'t save any kind of output. Useful for realtime tests'
                        , dest = 'dont_save'
                        , default = False
                        , action = 'store_true'
    )
    parser.add_argument('--simple-feedback'
                        , help = 'sum YARP error to pySpike output'
                        , dest = 'simple_feedback'
                        , default = False
                        , action = 'store_true'
    )
    parser.add_argument('--bypass-debug'
                        , help = 'Bypass iSpike angle output and force this angle value'
                        , dest = 'bypass_debug'
                        , default = False
    )
    return parser
