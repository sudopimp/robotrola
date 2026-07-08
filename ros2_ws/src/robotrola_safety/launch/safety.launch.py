from launch import LaunchDescription
from launch.actions import LogInfo


def generate_launch_description():
    return LaunchDescription([LogInfo(msg='Robotrola safety launch placeholder: wire rclpy node after hardware review')])
