#!/bin/python2

from sys import argv, exit
import ast #load saved dict

from InAndOut import importer

try:
    import Image
    have_Image = True
except:
    have_Image = False
    print("You don't have Image installed! Printing to terminal")
    print("Please note: this is not optimal. Install Image")

black = (0, 0, 0)
red =   (255, 0, 0)
green = (0, 255, 0)
blue =  (0, 0, 255)
white = (255, 255, 255)
try:
    output_file = argv[1]
except:
    exit("Usage: %s output_file [--force-terminal]" % (argv[0]))

try:
    have_Image = argv[2] != "--force-terminal"
except:
    pass

source = importer(output_file)

#Could get the following from the config which generated them
x = len(source) #Number of spikes
y = 0 #Number of neurons
for l in source:
    for i in source[l]:
        y = max(i, y)

print x, y
if have_Image:
    img = Image.new( 'RGB', (x,y+1), "white") # create a new black image
    pixels = img.load() # create the pixel map

    for i in range(1, x+1):    # for every pixel:
        col = source[i]
        if col:
            for l in col:
                pixels[i -1, l ] = black

    img.show()
else:
    for i in range(1, x+1):    # for every pixel:
        col = source[i]
        if col:
            for l in range(0, y+1):
                if l in col:
                    print l,
                else:
                    print " ",
            print ""
        else:
            print ""

    print("You don't have Image installed! Printing to terminal")
    print("Please note: this is not optimal. Install Image")
