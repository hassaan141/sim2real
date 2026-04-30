cmake_minimum_required(VERSION 3.8)
project(quest2ros2_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/OVR2ROSHapticFeedback.msg"
  "msg/OVR2ROSInputs.msg"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
