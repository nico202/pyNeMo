#!/usr/bin/env python2

def neuronSpikesToSquare(
        spikes
        , steps
        , time_window = 20
        , treshold = .05
):
    import numpy as np
    raw, data = runningMean(spikes, time_window, steps)
    array_np = np.asarray(data)
    tresholded = array_np > treshold
    #Numpy should be faster
#    tresholded = [ 1 if i > treshold else 0 for i in data ]
    return raw, tresholded

def getBurstFreq(raw, tresholded):
    '''Get frequency during and not during a burst'''
    import numpy as np
    tresholded = np.asarray(tresholded)
    raw = np.asarray(raw)
    bursting_freq = raw[tresholded].mean() #Bursting freq
    not_bursting_freq = raw[np.invert(tresholded)].mean() #Not bursting freq
#    bursting_time, not_bursting_time = 0, 0
#    bursting_spikes, not_bursting_spikes = 0, 0
#    for ms in range(len(tresholded)):
#        if tresholded[ms]: #Bursting:
#            bursting_time += 1
#            bursting_spikes += raw[ms] #either 0 or 1
#        else: #not bursting
#            not_bursting_time += 1
#            not_bursting_spikes += raw[ms]
#    return float(not_bursting_spikes)/not_bursting_time, float(bursting_spikes)/bursting_time
    return not_bursting_freq, bursting_freq

def runningMean(serie, window, steps):
    import pandas as pd
    import numpy as np
    spike_series = []
    prev = 0
    for t in serie:
        spike_series += [0] * ((t-prev) -1) + [1] #Lenght will be ms of last spike
        prev = t
    spike_series += (steps - len(spike_series)) * [0]
    #StackOverflow: 13728392
    return spike_series, pd.rolling_mean(np.array(spike_series), window)

def getFreq(seq, steps, period = True):
    from collections import Counter
    state = [[], []]#0 = off, 1 = on
    last_state = seq[0]
    last_change = 0
    i = 1
    
    for frame in seq[1:]:
        if frame != last_state:
            state[last_state].append(i - last_change)
            last_change=i
            last_state = frame
        i += 1
    else:
        state[last_state].append(i - last_change)
#        state[last_state].append(steps - i)
#         print state
#         print steps, len(seq), steps - i

    off_period = Counter(state[0])
    on_period = Counter(state[1])
    try:
        off_sample = off_period.most_common(1)[0][1]
    except IndexError:
        off_sample = 0
    try:
        on_sample = on_period.most_common(1)[0][1]
    except IndexError:
        on_sample = 0
    if (on_sample > 1) and (off_sample > 1):
        try:
            off_period_mode = off_period.most_common(1)[0][0]
            on_period_mode = on_period.most_common(1)[0][0]
        except IndexError:
            print "DEBUG ME"
            exit()
        if period:
            return off_period_mode, on_period_mode, True
        else:
            return 1000./off_period_mode, 1000./on_period_mode, True
    else: #Not oscillating. Mode (on/off) = max (state[0], state[1])
        try:
            off_state = max(state[0])
        except ValueError:
            off_state = 0
        try:
            on_state = max(state[1])
        except ValueError:
            on_state = 0
        return off_state, on_state, False
