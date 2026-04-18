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
        self.vision = self.create_publisher(Float32, 'vision',10)

        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
    def timer_callback(self):
        msg = Float32()
        print("Farming Automaton for Row-Intercopping Systems")
        choice = input("Input a for auto_move | Input c for camera move | Input m for manual move")
        if(choice[0].upper == "A"):
            msg.data = 1
            self.auto.publish(msg)

        if(choice == "m"):
            data = input("How far? (m)")
            msg.data = float(data)
            self.manual.publish(msg)
        if(choice[0].upper == "C"):
            msg.data = 1
            self.vision.publish(msg)
            
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
