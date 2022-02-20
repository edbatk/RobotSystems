#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/School/RobotSystems/ArmPi/')
import cv2
import time
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Perception():
    def __init__(self,camera) -> None:
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        },
        

        self.size = (640, 480)

        self.world_x = 0
        self.world_Y = 0
        self.world_x = 0
        self.world_y = 0
        self.last_x = 0
        self.last_y = 0
        self.target_color = ()
        
        self.camera = camera
        self.camera.camera_open()
    
    def get_image(self,show_frame=False,target_color='red'):
        self.target_color = target_color
        img = self.camera.frame
        if img is not None:
            frame = img.copy()
            if (show_frame):
                cv2.imshow('Frame', frame)
            return frame
            
    # def get_frame(self, show_frame=False):
    #     """ retrieves a frame from the camera
    #     :params bool show_frame: show the frame or not
    #     """
    #     img = self.camera.frame
    #     if img is not None:
    #         print('img acquired')
    #         frame = img.copy()
    #         if show_frame:
    #             cv2.imshow('Raw Frame', frame)
    #         return frame
    #     return None
            
    def process(self,Frame,show_frame=False):
        img_copy = Frame.copy()
        img_h, img_w = img_copy.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        # If an area is detected with a recognized object, the area is detected until there are none        
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space
        if (show_frame):
            cv2.imshow('Frame Lab', frame_lab)
        return frame_lab
    
    def find(self,frame_lab,show_frame=False):
        area_max = 0
        areaMaxContour = 0
        for i in color_range:
            if i in self.target_color:
                detect_color = i
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
    percep = Perception(camera)
    while True:
        # img = percep.get_frame(show_frame=True)
        img = percep.get_image(show_frame=True)
        if img is not None:
            process_img = percep.process(img,show_frame=(True))
            found_img = percep.find(process_img,show_frame=(True))
            key = cv2.waitKey(1) 
            if key == 27:
                break
        # else:
        #     break
        # key = cv2.waitKey(1)
        # if key == 27:
        #     break
    camera.camera_close()
    cv2.destroyAllWindows()
