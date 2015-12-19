from libs.templates import * #For ease of use, this line is mandatory
from libs.FasterPresets import _S
name = "Lewis_2005"

#neurons
_neuron_type = RS2 #Faster!

neurons = [ #TODO: support other type of neurons? Right now, IZ only
    _neuron_type * 4
]

save = range(0, 3)

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all
_synapse_type =  _S("FastNoLearnInh")   #Faster change!
_self_synapse_type = _S("StrongestSlowestNoLearnInh")
synapses = [
    [0, [1], _synapse_type],
    [1, [0], _synapse_type],
    [0, [0], _self_synapse_type],
    [1, [1], _self_synapse_type],
    [1, [3], _synapse_type],
    [3, [1], _synapse_type],
    [3, [3], _self_synapse_type],
    [3, [2], _synapse_type],
    [2, [3], _synapse_type],
    [2, [2], _self_synapse_type],
    [2, [1], _synapse_type],
    [1, [2], _synapse_type]
]
