#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    package_name = 'my_robot_harmonic'
    pkg_share = FindPackageShare(package=package_name)
    
    urdf_path = PathJoinSubstitution([pkg_share, 'urdf', 'robot.urdf.xacro'])
    world_path = PathJoinSubstitution([pkg_share, 'worlds', 'empty.world'])
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    robot_name = LaunchConfiguration('robot_name', default='my_robot')
    
    # Process xacro
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path]), value_type=str
    )
    
    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}]
    )
    
    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ]),
        launch_arguments={'gz_args': ['-r -v 4 ', world_path]}.items()
    )
    
    # Spawn robot
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=['-name', robot_name, '-topic', 'robot_description']
            )
        ]
    )
    
    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='True'),
        DeclareLaunchArgument('robot_name', default_value='my_robot'),
        robot_state_publisher,
        gazebo,
        spawn_robot,
        bridge
    ])
