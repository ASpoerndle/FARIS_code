import rclpy

from rclpy.node import Node

from std_msgs.msg import String

class CameraPublisher(Node):
    pipeline = rs.pipeline()
    
    def __init__(self):
        
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        adjustCam = AdjustCamera(480,480)
        # --- YOLOv8 Model Loading ---
        # Load your custom trained YOLOv8 model
        self.model = YOLO("./YOLOPencil.pt")

        # Define your class names (ensure they match your model's training)
        # YOLO models typically do not have a separate "background" class in their predictions.
        # The class indices in YOLO output directly correspond to your trained classes.
        self.CLASS_NAMES = ["Pencil"] # Adjust this based on your actual classes in YOLO.pt
        CameraPublisher.pipeline.start(config)
         

        super().__init__('minimal_publisher')

        self.publisher_ = self.create_publisher(Float32, "objDistance",10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i =0

    def getPipeline():
        return CameraPublisher.pipeline

    def timer_callback(self):
           # Get frameset of depth and color
        frames = CameraPublisher.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        #depth_image = np.asanyarray(depth_frame.get_data())
        original_color_image = np.asanyarray(color_frame.get_data())

        # Perform inference with YOLOv8 model
        # The YOLO model expects a BGR image (OpenCV's default) or RGB depending on its internal pre-processing.
        # Ultralytics YOLO models typically handle this internally when passed a numpy array.
        results = model(original_color_image, verbose=False) # verbose=False to suppress console output

        # Draw bounding boxes on the color image
        objDistance = draw_boxes(original_color_image, results,depth_frame, score_threshold=0.66)




        self.publisher_.publish(objDistance)
        self.get_logger().info('Publishing: "%f"' % objDistance.data)
        self.i+=1

    
def main(args = None):
    rclpy.init(args = args)
    camPublisher = CameraPublisher()
    rclpy.spin(camPublisher)
        
    #Destroy the node when it's finished
    camPublisher.getPipeline.
    camPublisher.destroy_node()
    rclpy.shutdown()
     
if __name__ == '__main__':
    main()
