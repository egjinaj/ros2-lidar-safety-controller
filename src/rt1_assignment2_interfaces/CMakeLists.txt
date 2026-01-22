cmake_minimum_required(VERSION 3.8)
project(rt1_assignment2_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObstacleInfo.msg"
  "srv/SetThreshold.srv"
  "srv/GetAverageVel.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()