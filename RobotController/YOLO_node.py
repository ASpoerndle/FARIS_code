import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from sensor_msgs.msg import Image

"""
In the future, change so it doesn't sound out until the box is first generated
"""
class YOLO_node(Node):

    def __init__(self):
        super().__init__('YOLO_node')
        self.publisher_ = self.create_publisher(String, 'bounding_box', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.subscription = self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
       

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        self.i += 1
    def listener_callback(self, msg):
        


def main(args=None):
    rclpy.init(args=args)

    yolo_node = YOLO_node()

    rclpy.spin(yolo_node)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    yolo_node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
