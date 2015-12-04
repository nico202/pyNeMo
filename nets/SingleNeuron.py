from templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S, _stimuli, _proportional_stimuli
name = "Accomodation"
#neurons

N = 1

neurons = [ #TODO: support other type of neurons? Right now, IZ only
     locals()[name] #Changing network name allows neuron change
]

save = range(0, N)
#stimuli = neuron, from step, to step

step_input = _stimuli(
    [
        [0, (0.04, 0, 10), 0, 20],
        [0, (0.04, 1, 1/50), 300, 312]
    ]
)

#step_input = _stimuli(
#    _proportional_stimuli(
#        [
#            [0, (0, -0.5, 1), 0, 30],
#            [0, (1, -0.5, 0.015), 30, 300],
#            [0, (0, -0.5, 1), 300, 350]
#        ]
#    )
#)
step_spike = {}
#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all

synapses = [
]
