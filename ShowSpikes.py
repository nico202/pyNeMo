#!/bin/python2

from sys import argv, exit
import ast #load saved dict
import os

from libs.InAndOut import importer, showImage, saveImage

try:
    import Image
    have_Image = True
except:
    have_Image = False
    print("You don't have Image installed! Printing to terminal")
    print("Please note: this is not optimal. Install Image")

if __name__ == "__main__":
    try:
        output_file = argv[1]
    except:
        exit("Usage: %s output_file [--force-terminal]" % (argv[0]))

    try:
        have_Image = argv[2] != "--force-terminal"
    except:
        pass

    try:
        source = importer(output_file)
    except SyntaxError:
        exit("Wrong input file!")

    #Could get the following from the config which generated them. What is better?

    image_name = output_file + '.png'
    if os.path.isfile(image_name):
        print("Image already created, showing!")
        showImage(image_name)
    else:
        if have_Image:
            saveImage(source, image_name)
            showImage(image_name)
        else:
            for i in range(1, x+1):    # for every pixel:
                col = source[i]
                if col:
                    for l in range(0, y+1):
                        if l in col:
                            print l,
                        else:
                            print " ",
                    print("")
                else:
                    print("")

            print("You don't have Image installed! Printing to terminal")
            print("Please note: this is not optimal. Install Image")
