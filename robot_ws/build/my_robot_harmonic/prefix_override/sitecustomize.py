import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/unicycle/Desktop/ROS2_Gazebo_Obj_Move/robot_ws/install/my_robot_harmonic'
