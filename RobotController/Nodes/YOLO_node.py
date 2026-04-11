import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Image
from robot_interfaces.msg import BoundingBox as BB
import cv2
import numpy as np
import torch
torch.backends.cudnn.benchmark = False
from ultralytics import YOLO
from cv_bridge import CvBridge
#model = YOLO("YOLOPencil.pt")
#CLASS_NAMES = ["Pencil"] 

"""
In the future, change so it doesn't send out until the box is first generated
"""

class YOLO_node(Node):
    
    def __init__(self):
        super().__init__('YOLO_node')
        #sets the msg variable to be equal to my custom topic 
        self.msg = BB()
        self.model = YOLO("/home/aidan/ros2_humble/src/RobotController/RobotController/YOLOPencil.pt")
        CLASS_NAMES = ["Pencil"]
        #creates a topic that the node can publish to (bounding_box) with the bounding_box message type and sends a max of 10 at any one time
        self.publisher_ = self.create_publisher(BB, 'bounding_box', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.publish_topic)
        #gets information from the /color/image_raw topic
        self.subscription = self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.get_data_from_topic,
            10)
        self.subscription  # prevent unused variable warning
        self.bridge = CvBridge()
       
    #method to publishes the bounding box outwards
    def publish_topic(self):
        self.publisher_.publish(self.msg)

    #uses the data from the /color/image_raw topic and puts it in the YOLO model and gets the bounding box coordinates 
    def get_data_from_topic(self, image):
        cv2image = self.bridge.imgmsg_to_cv2(image, "bgr8")
       #np.asanyarray(color_frame.get_data())
        results = self.model(cv2image, verbose=False, device = 'cpu') # verbose=False to suppress console output  device = 'cpu')
        cords = self.draw_boxes(cv2image, results, score_threshold=0.66)
        if(cords == None):
            self.msg.x1 = 0
            self.msg.x2 = 0
            self.msg.y1 = 0
            self.msg.y2 = 0
        else:
            x1,x2,y1,y2 = cords
            self.msg.x1 = x1
            self.msg.x2 = x2
            self.msg.y1 = y1
            self.msg.y2 = y2
        #actually gets the bounding box from the models results
    def draw_boxes(self, image, results,score_threshold):
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
                    return(x1,x2,y1,y2)
        return 0,1,0,1
                 #    # Draw rectangle
                 #    color = (0, 255, 0) # Green color for bounding box
                 #    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                 #   # print(x1,x2,y1,y2)
                 #    # Put text (label and score)
                 #    # Ensure the class ID is within the bounds of CLASS_NAMES
                 #    if cls < len(CLASS_NAMES):
                 #        text = f"{CLASS_NAMES[cls]}: {conf:.2f}"
                 #    else:
                 #        text = f"Class {cls}: {conf:.2f}" # Fallback if label index is out of bounds
                 #    print(text) 
                   
                 # #   cv2.putText(image, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                 #    centerx, centery = int((x2-x1) / 2), int((y2-y1)/2)
                 #    dis = depth_frame.get_distance(centerx, centery)
                            
                 #    if(dis < .26 and dis > 0):
                 #        print(x1)
                 #        adjustCam.setX1(x1)
                 #        adjustCam.adjustDir()    
            


def main(args=None):
    rclpy.init(args=args)

    yolo_node = YOLO_node()
    try:
        rclpy.spin(yolo_node)
    except KeyboardInterrupt:
        
        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
        yolo_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
