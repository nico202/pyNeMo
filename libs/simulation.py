#!/bin/python2

def simulation(
    Nsim,
    save = [],
    steps = -1,
    stims = {},
    fspikes = {},
    sensory_in = {},
    sensory_out = [], #List of [port_name, out_dof, [ids]]
    robot_name = '/doublePendulumGazebo/body',
    robot_mode = "Torque",
    reset_position = True,
):
    if sensory_in or sensory_out: #import only if needed
        import libs.pySpike
        import sys
        robot = libs.pYARP.YARPInterface(
            robot = robot_name,
            mode = robot_mode)
        #FIXME: pass those as paramater to simulation()
        robot.changeRefSpeed(1)
        robot.changeRefAcc(1)
        #Set robot to initial state
        if reset_position:
            robot.write(0, 0)
            robot.write(1, 0)
            robot.reach()

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
        #import subprocess   #We pause the world, to keep it in sync with the sim
        #FIXME: USE pygazebo bindings
        #subprocess.call("gz world -p 1", shell = True) #pause

        sens_net_in = []
        for nid in range(0, len(sensory_in)):
            #FIXME: add other params
            sens_net_in.append(
                libs.pySpike.sensNetIn(neuron_number = len(sensory_in[nid]))
            )

        sens_net_out = []
        sens_robot_out = []
        sens_out_map = {}
        for nid in range(0, len(sensory_out)):
            for i in range(0, len(sensory_out[nid][2])):
                sens_out_map[sensory_out[nid][2][i]] = i
            sens_net_out.append(
                libs.pySpike.sensNetOut(neuron_number = len(sensory_out[nid][2]))
            )
            sens_robot_out.append(
                [libs.pYARP.YARPInterface(sensory_out[nid][0]), sensory_out[nid][1]]
            )
    angles = [ [0] ] * len(sensory_out)#Used for analysis
    ##########################LOOP ############################################
    while steps: #go until 0 or indefinitely
#FIXME: How to sync yarp/gazebo time? If possible we should trigger a step here
        loop = total - steps
        if sensory_in:
            for grp in range(0, len(sensory_in)):
                s_vals = robot.read("All")
                sens_net_in[grp].setInput(s_vals[grp])
        grp_n = 0
        for grp in sensory_in:
            for sens, nsidx in grp.iteritems(): #List
                if not loop in stims: #initialize
                    stims[loop] = []
                # Add stimul suple list
                injection = sens_net_in[grp_n].getCurrent(nsidx)
                stims[loop].append( (sens, injection) )
            grp_n +=1
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
            angle = sens_net_out[nid].step([ sens_out_map[u] for u in sensory_fired])
            #write joint, angle
            sens_robot_out[nid][0].write(sens_robot_out[nid][1], angle)
            #Run a gazebo step
            #subprocess.call("gz world -s", shell = True) #FIXME: pygazebo bindings
            angles[nid].append(angle) #Analysis
            nid += 1

        for neuron in save: #Save membrane potential
            membrane_output[neuron].append(Nsim.get_membrane_potential(neuron))
        output_firings[loop] = [ i for i in fired ]
        steps -= 1
    #Loop ended. Returns
    return output_firings, membrane_output, stims, angles
