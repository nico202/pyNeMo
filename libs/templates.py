#This files is use for quickly add neurons /synapses to a net_config
from FasterPresets import _typicalN, _typicalS, _S
#from random import random as _rand
#IF testing new nets, use the option "--force"

#Parameters IZ: http://www.izhikevich.org/publications/spikes.pdf
#a: typ = 0.02      time scale of recovery variable (u)
#b: typ = 0.2       sensitivity of recovery variable (u) on subtreshold
#c: typ = -65       after-spike reset value
#d: typ = 2         after-spike recovery variable (u)
#s: typ = 0         input bias picked from gaussian [0, s)
#u: typ = b * v
#v: typ = -65
#Right now using function requires the conversion to list (to prevent saving it as a pointer to function)
#YES, 2 brackets. This allow us to use NeuronType * Nuber
#neurons: a, b, c, d, s, u, v
#http://www.izhikevich.org/publications/figure1.m

lamprey = _typicalN(a = 0.01, b = 0.2, c = -75, d = 9)
#DO_NOT_TOUCH
TonicSpiking = _typicalN(d = 6, v = -70, u = 0.2 * -65)
#DO_NOT_TOUCH
PhasicSpiking = _typicalN(b= 0.25, d = 6, v = -64)
#DO_NOT_TOUCH
TonicBursting = _typicalN(c = -50, d = 2, v = -70)
#DO_NOT_TOUCH
PhasicBursting = _typicalN(b = 0.25, c = -55, d = 0.05, v = -64)
#DO_NOT_TOUCH
MixedMode = _typicalN(c = -55, d = 4, v = -70)
#DO_NOT_TOUCH
SpikeFreqAdapt = _typicalN(a=0.01, d = 8, v = -70)
#DO_NOT_TOUCH
#NOT WORKING
ClassIExc = _typicalN(b=-0.1, c= -55, d = 6, v = -60)
#DO_NOT_TOUCH
ClassIIExc = _typicalN(a=0.2, b=0.26, c=-65, d = 0, v = -64)
#DO_NOT_TOUCH
SpikeLatency = _typicalN(a=0.02, d = 6, v = -70)
#DO_NOT_TOUCH
SubtresholdOSC = _typicalN(a=0.05,b=0.26,c=-60, d=0,v=-62)
#DO_NOT_TOUCH
Resonator = _typicalN(a=0.1, b=0.26, c=-60, d=-1, v=-62)
#DO_NOT_TOUCH
Accomodation = _typicalN(b=1, c=-55, d=4, v=-65, u=-16)

#DO_NOT_TOUCH
Bistability = _typicalN(a=0.1, b=0.26, c=-60, d=0, v=-61)


TonicBurstingTesting = _typicalN(c = -50, d = 2, v = -70)

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
#DO NOT TOUCH
RZ = _typicalN(a = 0.1, b = 0.25)

RS1 = _typicalN(a = 0.02, b = 0.2, c = -65, d = 8)
RS2 = _typicalN(a = 0.02, b = 0.3, c = -65, d = 8)

#Inhibitory
#DO_NOT_TOUCH
FS = _typicalN(a = 0.1) #Fast spiking
#DO_NOT_TOUCH
LTS = _typicalN(b = 0.25) #low-treshold spiking

LTSS = _typicalN(b = 0.27) #low-treshold spiking
LFS = _typicalN(a = 0.01, b = 0.05, d = 10) #Fast spiking
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
