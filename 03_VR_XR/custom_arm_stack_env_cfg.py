# Local copy-style task config for learning custom-arm XR teleoperation.
#
# This intentionally starts from Isaac Lab's Franka cube-stack IK task and only
# swaps the robot-specific pieces. Keep this file local; do not edit Isaac Lab's
# built-in task files while experimenting.

from isaaclab.controllers.differential_ik_cfg import DifferentialIKControllerCfg
from isaaclab.devices.keyboard import Se3KeyboardCfg
from isaaclab.devices.device_base import DeviceBase, DevicesCfg
from isaaclab.devices.openxr.openxr_device import OpenXRDeviceCfg
from isaaclab.devices.openxr.retargeters.manipulator.gripper_retargeter import GripperRetargeterCfg
from isaaclab.devices.openxr.retargeters.manipulator.se3_abs_retargeter import Se3AbsRetargeterCfg
from isaaclab.devices.openxr.retargeters.manipulator.se3_rel_retargeter import Se3RelRetargeterCfg
from isaaclab.envs.mdp.actions.actions_cfg import DifferentialInverseKinematicsActionCfg
from isaaclab.sensors import FrameTransformerCfg
from isaaclab.sensors.frame_transformer.frame_transformer_cfg import OffsetCfg
from isaaclab.utils import configclass

from isaaclab.markers.config import FRAME_MARKER_CFG
from isaaclab_tasks.manager_based.manipulation.stack import mdp
from isaaclab_tasks.manager_based.manipulation.stack.config.franka.stack_joint_pos_env_cfg import (
    FrankaCubeStackEnvCfg,
)

from humanoid import ARM_CFG


# Replace these names with the exact names from your arm USD.
ARM_JOINT_NAMES = [
    "shoulder_flexion_extension",
    "shoulder_abduction_adduction",
    "shoulder_rotation",
    "elbow_flexion_extension",
    "forearm_rotation",
    "wrist_extension",
]
GRIPPER_JOINT_NAMES = [
    "mcp_index",
    "pip_index",
    "dip_index",
    "mcp_middle",
    "pip_middle",
    "dip_middle",
    "mcp_thumb",
    "ip_thumb",
]

# These are body names inside the converted arm USD.
ROBOT_USD_ROOT = "arm_assembly"
ROBOT_ROOT_BODY = "base_link"
END_EFFECTOR_BODY = "PALM_GAVIN_1DoF_Hinge_v2_1"
RIGHT_FINGER_BODY = "DIP_INDEX_v1_1"
LEFT_FINGER_BODY = "IP_THUMB_v1_1"


@configclass
class CustomArmCubeStackEnvCfg(FrankaCubeStackEnvCfg):
    """Cube-stack task with a local custom arm instead of Franka."""

    use_relative_ik = False

    def __post_init__(self):
        super().__post_init__()

        # Spawn the user's robot asset instead of the Franka.
        self.scene.robot = ARM_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.robot.spawn.semantic_tags = [("class", "robot")]
        self.events.init_franka_arm_pose = None
        self.events.randomize_franka_joint_state = None

        # XR right-hand pose drives an absolute end-effector pose command.
        self.actions.arm_action = DifferentialInverseKinematicsActionCfg(
            asset_name="robot",
            joint_names=ARM_JOINT_NAMES,
            body_name=END_EFFECTOR_BODY,
            controller=DifferentialIKControllerCfg(
                command_type="pose",
                use_relative_mode=self.use_relative_ik,
                ik_method="dls",
            ),
            scale=0.5 if self.use_relative_ik else 1.0,
        )

        self.actions.gripper_action = mdp.BinaryJointPositionActionCfg(
            asset_name="robot",
            joint_names=GRIPPER_JOINT_NAMES,
            open_command_expr={
                "mcp_index": 0.0,
                "pip_index": 0.0,
                "dip_index": 0.0,
                "mcp_middle": 0.0,
                "pip_middle": 0.0,
                "dip_middle": 0.0,
                "mcp_thumb": 0.79,
                "ip_thumb": 0.0,
            },
            close_command_expr={
                "mcp_index": -0.8,
                "pip_index": 0.8,
                "dip_index": -0.6,
                "mcp_middle": -0.8,
                "pip_middle": 0.8,
                "dip_middle": 0.6,
                "mcp_thumb": 1.6,
                "ip_thumb": 0.8,
            },
        )
        self.gripper_joint_names = GRIPPER_JOINT_NAMES
        self.gripper_open_val = 0.0
        self.gripper_threshold = 0.05
        # The inherited Franka stack task assumes a 2-joint parallel gripper for
        # these observations/termination terms. Disable them for this multi-finger hand.
        self.observations.policy.gripper_pos = None
        self.observations.subtask_terms = None
        self.terminations.success = None

        marker_cfg = FRAME_MARKER_CFG.copy()
        marker_cfg.markers["frame"].scale = (0.1, 0.1, 0.1)
        marker_cfg.prim_path = "/Visuals/FrameTransformer"
        self.scene.ee_frame = FrameTransformerCfg(
            prim_path=f"{{ENV_REGEX_NS}}/Robot/{ROBOT_USD_ROOT}/{ROBOT_ROOT_BODY}",
            debug_vis=False,
            visualizer_cfg=marker_cfg,
            target_frames=[
                FrameTransformerCfg.FrameCfg(
                    prim_path=f"{{ENV_REGEX_NS}}/Robot/{ROBOT_USD_ROOT}/{END_EFFECTOR_BODY}",
                    name="end_effector",
                    offset=OffsetCfg(pos=[0.0, 0.0, 0.0]),
                ),
                FrameTransformerCfg.FrameCfg(
                    prim_path=f"{{ENV_REGEX_NS}}/Robot/{ROBOT_USD_ROOT}/{RIGHT_FINGER_BODY}",
                    name="tool_rightfinger",
                    offset=OffsetCfg(pos=[0.0, 0.0, 0.0]),
                ),
                FrameTransformerCfg.FrameCfg(
                    prim_path=f"{{ENV_REGEX_NS}}/Robot/{ROBOT_USD_ROOT}/{LEFT_FINGER_BODY}",
                    name="tool_leftfinger",
                    offset=OffsetCfg(pos=[0.0, 0.0, 0.0]),
                ),
            ],
        )

        self.teleop_devices = DevicesCfg(
            devices={
                "handtracking": OpenXRDeviceCfg(
                    retargeters=[
                        (
                            Se3RelRetargeterCfg(
                                bound_hand=DeviceBase.TrackingTarget.HAND_RIGHT,
                                zero_out_xy_rotation=True,
                                use_wrist_rotation=False,
                                use_wrist_position=True,
                                delta_pos_scale_factor=10.0,
                                delta_rot_scale_factor=10.0,
                                sim_device=self.sim.device,
                            )
                            if self.use_relative_ik
                            else Se3AbsRetargeterCfg(
                                bound_hand=DeviceBase.TrackingTarget.HAND_RIGHT,
                                zero_out_xy_rotation=True,
                                use_wrist_rotation=False,
                                use_wrist_position=True,
                                sim_device=self.sim.device,
                            )
                        ),
                        GripperRetargeterCfg(
                            bound_hand=DeviceBase.TrackingTarget.HAND_RIGHT,
                            sim_device=self.sim.device,
                        ),
                    ],
                    sim_device=self.sim.device,
                    xr_cfg=self.xr,
                ),
                "keyboard": Se3KeyboardCfg(
                    pos_sensitivity=0.05,
                    rot_sensitivity=0.05,
                    sim_device=self.sim.device,
                ),
            }
        )


@configclass
class CustomArmCubeStackRelEnvCfg(CustomArmCubeStackEnvCfg):
    """Relative IK variant for incremental teleoperation."""

    use_relative_ik = True
