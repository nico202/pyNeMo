#!/usr/bin/env python2
from PIL import Image
from libs.IO import cprint

try:
    from neuronpy.graphics import spikeplot
except ImportError:
    cprint ("You need nepuronpy to create spikes images\n\
    (as root) pip2 install neuronpy; pip2 install matplotlib", 'fail')
sp = spikeplot.SpikePlot(savefig=True)

def showImageFile(image_path):
    try:
        img = Image.open(image_path)
        img.show()
    except IOError:
        cprint ("ERROR: cannot load image (Image file does not exists)", 'fail')

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

def ImageFromSpikes(input_spikes, file_path = "./latest.png", show = True, save = True, xmin = False, xmax = False):
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
        neuron_id
        , Vm_list
        , save=False
        , show=True
        , stimuli = [0, 0]
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
        min(-5, min(stimuli))
        ,max(max_val, max(stimuli))
    )
    if title:
        plt.title(title)

    return plt

def ImageFromAngles(
        (angles_input
        , pyspike_output)
        , save=True
        , show=False
        , title="Joints Angles"
        , file_path='./latest.png'
): #Similar to ImageFromMembrane?
    import matplotlib.pyplot as plt
    import numpy as np
    
    angles_read = angles_input
    angles_wrote = pyspike_output
    if not len(angles_read):
        print("No angles data!")
        return False

    
    # for ms_couple in angles_wrote:
    #     for i, data in enumerate(ms_couple):
            
#        print angles_wrote
    #FIXME: non riesco ad assegnare a una lista O.o
    jnt_number = len(angles_read[0])
    angles_A = [] 
    angles_B = []
    i = 0
    for coppia in angles_read:
        angles_A.append(coppia[:][0])
        angles_B.append(coppia[:][1])
        i += 1
    angles = [angles_A, angles_B]
    plots = []
    init = False
    #FIXME: one plot above the other
    # for values in angles:
    #     x = len(values)
    #     x = np.array(range(0, x))
    #     if not init:
    #         fig, ax1 = plt.subplots()
    #         plots.append(ax1)
    #         plots[0].plot(x, np.array(values))
    #         plots[0].set_xlabel('time (ms)')
    #         plots[0].set_ylabel('Angle Joint %s' % joint)
    #     else:
    #         plots.append(plots[0].twinx())
    #         plots[-1].plot(values, colors = 'r')
    #         plots[-1].set_xlabel('time\n(ms)')
    #         plots[-1].set_ylabel('Angle Joint %s' % joint)
    #     init = True

    a = len(angles[0])
    b = len(angles[1])
    a = np.array(range(0, a))
    b = np.array(range(0, b))

    fig, ax1 = plt.subplots()
    plots.append(ax1)
    ax1.plot(a, np.array(angles[0]))
    ax1.set_xlabel('time (ms)')
    ax1.set_ylabel('Angle Joint %s' % (1))
    ax1.set_ylim([-90, 90])

    ax2 = ax1.twinx()
    ax2.plot(angles[1], color = 'r')
    ax2.set_xlabel('time (ms)')
    ax2.set_ylabel('Angle Joint %s' % (2))    
    ax2.set_ylim([-90, 90])

    if pyspike_output:
        out_zero = []
        out_one = []
        for ms in pyspike_output:
            out_zero.append(ms[0][1])
            out_zero = out_zero[:]
            out_one.append(ms[1][1])
            out_one = out_one[:]

        ax3 = ax2.twinx()
        ax3.plot(out_zero, color = 'g')
        ax3.set_xlabel('time (ms)')
        ax3.set_ylabel('pySpike %s' % (2))    
        ax3.set_ylim([-90, 90])

        ax4 = ax3.twinx()
        ax4.plot(out_one, color = 'c')
        ax4.set_xlabel('time (ms)')
        ax4.set_ylabel('pySpike %s' % (2))    
        ax4.set_ylim([-90, 90])

    if title:
        plt.title(title)
        
    if save:
        cprint("\t*\tSaving image to %s" % file_path, 'info')
        plt.savefig(file_path)
        
    return True
    
