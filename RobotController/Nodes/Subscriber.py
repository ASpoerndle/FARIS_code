import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from .MotorController import MotorController
from std_msgs.msg import Float32

class MinimalSubscriber(Node):


    def __init__(self):
        #Allow methods to run
        self.allowC = False
        self.allowM = False
        self.allowA = False
        self.manualDis = 0
        super().__init__('UserInputSub')
        self.subscription = self.create_subscription(String,'topic',self.listener_callback,10)
        self.sub2 = self.create_subscription(Float32, 'distance_from_obj',self.move_forward,10)
        self.sub3 = self.create_subscription(Float32, 'auto_move',self.setAutoMove,10)
        #Modes
        self.manual = self.create_subscription(Float32, 'manual_mode',self.manual_mode,10)
        self.auto = self.create_subcription(Float32, 'auto_mode',self.auto_mode,10)

        self.autoDis = 0
        self.subscription  # prevent unused variable warning
        self.motors = MotorController()
    def auto_mode(self,msg):
        print(msg.data)
        print(msg)
        if(self.autoDis != 0):
            self.move_forward(self.autoDis)
            self.autoDis = 0
    def vision_mode(self,msg):
        print(msg.data)
        print(msg)
    def manual_mode(self,msg):
        print(msg.data)
        print(msg)
        self.move_forward(msg.data)
    def setAutoMove(self,msg):
        self.autoDis = msg.data
    def listener_callback(self, msg):
        msg = msg.data
        print(msg)
        if(msg[0] == "C"):
            self.allowC = True
        if(msg[0] == "M"):
            self.allowM = True
            self.manualDis = int(msg[1:])
            self.move_forward(self.manualDis)
        if(msg[0] == "A"):
            self.allowA = True


            
        # self.motors.adjustForward()
        # self.motors.moveDistance(float(msg.data))
    def move_forward(self, distance):

        if(distance != 0 ):
            self.get_logger().info('Moving "%d"' % distance)
            self.motors.moveDistance(distance)
            self.manualDis = 0

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
