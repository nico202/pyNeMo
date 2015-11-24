#This files is use for quickly add neurons /synapses to a net_config

#IF YOU EDIT THIS FILE, PLEASE run "git commit -a" OR YOU'LL FACE WRONG CONFIGS

#YES, 2 brackets. This allow us to use NeuronType * Nuber
#neurons: a, b, c, d, s, u, v
FastSpiking = [(0.2, 0.5, -65, 8, 5, 0.2 * -65, -65)]
SlowSpiking = [(0.002, 0.4, -65, 8, 0, 0.2 * -65, -65)]
RandomSpiking = [(0.2, 0.5, -65, 8, 20, -10, -65)]

#Synapes
FastLearn = (1, 20, True)
InhibitoryTypeI = (2, -20, True)
ExcitatoryTypeI = (1, +20, True)
