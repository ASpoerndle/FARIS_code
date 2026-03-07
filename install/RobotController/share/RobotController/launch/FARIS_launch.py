from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='RobotController',
            executable='node',
            name='node',
            output='screen'
        ),
        Node(
            package='RobotController',
            executable='listener',
            name='listen',
            output='screen'
        ),
        # Add more nodes as needed
    ])

