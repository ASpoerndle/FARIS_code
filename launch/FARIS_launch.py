import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node  # Make sure you imported Node!

def generate_launch_description():

    # 1. Find the Realsense package directory
    realsense_share_dir = get_package_share_directory('realsense2_camera')

    # 2. Include the rs_launch.py file
    realsense_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(realsense_share_dir, 'launch', 'rs_launch.py')
        ),
        # 3. Pass custom arguments here
        launch_arguments={
            'depth_module.profile': '640x480x30',
            'rgb_camera.profile': '640x480x30',
            'enable_sync': 'true',
            'align_depth.enable': 'true'
        }.items()
    )

    # 4. Define your listener node (fixed syntax)
    listen_node = Node(
        package='RobotController',
        executable='listener',
        name='listen',
        output='log'
    )

    # 5. MUST RETURN the LaunchDescription so ROS knows what to run!
    return LaunchDescription([
        realsense_node,
        listen_node
    ])
