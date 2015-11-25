#This files is use for quickly add neurons /synapses to a net_config
from FasterPresets import _typicalN, _typicalS

#IF YOU EDIT THIS FILE, PLEASE run "git commit -a" OR YOU'LL FACE WRONG CONFIGS
#IF testing new nets, use the option "--force"

#Parameters IZ: http://www.izhikevich.org/publications/spikes.pdf
#a: typ = 0.02      time scale of recovery variable (u)
#b: typ = 0.2       sensitivity of recovery variable (u) on subtreshold
#c: typ = -65       after-spike reset value
#d: typ = 2         after-spike recovery variable (u)
#s: typ = 0         input bias picked from gaussian [0, s)
#Right now using function requires the conversion to list (to prevent saving it as a pointer to function)
#YES, 2 brackets. This allow us to use NeuronType * Nuber
#neurons: a, b, c, d, s, u, v
FastSpiking = [(0.2, 0.5, -65, 8, 5, 0.2 * -65, -65)]
SlowSpiking = [(0.002, 0.4, -65, 8, 0, 0.2 * -65, -65)]
RandomSpiking = [(0.2, 0.5, -65, 8, 20, -10, -65)]
CaoticSpiking = [(0.2, 2, -56, -16)] #http://www.izhikevich.org/publications/whichmod.pdf
#Examples: http://www.izhikevich.org/publications/spikes.pdf
#Excitatory
RS = _typicalN(c = -65, d = 8) #regular spiking
IB = _typicalN(c = -55, d = 4) #intrinsically bursting
CH = _typicalN(c = -50, d = 2) #chattering

#Inhibitory
FS = _typicalN(a = 0.1) #Fast spiking
LTS = _typicalN(b = 0.25) #low-treshold spiking

#Synapes
FastLearn = (1, 20, True)
InhibitoryTypeI = (2, -200, True)
ExcitatoryTypeI = (1, +2, True)
