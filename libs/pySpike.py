#!/bin/python2
"""
#####################################
#   iSpike-like joint conversion    #
#####################################
"""

class sensNetIn():
    #TODO: explain XD
    '''
    This object gets as input

    and returns as output:

    '''
    from sys import exit

    def __init__(self,
                 dof=0, #FIXME: NOT USED
                 std=0.5,
                 neuron_number=10,
                 min_angle=-90,
                 max_angle=90,
                 current_factor=1, #FIXME: unused?!
                 constant_current=0,
                 peak_current=40):
        import scipy.stats
        self._max_angle = max_angle
        self._min_angle = min_angle
        self._constant_current = constant_current
        self.dof = dof #Accessed by what?
        self.size = neuron_number #Linearized array?

        if self.size < 2:
            exit('ERROR: pySpike neuron size is less then 2!')
        # Angle covered by each neuron
        angle_dist = (max_angle - min_angle) / (self.size - 1)
        # Standard deviation expressed in angle
        sd_angle = std * angle_dist
        # Create normal distribution and calculate current factor
        self._normal_distribution = scipy.stats.norm(0, sd_angle)
        self._current_factor = peak_current / self._normal_distribution.pdf(0)
        # Populate the angles
        self._neuron_angles = []
        for n in range(self.size):
            self._neuron_angles.append(min_angle + n * angle_dist)
        self._angle = False

    def step(self, input_angle):
        '''
            Set the value of the current input. Allows getCurrent()
        '''
        # Check if angle is in range
        if input_angle > self._max_angle:
            print("ERROR: input angle not in range! (%d is too high)"
                  % (input_angle))
            self._angle = self._max_angle
        elif input_angle < self._min_angle:
            print("ERROR: input angle not in range! (%d is too low)"
                  % (input_angle))
            self._angle = self._min_angle
        else:
            self._angle = input_angle

        # Set input current to neurons
        current_input = []
        for i in range(self.size):
            current_input.append(
                (i
                 , self._constant_current + self._current_factor
                 * self._normal_distribution.pdf(
                     self._neuron_angles[i] - self._angle)
                ))
        return current_input

class sensNetOut():
    def __init__(self,
                 neuron_idx,
                 min_angle=-90, #The minimum angle to read
                 max_angle=90, #The maximum angle to read
                 decay_rate=0.25, #The rate of decay of the angle variables
                 #FIXME: current_increment UNUSED!?
                 #Increment of the input current to the neurons by each spike
                 current_increment=10,
                 dof=0, #Degree of freedom of joint. FIXME: NOT USED
                 integration_steps=1  #Step after which integration occurs (1step = 1ms)
                ):
        self.neuron_idx = neuron_idx
        neuron_number = len(neuron_idx)
        if neuron_number < 2:
            exit("FATAL ERROR: pySpike - You need at least 2 output neurons")
        # Calculate angle covered by each current variable
        angle_dist = (max_angle - min_angle) / (neuron_number - 1)
        # Set up current variables
        current_variables = [0.0] * neuron_number
        # Populate the current variable angles
        current_variable_angles = [0.0] * neuron_number
        for n in range(neuron_number):
            current_variable_angles[n] = min_angle + n * angle_dist
        #Set globals
        self.current_variables = current_variables
        self.current_variable_angles = current_variable_angles
        self.decay_rate = decay_rate
        self.neuron_number = neuron_number
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.integration_steps = integration_steps - 1 #check at nth, not nth+1
        self.missing_steps = integration_steps
        self.current_angle = None

    def step(self, fired):
        #same as iSpike setFiring()
        pattern = [1 if n in fired else 0 for n in self.neuron_idx]
        self.current_variables =\
        [x + y for x, y in zip(pattern, self.current_variables)]
        self.missing_steps -= 1

        #same as iSpike step()
        if not self.missing_steps:
            for d in range(0, len(self.current_variables)):
                self.current_variables[d] *= self.decay_rate

            angle_sum = 0
            weighted_sum = 0
            for n in range(0, self.neuron_number):
                angle_sum += self.current_variables[n]
                * self.current_variable_angles[n]
                weighted_sum += self.current_variables[n]

            new_angle = 0
            if weighted_sum:
                new_angle = angle_sum / weighted_sum
            if new_angle > self.max_angle:
                print "ERROR: new angle (%d) > maximum" % (new_angle)
                new_angle = self.max_angle
            elif new_angle < self.min_angle:
                print "ERROR: new angle (%d) < minimum" % (new_angle)
                new_angle = self.min_angle

            self.current_angle = new_angle
            self.missing_steps = self.integration_steps

        return self.current_angle
