cmake_minimum_required(VERSION 3.8)
project(robotrola_safety)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME} OPTIONAL)

install(
  PROGRAMS scripts/safety_supervisor_node.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
