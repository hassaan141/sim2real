#!/usr/bin/env bash
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
ROS_DISTRO="${ROS_DISTRO:-humble}"

if [ -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]; then
  set +u
  source "/opt/ros/${ROS_DISTRO}/setup.bash"
  set -u
fi

if [ -n "${QUEST2ROS2_WS:-}" ] && [ -f "${QUEST2ROS2_WS}/install/setup.bash" ]; then
  set +u
  source "${QUEST2ROS2_WS}/install/setup.bash"
  set -u
fi

cd "${ISAACLAB_DIR}"
exec env TERM="${TERM:-xterm}" PYTHONPATH="${THIS_DIR}:${PYTHONPATH:-}" ./isaaclab.sh -p \
  "${THIS_DIR}/quest2_so100_ik_teleop.py" \
  --source "${SOURCE:-quest_pose}" \
  --device "${DEVICE:-cuda:0}" \
  "$@"
