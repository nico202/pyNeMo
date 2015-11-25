#This files is use for quickly add neurons /synapses to a net_config
from FasterPresets import typicalN, typicalS

#IF YOU EDIT THIS FILE, PLEASE run "git commit -a" OR YOU'LL FACE WRONG CONFIGS
#IF testing new nets, use the option "--force"

#YES, 2 brackets. This allow us to use NeuronType * Nuber
#Parameters IZ: http://www.izhikevich.org/publications/spikes.pdf
#a: typ = 0.02      time scale of recovery variable (u)
#b: typ = 0.2       sensitivity of recovery variable (u) on subtreshold
#c: typ = -65       after-spike reset value
#d: typ = 2         after-spike recovery variable (u)

#neurons: a, b, c, d, s, u, v
FastSpiking = [(0.2, 0.5, -65, 8, 5, 0.2 * -65, -65)]
SlowSpiking = [(0.002, 0.4, -65, 8, 0, 0.2 * -65, -65)]
RandomSpiking = [(0.2, 0.5, -65, 8, 20, -10, -65)]
CaoticSpiking = [(0.2, 2, -56, -16)] #http://www.izhikevich.org/publications/whichmod.pdf
#Examples: http://www.izhikevich.org/publications/spikes.pdf
#Excitatory
RS = typicalN(c = -65, d = 8) #regular spiking
IB = typicalN(c = -55, d = 4) #intrinsically bursting
CH = typicalN(c = -50, d = 2) #chattering

#Inhibitory
FS = typicalN(a = 0.1) #Fast spiking
LTS = typicalN(b = 0.25) #low-treshold spiking

#Synapes
FastLearn = (1, 20, True)
InhibitoryTypeI = (2, -200, True)
ExcitatoryTypeI = (1, +2, True)
