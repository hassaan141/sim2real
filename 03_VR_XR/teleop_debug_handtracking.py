"""Register local tasks, then run Isaac Lab teleop with action debug prints."""

import os
import runpy
import sys


ISAACLAB_DIR = os.environ.get("ISAACLAB_DIR", "/home/hassaan/robotics/IsaacLab")
TELEOP_SCRIPT = os.path.join(ISAACLAB_DIR, "scripts/environments/teleoperation/teleop_se3_agent.py")

os.environ["ISAAC_TELEOP_DEBUG_ACTIONS"] = "1"

try:
    import custom_arm_tasks  # noqa: F401
except ModuleNotFoundError:
    pass

runpy.run_path(TELEOP_SCRIPT, run_name="__main__")
