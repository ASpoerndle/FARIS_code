import pyrealsense2 as rs
import cv2
import numpy as np
import torch
from ultralytics import YOLO # Import YOLO from ultralyticsvo
from AdjustCamera import AdjustCamera
val = "cuda"
device = torch.device("cpu")
# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
adjustCam = AdjustCamera(480,480)
# --- YOLOv8 Model Loading ---
# Load your custom trained YOLOv8 model
#model = YOLO("C:/Users/thega/anaconda_projects/test/YOLO.pt") # Ensure this path is correct
model = YOLO("./YOLOPencil.pt")
#print(model)
# Set the model to evaluation mode
#model.eval()

# Define your class names (ensure they match your model's training)
# YOLO models typically do not have a separate "background" class in their predictions.
# The class indices in YOLO output directly correspond to your trained classes.
CLASS_NAMES = ["Pencil"] # Adjust this based on your actual classes in YOLO.pt

def draw_boxes(image, results, depth_frame,score_threshold):
    # Ensure image is writeable for drawing
    image = image.copy()
    
    
    # YOLOv8 returns a list of Results objects
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
                color = (0, 255, 0) # Green color for bounding box
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
               # print(x1,x2,y1,y2)
                # Put text (label and score)
                # Ensure the class ID is within the bounds of CLASS_NAMES
                if cls < len(CLASS_NAMES):
                    text = f"{CLASS_NAMES[cls]}: {conf:.2f}"
                else:
                    text = f"Class {cls}: {conf:.2f}" # Fallback if label index is out of bounds
               
               
                cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                centerx, centery = int((x2-x1) / 2), int((y2-y1)/2)
                dis = depth_frame.get_distance(centerx, centery)
               
                if(dis < .26 and dis > 0):
                    print(x1)
                    adjustCam.setX1(x1)
                    adjustCam.adjustDir()
                
    return image

# --- Rest of your code ---
# Start streaming
pipeline.start(config)

try:
    while True:
        # Get frameset of depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        original_color_image = np.asanyarray(color_frame.get_data())

        # Perform inference with YOLOv8 model
        # The YOLO model expects a BGR image (OpenCV's default) or RGB depending on its internal pre-processing.
        # Ultralytics YOLO models typically handle this internally when passed a numpy array.
        results = model(original_color_image, verbose=False) # verbose=False to suppress console output

        # Draw bounding boxes on the color image
        color_image_with_boxes = draw_boxes(original_color_image, results,depth_frame, score_threshold=0.66)

        # Apply colormap on depth image (optional)
     #   depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
     #   images_to_show = np.hstack((color_image_with_boxes, depth_colormap))

        # Show images
        #cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        #cv2.imshow('RealSense', images_to_show)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

finally:
    # Stop streaming
    pipeline.stop()
    #cv2.destroyAllWindows()
