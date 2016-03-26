#!/usr/bin/env python2

if __name__ == "__main__":
    import argparse
    from libs.IO import is_folder
    from plugins.importer import import_history
    from plugins.images import IO as ImageIO

    from os import listdir
    from os.path import isfile, join
    from sys import exit
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray
    import imp

    parser = argparse.ArgumentParser(description='Offline analysis for\
     spiking neural networks')
    parser.add_argument('--history-dir',
                        help = 'Path of the history dir'
                        , dest = 'path'
                        , default = False
    )
    parser.add_argument('--general-hash',
                        help = 'Which file (loop) to end with'
                        , dest = 'general'
                        , default = False
    )
    parser.add_argument('--config-hash',
                        help = 'Return number of loops to be executed and exit'
                        , dest = 'config'
                        , default = False
    )

    args = parser.parse_args()
    path = args.path
    #TODO: allow uncompressed
    if not all([args.general, args.config, args.path]):
        exit("Missing parameter")
#    file_name = join(path, args.general + "_" + args.config + "_output.bz2")
    file_name = join(path, args.general + "_" + args.config + "_output.gz")

    #FIXME: allow uncompressed
    data =import_history(file_name, compressed = True)
    print ("Using file: %s" % file_name)
    is_folder("output_images")
    ImageIO.ImageFromSpikes(
        data["NeMo"][1]
        , file_path = "./output_images/%s_%s.png" % (args.general, args.config)
        , save = True
        , show = False
    )
    exit()
    #Filter out unwanted runs
    if end_to:
        outputs = outputs[start_from:end_to]
    else:
        outputs = outputs[start_from:]
    total = len(outputs) + start_from

    #Update index
    loop = start_from - 1 if start_from else 0

    print 1 * 2
    print("Total number of analysis to be run: %s" % (len(outputs)))
    if args.number_only:
        exit()

    neurons_to_analyze = [4, 5] #FIXME: read from cli
    for f in outputs:
        bypass = False
        print("Using file: %s" % f)
        neurons_info = {}
        loop += 1
        data =import_history(join(path, f), compressed = True) #FIXME: allow uncompressed
        input_file = join(path, f.split("_")[1]) + "_input.py" #_input.bz2 could be used, but is more difficult to extract data, and is heavier
        input_conf = imp.load_source('*', input_file)
        neuron_number = 0
        if not loop % 20: #TODO: READ FROM CONFIG
            print ("Loop: %s/%s" % (loop, total))

        all_neurons_spikes_list = spikesDictToArray(data["NeMo"][1])
        if len( all_neurons_spikes_list) < max(neurons_to_analyze) -1:
            neurons_info={}
            for n in neurons_to_analyze:
                neurons_info[n] = {}
                neurons_info[n]={}
                neurons_info[n]["on_time"] = 0
                neurons_info[n]["off_time"] = 0
                neurons_info[n]["mode"] = 3 #Dead neuron
                neurons_info[n]["not_burst_freq"] = 0
                neurons_info[n]["burst_freq"] = 0

            bypass = True
            
        if not bypass:
            for i in all_neurons_spikes_list:
                if neuron_number not in neurons_to_analyze:
                    neuron_number +=1 
                    continue
                raw, tresholded = spikes.neuronSpikesToSquare(i)
                off_time, on_time, osc = spikes.getFreq(tresholded, data["ran_steps"])
                not_burst_freq, burst_freq = spikes.getBurstFreq(raw, tresholded)

                if not osc: #Not oscillating
                    state = max(off_time, on_time)
                    if state == off_time:
                        mode = 0 #Neuron is stable OFF
                    else:
                        mode = 2 #Neuron is stable ON
                        on_time = 0
                        off_time = 0
                else: #Neuron IS oscillating
                    mode = 1 #Neuron is both ON and OFF
                neurons_info[neuron_number]={}
                neurons_info[neuron_number]["on_time"] = on_time
                neurons_info[neuron_number]["off_time"] = off_time
                neurons_info[neuron_number]["mode"] = mode
                neurons_info[neuron_number]["not_burst_freq"] = not_burst_freq
                neurons_info[neuron_number]["burst_freq"] = burst_freq
                neuron_number += 1
        save = open("./ANALYSIS.log", 'a')#We could open this before

        save.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"
                   %
                   (
                       f.split("_")[0] #Save somewhere to save time, used multimple times #1
                       , f.split("_")[1]
                       , neurons_info[4]["mode"]
                       , neurons_info[4]["on_time"]
                       , neurons_info[4]["off_time"]
                       , neurons_info[4]["burst_freq"]
                       , neurons_info[4]["not_burst_freq"]
                       , neurons_info[5]["mode"]
                       , neurons_info[5]["on_time"]
                       , neurons_info[5]["off_time"]
                       , neurons_info[5]["burst_freq"]
                       , neurons_info[5]["not_burst_freq"]
                       , input_conf.cerebellum_ctrl[0]
                       , input_conf.cerebellum_ctrl[1]
                       , input_conf.cerebellum_ctrl[2]
                       , input_conf._stim_a
                       , input_conf._stim_b
                       , input_conf._start_a
                       , input_conf._start_b
                       , input_conf._stop_a
                       , input_conf._stop_b
                       , input_conf.CIN[0][0]
                       , input_conf.CIN[0][1]
                       , input_conf.CIN[0][2]
                       , input_conf.CIN[0][3]
                       , input_conf.CIN[0][4]
                       , input_conf.CIN[0][5]
                       , input_conf.CIN[0][6] #28
#                       , data["ran_steps"] #29
                   )
        )
        save.close() #And close it after, to speed up
