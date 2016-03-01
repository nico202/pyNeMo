def import_history(file_path):
    #FIXME: add bzip2 suppor
    import ast
    try:
        ret = ast.literal_eval((open(file_path, 'r').readline()))
    except SyntaxError:
        print ("FATAL ERROR: input file broken!")
        return False
    return ret

def spikesDictToArray(input_spikes):
    spikes_dict = {}                                                               
    for ms in range(len(input_spikes)):                                            
        for neuron in input_spikes[ms]:                                            
            if neuron in spikes_dict:                                              
                spikes_dict[neuron].append(ms)                                     
            else:                                                                  
                spikes_dict[neuron] = [ms]                                         
                                                                                   
    spikes = []                                                                    
    for key in spikes_dict:                                                        
        spikes.append(spikes_dict[key])
    return spikes
