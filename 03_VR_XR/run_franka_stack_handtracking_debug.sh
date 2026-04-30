#!/usr/bin/env bash
set -euo pipefail

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
TASK="${TASK:-Isaac-Stack-Cube-Franka-IK-Rel-v0}"
DEVICE="${DEVICE:-cpu}"
CLOUDXR_ENV="${CLOUDXR_ENV:-${HOME}/.cloudxr/run/cloudxr.env}"

if [[ -f "${CLOUDXR_ENV}" ]]; then
  # shellcheck disable=SC1090
  source "${CLOUDXR_ENV}"
else
  echo "CloudXR env not found at ${CLOUDXR_ENV}. Start 03_VR_XR/run_cloudxr.sh first." >&2
  exit 1
fi

cd "${ISAACLAB_DIR}"

exec env TERM="${TERM:-xterm}" PYTHONPATH="${THIS_DIR}:${PYTHONPATH:-}" ./isaaclab.sh -p "${THIS_DIR}/teleop_debug_handtracking.py" \
  --task "${TASK}" \
  --teleop_device handtracking \
  --device "${DEVICE}"
