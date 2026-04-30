#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
TASK="${TASK:-Isaac-Stack-Cube-Franka-IK-Rel-v0}"
DEVICE="${DEVICE:-cpu}"
CLOUDXR_ENV="${CLOUDXR_ENV:-${HOME}/.cloudxr/run/cloudxr.env}"

if [[ -f "${CLOUDXR_ENV}" ]]; then
  # shellcheck disable=SC1090
  source "${CLOUDXR_ENV}"
else
  echo "CloudXR env not found at ${CLOUDXR_ENV}. Start 03_VR_XR/run_cloudxr.sh first if using Quest/OpenXR." >&2
  exit 1
fi

cd "${ISAACLAB_DIR}"

echo "After the headset connects, click Play in the XR teleop controls."
echo "The terminal should print: Teleoperation activated"
echo "Using task: ${TASK}"
echo "For absolute 1:1 pose mode, run: TASK=Isaac-Stack-Cube-Franka-IK-Abs-v0 $0"

exec env TERM="${TERM:-xterm}" ./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task "${TASK}" \
  --teleop_device handtracking \
  --device "${DEVICE}"
