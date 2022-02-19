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
    def __init__(self, camera) -> None:
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255)
        }
        
        self.size = (640, 480)

        # Garbo
        self.count = 0
        self.get_roi = False
        self.detect_color = 'None'
        self.target_color = ()
        
        # Camera from which to receive frames
        self.camera = camera
        self.camera.camera_open() 

    def get_frame(self, show_frame=False):
        """ retrieves a frame from the camera
        :params bool show_frame: show the frame or not
        """
        img = self.camera.frame
        if img is not None:
            frame = img.copy()
            if show_frame:
                cv2.imshow('Raw Frame', frame)
            return frame
        return None
    
    def preprocess(self, frame, show_frame=False):
        """ Performs some basic image preprocessing
        :params frame: frame to be processed
        :params bool show_frame: show the frame or not
        :return: image in LAB-space
        """
        frame_copy = frame.copy() # make a copy of the already copied frame?
        img_h, img_w = frame.shape[:2]  # get image dimensions
        cv2.line(frame, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(frame, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)
        
        
        frame_resize = cv2.resize(frame_copy, self.size, interpolation=cv2.INTER_NEAREST) # resizes the frame to be smaller, size is set outside the function -------------> bad
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11) # apply gaussian smoothing to resized frame
           
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)  # Convert image to LAB space

        if show_frame:
            cv2.imshow("LAB-space Frame", frame_lab)
        return frame_lab

    def find_cubes(self, frame_lab, frame, add_contours=True, show_frame=False):
        """ Finds a cube in a frame if it exists
        :params frame_lab: a frame in LAB space that has undergone preprocessing
        :params frame: the original frame
        :params bool add_contours: add contour boxes and text to original image
        :params bool show_frame: show the frame or not
        :return: frame with or without contours, and coordinates in world space of block (returns none if there is no block)
        """
        area_max = 0
        for i in color_range:  # loop over the "color range" which isn't defined anywhere somehow
            if i in self.target_color:  # and if the color is the target color
                detect_color = i  # = the target color
                frame_mask = cv2.inRange(frame_lab, color_range[detect_color][0], color_range[detect_color][1])  # Makes a black and white image where the color of interest (of a block) is between the range making it white and the background black
                opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))  # open operation
                closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))  # closed operation: attempts to remove false negatives imposed by the opening procedure
                contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]  # find the outline
                areaMaxContour, area_max = self.getAreaMaxContour(contours)  # find the largest contour (ideally the block) and return its area
        
        world_x = None  # if no 
        world_y = None
        if area_max > 2500:  # have found the largest area
            rect = cv2.minAreaRect(areaMaxContour) # places a rectangle around the contour (again ideally the block)
            box = np.int0(cv2.boxPoints(rect))  # not sure tbh

            roi = getROI(box) # get region of interest
            # get_roi = True 

            img_centerx, img_centery = getCenter(rect, roi, self.size, square_length)  # Get the coordinates of the center of the block
            world_x, world_y = convertCoordinate(img_centerx, img_centery, self.size) # Convert to real world coordinates
        
            if add_contours:
                cv2.drawContours(frame, [box], -1, self.range_rgb[detect_color], 2) # draw contour around the cube of the right color
                cv2.putText(frame, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[detect_color], 1) # draw center point
        
        return frame, (world_x, world_y)
    
    def reset(self) -> None:
        """ Reset all defaults, no parameters, returns nothing"""
        self.count = 0
        self.get_roi = False
        self.detect_color = 'None'
        self.target_color = ()
 
    @staticmethod
    def getAreaMaxContour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:  # iterate over all contours
            contour_area_temp = math.fabs(cv2.contourArea(c))  # calculate the contour area
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:  # The contour with the largest area is valid only if the 
                                            # area is greater than 300 to filter out the noise
                    area_max_contour = c

        return area_max_contour, contour_area_max  # returns the largest contour


if __name__ == "__main__":
    camera = Camera.Camera()
    p = Perception(camera)
    while True:
        frame = p.get_frame()
        if frame is not None:
            frame_preprocessed = p.preprocess(frame)
            frame_final, coords = p.find_cubes(frame_preprocessed, frame)
            cv2.imshow("Final Frame", frame_final)
            key = cv2.waitKey(1) 
            if key == 27:
                break
    camera.camera_close()
    cv2.destroyAllWindows()