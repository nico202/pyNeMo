from templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli
name = "Watts"
#neurons
neurons = [ #TODO: support other type of neurons? Right now, IZ only
    Bistability +
    Bistability
]

save = range(0, len(neurons) + 1)

step_input = _stimuli(
    [
        [0, 1, 200, 205],
        [0, 1, 235, 240],
        [0, 1, 270, 275],
        [0, 1, 305, 310],
        [0, 1, 340, 345]
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

]
