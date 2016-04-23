#!/usr/bin/env python2
from PIL import Image
from libs.IO import cprint

try:
    from neuronpy.graphics import spikeplot
except ImportError:
    cprint("You need nepuronpy to create spikes images\n\
    (as root) pip2 install neuronpy; pip2 install matplotlib", 'fail')
sp = spikeplot.SpikePlot(savefig=True)

def showImageFile(image_path):
    try:
        img = Image.open(image_path)
        img.show()
    except IOError:
        cprint("ERROR: cannot load image (Image file does not exists)", 'fail')

def saveRawImage(img, name, close=True):
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

def ImageFromSpikes(input_spikes,
                    file_path="./latest.png",
                    show=True,
                    save=True,
                    xmin=False,
                    xmax=False):
    '''Input: get converted to:
    spikes = list of lists (neurons) of ms
    ie. [[1, 3, 5], [2, 4, 5]] # 2 neurons, 3 spikes/neuron, ms 1, 3...
    '''
    global sp
    from plugins.importer import spikesDictToArray

    spikes = spikesDictToArray(input_spikes)
    if xmax or xmin: #TODO: Use numpy (faster) v1.0
        new_spikes = []
        for i in spikes:
            i = [l for l in i if l < xmax and l > xmin]
            new_spikes.append(i)
        spikes = new_spikes

    if save:
        cprint("\t*\tSaving image to %s" % file_path, 'info')
    sp.set_fig_name(file_path)
    sp.set_linestyle('-')
    sp.set_markerscale(0.8)
    sp.plot_spikes(spikes, draw=show, savefig=save)
#    del sp #fixes memory leak? Seems not
    del spikes
    del input_spikes
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
        neuron_id,
        Vm_list,
        save=False,
        show=True,
        stimuli=[0, 0],
        title=""
):
    import matplotlib.pyplot as plt
    import numpy as np
    x = len(Vm_list)
    x = np.array(range(0, x))
    fig, ax1 = plt.subplots()
    ax1.plot(x, np.array(Vm_list))
    ax1.set_xlabel('time (ms)')
    ax1.set_ylabel('Membrane Potential\n(mV)')

    ax2 = ax1.twinx()
    ax2.plot(stimuli, color='r')
    ax2.set_ylabel('Stimulation\n(mA)')
    max_val = 20
    ax2.set_ylim(
        min(-5, min(stimuli)),
        max(max_val, max(stimuli))
    )
    if title:
        plt.title(title)

    return plt

def ImageFromAngles(
        (angles_read
         , angles_wrote)
        , save=True
        , show=False
        , title="Joints Angles"
        , file_path='./latest.png'
): #Similar to ImageFromMembrane?
    import matplotlib.pyplot as plt
    import numpy as np
    from itertools import repeat
    if not len(angles_read):
        print "No angles data!"
        return False

    jnt_number = len(angles_read[0])
    # Create a list of lists (every list is one jnt)
    angles_out = [[] for i in repeat(None, jnt_number)]
    for ms, values in enumerate(angles_read):
        for jnt, angle in enumerate(values):
            angles_out[jnt].append(angle)

    angles_in = [[] for i in repeat(None, jnt_number)]
    for ms, values in enumerate(angles_wrote):
        for jnt, angle in values:
            angles_in[jnt].append(angle)
    
    plots = []
    init = False
    min_x = -90
    max_x = 90
    for l in angles_out:
        min_x = min(min_x, min(l))
        max_x = max(max_x, max(l))

    x = np.array(range(0, len(l)))
    fig, ax1 = plt.subplots()
    plots.append(ax1)
    for joint, l in enumerate(angles_out + angles_in):
        if not init:
            plots[0].plot(x, np.array(l))
            plots[0].set_xlabel('time (ms)')
            plots[0].set_ylabel('Angle Joint %s' % joint)
            plots[0].set_ylim([min_x, max_x])
        else:
            plots.append(plots[-1].twinx())
            # plots[-1].plot(x, np.array(l))
            plots[-1].plot(l, color=np.random.rand(3,))
            plots[-1].set_xlabel('time\n(ms)')
            plots[-1].set_ylabel('Angle Joint %s' % joint)
            plots[-1].set_ylim([min_x, max_x])
        init = True

    if title:
        plt.title(title)

    if save:
        cprint("\t*\tSaving image to %s" % file_path, 'info')
        plt.savefig(file_path)

    return True
