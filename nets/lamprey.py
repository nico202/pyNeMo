
from libs.templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli, _typicalN

#No prehooks
#Variables Loaded from the rhombus
#NEURONS
CIN = TonicBursting
EIN = PhasicBursting
MN = PhasicBursting

#SYNAPSES
EXC0 = _S("ExcFastNoLearnStrong")
EXC1 = _S("ExcFastNoLearnStrong")
EXC2 = _S("ExcFastNoLearnStrong")
INH0 = _S("InhFastLearnMedium")
INH1 = _S("InhFastNoLearnStrong")
INH2 = _S("InhStrongNoLearn")

#STIMULI
_stim_a = 8
_stim_b = 8
_start_a = 0
_start_b = 100
_stop_a = 300
_stop_b = 800

cerebellum_ctrl = (0, 0, 0)

cerebellum_ctrl=(0.04,800,35000);_stim_a=1.7;_stim_b=1.4;_start_b=45;_stop_a=138;_stop_b=138;CIN=_typicalN(a=0.04,b=0.2,c=-64.0,d=3.9,v=-72)

name = "nets/lamprey"
neurons = [
    CIN
 +
    CIN
 +
    EIN
 +
    EIN
 +
    MN
 +
    MN
]
sensory_neurons = [ #0 = ins, #1 = outs
[ #ins (std, Joint, min_angle, max_angle, [dests])
],
[ #outs (joint, [inputs])
]
]

save = [ 4, 5 ]

synapses = [
    [ 0, [1], INH0],
    [ 1, [0], INH0],
    [ 1, [2], INH1],
    [ 0, [3], INH1],
    [ 2, [0], EXC0],
    [ 3, [1], EXC0],
    [ 1, [4], INH2],
    [ 0, [5], INH2],
    [ 2, [4], EXC2],
    [ 3, [5], EXC2],
    [ 3, [3], EXC1],
    [ 2, [2], EXC1]
]

step_input = _stimuli([
	[3,	(	_stim_b,	 _start_b,	 _stop_b)	],
	[2,	(	_stim_a,	 _start_a,	 _stop_a)	],
	[0,		cerebellum_ctrl	],
	[1,		cerebellum_ctrl	],

])
step_spike = {}
