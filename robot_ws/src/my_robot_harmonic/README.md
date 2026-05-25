
## Prerequisites

- ROS 2 (Humble/Iron/Rolling)
- Gazebo Harmonic
- ROS 2 control packages

### Install Dependencies

```bash
# Install ROS 2 packages
sudo apt install ros-${ROS_DISTRO}-gazebo-ros-pkgs
sudo apt install ros-${ROS_DISTRO}-robot-state-publisher
sudo apt install ros-${ROS_DISTRO}-joint-state-publisher
sudo apt install ros-${ROS_DISTRO}-joint-state-publisher-gui
sudo apt install ros-${ROS_DISTRO}-xacro
sudo apt install ros-${ROS_DISTRO}-controller-manager
sudo apt install ros-${ROS_DISTRO}-diff-drive-controller
sudo apt install ros-${ROS_DISTRO}-joint-trajectory-controller


# Navigate to your workspace
cd ~/Desktop/ROS2_Gazebo_Obj_Move/robot_ws

# Build the package
colcon build --packages-select my_robot_harmonic

# Source the workspace
source install/setup.bash


ros2 launch my_robot_harmonic simulation_harmonic.launch.py