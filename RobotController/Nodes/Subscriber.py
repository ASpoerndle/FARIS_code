import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from .MotorController import MotorController


class MinimalSubscriber(Node):


    def __init__(self):
        super().__init__('UserInputSub')
        self.subscription = self.create_subscription(String,'topic',self.listener_callback,10)
        self.sub2 = self.create_subscription(Float32, 'distance_from_obj',self.move_forward,10)
        self.sub3 = self.create_subscription(Float32, 'auto_move',self.move_forward,10)
        self.subscription  # prevent unused variable warning
        self.motors = MotorController()
    def listener_callback(self, msg):
        msg = msg.data
        if(msg[0] == "C"):
            
        self.motors.adjustForward()
        self.motors.moveDistance(float(msg.data))
    def move_forward(self, distance):
        if(distance != 0):
            self.motors.moveDistance(distance)
def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()
    try:
        rclpy.spin(minimal_subscriber)
    except KeyboardInterrupt:
        
        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
        minimal_subscriber.destroy_node()
        rclpy.shutdown()
    


if __name__ == '__main__':
    main()
