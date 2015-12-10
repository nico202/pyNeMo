#!/bin/python2
######################################
#   iSpike-like joint conversion
######################################

class sensNet():
    '''
    This object gets as input

    and returns as output:

    '''
    from sys import exit

    def __init__(self,
        dof = 0,
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
        angle_dist = (max_angle - min_angle) / self.size - 1
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
