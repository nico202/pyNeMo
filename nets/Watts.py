from templates import * #For ease of use, this line is mandatory
name = "Watts"
#neurons
neurons = [ #TODO: support other type of neurons? Right now, IZ only
    FS * 2
]

save = [0, 1]

#synapses:
#From, to, (delay, weight, plastic)
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all
synapses = [
    [0, [1], (1, 20, True)],
    [1, [0], (1, 20, True)]
]
