import os
from sys import exit
from libs.VUEtoPy import *

#require ast (dict import), shutil (copy config), hashlib (Hash configs)

def startup_check(output_dir = ".store"):
    if not os.path.isdir(output_dir):
        if not os.path.exists(output_dir):
            try:
                os.mkdir(output_dir)
            except:
                exit("Unknown error creating folder")
            return True
        else:
            exit("Destination must be a folder! Check your config")
    else:
        return True

def hashIt(module): #We use this to check if configuration changed
    import hashlib
    key_string = str({key: value for key, value in module.__dict__.iteritems()
            if not (key.startswith('__') or key.startswith('_'))})

    return key_string, hashlib.sha1(key_string).hexdigest()

def saveKey(file_hash, values):
    output_name = '.' + file_hash

    if not os.path.isfile(output_name):
        try:
            output = open(output_name, 'w')
            output.write("%s" % values)
            output.close()
        except:
            print("Probem writing file?! DEBUG me")
            raise
        return True
    else:
        return False

def saveFile(file_name, file_hash, notouch = False):
    import shutil
    output_name = '.' + file_hash + '.py'
    if not os.path.isfile(output_name):
        try:
            if not notouch:
                out = '.' + file_hash + '.py'
            else:
                out = file_hash
            shutil.copy2(file_name, out)
        except:
            raise
            exit("Probem copying file?! DEBUG me")
        return True
    else:
        return False

def importer(filename, replace_pattern = False):
    import ast
    try:
        ret = ast.literal_eval((open(filename, 'r').readline()))
    except SyntaxError:
        exit("Wrong input file!")
    return ret

def showSourceImage(image_name):
    import Image
    try:
        img = Image.open(image_name)
        img.show()
    except IOError:
        print("Cannot load image: file not exists")

def saveRawImage(img, name, close = True):
    import Image
    try:
        img.save(name)
    except AttributeError:
        try:
            img.savefig(name)
            if close:
                img.close()
        except:
            raise

def saveSourceImage(source, image_name):
    try:
        from neuronpy.graphics import spikeplot
        spikes_dict = {}
        spikes = []
        for ms in source:
            for neuron in source[ms]:
                if neuron in spikes_dict:
                    spikes_dict[neuron].append(ms)
                else:
                    spikes_dict[neuron] = [ms]
        for key in spikes_dict:
            spikes.append(spikes_dict[key])
        if len(spikes): #If no data, it does not save image
            sp = spikeplot.SpikePlot(savefig=True)
            sp.set_fig_name(image_name)
            sp.set_linestyle('-')
            sp.set_markerscale(0.5)
            sp.plot_spikes(spikes, draw=False)
        else: #save it however
            saveFile("../.noSpikes.png", image_name, notouch = True)


    except ImportError:
        print ("You should install neuronpy (pip2 install neuronpy\n pip2 install matplotlib).\n\
        It provides better graphics. Falling back to ugly one")
        import Image
        color_map = {
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blu": (0, 0, 255),
            "white": (255, 255, 255)
        }
        x = len(source) #Number of spikes
        y = 0 #Number of neurons
        for l in source:
            for i in source[l]:
                y = max(i, y)

        img = Image.new( 'RGB', (x,y+1), "white") # create a new black image
        pixels = img.load() # create the pixel map

        for i in range(1, x+1):    # for every pixel:
            col = source[i]
            if col:
                for l in col:
                    pixels[i -1, l ] = color_map["black"]

        img.save(image_name)


def membraneImage(values, title = False, close = True, scales = []): #TODO: Add stimulation trace
    '''
        Output an image of the membrane potential from a list of Membrane values.
        zoom = (stretch_x, stretch_y) means the stretch that is applied to x and y axes
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    Vm_list, Stim_list = values
    if close:
        plt.clf()
        plt.cla()
    x = len(Vm_list)
    x = np.array(range (0, x))
    fig, ax1 = plt.subplots()
    ax1.plot(x, np.array(Vm_list))
    ax1.set_xlabel('time (ms)')
    ax1.set_ylabel('Membrane Potential\n(mV)')
    ax2 = ax1.twinx()
    ax2.plot(Stim_list, color = 'r')
    ax2.set_ylabel('Stimulation\n(mA)')
    ax2.set_ylim(min(-5, min(Stim_list)),max(20,max(Stim_list)))
    if title:
        plt.title(title)
    return plt

def allNeuronsMembrane(Vm_lists):
    '''
        Show an image where every line is a neuron
        and the color is the membrane value
    '''
    import Image

    y = len(Vm_lists)
    x = len(Vm_lists[0])

    img = Image.new( 'RGB', (x,y), "white") # create a new black image
    pixels = img.load() # create the pixel map

    for neuron in Vm_lists:
        xi = 0
        Vms = Vm_lists[neuron]
        maximum = max(Vms)
        minimum = min(Vms)
        Vm_range = maximum - minimum
        for Vm in Vms:
            print int( Vm_range - abs(Vm) )
            pixels[xi, neuron] = (int( Vm_range - abs(Vm) ) * 255, 0, 255 - int( Vm_range - abs(Vm) ) * 255)
            xi += 1
    return img
