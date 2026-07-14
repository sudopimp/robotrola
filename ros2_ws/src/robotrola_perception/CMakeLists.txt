cmake_minimum_required(VERSION 3.8)
project(robotrola_perception)
find_package(ament_cmake REQUIRED)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME} OPTIONAL)
install(
  PROGRAMS scripts/camera_config_node.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
