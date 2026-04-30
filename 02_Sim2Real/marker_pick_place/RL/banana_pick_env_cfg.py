import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import FrameTransformerCfg
from isaaclab.utils import configclass

from . import mdp
from marker_pick_place.assets.so100 import SO100_CFG
from marker_pick_place.assets.scene_objects import (
    BANANA_CFG,
    TABLE_LEG_BACK_LEFT_CFG,
    TABLE_LEG_BACK_RIGHT_CFG,
    TABLE_LEG_FRONT_LEFT_CFG,
    TABLE_LEG_FRONT_RIGHT_CFG,
    TABLE_TOP_CFG,
)


@configclass
class BananaSceneCfg(InteractiveSceneCfg):
    """Minimal scene for the local-grasp RL sub-task.

    Only the robot, banana, and table are included.  The cup is handled by the
    IL policy (transport + placement) and is not part of this RL environment.
    """

    robot = SO100_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")

    ee_frame = FrameTransformerCfg(
        prim_path="{ENV_REGEX_NS}/Robot/base",
        debug_vis=False,
        target_frames=[
            FrameTransformerCfg.FrameCfg(
                prim_path="{ENV_REGEX_NS}/Robot/gripper",
                name="gripper",
            ),
        ],
    )

    banana = BANANA_CFG

    table_top = TABLE_TOP_CFG
    table_leg_front_left = TABLE_LEG_FRONT_LEFT_CFG
    table_leg_front_right = TABLE_LEG_FRONT_RIGHT_CFG
    table_leg_back_left = TABLE_LEG_BACK_LEFT_CFG
    table_leg_back_right = TABLE_LEG_BACK_RIGHT_CFG

    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.CuboidCfg(
            size=(3.0, 3.0, 0.01),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.45, 0.45, 0.42)),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.005)),
    )

    light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=2500.0, color=(0.85, 0.85, 0.85)),
    )


@configclass
class ActionsCfg:
    """6-DOF joint position control with small action scale.

    Arm joints are limited to ±0.15 rad corrections per step so the policy
    only makes local approach/alignment adjustments. The gripper has a wider
    action range so it can start open and still close around the object.
    """

    joint_positions = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=[
            "shoulder_pan",
            "shoulder_lift",
            "elbow_flex",
            "wrist_flex",
            "wrist_roll",
            "gripper",
        ],
        scale={
            "shoulder_pan": 0.15,
            "shoulder_lift": 0.15,
            "elbow_flex": 0.15,
            "wrist_flex": 0.15,
            "wrist_roll": 0.15,
            "gripper": 1.4,
        },
        use_default_offset=True,
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # Robot state.
        joint_pos = ObsTerm(func=mdp.joint_pos_rel)
        joint_vel = ObsTerm(func=mdp.joint_vel_rel)
        gripper_opening = ObsTerm(func=mdp.gripper_opening)

        # End-effector position in env-local frame.
        ee_pos = ObsTerm(
            func=mdp.ee_pos_rel_env,
            params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
        )

        # Vector from gripper to banana — the key task signal.
        rel_ee_to_banana = ObsTerm(
            func=mdp.rel_ee_to_banana,
            params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
        )

        # Banana long axis in world frame — needed for the orientation reward.
        banana_long_axis = ObsTerm(func=mdp.banana_long_axis)

        # Previous action for temporal consistency.
        actions = ObsTerm(func=mdp.last_action)

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class RewardsCfg:
    # Orientation: gripper closing axis perpendicular to banana long axis.
    # Gated to only activate within 15 cm — far away orientation doesn't matter.
    gripper_orientation = RewTerm(
        func=mdp.gripper_perpendicular_to_banana,
        weight=2.0,
        params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
    )

    # Dense: close the distance to the banana.
    reach_banana = RewTerm(
        func=mdp.reach_banana,
        weight=1.0,
        params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
    )

    # Gripper shaping: keep the hand open while approaching, then close once
    # near and perpendicular enough to make a plausible grasp.
    gripper_open_while_approaching = RewTerm(
        func=mdp.gripper_open_while_approaching,
        weight=0.25,
        params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
    )
    gripper_close_when_aligned = RewTerm(
        func=mdp.gripper_close_when_aligned,
        weight=0.75,
        params={"ee_frame_cfg": SceneEntityCfg("ee_frame")},
    )

    # Dense height signal: non-zero only once the gripper closes on the banana.
    banana_height = RewTerm(
        func=mdp.banana_height,
        weight=3.0,
    )

    # Sparse success: full grasp achieved (banana lifted 1.5 cm).
    grasp_confirmed = RewTerm(
        func=mdp.grasp_confirmed,
        weight=20.0,
    )

    # Regularisation.
    action_rate = RewTerm(
        func=mdp.action_rate_l2,
        weight=-0.01,
    )
    joint_vel = RewTerm(
        func=mdp.joint_vel_l2,
        weight=-0.0001,
    )


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)

    # End the episode as soon as the grasp is confirmed.
    grasp_done = DoneTerm(func=mdp.grasp_confirmed_termination)


@configclass
class EventCfg:
    reset_scene = EventTerm(
        func=mdp.reset_scene_to_default,
        mode="reset",
    )

    # Small joint noise keeps the policy robust to slight arm misalignments
    # (as would be seen when the IL policy hands off to RL mid-approach).
    reset_robot_joints = EventTerm(
        func=mdp.reset_joints_by_offset,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg(
                "robot",
                joint_names=[
                    "shoulder_pan",
                    "shoulder_lift",
                    "elbow_flex",
                    "wrist_flex",
                    "wrist_roll",
                    "gripper",
                ],
            ),
            "position_range": (-0.05, 0.05),
            "velocity_range": (0.0, 0.0),
        },
    )

    # Randomise banana position so the policy generalises across the table area.
    reset_banana = EventTerm(
        func=mdp.reset_banana_pose,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("banana"),
            "pose_range": {
                "x": (-0.06, 0.06),
                "y": (-0.06, 0.06),
            },
        },
    )


@configclass
class BananaPickEnvCfg(ManagerBasedRLEnvCfg):
    """RL environment for the local-grasp sub-task.

    Scope: approach banana locally → align gripper → close gripper → lift banana.
    The IL policy handles coarse arm positioning and post-grasp transport.
    """

    scene: BananaSceneCfg = BananaSceneCfg(num_envs=2048, env_spacing=2.0)
    actions: ActionsCfg = ActionsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self):
        self.decimation = 2
        self.episode_length_s = 5.0  # short episodes: just grasp, not full transport

        self.sim.dt = 1.0 / 120.0
        self.sim.render_interval = self.decimation
        self.sim.physx.enable_ccd = True
        self.sim.physx.enable_stabilization = True

        self.viewer.eye = (0.75, -0.75, 1.25)
        self.viewer.lookat = (0.0, 0.0, 0.45)
