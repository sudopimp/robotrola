cmake_minimum_required(VERSION 3.8)
project(robotrola_msgs)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SafetyState.msg"
  "msg/FeatureCommand.msg"
  "msg/JointLimit.msg"
)
ament_export_dependencies(rosidl_default_runtime)
ament_package()
