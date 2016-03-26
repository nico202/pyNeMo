def import_history(file_path, compressed = False):
    #FIXME: automatic bzip2 support
    import ast
    from os.path import isfile, join
    try:
        if compressed:
            if ".bz2" in file_path:
                import bz2
                opened = bz2.BZ2File(file_path)
            elif ".gz" in file_path:
                import gzip
                opened = gzip.GzipFile(file_path)
            else:
                print("Error: file type not known! Try plain import")
                opened = open(file_path, 'r')
        else:
            opened = open(file_path, 'r')

        ret = ast.literal_eval(opened.readline())
        del opened
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
    del spikes_dict
    del input_spikes
    return spikes
