#!/usr/bin/env python2


def main_loop(content, remote, dummy):
    from os.path import isfile
    i = 0
    total = len(content)
    for values in content:
        filename = "./%s/%s_%s.png" % (values[1], values[2], values[3])
        cprint ("[%s/%s] %s match and is missing, generating image" % (i, total, filename),'info')
        #TODO:allow compressed
        data = import_history("%s/%s_%s_output.bz2" % (values[0], values[2], values[3]), compressed = True)
        ImageIO.ImageFromSpikes(
            data["NeMo"][1]
            , file_path = filename
            , save = True
            , show = False
        )
        i += 1

if __name__ == "__main__":
    import argparse
    from libs.IO import is_folder, cprint
    from plugins.importer import import_history
    from plugins.images import IO as ImageIO

    from os import listdir
    from os.path import isfile, join
    from sys import exit
    from plugins.analysis import spikes
    from plugins.importer import spikesDictToArray
    import imp
    
    from libs.multiProcess import chunks, dispatch_jobs, get_cores

    parser = argparse.ArgumentParser(description='Offline analysis for\
     spiking neural networks')
    parser.add_argument('--history-dir',
                        help = 'Path of the history dir'
                        , dest = 'path'
                        , default = False
    )
    parser.add_argument('--output-dir',
                        help = 'Path of the output images dir'
                        , dest = 'images_path'
                        , default = "output_images"
    )

    args = parser.parse_args()
    path = args.path

    #Read ANALYSIS file
    fname = "ANALYSIS.csv"
    with open(fname) as f:
        content = f.readlines()

    cprint("Total files provided: %s" % len(content),'info')
    is_folder(args.images_path)

    real_content = []
    for line in content:
        file_data = line.split(",")
        general = file_data[0]
        config = file_data[1]
        if file_data[2] == "1" == file_data[7]:
            filename = "./%s/%s_%s.png" % (args.images_path, general, config)
            if not isfile(filename): #Don't run it twice
                real_content.append((args.path, args.images_path, general, config))
    
    dispatch_jobs(real_content, get_cores(), main_loop, False) #Ugly, ya'know
    
    cprint("All done!", 'okgreen')
