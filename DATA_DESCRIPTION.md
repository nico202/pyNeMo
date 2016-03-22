#HistoryExplorer (current) Output file format
[1] General Config Hash, [2] Config Hash: Can be ignored. Useful to get the corresponding spike image without running the simulation again
[3] [8] mn_(A/B)_mode:	    	  spiking mode of the correpsonding (A/B) MotoNeuron. 0: long inactivity period, 1: oscillating, 2: long continuous-activity period, 3: almost no spikes (all 0 after running mean)
[4][5] [9][10] mn_(A/B)_half_period_(on/off):
    if mode == 0 || mode == 2: max period the neuron stayed on/off
    if mode == 1: most common (mode) on/off period
    if mode == 3: always 0 (almost no spikes)
[6][7] [11][12] mn_(A/B)_(not_)burst_freq: spikes/ms (not) during a burst
[13] crb_stim_value: input current value
[14][15] crb_stim_(start/stop): (ms) stimulation start and stop (on both EXC neurons)
[16][17] stim_(a/b): value of stimulus (only on CIN (A/B))
[18][19] start_(a/b): stimulus (a/b only) start
[20][21] stop_(a/b): stimulus (a/b only) stop
[22-28] CIN neuron parameters: (a, b, c, d, s (random input, always used 0), u, v)
[29] run_steps: simulation steps (ms)
