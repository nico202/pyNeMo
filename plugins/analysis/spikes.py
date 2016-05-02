#!/usr/bin/env python2
"""
This module provides function useful to analyze spike sequences
"""
#Import modules needed for all
import numpy as np
from collections import Counter

def neuronSpikesToSquare(
        spikes,
        steps=False,
        time_window=15,
        threshold=.05,
        split_range=(False, False) #Limit analysis on subset
):
    #TODO: check (debugging)
    if not steps:
        steps = spikes[-1]
    #TODO: use split_range to allow multiple analysis contemporarily
    start = split_range[0]
    end = split_range[1] if split_range[1] else spikes[-1]
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
        steps = serie[-1]
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

def getFreq((raw, tresholded), period=True):
    seq = tresholded #
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
    periods = [[], []]
    off_period = Counter(state[0])
    on_period = Counter(state[1])
    periods[0] = Counter(state[0])
    periods[1] = Counter(state[1])

    state_write = 0

    try:
        off_sample = periods[0].most_common(1)[0][1]
    except IndexError:
        off_sample = 0
    try:
        on_sample = periods[1].most_common(1)[0][1]
    except IndexError:
        on_sample = 0
    if (on_sample > 1) and (off_sample > 1):
        try:
            off_period_mode = off_period.most_common(1)[0][0]
            on_period_mode = on_period.most_common(1)[0][0]
        except IndexError:
            print "DEBUG ME"
            raise
        if period:
            return off_period_mode, on_period_mode, True, periods
        else:
            return 1000./off_period_mode, 1000./on_period_mode, True, periods
    else: #Not oscillating. Mode (on/off) = max (state[0], state[1])
        # Get the mean excluding max and mean value
        # If len = 1 -> - X / - 2  -> X :D
        broken = False
        if type(state[1] != bool):
            broken = True
        if not broken and len(state[1] != 2):
            on_state = (sum(state[1]) - max(state[1]) - min(state[1])) / (len(state[1]) - 2)
        else:
            broken = True
        if not broken and len(state[0] != 2):
            off_state = (sum(state[0]) - max(state[0]) - min(state[0])) / (len(state[0]) - 2)
            return off_state, on_state, True, periods
        else:
            try:
                off_state = max(state[0])
            except ValueError:
                off_state = 0
            try:
                on_state = max(state[1])
            except ValueError:
                on_state = 0
            return off_state, on_state, False, periods
