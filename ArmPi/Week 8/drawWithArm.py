#!/usr/bin/python3
# coding=utf8
import numpy as np
import sys
# import pandas as pd
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
    
    # coords = pd.read_csv('draw_coords.csv')
    # coords = coords.to_numpy()
    coords = np.loadtxt('draw_coords.csv', delimiter=",")
    coords = coords/10
    coords = np.round(coords)
    
    coords[:,0] -= 10
    coords[:,1] += 1
    
    i = 1
    while i < len(coords):
        if (coords[i] == coords[i-1]).all():
            coords = np.delete(coords, i-1, 0)
        else:
            i += 1
    
    print("Starting Masta' Peace! (˘ ³˘)♥ ")
    
    arm.sweep(coords[0,0],coords[0,1],10,0,-180,180)
    time.sleep(0.5)
    
    for i in range(len(coords)):
        print(f"current coordinates: {coords[i]}")
        arm.sweep(coords[i,0],coords[i,1],10,0,-180,180)
        # time.sleep(0.01)
        
    print("All done!")
    