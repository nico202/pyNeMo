
from libs.templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli, _typicalN

#PreHooks:
#No prehooks
#Variables Loaded from the rhombus
#NEURONS
#CIN = TonicBursting
CIN = _typicalN(c=-50.3, d=2.1, v=-72)
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
_stim_a = 1.7
_stim_b = 1.4
_start_a = 0
_start_b = 57
_stop_a = 114
_stop_b = 114

cerebellum_ctrl = (0.02,800,60000)

min_angle = -45
max_angle = 45

#PostHooks:
#No posthooks

name = "nets/lamprey_YARP"
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
	[ 0, 0.5, min_angle, max_angle, [4, 5] ],
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
