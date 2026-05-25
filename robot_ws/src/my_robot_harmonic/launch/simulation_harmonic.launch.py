#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    """
    Launch file for spawning a robot in Gazebo Harmonic with ROS2 control
    """
    
    # Package name
    package_name = 'my_robot_harmonic'
    
    # Get package directories
    pkg_share = FindPackageShare(package=package_name)
    
    # Define paths
    urdf_path = PathJoinSubstitution([
        pkg_share,
        'urdf',
        'robot.urdf.xacro'
    ])
    
    controllers_path = PathJoinSubstitution([
        pkg_share,
        'config',
        'controllers.yaml'
    ])
    
    world_path = PathJoinSubstitution([
        pkg_share,
        'worlds',
        'empty.world'
    ])
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub', default='True')
    use_joint_state_pub_gui = LaunchConfiguration('use_joint_state_pub_gui', default='False')
    use_rviz = LaunchConfiguration('use_rviz', default='False')
    world = LaunchConfiguration('world', default=world_path)
    robot_name = LaunchConfiguration('robot_name', default='my_robot')
    spawn_x = LaunchConfiguration('spawn_x', default='0.0')
    spawn_y = LaunchConfiguration('spawn_y', default='0.0')
    spawn_z = LaunchConfiguration('spawn_z', default='0.1')
    
    # Declare launch arguments
    declared_arguments = [
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='True',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'use_robot_state_pub',
            default_value='True',
            description='Launch robot state publisher'
        ),
        DeclareLaunchArgument(
            'use_joint_state_pub_gui',
            default_value='False',
            description='Launch joint state publisher GUI'
        ),
        DeclareLaunchArgument(
            'use_rviz',
            default_value='False',
            description='Launch RViz visualization'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=world_path,
            description='Gazebo world file'
        ),
        DeclareLaunchArgument(
            'robot_name',
            default_value='my_robot',
            description='Name of the robot'
        ),
        DeclareLaunchArgument(
            'spawn_x',
            default_value='0.0',
            description='X coordinate for spawning'
        ),
        DeclareLaunchArgument(
            'spawn_y',
            default_value='0.0',
            description='Y coordinate for spawning'
        ),
        DeclareLaunchArgument(
            'spawn_z',
            default_value='0.1',
            description='Z coordinate for spawning'
        ),
    ]
    
    # Process xacro to get robot description - FIXED THIS PART
    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )
    
    # Robot State Publisher - FIXED PARAMETER PASSING
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        condition=IfCondition(use_robot_state_pub),
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Joint State Publisher GUI (optional, for manual joint control)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(use_joint_state_pub_gui),
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Gazebo Harmonic launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'gz_args': ['-r -v 4 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )
    
    # Log message when Gazebo is ready
    gazebo_ready_log = LogInfo(
        msg="Gazebo is starting... Robot will spawn in 5 seconds"
    )
    
    # Spawn robot in Gazebo Harmonic
    spawn_entity = TimerAction(
        period=5.0,
        actions=[
            LogInfo(msg="Spawning robot..."),
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', robot_name,
                    '-topic', 'robot_description',
                    '-x', spawn_x,
                    '-y', spawn_y,
                    '-z', spawn_z
                ],
                parameters=[{
                    'use_sim_time': use_sim_time
                }],
                output='screen'
            )
        ]
    )
    
    # ROS-Gazebo bridge for essential topics
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        arguments=[
            # Clock bridge
            '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock',
            # Command velocity
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            # Odometry
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            # TF
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            # Joint states (from Gazebo to ROS)
            '/world/empty/model/my_robot/joint_state@sensor_msgs/msg/JointState@gz.msgs.Model',
        ],
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('/world/empty/model/my_robot/joint_state', '/joint_states')
        ],
        output='screen'
    )
    
    # ROS2 Control node
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager',
        parameters=[{
            'use_sim_time': use_sim_time
        }, controllers_path],
        output='screen'
    )
    
    # Spawn joint state broadcaster
    joint_state_broadcaster_spawner = TimerAction(
        period=8.0,
        actions=[
            LogInfo(msg="Loading joint_state_broadcaster..."),
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'joint_state_broadcaster',
                    '--controller-manager', '/controller_manager'
                ],
                parameters=[{
                    'use_sim_time': use_sim_time
                }],
                output='screen'
            )
        ]
    )
    
    # Spawn diff drive controller
    diff_drive_controller_spawner = TimerAction(
        period=10.0,
        actions=[
            LogInfo(msg="Loading diff_drive_controller..."),
            Node(
                package='controller_manager',
                executable='spawner',
                arguments=[
                    'diff_drive_controller',
                    '--controller-manager', '/controller_manager'
                ],
                parameters=[{
                    'use_sim_time': use_sim_time
                }],
                output='screen'
            )
        ]
    )
    
    # Static transform publisher (if needed)
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'odom'],
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # RViz for visualization (optional)
    rviz_config_path = PathJoinSubstitution([
        pkg_share,
        'config',
        'display.rviz'
    ])
    
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        condition=IfCondition(use_rviz),
        parameters=[{
            'use_sim_time': use_sim_time
        }],
        output='screen'
    )
    
    # Create launch description
    ld = LaunchDescription(declared_arguments)
    
    # Add actions to launch description
    ld.add_action(robot_state_publisher)
    ld.add_action(joint_state_publisher_gui)
    ld.add_action(gazebo)
    ld.add_action(gazebo_ready_log)
    ld.add_action(spawn_entity)
    ld.add_action(bridge)
    ld.add_action(controller_manager)
    ld.add_action(joint_state_broadcaster_spawner)
    ld.add_action(diff_drive_controller_spawner)
    ld.add_action(static_tf)
    ld.add_action(rviz)
    
    return ld
