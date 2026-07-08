
# ROS 2 setup

Baseline: Ubuntu 24.04 + ROS 2 Jazzy.

```bash
sudo apt update
sudo apt install python3-colcon-common-extensions python3-rosdep
sudo rosdep init || true
rosdep update
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Package roles:

- `robotrola_description`: URDF, meshes, RViz config.
- `robotrola_msgs`: custom safety/feature messages.
- `robotrola_safety`: runtime safety gate.
- `robotrola_control`: controller configs and action filters.
- `robotrola_perception`: RGB-D camera and detection configs.
- `robotrola_bringup`: launch files.
- `robotrola_teleop`: guarded teleoperation.
