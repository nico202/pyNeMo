#!/bin/python2
######################################
#   iSpike-like joint conversion
######################################

class sensNetIn():
    '''
    This object gets as input

    and returns as output:

    '''
    from sys import exit

    def __init__(self,
        dof = 0, #FIXME: NOT USED
        std = 0.5,
        min_angle = -90,
        max_angle = 90,
        current_factor = 1,
        contant_current = 0,
        neuron_number = 10,
        param_a = 0.1,
        param_b = 0.2,
        param_c = -65,
        param_d = 2,
        peak_current = 40,
        constant_current = 0
    ):
        import scipy.stats
        self._max_angle = max_angle
        self._min_angle = min_angle
        self._constant_current = constant_current
        self.dof = dof #Accessed by what?
        self.size = neuron_number #Linearized array?

        if self.size < 2:
            exit('ERROR: neuron size is less then 2!')
        #Angle covered by each neuron
        angle_dist = (max_angle - min_angle) / (self.size - 1)
        #Standard deviation expressed in angle
        sd_angle = std * angle_dist;
        #Create normal distribution and calculate current factor
        self._normal_distribution = scipy.stats.norm(0, sd_angle)
        self._current_factor = peak_current / self._normal_distribution.pdf(0)
        self._neuron_angles = []
        for n in range(self.size):
            self._neuron_angles.append(min_angle + n * angle_dist)
        self._angle = False

    def setInput(self, tmp_angle):
        '''
            Set the value of the current input. Allows getCurrent()
        '''
        if tmp_angle > self._max_angle:
            print("ERROR: input angle not in range! (%d is too high)" % (tmp_angle))
            self._min_angle = self._max_angle
        elif tmp_angle < self._min_angle:
            print("ERROR: input angle not in range! (%d is too low)" % (tmp_angle))
            tmp_angle = self._min_angle
        else:
            self._angle = tmp_angle

    def getCurrent(self, neuron_id):
        '''
            Get the gaussian-filtered current for the neuron (id)
        '''
        return self._constant_current + self._current_factor * self._normal_distribution.pdf(self._neuron_angles[neuron_id] - self._angle)

class sensNetOut():
    def __init__(self,
        min_angle = -90, #The minimum angle to read
        max_angle = 90, #The maximum angle to read
        decay_rate = 0.25, #The rate of decay of the angle variables
        current_increment = 10, #The amount by which the input current to the neurons is incremented by each spike
        neuron_number = 10, #
        dof = 0, #Degree of freedom of joint. FIXME: NOT USED
        integration_steps = 10  #Step after which integration occurs (1step = 1ms)
    ):
        if neuron_number < 2:
            exit("FATAL ERROR: You need at least 2 neurons")
        angle_dist = (max_angle - min_angle) / (neuron_number - 1)
        current_variables = [0] * neuron_number
        current_variable_angles = [0] * neuron_number
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
        self.current_angle = False

    def step(self, fired):
        #same as iSpike setFiring()
        pattern = [1 if n in fired else 0 for n in range(self.neuron_number)]
        self.current_variables =\
        [x + y for x, y in zip(pattern, self.current_variables)]
        self.missing_steps -= 1

        #same as iSpike step()
        if not self.missing_steps:
            for d in range(0, len(self.current_variables)):
                self.current_variables[d] *= self.decay_rate
            angle_sum = 0; weighted_sum = 0
            for n in range(0, self.neuron_number):
                angle_sum += self.current_variables[n] * self.current_variable_angles[n]
                weighted_sum += self.current_variables[n]

            new_angle = 0
            if weighted_sum:
                new_angle = angle_sum / weighted_sum
            if new_angle > self.max_angle:
                print("ERROR: new angle (%d) > maximum" % (new_angle))
            elif new_angle < self.min_angle:
                print("ERROR: new angle (%d) < minimum" % (new_angle))
            self.current_angle = new_angle
            self.missing_steps = self.integration_steps
        return self.current_angle
