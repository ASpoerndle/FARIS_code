import rclpy
from rclpy.node import Node
from std_msgs.msg import String
class ExampleNode(Node):
    def __init__(self):
        super().__init__("User Input")
        self.get_logger().info("Hello from ROS2")
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
    def timer_callback(self):
        msg = String()
        print("Farming Automaton for Row-Intercopping Systems")
        choice = input("Input a for auto_move | Input c for camera move | Input m for manual move")
        if(choice[0].upper == "A"):
            msg.data = "A"
        if(choice[0].upper == "M"):
            data = input("How far? (m)")
            msg.data = "M" + data
        if(choice[0].upper == "C"):
            msg.data = "C"
            
        msg.data = input("what distance?")
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1



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
