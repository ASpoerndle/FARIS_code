import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Image
from std_msgs.msg import Float32
from robot_interfaces.msg import BoundingBox as BB
import cv2
import numpy as np
import torch
torch.backends.cudnn.benchmark = False
from ultralytics import YOLO
from cv_bridge import CvBridge
import message_filters
#model = YOLO("YOLOPencil.pt")
CLASS_NAMES = ["Pencil"] 

"""
In the future, change so it doesn't send out until the box is first generated
"""

class YOLO_node(Node):
    
    def __init__(self):
        super().__init__('YOLO_node')
        #sets the msg variable to be equal to my custom topic 
        self.msg = Float32()
        self.msg2 = BB()
        self.model = YOLO("/home/aidan/ros2_humble/src/RobotController/RobotController/best.pt")
        #CLASS_NAMES = ["radish","tomato"]
        #creates a topic that the node can publish to (bounding_box) with the bounding_box message type and sends a max of 10 at any one time
        self.publisher_ = self.create_publisher(BB, 'bounding_box', 10)
        self.distance_from_object = self.create_publisher(Float32, 'distance_from_obj', 10)
        self.vision = self.create_subscription(Float32, 'vision_mode', self.push_distance_to_listener, 10)


        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.publish_topic)
        #gets information from the /color/image_raw topic

        self.raw_image = message_filters.Subscriber(
            self,Image,
            '/camera/camera/color/image_raw')
        self.depth_image = message_filters.Subscriber(self, Image, '/camera/camera/depth/image_rect_raw')
        # self.sub_a = message_filters.Subscriber(self, PoseStamped, 'robot/pose_left')

        self.bridge = CvBridge()
        self.synced_cam_data = message_filters.ApproximateTimeSynchronizer(
            [self.raw_image, self.depth_image],
            queue_size=10,
            slop=0.1 #time delay idk why they call it slop seems kinda strange ngl
        )
        self.synced_cam_data.registerCallback(self.get_data_from_topic)
        self.distance = 0
       
    #method to publishes the bounding box outwards
    def publish_topic(self):
        self.publisher_.publish(self.msg2)

    #uses the data from the /color/image_raw topic and puts it in the YOLO model and gets the bounding box coordinates 
    def get_data_from_topic(self, raw_image,depth_image):
        cv2image = self.bridge.imgmsg_to_cv2(raw_image, "bgr8")
        cv2image = cv2.resize(cv2image,(848,480))
        results = self.model(cv2image, verbose=False, device = 'cpu')
        cords = self.grab_cords(results, score_threshold=0.66)
        if((not cords == None)):
            x1,x2,y1,y2 = cords
            if(x1 == 0):
                return
            cv_depth_image = self.bridge.imgmsg_to_cv2(depth_image, desired_encoding='passthrough')
            self.msg2.x1 = x1
            self.msg2.x2 = x2
            self.msg2.y1 = y1
            self.msg2.y2 = y2
            centerx = int((x2 + x1) / 2)
            centery = int((y2 + y1) / 2)
            
            print(x1,x2,y1,y2)
            print(f'Centerx: {centerx} | Centery: {centery}')
            if (centerx < 848 and centery < 480):
                depth_value = cv_depth_image[int(centery), int(centerx)]
                if(depth_value < self.distance and depth_value != 0 or self.distance == 0):
                    self.distance = float(depth_value / 1000)
                print(self.distance, "mm")
                self.publish_topic()

    def push_distance_to_listener(self,msg):
        dis = self.distance
        self.distance =0
        msg = Float32()
        msg.data = float(dis)
        self.distance_from_object.publish(msg)
        #actually gets the bounding box from the models results
    def grab_cords(self, results,score_threshold):
        if results and len(results) > 0:
            result = results[0]
    
            # Boxes, scores, and class IDs are typically accessed via result.boxes
            for box in result.boxes:
                conf = box.conf.item() # Confidence score
                cls = int(box.cls.item()) # Class ID

                xyxy = box.xyxy[0].cpu().numpy()
                if conf > score_threshold:
                    #print(cls)
                    x1, y1, x2, y2 = map(int, xyxy)
                    return(x1,x2,y1,y2)
        return 0,0,0,0



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
