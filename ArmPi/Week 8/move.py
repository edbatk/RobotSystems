#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')
import time
from math import sqrt
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Motion():
    def __init__(self):
        self.neutral = 512 # dynamixel servo 12 O'Clock position
        self.move = ArmIK()
        self.reachability = True
        self.color_coords = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        self.done = False
    
    
    def sweep(self,x,y,z,a,a1,a2):
        """
        Given the coordinates coordinate_data and pitch angle alpha, 
        and the range of pitch angle range alpha1, alpha2, automatically find 
        the solution closest to the given pitch angle, and go to the target position.
        If there is no solution, return False, otherwise return to servo angle, pitch angle, running time
        Coordinate unit cm, passed in as a tuple, for example (0, 5, 10)
        alpha is the given pitch angle
        alpha1 and alpha2 are the value ranges of the pitch angle
        movetime is the rotation time of the steering gear, the unit is ms, if the time is not given, it will be automatically calculated
        """
        angle = self.move.setPitchRangeMoving((x,y,z),a,a1,a2)
        time.sleep(2)
        return angle

    def move_obj(self,pos1,pos2):
        """
        Grasp an object from a location and place it
        pos1 (initial object position) :  tuple (x,y,rotation_angle)
        pos2 (new destined object position) : tuple (x,y,rotation_angle,z)
        """
        while not self.done:
            self.sweep(pos1[0],pos1[1]- 2, 5, -90, -90, 0) # lower arm
            self.open_claw() # open claw
            self.rotate_claw(getAngle(pos1[0],pos1[1],pos1[2])) # rotate claw to grasp
            self.sweep(pos1[0], pos1[1], 2, -90, -90, 0) # move claw to positon 1
            self.close_claw() # grasp
            self.sweep(pos1[0], pos1[1], 12, -90, -90, 0) # raise arm
            self.sweep(pos2[0],pos2[1],pos2[2]+10,-90,-90,0) # move claw to above position 2
            self.sweep(pos2[0],pos2[1],pos2[2],-90,-90,0) # lower claw to position 2
            self.rotate_claw(getAngle(pos2[0],pos2[1],pos2[3])) # rotate claw to release
            self.open_claw() # release object
            self.sweep(pos2[0], pos2[1], 12, -90, -90, 0) # raise arm
            self.initMove() # move back to home
            self.done = True

    def close_claw(self):
        Board.setBusServoPulse(1, self.neutral - 50, 300)
        time.sleep(1)
        
    def open_claw(self):
        Board.setBusServoPulse(1, self.neutral - 280, 500)
        time.sleep(1)
        
    def rotate_claw(self,a):
        Board.setBusServoPulse(2, a, 500)
        time.sleep(1)

    def initMove(self):
        self.close_claw()
        self.rotate_claw(512)
        self.sweep(0, 10, 10, -30, -30, -90)
    
if __name__ == "__main__":
    arm = Motion()
    arm.initMove()
    # arm.move_obj((-15 + 0.5, 12 - 0.5, -90), (-1.66, 15, 2, -62))
    key = cv2.waitKey(1) 
    while True:
        time.sleep(0.5)
        print('enter command: x, y, z, pitch angle, low bound, high bound')
        x,y,z,a,a1,a2 = int(input().split())
        print(f"x: {x}, y: {y}, z: {z}, a: {a}, a1: {a1}, a2 {a2}")
        print(f"Moving...")
        arm.sweep(x,y,z,a,a1,2)
        time.sleep(0.5)
        print("")
        
        if key == 27:
            break
        