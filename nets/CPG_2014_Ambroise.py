from libs.templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S
name = "Ambroise_2014"
#neurons
N = 1
neurons = [ #TODO: support other type of neurons? Right now, IZ only
     RS * N
]

save = range(0, N)

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all
_etero_synapse_inh = _S("StrongInhSlowNoLearn")

synapses = [
    [0, [3], _etero_synapse_inh],
    [1, [2], _etero_synapse_inh],
    [2, [0, 6], _etero_synapse_inh],
    [3, [1, 7], _etero_synapse_inh],
    [4, [7], _etero_synapse_inh],
    [5, [6], _etero_synapse_inh],
    [6, [4, 2], _etero_synapse_inh],
    [7, [5, 3], _etero_synapse_inh],
]
