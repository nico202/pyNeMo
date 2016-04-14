#!/usr/bin/env python2

#Class for yarp. Require "yarp" python module
#Also, yarpserver should be running

class RobotYARP ():
    def __init__ (
            self
            , device_name = "nemo_yarp_ctrl" #this controller's name
            , robot_name = '/doublePendulumGazebo/body' #robot to control
            , mode = "Position" #Positon, Torque
            , speed_val = 10
            , ref_speed = 100
            , acc_val = 50
    ):
        import yarp
        import time
        from sys import exit

        self.YARP = yarp
        self.YARP.Network.init()
        self.props = self.YARP.Property()
        self.props.put("device", "remote_controlboard")
        self.mode = 0
        #TODO: prevent conflicting names
        self.props.put("local","/client/nemo_ctrl")
        self.props.put("remote", robot_name)
        # create remote driver
        self.armDriver = self.YARP.PolyDriver(self.props)

        self.iPos = self.armDriver.viewIPositionControl()
        iVel = self.armDriver.viewIVelocityControl()
        self.iEnc = self.armDriver.viewIEncoders()

        try:
            #retrieve number of joints
            self.jnts = self.iPos.getAxes()
            self.encs = self.YARP.Vector(self.jnts)
        except AttributeError:
            print("ERROR: Read error")
            print("Cannot initialize robot. If yarp is not running, you can use --disable-sensory option")
            exit()

        while not self.iEnc.getEncoders(self.encs.data()):
                time.sleep(0.1)

        self.angles = [0] * self.jnts

        #initialize a new tmp vector identical to encs
        tmp = self.YARP.Vector(self.jnts, self.encs.data())
        speed = self.YARP.Vector(self.jnts, self.encs.data())
        acc = self.YARP.Vector(self.jnts, self.encs.data())    
        
        # Set Ref Acceleration and Speed
        for i in range(self.jnts):
            speed.set(i, speed_val)
            self.iPos.setRefSpeed(i,ref_speed)
            acc.set(i, acc_val)
            self.angles[i] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(i)
        
    #READ
    def read (self, jnt = "All"):
        '''
            Returns the angle of a joint, unless jnt = "All".
            In the latter case, returns a list with all joints value
        '''
        if jnt == "All":
            for jnt in range(0, self.jnts):
                self.iEnc.getEncoders(self.encs.data())
                self.angles[jnt] = self.YARP.Vector(self.jnts, self.encs.data()).get(jnt)
            return self.angles
        else:
            self.angles[jnt] = self.YARP.Vector(self.jnts, self.YARP.Vector(self.jnts).data()).get(jnt)
            return self.angles[jnt]

    #TODO: ADD torque etc
    def write(self, jnts_angles):
        has_to_move = False
        for jnt, angle in jnts_angles:
            tmp = self.YARP.Vector(self.jnts
                                   , self.encs.data())
            if angle != None:
                has_to_move = True
                try:
                    # tmp.set(jnt, 0) #to debug
                    tmp.set(jnt, angle)
                except:
                    raise
        #The motion is done ones for all joints
        if has_to_move:
            self.iPos.positionMove(tmp.data())
            
        #This is to try to sync them.
        #Pretty useless, substitute with C++
        # self.YARP.Time.delay(0.001)
        # self.iPos.stop()
        # I can check motion is done?

        return True

    def get_output(self):
        
        #FIXME:
        return 

    def reset_all (self, home_position = 0):
        '''
        This function port every joint to the default (home) position. Default is 0.
        '''
        tmp = self.YARP.Vector(self.jnts)
        for jnt in range(self.jnts):
            print "Set %s %s" % (jnt, home_position)
            tmp.set(jnt, home_position)
        #Move ones for all joints
        self.iPos.positionMove(tmp.data())
        #FIXME: seems not working
        while not self.iPos.checkMotionDone(): #Wait home position reached
            print "sleeping"
            self.YARP.Time.delay(0.01)
        return True

#Torque:
#getTorque
