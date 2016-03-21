#!/usr/bin/env python2

from libs.web import ip_port

def response_request(to_save, master_ip, master_port):
    import dill
    import requests
    from libs.IO import cprint
    requests.post(ip_port(str(master_ip), str(master_port)) + "/save", data = to_save)
    cprint("Result sended, waiting for next", 'okgreen')

def read_output(f, path):
    import imp
    from plugins.importer import import_history
    from os.path import isfile, join
    
    fail = False
    total = 0
    print("[%s/%s]\tUsing file: %s" % (0, 0, f))
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
    data = import_history(join(path, f), compressed = True) #FIXME: allow uncompressed

    return data, input_conf_clear if not fail else False

def return_analysis_output(f, neurons_info, input_conf, steps):
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
    return to_write

def main_loop(outputs, master_ip = False, in_data = False):
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray
    #???? Depends on kind of analysis, what to do??
    neurons_to_analyze = [4, 5] #FIXME: read from cli
    #TODO: add loop count
    idx = 0
#    outputs = outputs[0]
    for f in outputs:
        bypass = False
        if not master_ip:
            data, input_conf = read_output(f, args.path)
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

            bypass = True

        if not bypass:
            for i in all_neurons_spikes_list:
                if neuron_number not in neurons_to_analyze:
                    neuron_number +=1 
                    continue
                raw, tresholded = spikes.neuronSpikesToSquare(i, data["ran_steps"])
                off_time, on_time, osc = spikes.getFreq(tresholded, data["ran_steps"])
                not_burst_freq, burst_freq = spikes.getBurstFreq(raw, tresholded)

                if not osc: #Not oscillating
                    state = max(off_time, on_time)
                    if state == off_time:
                        mode = 0 #Neuron is stable OFF
                    else:
                        mode = 2 #Neuron is stable ON
                        #on_time = 0
                        #off_time = 0
                else: #Neuron IS oscillating
                    mode = 1 #Neuron is both ON and OFF
                neurons_info[neuron_number]={}
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


#Multiprocessing: https://gist.github.com/baojie/6047780
def chunks(l, n):
    if len(l) > n:
        return [l]
    else:
        return [l[i:i+n] for i in range(0, len(l), n)]

def dispatch_jobs(data, job_number, remote = False, in_data = False):
    import multiprocessing
    total = len(data)
    chunk_size = total / job_number
    _slice = chunks(data, chunk_size)
    jobs = []
    
    for s in _slice:
        j = multiprocessing.Process(target=main_loop, args=(s, remote, in_data))
        jobs.append(j)
    
    for j in jobs:
        j.start()


def get_cores():
    import multiprocessing
    return multiprocessing.cpu_count()

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
        
def list_all(path, start_from, end_to):
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(path) if isfile(join(path, f))]
    #FIXME: allow uncompressed
    outputs = list(set([ f for f in files if "_output.bz2" in f ]))

    #Filter out unwanted runs
    outputs = outputs[start_from:end_to] if end_to else outputs[start_from:]
    total = len(outputs) + start_from

    return outputs, total
    
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
    
    dispatch_jobs(outputs, core_number)
