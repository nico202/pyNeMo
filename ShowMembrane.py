#!/bin/python2

from sys import argv, exit
import ast #load saved dict
try:
    import Image
except:
    exit("You need the Image library to use this. Exiting")

try:
    output_file = argv[1]
except:
    exit("Usage: %s output_file" % (argv[0]))

if "_membrane" in output_file:
    source = ast.literal_eval((open(output_file, 'r').readline()))
else:
    exit("Not a membrane potential file")

#Could get the following from the config which generated them
for neuron in source:
    x = len(source[0])
    #TODO: maintain the scale across all neurons
    y = (min(source[0]) - max(source[0])) * 10
    xi = 0

    img = Image.new( 'L', (int(x),abs(int(y))), "white") # create a new black or white image
    pixels = img.load() # create the pixel map
    for Vm in source[neuron]:
        pixels[xi, int(Vm - min(source[0]))] = 1 #TODO: How to interpolate points? :(
        xi += 1
    img.show()
