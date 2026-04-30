#!/usr/bin/env bash
set -euo pipefail

ISAACLAB_DIR="${ISAACLAB_DIR:-/home/hassaan/robotics/IsaacLab}"
CLOUDXR_ENV_CONFIG="${CLOUDXR_ENV_CONFIG:-/home/hassaan/robotics/isaac_tuts/03_VR_XR/cloudxr_quest2.env}"

cd "${ISAACLAB_DIR}"

exec env TERM="${TERM:-xterm}" ./isaaclab.sh -p -m isaacteleop.cloudxr \
  --accept-eula \
  --cloudxr-env-config "${CLOUDXR_ENV_CONFIG}" \
  "$@"
