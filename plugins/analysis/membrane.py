#!/bin/python2
#

def analyzeMembrane(neurons_membrane):
    '''Input:   dict of lists of neuron membrane potential
    Output:     dict'''
    pi = 3.141592653589793
    output = {
        "fundamental": [],
        "phase_shift": [0], #First shift assumed to be 0
        "duty_cycle": []
    } #Formatted output
    n = []
    from numpy import fft, angle, mean
    #Convert dict into list. Should we use lists directly?
    for neuron in neurons_membrane:
        n.append(neurons_membrane[neuron])

    sample_n = len(n[0]) #Assume all neurons have same sample number

    first = True
    for Vm_list in n:
        fft_filtered = fft.fft(Vm_list-mean(Vm_list))
        fft_unfiltered = fft.fft(Vm_list)
        fundamental = list(abs(fft_filtered)).index(max(list(abs(fft_filtered)[0:sample_n/2])))
        fundamental_hz = fundamental *1000/sample_n #sample to Hz correction
        threshold = mean(abs(fft.ifft(list(abs(fft_unfiltered[0:sample_n/5]))+([0]*(sample_n*4/5)))))
        square = [ sample > -threshold for sample in Vm_list ]
        duty_cycle = mean(square)
        #Appends
        output["fundamental"].append(fundamental_hz)
        output["duty_cycle"].append(duty_cycle)
        if first:#find ref
        #We need a ref for the phase shift. Use the first neuron, and calculate the
        #differences from the others. If the fundamental is different we should save
        #a list of shifts?
            phase_shift_ref = angle(fft_unfiltered)[fundamental-1:fundamental+2]/(2*pi * fundamental_hz)*1000/sample_n
            phase_freq_ref = fundamental
            first = False
        else:   #FIXME: sensible to sumple number. Fix
            if fundamental == phase_freq_ref:
                phase_shift = (angle(fft_unfiltered)[fundamental-1:fundamental+2] - phase_shift_ref)/(2*pi * fundamental_hz)/sample_n

            else: #Create a list?
                phase_shift = (angle(fft_filtered) - phase_shift_ref)/(2*pi * fundamental_hz)*sample_n
                phase_shift = list(phase_shift) #List, not numpy array
            output["phase_shift"].append(phase_shift)
    return output

    #First is used as a ref
