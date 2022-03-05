#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')
sys.path.append('/home/ryan/Documents/RobotSystems/RobotSystems/ArmPi')
import time
from math import sqrt
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
from move import Motion
from doodleInput import DoodleInput



if __name__ == "__main__":
    arm = Motion()
    doodle = DoodleInput()
    print("HERE")