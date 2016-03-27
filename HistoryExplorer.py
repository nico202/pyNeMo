#!/usr/bin/env python2

from libs.web import ip_port, response_request
from libs.IO import read_output, list_all, cprint
from libs.multiProcess import dispatch_jobs, get_cores

def return_analysis_output(f, neurons_info, input_conf, steps):
    try:
        to_write = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
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
            , input_conf["cerebellum_ctrl"][0]
            , input_conf["cerebellum_ctrl"][1]
            , input_conf["cerebellum_ctrl"][2]
            , input_conf["_stim_a"]
            , input_conf["_stim_b"]
            , input_conf["_start_a"]
            , input_conf["_start_b"]
            , input_conf["_stop_a"]
            , input_conf["_stop_b"]
            , input_conf["CIN"][0][0]
            , input_conf["CIN"][0][1]
            , input_conf["CIN"][0][2]
            , input_conf["CIN"][0][3]
            , input_conf["CIN"][0][4]
            , input_conf["CIN"][0][5]
            , input_conf["CIN"][0][6]
            , steps #29
        )
    except KeyError:
        to_write =  "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
            f.split("_")[0] #Save somewhere to save time, used multimple times #1
            , f.split("_")[1]
            , 3
            , 0
            , 0
            , 0
            , 0
            , 3
            , 0
            , 0
            , 0
            , 0
            , input_conf["cerebellum_ctrl"][0]
            , input_conf["cerebellum_ctrl"][1]
            , input_conf["cerebellum_ctrl"][2]
            , input_conf["_stim_a"]
            , input_conf["_stim_b"]
            , input_conf["_start_a"]
            , input_conf["_start_b"]
            , input_conf["_stop_a"]
            , input_conf["_stop_b"]
            , input_conf["CIN"][0][0]
            , input_conf["CIN"][0][1]
            , input_conf["CIN"][0][2]
            , input_conf["CIN"][0][3]
            , input_conf["CIN"][0][4]
            , input_conf["CIN"][0][5]
            , input_conf["CIN"][0][6]
            , steps #29
        )
        cprint("Key error!","fail")
    return to_write

def main_loop(outputs, master_ip = False, in_data = False):
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray
    #???? Depends on kind of analysis, what to do??
    neurons_to_analyze = [4, 5] #FIXME: read from cli
    #TODO: add loop count
    idx = 0
    total = len(outputs)
    for f in outputs:
        if not master_ip: #Locale, read file
            data, input_conf = read_output(f, args.path, idx, total)
        else: #Already read file from host
            data, input_conf = in_data[idx][0], in_data[idx][1]
        idx += 1
        if not data:
            continue

        # FIXME: re-enable when dispatch works
        # if args.save_images:
        #     cprint("Saving image",'info')
        #     ImageIO.ImageFromSpikes(
        #         data["NeMo"][1]
        #         , file_path = "./latest.png" #FIXME: set wright path
        #         , save = True
        #         , show = False #Quite useless if True, right?
        #     )
        #     if args.images_only:
        #         continue

        neuron_number = 0
        neurons_info = {}
        all_neurons_spikes_list = spikesDictToArray(data["NeMo"][1])
        if len(all_neurons_spikes_list) < max(neurons_to_analyze) -1:
            neurons_info={}
            for n in neurons_to_analyze:
                neurons_info[n] = {}
                neurons_info[n]["on_time"] = 0
                neurons_info[n]["off_time"] = 0
                neurons_info[n]["mode"] = 3 #Dead neuron
                neurons_info[n]["not_burst_freq"] = 0
                neurons_info[n]["burst_freq"] = 0
        else:
            for i in all_neurons_spikes_list:
                #What's the pythonic way to do this?
                if neuron_number not in neurons_to_analyze:
                    neuron_number +=1 
                    continue
                raw, thresholded = spikes.neuronSpikesToSquare(i, data["ran_steps"])
                off_time, on_time, osc = spikes.getFreq(thresholded, data["ran_steps"])
                not_burst_freq, burst_freq = spikes.getBurstFreq(raw, thresholded)

                if not osc: #Not oscillating
                    state = max(off_time, on_time)
                    if state == off_time:
                        mode = 0 #Neuron is stable OFF
                    else:
                        mode = 2 #Neuron is stable ON
                else: #Neuron IS oscillating
                    mode = 1 #Neuron is both ON and OFF
                neurons_info[neuron_number] = {}
                neurons_info[neuron_number]["on_time"] = on_time
                neurons_info[neuron_number]["off_time"] = off_time
                neurons_info[neuron_number]["mode"] = mode
                neurons_info[neuron_number]["not_burst_freq"] = not_burst_freq
                neurons_info[neuron_number]["burst_freq"] = burst_freq
                neuron_number += 1
                
        to_write = return_analysis_output(f, neurons_info, input_conf, data["ran_steps"])
        if not master_ip:
            #        is_folder("analysis") TODO: better dir organization
            save = open("ANALYSIS.csv", 'a')#We could open this before
            save.write(to_write)
            save.close() #And close it after, to speed up
        else:
            response_request(to_write, master_ip, "10665")

def info_print(total, core_number, print_only = False):
    from libs.IO import cprint
    cprint("Total number of analysis to be run: %s" % (total), 'okblue')
    cprint("And we are going to use %s%s %s"
           %
           ( #Style :D
               "even " if core_number >= 8 \
               else "well " if core_number >= 4 \
               else "just " if core_number <= 2 \
               else ""
               , core_number
               , "core" if core_number == 1 else "cores"
           ) #Style again XD
           , 'okgreen' if core_number >= 4 \
           else 'okblue' if core_number >= 3 \
           else 'warning' if core_number >= 2 \
           else 'red'
           
    )
    if print_only: #Print simulations number and exit!
        exit()
        
if __name__ == "__main__":
    import argparse
    from sys import exit

    parser = argparse.ArgumentParser(description='Offline analysis for\
     spiking neural networks')
    parser.add_argument('--history-dir',
                        help = 'Path of the history dir'
                        , dest = 'path'
                        , default = "history"
    )
    parser.add_argument('--start-from',
                        help = 'Which file (loop) to start with'
                        , dest = 'start_from'
                        , default = 0
    )
    parser.add_argument('--end-to',
                        help = 'Which file (loop) to end with'
                        , dest = 'end_to'
                        , default = False
    )
    parser.add_argument('--get-cycle-number',
                        help = 'Return number of loops to be executed and exit'
                        , dest = 'number_only'
                        , default = False
                        , action = 'store_true'
    )
    parser.add_argument('--cores',
                        help = 'Number of cores to use. Max if none set'
                        , dest = 'core_number'
                        , default = False
    )
    parser.add_argument('--save-spike-images',
                        help = 'Generate spike images and saves them'
                        , dest = 'save_images'
                        , default = False
                        , action = 'store_true'
    )
    parser.add_argument('--save-images-only',
                        help = 'Save images (auto-enable save-spike-images if False).\
                        Don\t run any other analysis'
                        , dest = 'images_only'
                        , default = False
                        , action = 'store_true'
    )

    args = parser.parse_args()

    if args.images_only or args.save_images:
        import plugins.images.IO as ImageIO
    
    core_number = int(args.core_number) if args.core_number else get_cores()

    path = args.path
    start_from = int(args.start_from)
    end_to = int(args.end_to)
    
    outputs, total = list_all(path, start_from, end_to)
    
    #Update index
    loop = start_from - 1 if start_from else 0

    info_print(total, core_number, args.number_only)

    dispatch_jobs(outputs, core_number, main_loop)
