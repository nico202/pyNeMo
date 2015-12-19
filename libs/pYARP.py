###
 # * @ingroup icub_tutorials
 # *
 # * \defgroup icub_python_motor_interfaces Using motor interfaces with Python
 # *
 # * Shows how to control the robot using motor interfaces within Python.
 # *
 # * \author Lorenzo Natale
 # *
 # * CopyPolicy: Released under the terms of GPL 2.0 or later
# ###
# import yarp
# YARP = yarp
# YARP.Network.init()
# props = self.YARP.Property()
# # OUT: Traceback (most recent call last):
# # OUT:   File "<input>", line 1, in <module>
# # OUT: NameError: name 'self' is not defined
# props = YARP.Property()
# props.put("device","remote_controlboard")
# props.put("remote", "/doublePendulumGazebo/body")
# props.put("local","/client/asd")
# armDriver = YARP.PolyDriver(props)
# ITor = armDriver.viewITorqueControl()
# armDriver.setTorqueMode()
# # OUT: Traceback (most recent call last):
# # OUT:   File "<input>", line 1, in <module>
# # OUT:   File "/usr/local/lib/python2.7/dist-packages/yarp.py", line 5693, in <lambda>
# # OUT:     __getattr__ = lambda self, name: _swig_getattr(self, PolyDriver, name)
# # OUT:   File "/usr/local/lib/python2.7/dist-packages/yarp.py", line 57, in _swig_getattr
# # OUT:     raise AttributeError(name)
# # OUT: AttributeError: setTorqueMode
# ITor.setTorqueMode()
# # OUT: True
# ITor.setRefTorque(0,0)
# # OUT: True
# ITor.setRefTorque(1,0)
# # OUT: True

class YARPInterface():
    def __init__(self,
            mode = "Position",
            robot = '/doublePendulumGazebo/body',
            speed_val = 20,
            acc_val = 50,
            ref_speed = 1
        ):
        #TODO: dof?
        import yarp
        import time
        import random
        from sys import exit
        self.YARP = yarp
        self.YARP.Network.init()
        self.props = self.YARP.Property()
        self.props.put("device","remote_controlboard")
        #FIXME: better namings XD
        self.props.put("local","/client/" + str(random.random())) #prevent conflict
        self.props.put("remote", robot)
        # create remote driver
        self.armDriver = self.YARP.PolyDriver(self.props)

        #query motor control interfaces
        if mode:
            self.iPos = self.armDriver.viewIPositionControl()
            iVel = self.armDriver.viewIVelocityControl()
            iEnc = self.armDriver.viewIEncoders()
            try:
                #retrieve number of joints
                self.jnts=self.iPos.getAxes()
                self.encs=self.YARP.Vector(self.jnts)
            except AttributeError:
                print("ERROR: Read error")
                print("Cannot initialize robot. If yarp is not running, you can use --disable-sensory option")
                exit()
            while not iEnc.getEncoders(self.encs.data()):
                time.sleep(0.1)
            #initialize a new tmp vector identical to encs
            tmp=self.YARP.Vector(self.jnts,self.encs.data())
            speed=self.YARP.Vector(self.jnts,self.encs.data())
            acc=self.YARP.Vector(self.jnts,self.encs.data())

            self.angles = [0] * self.jnts
            # Set Ref Acceleration and Speed
            for i in range(self.jnts):
                speed.set(i, speed_val)
                self.iPos.setRefSpeed(i,ref_speed)
                acc.set(i, acc_val)
                self.angles[i] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(i)
            self.iPos.setRefAccelerations(acc.data())
            self.mode = 0
        elif mode == "Torque":
            self.iTor = self.armDriver.viewITorqueControl()
            self.iTor.setTorqueMode()
            self.iTor.setRefTorque(1,0)
            self.iTor.setRefTorque(0,0)

            try:
                #retrieve number of joints
                self.jnts=self.iTor.getAxes()
                self.encs=self.YARP.Vector(self.jnts)
                for j in range(self.jnts):
                    self.iTor.setRefTorque(j,0)
            except AttributeError:
                print("ERROR: Read error")
                print("Cannot initialize robot. If yarp is not running, you can use --disable-sensory option")
                exit()
            #Wait position reached?
            self.mode = 1
        else:
            print "NOT implemented yet"
            self.mode = 1

    def read(self, jnt = "All"):
        '''
            Returns the angle of a joint, unless jnt = "All".
            In the latter case, returns a list with all joints value
        '''
        if jnt == "All":
            for jnt in range(0, self.jnts):
                self.angles[jnt] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(jnt)
                #print self.angles
                return self.angles
            else:
                self.angles[jnt] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(jnt)
                return self.angles[jnt]

    def write(self, jnt, angle):
        #if angle is False:
        #    angle = self.angles[jnt]
        success = False
        try:
            if self.mode == 0: #Mode vs Torque
                tmp  = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data())
                tmp.set(jnt, angle)

                self.iPos.positionMove(tmp.data())
                success = True
        except:
            raise
        return success

    def reach(self):
        import time
        #import subprocess #FIXME
        print "Waiting until robot reaches position"
        if self.mode == 0: #torque vs pos
            while not self.iPos.isMotionDone():
                time.sleep(1)
                #subprocess.call("gz world -s", shell = True) #FIXME: pygazebo bindings
        return True

    #Implement
    def changeRefSpeed(self, ref_speed, jnt = 'All'):
        if jnt == 'All':
            for i in range(self.jnts):
                if self.mode == 1:
                    self.iPos.setRefSpeed(i, ref_speed)
        else:
            if self.mode == 1:
                self.iPos.setRefSpeed(jnt, ref_speed)

    def changeRefAcc(self, ref_acc, jnt = 'All'):
        if jnt == 'All':
            for i in range(self.jnts):
                if self.mode == 1:
                    self.iPos.setRefAcceleration(i,ref_acc)
        else:
            if self.mode == 1:
                self.iPos.setRefAcceleration(jnt, ref_acc)
