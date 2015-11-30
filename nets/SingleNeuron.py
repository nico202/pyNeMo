from templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli
name = "RS"
#neurons

N = 1
neurons = [ #TODO: support other type of neurons? Right now, IZ only
     RS
]

save = range(0, N)
#stimuli = neuron, from step, to step

step_input = _stimuli(
    [
        [0, 10, 200, 400]
    ]
)
step_spike = {}
#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all

synapses = [
]
