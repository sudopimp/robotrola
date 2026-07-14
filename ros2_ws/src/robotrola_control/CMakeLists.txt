cmake_minimum_required(VERSION 3.8)
project(robotrola_control)
find_package(ament_cmake REQUIRED)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME} OPTIONAL)
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME} OPTIONAL)
install(
  PROGRAMS scripts/joint_command_filter_node.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
