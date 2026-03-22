# This node will take in a bounding box from the YOLO_node and the depth data from the depth/image_read_raw topic to find
# the distance from the robot to the center of the object

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Image
from robot_interfaces.msg import BoundingBox as BB
import cv2
import numpy as np
from cv_bridge import CvBridge
#model = YOLO("YOLOPencil.pt")
#CLASS_NAMES = ["Pencil"] 

"""
In the future, change so it doesn't send out until the box is first generated
"""

class DistanceFromObj_node(Node):
    
    def __init__(self):
        super().__init__('DistanceFromObj_node')
        self.msg = 0.0
        #sets the msg variable to be equal to my custom topic 
        #creates a topic that the node can publish to (bounding_box) with the bounding_box message type and sends a max of 10 at any one time
        self.publisher_ = self.create_publisher(float, 'distance_from_obj', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.publish_topic)
        #gets information from the /color/image_raw topic
        self.subscription = self.create_subscription(
            BB,
            'bounding_box',
            self.get_data_from_topic,
            10)
        self.subscription2 = self.create_subscription(Image,
            '/camera/camera/depth/image_rect_raw', self.retrieveDistance, 10)
        self.subscription  # prevent unused variable warning
        self.bridge = CvBridge()
       
    #method to publishes the bounding box outwards
    def publish_topic(self):
        self.publisher_.publish(self.msg)

    #uses the data from the /color/image_raw topic and puts it in the YOLO model and gets the bounding box coordinates 
    def get_data_from_topic(self, data):
      self.x1,self.x2,self.y1,self.y2 =  data.x1, data.x2, data.y1, data.y2
      
    def retrieveDistance(self):
      #method
      


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
