#IF YOU EDIT THIS FILE, PLEASE run "git commit -a" OR YOU'LL FACE WRONG CONFIGS

#This files is use for quickly add neurons /synapses to a net_config
from libs.FasterPresets import _typicalN, _typicalS, _S
#from random import random as _rand
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

#http://www.izhikevich.org/publications/whichmod.pdf
#Examples: http://www.izhikevich.org/publications/spikes.pdf
#Excitatory
#DO_NOT_TOUCH
RS = _typicalN(a = 0.02, b = 0.2, c = -65, d = 8) #regular spiking (Ambroise 2014)
#DO_NOT_TOUCH
IB = _typicalN(c = -55, d = 4) #intrinsically bursting
#DO_NOT_TOUCH
CH = _typicalN(c = -50) #chattering
#DO NOT TOUCH
TC = _typicalN(b = 0.25, d = 0.05)
RS1 = _typicalN(a = 0.02, b = 0.2, c = -65, d = 8)
RS2 = _typicalN(a = 0.02, b = 0.3, c = -65, d = 8)
RZ = _typicalN(a = 0.1, b = 0.25)
#Inhibitory
#DO_NOT_TOUCH
FS = _typicalN(a = 0.1) #Fast spiking
#DO_NOT_TOUCH
LTS = _typicalN(b = 0.25) #low-treshold spiking

LTSS = _typicalN(b = 0.27) #low-treshold spiking
LFS = _typicalN(a = 0.01, b = 0.05, d = 10) #Fast spiking
LTS_no_spontaneous = _typicalN(a = 0.01, b = 0.05, d = 10, s = 0)
#Synapes
FastLearn = (1, 20, True)
FastNoLearn = (1, 20, False)
SlowNoLearn = (3, 20, False)
InhSlowNoLearn = (5, -25, False)
InhFastNoLearn = (1, -25, False)
SmallInhFastNoLearn = (1, -1, False)
MediumInhFastNoLearn = (1, -20, False)
BigInhFastNoLearn = (1, -100, False)

InhibitoryTypeI = (2, -20, True)
ExcitatoryTypeI = (1, +2, True)
