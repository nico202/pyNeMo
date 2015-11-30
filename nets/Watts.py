from templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli
name = "Watts"
#neurons
neurons = [ #TODO: support other type of neurons? Right now, IZ only
    RS1 +
    RS2
]

save = range(0, len(neurons))

step_input = _stimuli(
    [
        [[0,1], 10, 10, 20],
    ]
)
step_spike = {}

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all

synapses = [
    [0, [1], _S("WeakExc")],
    [1, [0], _S("MediumInh")],
    [0, [0], _S("MediumInh")]
]
