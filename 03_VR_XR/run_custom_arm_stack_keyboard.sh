#!/usr/bin/env bash
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
TASK="${TASK:-Isaac-Stack-Cube-CustomArm-IK-Rel-v0}"
DEVICE="${DEVICE:-cpu}"

cd "${ISAACLAB_DIR}"

echo "Using custom arm task: ${TASK}"

exec env TERM="${TERM:-xterm}" PYTHONPATH="${THIS_DIR}:${PYTHONPATH:-}" ./isaaclab.sh -p "${THIS_DIR}/teleop_custom_arm.py" \
  --task "${TASK}" \
  --teleop_device keyboard \
  --device "${DEVICE}"
