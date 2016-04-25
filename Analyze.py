#!/bin/python2

if __name__ == "__main__": #if run in standalone
    from sys import exit
    import argparse
    from libs.InAndOut import importer, saveKey
    parser = argparse.ArgumentParser(description='Offline analysis for\
     spiking neural networks')
    #Files to open
    parser.add_argument('--store-dir',
            help = 'Path of the store dir',
            dest = 'path'
            )
    parser.add_argument('--general-hash',
        help = 'General hash file. Always needed',
        dest = 'general'
        )
    parser.add_argument('--config-hash',
        help = 'Hash of the neural net file that needs to be opened.',
        dest = 'config_hash'
        )

    #Analysis to run
    parser.add_argument('--all',
        help = 'Run all available analysis (all the possible for the input)',
        action = 'store_true'
        )
    parser.add_argument('--phase',
        action = 'store_true',
        help = 'Check the phase distance. Needs membrane data'
        # FIXME: enable phase distance on spikes
        )
    parser.add_argument('--frequency',
        action = 'store_true',
        help = 'Return the fundamental frequency for each neuron. Needs membrane data')
        # FIXME: enable this on spikes

    parser.add_argument('--duty',
        action = 'store_true',
        help = 'Return the duty cycle for each neurons. Needs membrane data')
        # FIXME: enable this on spikes
    parser.add_argument('--update-json',
        action = 'store_true',
        help = 'Save data to json (for historyGUI)',
        default = False)
    parser.add_argument('--batch',
        action = 'store_true',
        help = 'Suppress output, save to file',
        default = False)

    args = parser.parse_args()
    batch = args.batch

    if not args.path:
        print "WARNING:\tYou must define the store dir! Using general_config default"
        try:
            import general_config
            args.path = general_config._history_dir
        except:
            raise #debug file not found etc.
            exit("FATAL:\t\tCannot import general config. Define a store dir, please")

    #Check required
    if not args.general:
        exit("FATAL:\t\tYou need to define a general config file hash")
    #TODO: copy this for other analysis. Make a function if it get boring
    if args.phase or args.duty or args.frequency or args.all:
        if not args.config_hash:
            exit("ERROR:\t\tto run this analysis, you must provide the config hash")
        else:
            membrane_file = args.path + '/.' + args.general + args.config_hash + '_membrane'
            Vm_dict = importer(membrane_file)

    if args.config_hash:
        if not batch:
            print not batch, "INFO: Opened file %s" % membrane_file
            print not batch, "INFO: This is a membrane file."
            print batch, "INFO: There are %s neurons in this net, and %s samples (ms)" % (len(Vm_dict), len(Vm_dict[0]))
        if args.phase or args.duty or args.frequency or args.all:
            #Run import only if needed
            import plugins.analysis.membrane as membrane_analysis
            results = membrane_analysis.analyzeMembrane(Vm_dict)
            if args.all:
                print(not batch, results)
            else:
                if args.phase:
                    print(not batch, results["phase"])
                if args.fundamental:
                    print(not batch, results["fundamental"])
                if args.duty_cycle:
                    print(not batch, results["duty_cycle"])
            saveKey(args.general + args.config_hash + "_analysis", results, out_dir = args.path)

    if args.update_json:
        import json
        data_to_json = []
        for n in Vm_dict:
            x = 0
            neuron = []
            for y in Vm_dict[n]:
                point = {"x":x,"y":y}
                x+=1
                neuron.append(point)
            data_to_json.append(neuron)
        with open('./historyGUI/data.json', 'w') as outfile:
            json.dump(data_to_json, outfile)
