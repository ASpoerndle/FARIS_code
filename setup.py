import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'RobotController'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='aidan',
    maintainer_email='aidan@todo.todo',
    description='TODO: Package description',
    license='Apache License 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'node = RobotController.SampleNode:main',
            'listener = RobotController.Subscriber:main',
            'YOLO_node = RobotController.YOLO_node:main',
            'distance_node = RobotController.distanceFromObjNode.py:main'

        ],
    },
)
