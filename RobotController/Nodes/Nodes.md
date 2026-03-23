## This Folders holds the ROS2 nodes for the FARIS project

### SampleNode
#### Node name: node
#####The purpose of this node is to act as an interface for me to input a desired speed and for FARIS to move at that speed
---
### Subscriber
#### Node name: listener
#####The purpose of this node is to take in the input from **node** and to set the motors speed to that numerical value using the MotorController class
---
### YOLO_node
#### Node name: YOLO_node
#####The purpose of this node is to take in an image input from the Intel RealSense raw_image topic, run it through a premade YOLO model, and output a bounding box of where on the image one object is
---
### distanceFromObjNode.py
#### Node name: distance_node
#####The purpose of this node is to take in a bounding box message, take in a depth image input from the Intel RealSense depth/image_rect_raw topic and output how far away the bject is from the camera   
