from templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli
name = "Watts"
#neurons
neurons = [ #TODO: support other type of neurons? Right now, IZ only
    IB +
    IB
]

save = range(0, len(neurons) + 1)

step_input = _stimuli(
    [
        [0, 10, 200, 300],
    ]
)
step_spike = {}

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all

synapses = [
    [0, [1], _S("StrongExc")],
    [1, [0], _S("StrongInhSlow")],
    [0, [0], _S("StrongInh")]
]
