from templates import * #For ease of use, this line is mandatory

#neurons
neurons = [ #TODO: support other type of neurons? Right now, IZ only
     FastSpiking * 8
]

save = [0]

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all
synapses = [
    [0, [3], FastLearn],
    [1, [2], FastLearn],
    [2, [0, 6], FastLearn],
    [3, [1, 7], FastLearn],
    [4, [7], FastLearn],
    [5, [6], FastLearn],
    [6, [4, 2], FastLearn],
    [7, [5, 3], FastLearn],
]
