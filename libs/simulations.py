"""
This module simulations that can be run.
They MUST provide a step() function thet steps forward 1 ms.
They MUST log what they output, and return this with get_output()
The exception is "main_simulation_run", the one which creates and
runs every other sim.
"""
#FIXME/TODO?: Move to new-style class?
class NemoSimulation():
    """
Creates an object matching the input NeMo configuration
    """
    def __init__(
            self,
            simulation,
            (to_save, neuron_number),
            save_membrane=False
    ):
        self.simulation = simulation
        self.to_save = to_save
        self.neuron_number = neuron_number
        self.fired_history = []
        # Do it better
        self.membrane_history = {i: [] for i in self.to_save}
        self.save_membrane = save_membrane

    def step(
            self,
            stimuli
    ):
        """
Simulate 1 ms
Input: stimuli
Output: fired, membrane
        """
        if stimuli != None:
            fired = list(self.simulation.step(istim=stimuli))
        else:
            fired = list(self.simulation.step())

        # Saving membrane
        #TODO: add option to disable membrane save (saves lot of time)
        #Appends are quite slow though
        if self.save_membrane:
            for neuron in self.to_save: #Save membrane potential
                self.membrane_history[neuron].append(
                    self.simulation.get_membrane_potential(neuron))

        # Saving spikes
        self.fired_history.append(fired)

        return fired

    def get_output(self): #FIXME: return fired_history only if in to_save
        """
Returns this simulation output
Returns: membrane_history, fired_history
        """
        return self.membrane_history, self.fired_history

class GazeboSimulation():
    """
Interface with gazebo.
Step: should move 1 ms fw the simulation. Will be implemented in c++?
    """
    def __init__(self):
        return None
    def step(self):
        """
Exec 1 ms, pause. TODO: Implement (or replace with C++)
        """
        process_output = {}
        return process_output

class CerebellumSimulation():
    """
Simulate one ms of cerebellum.
TODO: This is to implement. What inputs and outputs does it need?
    """
    def __init__(self):
        return None

    def step(self):
        """
Run 1 ms cerebellum
        """
        process_output = {}
        return process_output

class PySpikeSimulation():
    """
Joint-to-spikes and Spikes-to-join conversion (iSpike-like)
It's an wrapper to libs/pySpike (for easier call)
    """
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
                        out, #nemo INput ids
                        jnt,
                        pySpike.sensNetIn(
                            neuron_number=len(out),
                            std=std,
                            #FIXME: add as many parameters possible
                            min_angle=min_angle,
                            max_angle=max_angle,
                            # current_factor = 1,
                            # peak_current = 40,
                            # constant_current = 0
                        )
                    )
                )

            for jnt, decay, min_angle, max_angle, ins in sensory_neurons_out:
                self.networks_out.append(
                    (
                        jnt, #NeMo OUT
                        ins,
                        pySpike.sensNetOut(
                            ins,
                            decay_rate=decay,
                            min_angle=min_angle,
                            max_angle=max_angle
                        )
                    )
                )

    def step(self, yarp_angles, fired):
        """
        Coneverts joint angle into current inputs to give to NeMo neurons
        """
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
        """
Returns (stims, angles)
        """
        return (self.stims, self.angles)

def main_simulation_run(
        configuration
        , (nemo_sim, to_save, stimuli_dict)
        , (yarp_robot)
        , (sensory_neurons)
        , simple_feedback=False
        , alpha=0.9
        , beta=0.1
        , non_linear_correction=False#"squared"#False to use linear
        , bypass_debug=False #Angle to force (debug function, bypasses ispike)
        , save_membrane=False
):
    """
This is the core of all pyNeMo
It's used to create all the Sims defined here, and calls them when needed
taking care of passing the data from one sim to the other
    """
    #Import & configure varios plugins
    nemo_simulation = NemoSimulation(nemo_sim, to_save, save_membrane)
    if yarp_robot:
        #FIXME: Don't use gazebo, yarp, pySpike if no sensory (no Robot)
        gazebo_simulation = GazeboSimulation()
        pySpike_simulation = PySpikeSimulation(sensory_neurons)

    cerebellum_simulation = CerebellumSimulation()

    #Singal support: stop indefinite simulations
    total_steps = configuration["steps"] or -1
    ran_steps = 0
    add_stims = []

    keep_running = True

    global_output = {
        "NeMo": [],
        "pySpike": [],
        "stimuli" : [],
        "ran_steps": 0,
        "YARP": {
            "read": [],
            "wrote": []#MOVE TO PYSPIKE (it's HIS output)
        }
    }

    #Main loop
    jnt_angles = False #Needed for the first feedback loop
    ang_diff = False #Extremely ulgy FIXME
    jnt_angles_tmp = False

    #Allow indefinite loops (total=-1). Exit with CTRL-C
    while ran_steps != total_steps and keep_running:
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

            nemo_firings = nemo_simulation.step(stimuli)
            #Cerebellum: input/outputs?
            #Disable right now (not implemented)
            #TODO: implement
            # cerebellum_simulation.step()

            if yarp_robot:
                #YARP: input/outputs?
                yarp_angle = yarp_robot.read() #READ yarp
                #Calculate the diff for feedback
                #BYPASS ispike angles (test with continuous signal)
                if bypass_debug: #bypass debug is an angle (or False)
                    if not jnt_angles: #First loop
                        data = [(0, 0), (1, 0)]
                    else:
                        data = [(0, bypass_debug), (1, bypass_debug)]
                        jnt_angles = data[:]
                if simple_feedback and jnt_angles:
                    #FIXME: change ispike output to a simple list - simplify everithing
                    #FIXME: quick hack, write better
                    if jnt_angles:
                        spike_angles = [v[1] for v in jnt_angles]
                        if not None in spike_angles:
                            if not non_linear_correction:
                                ang_diff = [
                                    ((spike_angles[i] - yarp_angle[i]) * alpha
                                     +
                                     beta * (spike_angles[i]))
                                    for i in range(len(jnt_angles))
                                ]
                            elif non_linear_correction == "power-two":
                                error = [
                                    spike_angles[i] - yarp_angle[i]
                                    for i in range(len(jnt_angles))
                                ]
                                sign = [
                                    1 if error[i] > 0 else -1
                                    for i in range(len(jnt_angles))
                                ]
                                ang_diff = [
                                    ((error[i] ** 2) * sign[i] * alpha
                                     + beta * (spike_angles[i]))
                                    for i in range(len(jnt_angles))
                                ]
                            elif non_linear_correction == "squared":
                                error = [
                                    spike_angles[i] - yarp_angle[i]
                                    for i in range(len(jnt_angles))
                                ]
                                sign = [
                                    1 if error[i] > 0 else -1
                                    for i in range(len(jnt_angles))
                                ]
                                ang_diff = [
                                    ((abs(error[i]) ** 0.5) * sign[i] * alpha
                                     + beta * (spike_angles[i]))
                                    for i in range(len(jnt_angles))
                                ]
                    else:
                        ang_diff = [] * len(jnt_angles)
                #Update pySpike
                add_stims, jnt_angles = pySpike_simulation.step(
                    yarp_angle
                    , nemo_firings)
                # #BYPASS
                if bypass_debug:
                    jnt_angles = data[:]
                    if simple_feedback and ang_diff: #TODO: Use numpy
                        # print "Diff is: %s" % ang_diff
                        jnt_angles_tmp = jnt_angles[:]
                        jnt_angles = [
                            (i, ang_diff[i] + jnt_angles[i][1])
                            for i in range(len(jnt_angles))
                        ] #FIXME: keep the right i

                yarp_robot.write(jnt_angles)
                if jnt_angles_tmp:
                    jnt_angles = jnt_angles_tmp[:]
                #Gazebo: input/outputs?
                gazebo_simulation.step()
            ran_steps += 1

        except KeyboardInterrupt:
            keep_running = False

    if yarp_robot:
        global_output["pySpike"] = pySpike_simulation.get_output()
        yarp_read, yarp_wrote = yarp_robot.get_output()
        global_output["YARP"]["read"] = yarp_read
        global_output["YARP"]["wrote"] = yarp_wrote

    global_output["NeMo"] = nemo_simulation.get_output()
    global_output["ran_steps"] = ran_steps
    global_output["stimuli"] = stimuli_dict

    return global_output
