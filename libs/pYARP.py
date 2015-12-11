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
###

class YARPInterface():
    def __init__(self,
            robot = '/doublePendulumGazebo/body',
            speed_val = 20,
            acc_val = 50,
            ref_speed = 1
        ):
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
        self.iPos = self.armDriver.viewIPositionControl()
        iVel = self.armDriver.viewIVelocityControl()
        iEnc = self.armDriver.viewIEncoders()
        try:
            #retrieve number of joints
            self.jnts=self.iPos.getAxes()
            self.encs=self.YARP.Vector(self.jnts)
        except AttributeError:
            exit("ERROR: Read error")
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

    def read(self, jnt):
        self.angles[jnt] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(jnt)
        return self.angles[jnt]

    def write(self, jnt, angle):
        if angle is False:
            angle = self.angles[jnt]
        success = False
        try:
            tmp  = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data())
            tmp.set(jnt, angle)
            self.iPos.positionMove(tmp.data())
            success = True
        except:
            raise
        return success

    def reach(self):
        import time
        while not self.iPos.isMotionDone():
            time.sleep(1)
        return True

    #Implement
    def changeRefSpeed(self, ref_speed, jnt = 'All'):
        if jnt == 'All':
            for i in range(self.jnts):
                self.iPos.setRefSpeed(i, ref_speed)
        else:
            self.iPos.setRefSpeed(jnt, ref_speed)

    def changeRefAcc(self, ref_acc, jnt = 'All'):
        if jnt == 'All':
            for i in range(self.jnts):
                self.iPos.setRefAcceleration(i,ref_acc)
        else:
            self.iPos.setRefAcceleration(jnt, ref_acc)
