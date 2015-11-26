#!/bin/python2
from sys import argv, exit
from libs.InAndOut import importer, membraneImage, allNeuronsMembrane

if __name__ == "__main__":
    try:
        output_file = argv[1]
    except:
        exit("Usage: %s output_file" % (argv[0]))

    if "_membrane" in output_file:
        source = importer(output_file)
    else:
        exit("Not a membrane potential file")

    allNeuronsMembrane(source).show()
