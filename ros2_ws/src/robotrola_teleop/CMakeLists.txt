cmake_minimum_required(VERSION 3.8)
project(robotrola_teleop)
find_package(ament_cmake REQUIRED)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME} OPTIONAL)
install(
  PROGRAMS scripts/keyboard_teleop_node.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
