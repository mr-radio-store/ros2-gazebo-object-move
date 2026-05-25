#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import select
import termios
import tty
import os

class TeleopKeyboardHarmonic(Node):
    def __init__(self):
        super().__init__('teleop_keyboard_harmonic')
        
        # Publisher for velocity commands
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Movement parameters
        self.linear_speed = 0.5
        self.angular_speed = 1.0
        
        self.get_logger().info(
            "\nTeleop Keyboard for Gazebo Harmonic\n"
            "-------------------------------------\n"
            "Use arrow keys or WASD to move:\n"
            "  ↑/W: Forward\n"
            "  ↓/S: Backward\n"
            "  ←/A: Turn Left\n"
            "  →/D: Turn Right\n"
            "  Space: Stop\n"
            "  Q: Quit\n"
        )
        
    def get_key(self):
        """Non-blocking keyboard input"""
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key
    
    def run(self):
        """Main control loop"""
        # Save terminal settings
        self.settings = termios.tcgetattr(sys.stdin)
        twist = Twist()
        
        try:
            while rclpy.ok():
                key = self.get_key()
                
                # Handle arrow keys (escape sequences)
                if key == '\x1b':
                    key += self.get_key() + self.get_key()
                
                # Reset twist
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                
                if key == '\x1b[A' or key == 'w':  # Up or W
                    twist.linear.x = self.linear_speed
                    self.get_logger().info('Moving forward')
                elif key == '\x1b[B' or key == 's':  # Down or S
                    twist.linear.x = -self.linear_speed
                    self.get_logger().info('Moving backward')
                elif key == '\x1b[D' or key == 'a':  # Left or A
                    twist.angular.z = self.angular_speed
                    self.get_logger().info('Turning left')
                elif key == '\x1b[C' or key == 'd':  # Right or D
                    twist.angular.z = -self.angular_speed
                    self.get_logger().info('Turning right')
                elif key == ' ':  # Space
                    self.get_logger().info('Stopping')
                elif key == 'q':  # Quit
                    self.get_logger().info('Quitting teleop')
                    break
                
                # Publish command
                self.publisher.publish(twist)
                
                # Small delay
                rclpy.spin_once(self, timeout_sec=0.1)
                
        except Exception as e:
            self.get_logger().error(f'Error: {e}')
        finally:
            # Stop robot
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher.publish(twist)
            
            # Restore terminal
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopKeyboardHarmonic()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()