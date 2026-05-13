import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from .MotorController import MotorController
from std_msgs.msg import Float32
from .Controller import controller

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
        self.auto = self.create_subscription(Float32, 'auto_mode',self.auto_mode,10)





        self.autoDis = 0
        #self.subscription  # prevent unused variable warning
        self.motors = MotorController()
        self.motors.adjustForward(False)
        self.controller = controller(self.motors)
    def auto_mode(self,msg):
        print(msg.data)
        print(msg)
        if(self.autoDis != 0):
            self.move_distance(self.autoDis)
            self.autoDis = 0

    def controller_mode(self):
        self.controller.use_controller()
    def manual_mode(self,msg):
        data = msg.data

        print(data)
        

        if(data <= 1 and data >= -1):
            self.move_forward(data,1)
        if(data == 1001.0):
            self.motors.horizontalMode()
        if(data >= 1002.0 and data < 1003.0):
            dis = abs(1002-data) * 100
            self.motors.boxDrill(int(dis))
        if(data >= 1003 and data < 1004):
            rotate = abs(1003-data) * 360
            if(rotate > 180):
                rotate -= 360
            print("Rotation: " + str(rotate))
            self.motors.rotatePods(rotate,0.5)
        if(data == 1005):
            self.motors.adjustForward()
        if(data == 1006):
            print(f"===Init Controller Mode===")
            self.controller_mode()
            
    def setAutoMove(self,msg):
        self.autoDis = msg.data
        print(msg.data)
        self.motors.moveDistance(self.autoDis,False,False)
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
        dis = distance.data
        if(distance != 0 ):
            self.get_logger().info('Moving "%d"' % dis)
            self.motors.moveDistance(dis/10, False,False)


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
