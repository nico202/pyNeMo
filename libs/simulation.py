#!/bin/python2

def simulation(
    Nsim,
    save = [],
    steps = -1,
    stims = {},
    fspikes = {}
):
    #Indefinite loop?
    steps = steps or -1
    #Returns the following
    membrane_output = {}
    output_firings = {}

    #Initialize dict
    for i in save:
        membrane_output[i] = [] #We save the dict containing neurons_Vm

    total = steps

    while steps: #go until 0 or indefinitely
        loop = total - steps
        #Optimize this for speed if not stim given
        if loop in stims:
            fired = Nsim.step(istim = stims[loop])
        elif loop in fspikes:
            fired = Nsim.step(fstim = fspikes[loop])
        else:
            fired = Nsim.step()

        for neuron in save: #Save membrane potential
            membrane_output[neuron].append(Nsim.get_membrane_potential(neuron))
        output_firings[steps] = [ i for i in fired ]
        steps -= 1
    #Loop ended. Returns
    return output_firings, membrane_output
