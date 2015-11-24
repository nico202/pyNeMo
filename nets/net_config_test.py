#neurons: a, b, c, d
a, b, c, d = [0.002, 0.4, -65, 8]

neurons = [
    [a, b, c, d], #L1 = 0
    [a, b, c, d], #L2 = 1
    [a, b, c, d], #L3 = 2
    [a, b, c, d], #L4 = 3
    [a, b, c, d], #R1 = 4
    [a, b, c, d], #R2 = 5
    [a, b, c, d], #R3 = 6
    [a, b, c, d], #R4 = 7
]

#synapses:
weight_factor = 5.1
#From, to, 1?, weight, ?False
#"To" can be both an array or a single value
#"Weight" can be both an array or a single value. If it point "To" many neurons,
#   the value will be used for all
synapses = [
    [0, [3], 1, weight_factor, False],
    [1, [2], 1, weight_factor, False],
    [2, [0, 6], 1, weight_factor, False],
    [3, [1, 7], 1, weight_factor, False],
    [4, [7], 1, weight_factor, False],
    [5, [6], 1, weight_factor, False],
    [6, [4, 2], 1, weight_factor, False],
    [7, [5, 3], 1, weight_factor, False],
]
