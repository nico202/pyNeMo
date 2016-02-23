#!/usr/bin/env python2
import Image

def showImageFile(image_path):
    try:
        img = Image.open(image_path)
        img.show()
    except IOError:
        print ("ERROR: cannot load image (Image file does not exists)")

def saveRawImage(img, name, close = True):
    try:
        img.save(name)
    except AttributeError:
        try:
            img.savefig(name)
            if close:
                img.close()
        except:
            raise
    return True

def ImageFromSpikes(input_spikes, file_path = "", show = True, save = True):
    '''Input: get converted to:
    spikes = list of lists (neurons) of ms
    ie. [[1, 3, 5], [2, 4, 5]] # 2 neurons, 3 spikes/neuron, ms 1, 3...
    '''
    from sys import exit
    try:
        from neuronpy.graphics import spikeplot
    except ImportError:
        print ("You need nepuronpy to create spikes images\n\
        (as root) pip2 install neuronpy; pip2 install matplotlib")
        return False
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
    sp = spikeplot.SpikePlot(savefig=save)
    sp.set_fig_name(file_path)
    sp.set_linestyle('-')
    sp.set_markerscale(0.8)
    sp.plot_spikes(spikes, draw=show)
    return True

def ImageFromMembranes(all_membranes):
    for neuron_id in all_membranes:
        image = ImageFromMembrane(
            neuron_id
            , all_membranes[neuron_id]
            , False, True)
        image.show()

    return

def ImageFromMembrane(
        neuron_id
        , Vm_list
        , save = False
        , show = True
        , stimuli = []
        , title = ""
):
    import matplotlib.pyplot as plt
    import numpy as np
    x = len(Vm_list)
    x = np.array(range (0, x))
    fig, ax1 = plt.subplots()
    ax1.plot(x, np.array(Vm_list))
    ax1.set_xlabel('time (ms)')
    ax1.set_ylabel('Membrane Potential\n(mV)')
    ax2 = ax1.twinx()
    ax2.plot(stimuli, color = 'r')
    ax2.set_ylabel('Stimulation\n(mA)')
    max_val = 20
    ax2.set_ylim(
        min(-5, min(stimuli) if stimuli else 0)
        ,max(max_val, max(stimuli) if stimuli else max_val)
    )
    if title:
        plt.title(title)

    return plt
