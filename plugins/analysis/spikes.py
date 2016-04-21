#!/usr/bin/env python2
"""
This module provides function useful to analyze spike sequences
"""
#Import modules needed for all
import numpy as np

def neuronSpikesToSquare(
        spikes,
        steps,
        time_window=20,
        threshold=.05,
        split_range=(False, False) #Limit analysis on subset
):
    #TODO: use split_range to allow multiple analysis contemporarily
    start = split_range[0]
    end = split_range[1] if split_range[1] else len(spikes)

    if split_range[0] or split_range[1]:
        steps = split_range[1]-split_range[0]

    spikes = np.asarray(spikes)
    spikes = spikes[(spikes > start) & (spikes < end)]
    raw, data = runningMean(spikes, time_window, steps)
    thresholded = np.asarray(data) > threshold
    return raw, thresholded

def getBurstFreq(raw, thresholded):
    '''Get frequency during and not during a burst
    Arguments must be numpy arrays'''
    bursting_freq = raw[thresholded].mean() #Bursting freq
    not_bursting_freq = raw[np.invert(thresholded)].mean() #Not bursting freq
    return not_bursting_freq, bursting_freq

def runningMean(serie, window, steps=False):
    """
Returns the running mean of a series.
Input: serie - the data to analyze
       window - the temporal window (ms)
       steps - total lenght of the series, optional (=len(serie) if not given)
    """
    import pandas as pd
    if not steps:
        steps = len(serie)
    spike_series = []
    prev = 0
    #TODO: speed this up (numpy)
    for t in serie:
        #Lenght will be ms of last spike
        spike_series += [0] * ((t-prev) -1) + [1]
        prev = t
    spike_series += (steps - len(spike_series)) * [0]
    spike_series = np.asarray(spike_series) #remove when np used directly
    #StackOverflow: 13728392
    #Replaced (went unsupported):
    #    pd.rolling_mean(np.array(spike_series), window)
    return spike_series, pd.Series(spike_series).rolling(window=window).mean()

def getFreq(seq, period=True):
    from collections import Counter
    state = [[], []]#0 = off, 1 = on
    last_state = seq[0]
    last_change = 0
    i = 1

    for frame in seq[1:]:
        if frame != last_state:
            state[last_state].append(i - last_change)
            last_change = i
            last_state = frame
        i += 1
    state[last_state].append(i - last_change)

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
            raise
#            exit()
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
