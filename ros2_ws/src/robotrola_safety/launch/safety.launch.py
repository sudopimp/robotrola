from launch import LaunchDescription
from launch.actions import LogInfo, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from pathlib import Path


def generate_launch_description():
    # repo root: .../ros2_ws/src/robotrola_safety/launch/this → parents[4]
    repo = Path(__file__).resolve().parents[4]
    default_limits = str(repo / "configs" / "safety_limits.yaml")
    # installed script path may differ; node executable name matches install PROGRAMS
    return LaunchDescription(
        [
            DeclareLaunchArgument("limits_path", default_value=default_limits),
            LogInfo(msg="Robotrola safety launch: thin node → robotrola.safety library"),
            Node(
                package="robotrola_safety",
                executable="safety_supervisor_node.py",
                name="robotrola_safety_supervisor",
                output="screen",
                parameters=[{"limits_path": LaunchConfiguration("limits_path")}],
            ),
        ]
    )
