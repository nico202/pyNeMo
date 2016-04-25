#!/usr/bin/env python2

def main_loop(content, remote, dummy):
    i = 0
    total = len(content)
    for values in content:
        filename = "./%s/%s_%s.png" % (values[1], values[2], values[3])
        cprint("[%s/%s] %s match and is missing, generating image\r" % (i, total, filename), 'info')
        #TODO:allow compressed
        data = import_history("%s/%s_%s_output.gz" % (values[0], values[2], values[3]), compressed=True)
        state = ImageIO.ImageFromSpikes(
            data["NeMo"][1],
            file_path = filename,
            save = True,
            show = False
        )
        del state
        del data #Memory leak again?
        i += 1

if __name__ == "__main__":
    import argparse
    from libs.IO import is_folder, cprint
    from plugins.importer import import_history
    from plugins.images import IO as ImageIO

    from os.path import isfile
    # from plugins.analysis import spikes
    # from plugins.importer import spikesDictToArray
    # import imp
    
    from libs.multiProcess import dispatch_jobs, get_cores

    parser = argparse.ArgumentParser(description='Offline analysis for\
     spiking neural networks')
    parser.add_argument('--history-dir',
                        help = 'Path of the history dir'
                        , dest = 'path'
                        , default = False
    )
    parser.add_argument('--analysis-file',
                        help = 'Path of the analysis csv file (to filter)'
                        , dest = 'analysis_file'
                        , default = "ANALYSIS.csv"
    )
    parser.add_argument('--output-dir',
                        help = 'Path of the output images dir'
                        , dest = 'images_path'
                        , default = "output_images"
    )
    parser.add_argument('--run-all',
                        help = 'Ran all the sims'
                        , dest = 'run_all'
                        , default = 'false'
                        , action = 'store_true'
    )
    parser.add_argument('--cores',
                        help = 'Number of cores to use. All by default'
                        , dest = 'cores'
                        , default = get_cores()
    )
  
    args = parser.parse_args()
    path = args.path

    #Read ANALYSIS file
    fname = args.analysis_file
    with open(fname) as f:
        content = f.readlines()

    cprint("Total files provided: %s; Number of cores: %s" % (len(content), args.cores), 'info')
    is_folder(args.images_path)

    real_content = []
#    existing = listdir(args.images_path) #Slower than isfile
    for line in content:
        file_data = line.split(",")
        general = file_data[0]
        config = file_data[1]
        if args.run_all or (file_data[2] == "1" == file_data[7]):
            filename = "%s_%s.png" % (general, config)
            if not isfile("./%s" % args.images_path + filename):
           # if filename not in existing: #Slower than isfile O.o
                real_content.append((args.path, args.images_path, general, config))
#            else: existing.remove(filename)

    dispatch_jobs(real_content, int(args.cores), main_loop, False) #Ugly, ya'know
    
    cprint("All done!", 'okgreen')
