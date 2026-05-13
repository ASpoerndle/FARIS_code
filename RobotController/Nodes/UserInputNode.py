import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Float32
class ExampleNode(Node):
    def __init__(self):
        super().__init__("UserInput")
        self.get_logger().info("Hello from ROS2")
        self.manual = self.create_publisher(Float32, 'manual_mode', 10)
        self.auto = self.create_publisher(Float32,'auto_mode',10)
        self.vision = self.create_publisher(Float32, 'vision_mode',10)

        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = Float32()
        print("Farming Automaton for Row-Intercopping Systems")
        choice = input("Input a for auto_move | Input c for controller | Input m for manual move")
        choice = choice[0].upper()
        if(choice[0].upper() == "A"):
            msg.data = 1.0
            self.auto.publish(msg)

        if(choice == "M"):
            choice = input("H for horizontal mode | F for forward/backward movement | B for box drill | R for rotation | A for adjust forward")
            if(choice == "H"):
                msg.data = 1001.0
            if(choice == "F"):
                data = input("How far? (m)")
                msg.data = float(data)
            if(choice == "B"):
                distance = float(input("How far? (m)"))
                msg.data = 1002 + distance/100
            if(choice == "R"):
                rotation = float(input("How much rotation? (degrees)"))
                rotation = rotation % 360
                msg.data = 1003.0 + rotation/360
            if(choice == "A"):
                msg.data = 1005.0
            self.manual.publish(msg)
        if(choice[0].upper() == "V"):
            msg.data = 1.0
            self.vision.publish(msg)
        if(choice == "C"):
            msg.data = 1006.0
            self.manual.publish(msg)

            
        #msg.data = input("what distance?")
        #self.publisher_.publish(msg)
        #self.get_logger().info('Publishing: "%s"' % msg.data)
        #self.i += 1



def main(args=None):
    rclpy.init(args=args)
    node = ExampleNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        
        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
        main()
