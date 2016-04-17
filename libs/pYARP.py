#!/usr/bin/env python2

#Class for yarp. Require "yarp" python module
#Also, yarpserver should be running

modes_map = ("Position", "Torque")

class RobotYARP(): #TODO: Save history (if save enabled)
    '''
    Interface to the YARP python bindings
    Creates a robot and allows reads and writes easily
    '''
    def __init__(
            self
            , device_name="nemo_yarp_ctrl" #this controller's name
            , robot_name='/doublePendulumGazebo/body' #robot to control
            , mode="Position" #Positon, Torque
            , speed_val=10
            , ref_speeds=10 #Both a single value or a tuple
            , acc_val=10
            , ref_accs=10 #Both a single value or a tuple
            , ref_torques=9
    ):
        import yarp
        import time
        from sys import exit

        self.YARP = yarp
        self.YARP.Network.init()
        self.props = self.YARP.Property()
        self.props.put("device", "remote_controlboard")

        #Save mode as index number (read "modes_map" values for info)
        try:
            self.mode = modes_map.index(mode)
        except ValueError:
            exit("Unknown mode: %s! Available modes are:\n  %s"
                 % (mode, modes_map))

        #TODO: prevent conflicting names
        self.props.put("local", "/client/nemo_ctrl")
        self.props.put("remote", robot_name)
        # create remote driver
        self.armDriver = self.YARP.PolyDriver(self.props)
        self.iPos = self.armDriver.viewIPositionControl()
        #FIXME: Used?
        self.iVel = self.armDriver.viewIVelocityControl()
        self.iEnc = self.armDriver.viewIEncoders()
        self.iImp = self.armDriver.viewIImpedanceControl()
        self.iTor = self.armDriver.viewITorqueControl()

        try:
            #retrieve number of joints
            self.jnts = self.iPos.getAxes()
            self.encs = self.YARP.Vector(self.jnts)
            #Which do we need?
            self.tmp = yarp.Vector(self.jnts)
            self.encoders = yarp.Vector(self.jnts)
            self.command_position = yarp.Vector(self.jnts)
            self.command_velocity = yarp.Vector(self.jnts)

        except AttributeError:
            print("ERROR: Read error")
            print("Cannot initialize robot.\
        If yarp is not running, you can use --disable-sensory option\
            If yarp is running but it cannot bind the port, use \"netstat -lnp\" to know which process is accessing it, and kill (ie. killall gz)")
            exit()

        self.angles = [0] * self.jnts
        self.readAnglesHistory = [] #YARP output
        self.wroteAnglesHistory = [] #YARP input
        #Define something like "get_current_angles"
        # for i in range(self.jnts):
        #     self.angles[i] = self.YARP.Vector(
        #         self.jnts
        #         , self.YARP.Vector(self.jnts).data()).get(i)

        if self.mode == 0: #Position control
            while not self.iEnc.getEncoders(self.encs.data()):
                time.sleep(0.1)

            #initialize a new tmp vector identical to encs
            tmp = self.YARP.Vector(self.jnts, self.encs.data())
            speed = self.YARP.Vector(self.jnts, self.encs.data())
            acc = self.YARP.Vector(self.jnts, self.encs.data())

            #FIXME: use same as down
            # Set Ref Acceleration and Speed
            for i in range(self.jnts):
                speed.set(i, speed_val)
                self.iPos.setRefSpeed(i, ref_speeds)
                acc.set(i, acc_val)
        elif self.mode == 1: #Torque
            #TODO: add impendence control
            try:
                assert(self.iTor.setTorqueMode())
            except AssertionError:
                exit("Robot does not support toruqe mode!")
            #Set jnts accelerations
            #int -> single value to all jnts
            #TODO: you can write something more clearly
            tmp = self.YARP.Vector(self.jnts, self.encs.data())
            tmp = self.set_references(ref_accs
                                      , tmp)
            self.iPos.setRefAccelerations(tmp.data())
            #Set jnts speeds
            tmp = self.YARP.Vector(self.jnts, self.encs.data())
            tmp = self.set_references(ref_speeds
                                      , tmp)
            self.iPos.setRefSpeeds(tmp.data())
            tmp = self.YARP.Vector(self.jnts, self.encs.data())
            tmp = self.set_references(ref_torques
                                      , tmp)
            self.iTor.setRefTorques(tmp.data())
            
        else:
            exit("Unknown bug happened")
    #READ
    def read(self):
        '''
            Returns the angle of all joints.
        '''
        self.iEnc.getEncoders(self.encs.data())
        for jnt in range(self.jnts):
            self.angles[jnt] = self.encs[jnt]
        # self.angles[jnt] = self.YARP.Vector(
        #     self.jnts
        #     , self.encs.data()).get(jnt)
        #TODO: disable this if no save asked
        self.readAnglesHistory.append(self.angles[:])
        return self.angles
        
        # if jnt == "All":
        #     for jnt in range(0, self.jnts):
        #     return self.angles
        # else:
        #     # self.angles[jnt] = self.YARP.Vector(
        #     #     self.jnts
        #     #     , self.YARP.Vector(self.jnts).data()).get(jnt)
        #     return self.angles[jnt]

    #TODO: ADD torque etc
    def write(self, jnts_angles):
        has_to_move = False
        tmp = self.YARP.Vector(self.jnts
                               , self.encs.data())
        for jnt, angle in jnts_angles:
#        for jnt, angle in enumerate(jnts_angles):
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
        self.wroteAnglesHistory.append(jnts_angles[:])
        #This is to try to sync them.
        #Pretty useless, substitute with C++
        # self.YARP.Time.delay(0.001)
        # self.iPos.stop()
        # I can check motion is done?

        return True

    def get_output(self):
        return self.readAnglesHistory, self.wroteAnglesHistory

    def reset_all(self, home_position=0):
        '''
        This function port every joint to the default (home) position. Default is 0.
        '''
        print("Resetting robot to home position (0). Disable with --no-home-position")
        tmp = self.YARP.Vector(self.jnts)
        for jnt in range(self.jnts):
            tmp.set(jnt, home_position)
        #Move ones for all joints
        self.iPos.positionMove(tmp.data())
        #FIXME: seems not working
        while not self.iPos.checkMotionDone(): #Wait home position reached
            self.YARP.Time.delay(0.01)
        self.YARP.Time.delay(5)
        self.iPos.stop()
        print("Reset done!")
        return True

    def reset_world(self): #TODO: move to own function (like in IO.py)
        '''
        Reset gazebo world. Replaces reset_all
        '''
        import subprocess
        subprocess.call(["gz", "world", "-r"])
        return True

    def set_references(self, ref, tmp):
        if type(ref) == int:
            for i in range(self.jnts):
                tmp[i] = ref
        #tuple/list: map one value to one joint
        elif type(ref) in [tuple, list]: #tuple is better
            if self.jnts != len(ref):
                exit("Ref lenght and jnts number differs!")
            for (jnt_number, jnt_ref) in enumerate():
                tmp[jnt_number] = jnt_ref
        else:
            exit("Cannot set reference (unknown type %s)"
                 % (type(ref)))
        return tmp

#Torque:
#getTorque
