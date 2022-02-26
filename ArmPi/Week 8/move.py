#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')
import cv2
import time
import Camera
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
        time.sleep(0.25)
        return angle

    def close_claw(self):
        Board.setBusServoPulse(1, self.neutral - 50, 300)
        time.sleep(1)
        
    def open_claw(self):
        Board.setBusServoPulse(1, self.neutral - 280, 500)
        time.sleep(1)
        
    def rotate_claw(self,a):
        Board.setBusServoPulse(2, a, 500)
        time.sleep(1)

    def initMove():
        self.close_claw
        self.rotate_claw(512)
        self.sweep((0, 10, 10), -30, -30, -90)
    
if __name__ == "__main__":
    initMove()
    sweep((-15 + 0.5, 6 - 0.5,  1.5),-90,-90,0)

