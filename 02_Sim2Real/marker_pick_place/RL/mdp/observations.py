from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

import isaaclab.utils.math as math_utils
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import FrameTransformer

# Banana long axis in the object's local frame (from the YCB 011_banana USD).
# If the orientation reward looks inverted in sim, change to [0,1,0] or [0,0,1].
_BANANA_LONG_AXIS_LOCAL = (1.0, 0.0, 0.0)


def _safe(x: torch.Tensor, clamp: float = 100.0) -> torch.Tensor:
    """Replace NaN/inf with zeros and clamp to a finite range.

    A single env producing NaN observations (rare physics divergence at hard
    contact, e.g. gripper clamping the banana) otherwise poisons the critic
    via NaN gradients and crashes training many iterations later.
    """
    return torch.nan_to_num(x, nan=0.0, posinf=clamp, neginf=-clamp).clamp(-clamp, clamp)


def rel_ee_to_banana(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """Vector from the gripper to the banana (world frame). Shape: (num_envs, 3).

    Positive when the banana is ahead of the EE. Drives the arm toward the banana.
    """
    ee_frame: FrameTransformer = env.scene[ee_frame_cfg.name]
    ee_pos = ee_frame.data.target_pos_w[:, 0, :]
    banana_pos = env.scene["banana"].data.root_pos_w
    return _safe(banana_pos - ee_pos)


def ee_pos_rel_env(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """Gripper (EE) position relative to the environment origin. Shape: (num_envs, 3)."""
    ee_frame: FrameTransformer = env.scene[ee_frame_cfg.name]
    return _safe(ee_frame.data.target_pos_w[:, 0, :] - env.scene.env_origins)


def banana_long_axis(env: ManagerBasedRLEnv) -> torch.Tensor:
    """Banana's long axis expressed in world frame. Shape: (num_envs, 3).

    Gives the policy the banana's orientation so it can rotate the gripper
    perpendicular to it.  Adjust _BANANA_LONG_AXIS_LOCAL if the YCB USD
    stores the long axis on a different local axis.
    """
    banana_quat = env.scene["banana"].data.root_quat_w
    local = torch.tensor(
        [_BANANA_LONG_AXIS_LOCAL], device=env.device, dtype=torch.float32
    ).expand(env.num_envs, -1)
    return _safe(math_utils.quat_apply(banana_quat, local))


def gripper_opening(env: ManagerBasedRLEnv) -> torch.Tensor:
    """Gripper joint position (scalar per env). Shape: (num_envs, 1).

    Positive = open, zero/negative = closed.  Gives the policy direct
    feedback on its own gripper state without inferring it from joint_pos_rel.
    """
    robot = env.scene["robot"]
    ids, _ = robot.find_joints("gripper")
    return _safe(robot.data.joint_pos[:, ids])
