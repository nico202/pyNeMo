#!/bin/python2
"""
Useful helper function for creating synapses, neurons, and stimuli
"""
#On function defined here, the "_" is mandatory

def _typicalN( #DO NOT TOUCH
        a=0.02,   # time scale of recovery variable (u)
        b=0.2,    # sensitivity of recovery variable (u) on subtreshold
        c=-65,    # after-spike reset value
        d=2,      # after-spike recovery variable (u)
        s=0,      # input bias picked from gaussian [0, s)
        u=False,  # default calculated down here
        v=-65     # Initial membrane potential
    ):
    if not u:
        u = b * v
    return [(a, b, c, d, s, u, v)]

def _randomN(): #TODO: WriteMe
    from random import random
    exit("_randomN has still to be written!")
    return [(a, b, c, d, s, u, v)]    

def _typicalS(d=1, w=10, l=False): #TODO: not tested
    """
Creates a synapse with default values where omitted.
_typicalS(d=delay, w=weight, l=learn)
Return a list containing a tuple: [(delay, weight, learn)]
    """
    #return fixing unsupported values
    return [(d if d >= 1 else 1, w, True if l else False)]

def _S(Stype="WeakInhFastNoLearn"):
    """
        Convert a string into a synapse
    """
    #Delay:
    if 'Fast' in Stype:
        delay = 1
    elif 'Slowest' in Stype:
        delay = 15
    elif 'Slower' in Stype:
        delay = 10
    elif 'Slow' in Stype:
        delay = 5
    else:
        delay = 1

    #Weight:
    if 'Weak' in Stype:
        weight = 1
    elif 'WeaMed' in Stype:
        weight = 5
    elif 'Medium' in Stype:
        weight = 10
    elif 'Strongest' in Stype:
        weight = 200
    elif 'Stronger' in Stype:
        weight = 50
    elif 'Strong' in Stype:
        weight = 20
    else:
        weight = 10

    #Inhibitory/Excitatory
    if 'Inh' in Stype:
        weight = - weight
    elif 'Exc' in Stype:
        weight = abs(weight)

    #Learn?
    if 'NoLearn' in Stype:
        learn = False
    elif 'Learn' in Stype:
        learn = True
    else:
        learn = False

    return (delay, weight, learn)

def _stimuli(input_list):
    """
        Convert the input list of the kind:
            [[neuron#, value, stimul from, stimul to]]
        to a dict:
            {step: [(neuron#, value), (..), ..]}
    """
#    try:
#
#        input_list = _proportional_stimuli(input_list)
#    except IndexError:
#        pass
    output_dict = {}
    for stimul in input_list:
        for step in range(int(stimul[1][1]), int(stimul[1][2])):
            neurons, input_value = stimul[0], stimul[1][0]
            if not isinstance(neurons, list):
                neurons = [neurons]
            for neuron in neurons:
                if not step in output_dict:
                    output_dict[step] = []
                stim_tuple = (neuron, float(input_value))
                output_dict[step].append(stim_tuple)
    return output_dict

def _proportional_stimuli(input_list):
    """
        [
            [neuron#, (step, offset, multi), stimul from, stimul to]
        ]
        is converted to the default list that feeds _stimulti
    """
    output = []
    n = 0
    for stimul in input_list:
        neuron, (value, offset, multi), start, stop = stimul

        for i in range(0, stop - start):
            output.append(
                [
                    neuron,
                    multi * (value * (i + 1)) + offset,
                    i + start,
                    (i + 1) + start,
                ]
            )

        n += 1
    return output
