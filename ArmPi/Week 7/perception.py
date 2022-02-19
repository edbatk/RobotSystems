#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')
import cv2
import time
import Camera
import threading
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class perception():
    def __init__(self,camera):
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        self.camera = camera
        self.camera.camera_open()
        self.target_color = ()
        self.grip = 500 # servo grip angle
        self.count = 0
        self.track = False
        self._stop = False
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_x = 0
        self.world_Y = 0
        self.world_x = 0
        self.world_y = 0
        self.last_x = 0
        self.last_y = 0

        self.color_range = {
        'red': [(0, 151, 100), (255, 255, 255)], 
        'green': [(0, 0, 0), (255, 115, 255)], 
        'blue': [(0, 0, 0), (255, 255, 110)], 
        'black': [(0, 0, 0), (56, 255, 255)], 
        'white': [(193, 0, 0), (255, 250, 255)], 
        }
        
    def reset(self):
        self.grip = 500 # servo grip angle
        self.count = 0
        self.get_roi = False
        self.center_list = []
        self.first_move = True
        self.__isRunning = False
        self.detect_color = 'None'
        self.action_finish = True
        self.start_pick_up = False
        self.start_count_t1 = True
        self.rect = None
        self.size = (640, 480)
        self.rotation_angle = 0
        self.unreachable = False
        self.world_x = 0
        self.world_Y = 0
        self.world_x = 0
        self.world_y = 0
        self.last_x = 0
        self.last_y = 0
    
    def get_image(self,camera,show_frame=False,target_color='red'):
        self.target_color = target_color
        print(f"my_camera: {self.camera}")
        camera_open()
        # img = self.camera.frame()
        img = camera.frame()
        print(f"image: {img}")
        if img is not None:
            frame = img.copy()
            Frame = run(frame)  
            if (show_frame):
                cv2.imshow('Frame', Frame)
            return Frame
        else:
            print('Error no image')
            
    def process(self,Frame,show_frame=False):
        img_copy = Frame.copy()
        img_h, img_w = img_copy.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        frame_resize = cv2.resize(img_copy, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        # If an area is detected with a recognized object, the area is detected until there are none
        if get_roi and start_pick_up:
            get_roi = False
            frame_gb = getMaskROI(frame_gb, roi, size)           
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        if (show_frame):
            cv2.imshow('Frame Lab', frame_lab)
        return frame_lab
    
    def find(self,frame_lab,show_frame=False):
        area_max = 0
        areaMaxContour = 0
        for i in self.color_range:
            if j in self.target_color:
                detect_color = j
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # Bitwise operations on the original image and mask
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # closed operation
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find the outline
                areaMaxContour, area_max = getAreaMaxContour(contours)  # find the largest contour
        if area_max > 2500:  # have found the largest area
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))

            roi = getROI(box) # get roi region
            get_roi = True

            img_centerx, img_centery = getCenter(rect, roi, size, square_length)  # Get the coordinates of the center of the block
            self.world_x, self.world_y = convertCoordinate(img_centerx, img_centery, size) # Convert to real world coordinates
            
            
            cv2.drawContours(img, [box], -1, range_rgb[detect_color], 2)
            cv2.putText(img, '(' + str(self.world_x) + ',' + str(self.world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, range_rgb[detect_color], 1) # draw center point
            distance = math.sqrt(pow(self.world_x - self.last_x, 2) + pow(self.world_y - self.last_y, 2)) # Compare the last coordinates to determine whether to move
            self.last_x, self.last_y = self.world_x, self.world_y
            
            if (show_frame):
                cv2.imshow('Found Frame', img)
            
            return img
        
    def getAreaMaxContour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # iterate over all contours
            contour_area_temp = math.fabs(cv2.contourArea(c))  # Calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # The contour with the largest area is valid only if the area is greater than 300 to filter out the noise
                    area_max_contour = c

        return area_max_contour, contour_area_max  # returns the largest contour
        
if __name__ == "__main__":
    camera = Camera.Camera()
    print(f"camera: {camera}")
    percep = perception(camera)
    # percep.reset()
    while True:
        img = percep.get_image(camera,how_frame=(True))
        print('image collected')
        if img is not None:
            process_img = percep.process(img,show_frame=(True))
            print('image processed')
            found_img = percep.find(process_img,show_frame=(True))
            print('block found')
            key = cv2.waitKey(1) 
            if key == 27:
                break
        else:
            break
    camera.camera_close()
    cv2.destroyAllWindows()
