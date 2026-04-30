#!/usr/bin/env bash
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"
WS="${QUEST2ROS2_WS:-${THIS_DIR}/quest2ros2_ws}"

if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  set +u
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
  set -u
fi

mkdir -p "${WS}/src"
ln -sfn "${THIS_DIR}/quest2ros2_msgs" "${WS}/src/quest2ros2_msgs"
cd "${WS}"
colcon build --packages-select quest2ros2_msgs

echo "Built quest2ros2_msgs in ${WS}"
echo "Use: export QUEST2ROS2_WS=${WS}"
