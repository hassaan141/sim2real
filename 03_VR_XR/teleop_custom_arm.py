"""Register local custom tasks, then run Isaac Lab's standard SE(3) teleop script."""

import os
import runpy

import custom_arm_tasks  # noqa: F401


ISAACLAB_DIR = os.environ.get("ISAACLAB_DIR", "/home/hassaan/robotics/IsaacLab")
TELEOP_SCRIPT = os.path.join(ISAACLAB_DIR, "scripts/environments/teleoperation/teleop_se3_agent.py")

runpy.run_path(TELEOP_SCRIPT, run_name="__main__")
