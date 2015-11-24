#This files is use for quickly add neurons /synapses to a net_config

#IF YOU EDIT THIS FILE, PLEASE run "git commit -a" OR YOU'LL FACE WRONG CONFIGS

#Neurons #YES, 2 brackets. This allow us to use NeuronType * Nuber
#neurons: a, b, c, d #FIXME: add state parameters (v, u)
FastSpiking = [(0.2, 0.5, -65, 8)]
SlowSpiking = [(0.002, 0.4, -65, 8)]

#Synapes
FastLearn = (1, 20, False)
