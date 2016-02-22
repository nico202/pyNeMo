class nemoSimulation ():
    def __init__(
            self
            , simulation
            , (to_save, neuron_number)
    ):
        self.simulation = simulation
        self.to_save = to_save
        self.neuron_number = neuron_number
        self.fired_history = []
        self.membrane_history = { i: [] for i in self.to_save }

    def step(
            self
            , nemo_network
            , stimuli
    ):
        '''
        Input: stimuli
        Output: fired, membrane
        '''

        if stimuli != None:
            fired = list(self.simulation.step(istim=stimuli))
        else:
            fired = list(self.simulation.step())

        #Appends are quite slow though
        for neuron in self.to_save: #Save membrane potential
            self.membrane_history[neuron].append(
                self.simulation.get_membrane_potential(neuron))
        self.fired_history.append(fired)

        return fired

    def get_output (self):
        return self.membrane_history, self.fired_history

class gazeboSimulation ():
    def __init__(self):
        return None
    def step (self):
        '''
        Exec 1 ms, pause
        '''
        process_output = {}
        return process_output

class cerebellumSimulation ():
    def __init__(self):
        return None

    def step (self):
        process_output = {}
        return process_output

class pySpikeSimulation ():
    def __init__(
            self
            , (sensory_neurons_in, sensory_neurons_out)
    ):
        self.angles = []
        self.stims = []
        if sensory_neurons_in or sensory_neurons_out:
            import libs.pySpike as pySpike
            #prepare output
            self.networks_ins = []
            self.networks_out = []
            for std, jnt, min_angle, max_angle, out\
            in sensory_neurons_in:
                self.networks_ins.append(
                    (
                        out #nemo INput ids
                        , jnt
                        , pySpike.sensNetIn(
                            neuron_number = len(out)
                            , std = std
                #FIXME: add as many parameters possible
                            , min_angle = min_angle
                            , max_angle = max_angle
                            #, current_factor = 1
                            #, peak_current = 40
                            #, constant_current = 0
                        )
                    )
                )
            
            for jnt, decay, min_angle, max_angle, ins in sensory_neurons_out:
                self.networks_out.append(
                    (
                        jnt #NeMo OUT
                        , ins
                        , pySpike.sensNetOut(
                            ins
                            , decay_rate = decay
                            , min_angle = min_angle
                            , max_angle = max_angle
                        )
                    )
                )

    def step(self, yarp_angles, fired):
        #Convert jnt angle to current
        stims = [] #and saves them as stimuli
        for ins, jnt, net_obj in self.networks_ins:
            for nidx, current in net_obj.step(yarp_angles[jnt]):
                stims.append((ins[nidx], current))

        #Convert spikes to jnt angle
        angles = []
        for jnt, out, net_obj in self.networks_out:
            sens_fired = list(set(fired) & set(out))
            #Sens_fired MUST be converted to neurons id relative to the net!
            angles.append((jnt, net_obj.step(sens_fired)))
        
        self.stims.append(stims)
        self.angles.append(angles)
        return stims, angles

    def get_output(self):
        return (self.stims, self.angles)

def main_simulation_run (
        configuration
        , (nemo_sim, to_save, stimuli_dict)
        , (yarp_robot)
        , (sensory_neurons)
):
    #Import & configure varios plugins
    nemo_simulation = nemoSimulation(nemo_sim, to_save)
    if yarp_robot:
        #FIXME: Don't use gazebo, yarp, pySpike if no sensory (no Robot)
        gazebo_simulation = gazeboSimulation()
        pySpike_simulation = pySpikeSimulation(sensory_neurons)

    cerebellum_simulation = cerebellumSimulation()

    #Singal support: stop indefinite simulations
    total_steps = configuration["steps"] or -1
    ran_steps = 0
    add_stims = []
    
    keep_running = True
    global_output = {
        "NeMo": []
        , "pySpike": []
        , "stimuli" : []
        , "ran_steps": 0
    }

    #Main loop
    while ( #Allow indefinite loops (total=-1). Exit with CTRL-C
            ran_steps != total_steps and keep_running):
        try:
            ####Main part of the main loop######

            #NeMo
            #Load stimuli from config
            stimuli = stimuli_dict[ran_steps] if ran_steps in stimuli_dict else None

            #FIXME:
            if stimuli != None:
                stimuli += add_stims
            else:
                stimuli = add_stims

            nemo_firings = nemo_simulation.step (
                nemo_simulation
                , stimuli
            )
            #Cerebellum: input/outputs?
            cerebellum_simulation.step ()

            if yarp_robot:
                #YARP: input/outputs?
                yarp_angle = yarp_robot.read() #READ yarp
                #print yarp_angle, nemo_firings
                add_stims, jnt_angles = pySpike_simulation.step (
                    yarp_angle
                    , nemo_firings
                )
                #print jnt_angles
                yarp_robot.write(jnt_angles)
                #Gazebo: input/outputs?
                gazebo_simulation.step ()

            ran_steps += 1

        except KeyboardInterrupt:
            keep_running = False

    global_output["pySpike"] = pySpike_simulation.get_output()
    global_output["NeMo"] = nemo_simulation.get_output()
    #FIXME: enable
    #global_output["YARP"] = yarp_robot.get_output()
    global_output["ran_steps"] = ran_steps
    global_output["stimuli"] = stimuli_dict
    
    return global_output
