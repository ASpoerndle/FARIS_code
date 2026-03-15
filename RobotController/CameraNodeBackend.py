"""import pyrealsense2 as rs
import cv2
import numpy as np
import torch
from ultralytics import YOLO # Import YOLO from ultralyticsvo
from AdjustCamera import AdjustCamera

class CameraNodeBackend():
    def __init__(self):
        


# Configure depth and color streams
    def draw_boxes(image, results, depth_frame,score_threshold):
        image = image.copy()
        
            
        # Assuming batch size of 1, we take the first result
        if results and len(results) > 0:
            result = results[0]

            # Boxes, scores, and class IDs are typically accessed via result.boxes
            for box in result.boxes:
                conf = box.conf.item() # Confidence score
                cls = int(box.cls.item()) # Class ID
                xyxy = box.xyxy[0].cpu().numpy() # Bounding box coordinates [x1, y1, x2, y2]

                if conf > score_threshold:
                    x1, y1, x2, y2 = map(int, xyxy)

                    # Draw rectangle
                    # Put text (label and score)
                    # Ensure the class ID is within the bounds of CLASS_NAMES
                    #if cls < len(CLASS_NAMES):
                    #    text = f"{CLASS_NAMES[cls]}: {conf:.2f}"
                    #else:
                    #    text = f"Class {cls}: {conf:.2f}" # Fallback if label index is out of bounds
                    if cls < len(CLASS_NAMES):
                        text = [CLASS_NAMES[cls],conf]

                    print(text) 
                   
                    centerx, centery = int((x2-x1) / 2), int((y2-y1)/2)
                    dis = depth_frame.get_distance(centerx, centery)
                      
    #Code to adjust the robot to align center with an object

                  #  if(dis < .26 and dis > 0):
                   #     print(x1)
                    #    adjustCam.setX1(x1)
                     #   adjustCam.adjustDir()
                    
        

    # --- Rest of your code ---
    # Start streaming
        # Stop streaming
   

"""
