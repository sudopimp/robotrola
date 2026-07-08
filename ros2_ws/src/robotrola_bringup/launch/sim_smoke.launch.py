from launch import LaunchDescription
from launch.actions import LogInfo, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    desc_launch = (
        Path(get_package_share_directory("robotrola_description"))
        / "launch"
        / "display.launch.py"
    )
    safety_launch = (
        Path(get_package_share_directory("robotrola_safety"))
        / "launch"
        / "safety.launch.py"
    )
    return LaunchDescription(
        [
            LogInfo(
                msg="Robotrola sim smoke: description display + safety supervisor node"
            ),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(desc_launch))),
            IncludeLaunchDescription(PythonLaunchDescriptionSource(str(safety_launch))),
        ]
    )
