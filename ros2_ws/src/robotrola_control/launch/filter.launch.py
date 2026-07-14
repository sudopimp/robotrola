from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="robotrola_control",
                executable="joint_command_filter_node.py",
                name="robotrola_joint_command_filter",
                output="screen",
            )
        ]
    )
