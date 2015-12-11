#!/bin/python2

def simulation(
    Nsim,
    save = [],
    steps = -1,
    stims = {},
    fspikes = {},
    sensory_in = {},
    sensory_out = [] #List of [port_name, out_dof, [ids]]
):
    if sensory_in or sensory_out: #import only if needed
        import libs.pySpike
        import sys
        #FIXME: pass robot name as paramater to simulation()
        robot = libs.pYARP.YARPInterface('/doublePendulumGazebo/body')
        #FIXME: pass those too
        robot.changeRefSpeed(1)
        robot.changeRefAcc(1)
        robot.write(0, 0)
        robot.write(1, 0)

    #FIXME:Indefinite loop?
    steps = steps or -1
    #Returns the following
    membrane_output = {}
    output_firings = {}
    #Initialize dict
    for i in save:
        membrane_output[i] = [] #We save the dict containing neurons_Vm

    total = steps
    if sensory_in or sensory_out:
        #FIXME: add other params
        sens_net = libs.pySpike.sensNetIn(neuron_number = len(sensory_in))
        sens_net_out = []
        sens_robot_out = []
        for nid in range(0, len(sensory_out)):
            sens_net_out.append(
                libs.pySpike.sensNetOut(neuron_number = len(sensory_out[nid][2]))
            )
            sens_robot_out.append(
                [libs.pYARP.YARPInterface(sensory_out[nid][0]), sensory_out[nid][1]]
            )
    angles = [ [0] ] * len(sensory_out)#Used for analysis
    while steps: #go until 0 or indefinitely
#FIXME: How to sync yarp/gazebo time? If possible we should trigger a step here
        loop = total - steps
        if sensory_in:
            s_val = robot.read(1) #FIXME: DoF
            sens_net.setInput(s_val)

        for sens, nsidx in sensory_in.iteritems(): #List
            if not loop in stims: #initialize
                stims[loop] = []
            # Add stimul suple list
            injection = sens_net.getCurrent(nsidx)
            stims[loop].append( (sens, injection) )
        #Optimize this for speed if not stim given
        if loop in stims:
            fired = Nsim.step(istim = stims[loop])
        elif loop in fspikes:
            fired = Nsim.step(fstim = fspikes[loop])
        else:
            fired = Nsim.step()
        #Update YARP
        nid = 0
        for s_out in sensory_out: #List of lists
            sensory_fired = list(set(fired) & set(s_out[2]))
            angle = sens_net_out[nid].step(sensory_fired)
            sens_robot_out[nid][0].write(sens_robot_out[nid][1], angle)
            angles[nid].append(angle) #Analysis
            nid += 1

        for neuron in save: #Save membrane potential
            membrane_output[neuron].append(Nsim.get_membrane_potential(neuron))
        output_firings[loop] = [ i for i in fired ]
        steps -= 1
    #Loop ended. Returns
    return output_firings, membrane_output, stims, angles
