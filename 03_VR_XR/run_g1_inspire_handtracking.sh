#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
TASK="${TASK:-Isaac-PickPlace-G1-InspireFTP-Abs-v0}"
DEVICE="${DEVICE:-cpu}"
CLOUDXR_ENV="${CLOUDXR_ENV:-${HOME}/.cloudxr/run/cloudxr.env}"

if [[ -f "${CLOUDXR_ENV}" ]]; then
  # shellcheck disable=SC1090
  source "${CLOUDXR_ENV}"
else
  echo "CloudXR env not found at ${CLOUDXR_ENV}. Start 03_VR_XR/run_cloudxr.sh first if using Quest/OpenXR." >&2
fi

cd "${ISAACLAB_DIR}"

exec env TERM="${TERM:-xterm}" ./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py \
  --task "${TASK}" \
  --teleop_device handtracking \
  --device "${DEVICE}" \
  --enable_pinocchio
