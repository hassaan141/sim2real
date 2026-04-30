from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv

import isaaclab.utils.math as math_utils
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import FrameTransformer

# Banana rests at this z on the table at spawn.
_BANANA_TABLE_Z = 0.485

# Banana long axis in the object's local frame — must match observations.py.
# Change to [0,1,0] or [0,0,1] if the YCB USD uses a different principal axis.
_BANANA_LONG_AXIS_LOCAL = (1.0, 0.0, 0.0)

# Gripper closing axis in the gripper's local frame for the SO100.
# The two fingers move toward each other along this axis.
# Change to [1,0,0] or [0,0,1] if the SO100 gripper USD uses a different axis.
_GRIPPER_CLOSE_AXIS_LOCAL = (0.0, 1.0, 0.0)

# Only apply the orientation reward within this distance (metres).
_ORIENT_GATE_DIST = 0.15

# Banana must rise this much above the table for a grasp to be considered confirmed.
_LIFT_THRESHOLD_Z = _BANANA_TABLE_Z + 0.015  # 1.5 cm

# SO100 gripper joint positions. Teleop maps the joint roughly from -0.2 to
# 2.0 rad; the RL task starts open and rewards closing only at the grasp pose.
_GRIPPER_OPEN_POS = 1.2
_GRIPPER_CLOSED_POS = 0.0


# ---------------------------------------------------------------------------
# Phase 1 — Local approach / alignment
# ---------------------------------------------------------------------------

def _ee_banana_distance_and_alignment(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg,
) -> tuple[torch.Tensor, torch.Tensor]:
    ee_frame: FrameTransformer = env.scene[ee_frame_cfg.name]
    ee_pos = ee_frame.data.target_pos_w[:, 0, :]
    banana_pos = env.scene["banana"].data.root_pos_w

    dist = torch.norm(banana_pos - ee_pos, dim=-1)

    banana_quat = env.scene["banana"].data.root_quat_w
    long_local = torch.tensor(
        [_BANANA_LONG_AXIS_LOCAL], device=env.device, dtype=torch.float32
    ).expand(env.num_envs, -1)
    banana_long = math_utils.quat_apply(banana_quat, long_local)
    banana_long = banana_long / (banana_long.norm(dim=-1, keepdim=True) + 1e-6)

    ee_quat = ee_frame.data.target_quat_w[:, 0, :]
    close_local = torch.tensor(
        [_GRIPPER_CLOSE_AXIS_LOCAL], device=env.device, dtype=torch.float32
    ).expand(env.num_envs, -1)
    gripper_close = math_utils.quat_apply(ee_quat, close_local)
    gripper_close = gripper_close / (gripper_close.norm(dim=-1, keepdim=True) + 1e-6)

    cos_angle = torch.abs((banana_long * gripper_close).sum(dim=-1))
    perp_score = 1.0 - cos_angle
    return dist, perp_score


def _gripper_open_score(env: ManagerBasedRLEnv) -> torch.Tensor:
    robot = env.scene["robot"]
    ids, _ = robot.find_joints("gripper")
    gripper_pos = robot.data.joint_pos[:, ids[0]]
    return torch.clamp(
        (gripper_pos - _GRIPPER_CLOSED_POS) / (_GRIPPER_OPEN_POS - _GRIPPER_CLOSED_POS),
        min=0.0,
        max=1.0,
    )

def gripper_perpendicular_to_banana(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """Reward the gripper for being perpendicular to the banana's long axis.

    A parallel-jaw gripper must close across the banana's *width*, not its
    length.  This reward is 1.0 when the gripper closing axis is exactly
    perpendicular to the banana long axis, and 0.0 when they are parallel.

    Gated: only active within _ORIENT_GATE_DIST of the banana so the policy
    is not penalised for orientation when the arm is still far away.

    Tune constants at the top of this file if the wrong axis is assumed for
    the banana USD or the SO100 gripper USD.
    """
    dist, perp_score = _ee_banana_distance_and_alignment(env, ee_frame_cfg)
    is_near = (dist < _ORIENT_GATE_DIST).float()

    return is_near * perp_score


def reach_banana(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """Dense, monotonically increasing reward toward the banana.

    Exponential with a 5 cm characteristic length keeps the gradient alive
    all the way to contact, instead of saturating before the gripper arrives.
    """
    ee_frame: FrameTransformer = env.scene[ee_frame_cfg.name]
    ee_pos = ee_frame.data.target_pos_w[:, 0, :]
    banana_pos = env.scene["banana"].data.root_pos_w

    dist = torch.norm(banana_pos - ee_pos, dim=-1)
    return torch.exp(-dist / 0.05)


def gripper_grasp_shaping(
    env: ManagerBasedRLEnv,
    ee_frame_cfg: SceneEntityCfg = SceneEntityCfg("ee_frame"),
) -> torch.Tensor:
    """Continuous reward for closing the gripper at a good grasp pose.

    pose_score is high when the EE is close *and* well aligned with the
    banana long axis; closed_score is high when the gripper joint is near
    the closed position.  The product pays zero when the gripper sits at
    the default-open pose (no free reward for doing nothing) and grows
    smoothly as the policy moves into a grasp pose and squeezes.
    """
    dist, perp_score = _ee_banana_distance_and_alignment(env, ee_frame_cfg)
    proximity = torch.exp(-dist / 0.04)
    alignment = torch.clamp(perp_score, 0.0, 1.0)
    pose_score = proximity * alignment
    closed_score = 1.0 - _gripper_open_score(env)
    return pose_score * closed_score


# ---------------------------------------------------------------------------
# Phase 2 — Grasp confirmation (height-based density)
# ---------------------------------------------------------------------------

def banana_height(env: ManagerBasedRLEnv) -> torch.Tensor:
    """Reward how much the banana has been lifted off the table.

    Proportional to height above the resting z, clamped to zero below it.
    This is zero until the gripper actually closes and picks the banana up,
    providing a dense gradient that bridges the approach and lift phases.
    """
    banana_z = env.scene["banana"].data.root_pos_w[:, 2]
    return torch.clamp(banana_z - _BANANA_TABLE_Z, min=0.0) * 5.0


def grasp_confirmed(env: ManagerBasedRLEnv) -> torch.Tensor:
    """Sparse success bonus: banana has been lifted 1.5 cm above the table.

    Lifting requires the gripper to be closed, so this implicitly rewards a
    stable grasp without contact sensors.
    """
    banana_z = env.scene["banana"].data.root_pos_w[:, 2]
    return (banana_z > _LIFT_THRESHOLD_Z).float()


# ---------------------------------------------------------------------------
# Termination helper (called from TerminationsCfg)
# ---------------------------------------------------------------------------

def grasp_confirmed_termination(env: ManagerBasedRLEnv) -> torch.Tensor:
    """Boolean termination: True when the banana has been lifted 1.5 cm.

    Ends the episode early so the large grasp_confirmed bonus is collected
    and a new episode begins, keeping training dense.
    """
    banana_z = env.scene["banana"].data.root_pos_w[:, 2]
    return banana_z > _LIFT_THRESHOLD_Z


# ---------------------------------------------------------------------------
# Reset helper (used as EventTerm.func)
# ---------------------------------------------------------------------------

def reset_banana_pose(
    env,
    env_ids: torch.Tensor,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("banana"),
    pose_range: dict | None = None,
) -> None:
    """Randomise the banana position on the table at each episode reset."""
    from marker_pick_place.mdp.resets import random_asset_pose

    if pose_range is None:
        pose_range = {}

    banana = env.scene[asset_cfg.name]
    random_asset_pose(env, env_ids, banana, pose_range, pos_offset={})
