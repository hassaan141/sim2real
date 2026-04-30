import isaaclab.sim as sim_utils
import numpy as np
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.utils import configclass
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import CameraCfg, FrameTransformerCfg
import isaaclab.utils.math as math_utils
from isaacsim.core.utils.rotations import euler_angles_to_quat
from marker_pick_place.mdp import randomize_robot_color, reset_joints_by_offset
from isaaclab.sim import get_current_stage
from pxr import Gf, Sdf, UsdGeom

import torch


from marker_pick_place.assets.so100 import SO100_CFG
from marker_pick_place.assets.scene_objects import (
    BACK_BASEBOARD_CFG,
    BACK_WALL_CFG,
    BANANA_CFG,
    CUP_BACK_WALL_CFG,
    CUP_BOTTOM_CFG,
    CUP_FRONT_WALL_CFG,
    CUP_HANDLE_BOTTOM_CFG,
    CUP_HANDLE_OUTER_CFG,
    CUP_HANDLE_TOP_CFG,
    CUP_LEFT_WALL_CFG,
    CUP_RIGHT_WALL_CFG,
    FLOOR_CFG,
    LEFT_JOG_BASEBOARD_21_CFG,
    LEFT_JOG_BASEBOARD_42_5_CFG,
    LEFT_JOG_WALL_21_CFG,
    LEFT_JOG_WALL_42_5_CFG,
    LEFT_LONG_BASEBOARD_100_CFG,
    LEFT_LONG_WALL_100_CFG,
    RIGHT_BASEBOARD_CFG,
    RIGHT_FACE_BASEBOARD_CFG,
    RIGHT_UP_BASEBOARD_CFG,
    RIGHT_WALL_CFG,
    RIGHT_WALL_FACE_CFG,
    RIGHT_WALL_UP_CFG,
    TABLE_LEG_BACK_LEFT_CFG,
    TABLE_LEG_BACK_RIGHT_CFG,
    TABLE_LEG_FRONT_LEFT_CFG,
    TABLE_LEG_FRONT_RIGHT_CFG,
    TABLE_TOP_CFG,
)

from marker_pick_place.mdp import (
    JointPositionActionCfg,
    ee_frame_state,
    image,
    joint_pos,
    joint_pos_rel,
)


camera_cfg = CameraCfg(
    prim_path="",
    update_period=0.0,
    height=480,
    width=640,
    data_types=["rgb"],
    spawn=sim_utils.PinholeCameraCfg(
        projection_type="pinhole",
        f_stop=100,
        focal_length=13.5,
        focus_distance=0.05,
    ),
    offset=CameraCfg.OffsetCfg(
        pos=(0.0, 0.0, 0.0),
        rot=euler_angles_to_quat(np.array([0, 0, 0]), degrees=True),
        convention="opengl",
    ),
)

# Screenshot-tuned camera poses from Isaac Sim. These use the same 640x480,
# 13.5 mm focal length, 0.05 m focus distance, and OpenGL convention above.
GRIPPER_CAMERA_POS = (-0.0131, 0.10462, -0.07344)
GRIPPER_CAMERA_ROT_DEG = (-84.84, -3.105, 88.952)


def _xform_attr(prim, attr_name, add_op):
    attr = prim.GetAttribute(attr_name)
    if attr.IsValid():
        return attr
    return add_op(UsdGeom.Xformable(prim)).GetAttr()


def refresh_config_cameras(env, env_ids, camera_names=None):
    """Re-apply configured camera xforms so render products initialize cleanly."""
    if camera_names is None:
        camera_names = ["env_cam", "gripper_cam"]

    stage = get_current_stage()
    camera_updates = []
    for name in camera_names:
        camera = env.scene[name]
        prim_path_pattern = camera.cfg.prim_path.replace("{ENV_REGEX_NS}", "/World/envs/env_.*")
        for prim in sim_utils.find_matching_prims(prim_path_pattern):
            if prim.IsValid():
                camera_updates.append((prim, camera.cfg.offset.pos, camera.cfg.offset.rot))

    with Sdf.ChangeBlock():
        for prim, pos, _ in camera_updates:
            translate_attr = _xform_attr(prim, "xformOp:translate", lambda xform: xform.AddTranslateOp())
            translate_attr.Set(Gf.Vec3d(pos[0] + 1.0e-6, pos[1], pos[2]))

    with Sdf.ChangeBlock():
        for prim, pos, quat in camera_updates:
            translate_attr = _xform_attr(prim, "xformOp:translate", lambda xform: xform.AddTranslateOp())
            orient_attr = _xform_attr(prim, "xformOp:orient", lambda xform: xform.AddOrientOp())
            translate_attr.Set(Gf.Vec3d(*pos))
            orient_attr.Set(Gf.Quatd(float(quat[0]), float(quat[1]), float(quat[2]), float(quat[3])))


def sync_gripper_camera_to_frame(
    env,
    env_ids,
    camera_cfg=SceneEntityCfg("gripper_cam"),
    ee_frame_cfg=SceneEntityCfg("ee_frame"),
):
    """Keep the external gripper camera riding on the gripper frame."""
    camera = env.scene[camera_cfg.name]
    ee_frame = env.scene[ee_frame_cfg.name]
    gripper_pos = ee_frame.data.target_pos_w[:, 0, :]
    gripper_quat = ee_frame.data.target_quat_w[:, 0, :]
    offset_pos = torch.tensor(camera.cfg.offset.pos, device=env.device, dtype=torch.float32).repeat(env.num_envs, 1)
    offset_quat = torch.tensor(camera.cfg.offset.rot, device=env.device, dtype=torch.float32).repeat(env.num_envs, 1)
    camera_pos, camera_quat = math_utils.combine_frame_transforms(
        gripper_pos,
        gripper_quat,
        offset_pos,
        offset_quat,
    )
    camera.set_world_poses(camera_pos.to(dtype=torch.float32), camera_quat.to(dtype=torch.float32), convention="opengl")


@configclass
class MarkerSceneCfg(InteractiveSceneCfg):
    """Scene for banana pick-place demo collection."""

    num_envs = 1
    env_spacing = 2.0

    robot = SO100_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
    )

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

    env_cam = camera_cfg.replace()
    env_cam.prim_path = "{ENV_REGEX_NS}/EnvCam"
    env_cam.offset.pos = (-0.55, -0.75, 0.75)
    env_cam.offset.rot = euler_angles_to_quat(np.array([55, 0, -45]), degrees=True)

    gripper_cam = camera_cfg.replace()
    gripper_cam.prim_path = "{ENV_REGEX_NS}/GripperCamera"
    gripper_cam.width = 320
    gripper_cam.height = 240
    gripper_cam.spawn.focus_distance = 0.05
    gripper_cam.offset.pos = GRIPPER_CAMERA_POS
    gripper_cam.offset.rot = euler_angles_to_quat(np.array(GRIPPER_CAMERA_ROT_DEG), degrees=True)

    ground = AssetBaseCfg(
        prim_path="/World/Ground",
        spawn=sim_utils.GroundPlaneCfg(),
    )

    light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(
            intensity=2800.0,
            color=(0.85, 0.85, 0.85),
        ),
    )

    floor = FLOOR_CFG

    back_wall = BACK_WALL_CFG
    right_wall = RIGHT_WALL_CFG
    right_wall_face = RIGHT_WALL_FACE_CFG
    right_wall_up = RIGHT_WALL_UP_CFG
    left_jog_wall_42_5 = LEFT_JOG_WALL_42_5_CFG
    left_jog_wall_21 = LEFT_JOG_WALL_21_CFG
    left_long_wall_100 = LEFT_LONG_WALL_100_CFG

    back_baseboard = BACK_BASEBOARD_CFG
    right_baseboard = RIGHT_BASEBOARD_CFG
    right_face_baseboard = RIGHT_FACE_BASEBOARD_CFG
    right_up_baseboard = RIGHT_UP_BASEBOARD_CFG
    left_jog_baseboard_42_5 = LEFT_JOG_BASEBOARD_42_5_CFG
    left_jog_baseboard_21 = LEFT_JOG_BASEBOARD_21_CFG
    left_long_baseboard_100 = LEFT_LONG_BASEBOARD_100_CFG

    table_top = TABLE_TOP_CFG
    table_leg_front_left = TABLE_LEG_FRONT_LEFT_CFG
    table_leg_front_right = TABLE_LEG_FRONT_RIGHT_CFG
    table_leg_back_left = TABLE_LEG_BACK_LEFT_CFG
    table_leg_back_right = TABLE_LEG_BACK_RIGHT_CFG

    cup_bottom = CUP_BOTTOM_CFG
    cup_front_wall = CUP_FRONT_WALL_CFG
    cup_back_wall = CUP_BACK_WALL_CFG
    cup_left_wall = CUP_LEFT_WALL_CFG
    cup_right_wall = CUP_RIGHT_WALL_CFG
    cup_handle_top = CUP_HANDLE_TOP_CFG
    cup_handle_bottom = CUP_HANDLE_BOTTOM_CFG
    cup_handle_outer = CUP_HANDLE_OUTER_CFG

    banana = BANANA_CFG


@configclass
class ActionsCfg:
    joint_positions = JointPositionActionCfg(
        asset_name="robot",
        joint_names=[
            "shoulder_pan",
            "shoulder_lift",
            "elbow_flex",
            "wrist_flex",
            "wrist_roll",
            "gripper",
        ],
        scale=1,
        use_default_offset=False,
    )

@configclass
class EventCfg:
    startup_refresh_camera_xforms = EventTerm(
        func=refresh_config_cameras,
        mode="startup",
        params={
            "camera_names": ["env_cam"],
        },
    )

    refresh_camera_xforms = EventTerm(
        func=refresh_config_cameras,
        mode="reset",
        params={
            "camera_names": ["env_cam"],
        },
    )

    sync_gripper_camera = EventTerm(
        func=sync_gripper_camera_to_frame,
        mode="interval",
        interval_range_s=(0.0, 0.0),
        is_global_time=True,
    )

    reset_robot_position = EventTerm(
        func=reset_joints_by_offset,
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
            "position_range": (0, 0),
            "velocity_range": (0, 0),
        },
    )

    reset_sync_gripper_camera = EventTerm(
        func=sync_gripper_camera_to_frame,
        mode="reset",
    )

    set_robot_white = EventTerm(
        func=randomize_robot_color,
        mode="reset",
        params={
            "color_names": ["white"],
        },
    )

def banana_pose(env):
    banana = env.scene["banana"]
    return torch.cat(
        [
            banana.data.root_pos_w,
            banana.data.root_quat_w,
        ],
        dim=-1,
    )

def cup_pose(env):
    cup_pos = torch.tensor(
        [-0.275 + 0.23, -0.275 + 0.12, 0.45 + 0.004],
        device=env.device,
    ).repeat(env.num_envs, 1)
    cup_quat = torch.tensor(
        [1.0, 0.0, 0.0, 0.0],
        device=env.device,
    ).repeat(env.num_envs, 1)
    return torch.cat([cup_pos, cup_quat], dim=-1)

@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        joint_pos_obs = ObsTerm(func=joint_pos)
        joint_pos_rel = ObsTerm(func=joint_pos_rel)
        banana_pose = ObsTerm(func=banana_pose)
        cup_pose = ObsTerm(func=cup_pose)
        ee_frame_state = ObsTerm(
            func=ee_frame_state,
            params={
                "ee_frame_cfg": SceneEntityCfg("ee_frame"),
                "robot_cfg": SceneEntityCfg("robot"),
            },
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False

    policy: PolicyCfg = PolicyCfg()

    @configclass
    class VisualCfg(ObsGroup):
        rgb_env = ObsTerm(
            func=image,
            params={
                "sensor_cfg": SceneEntityCfg("env_cam"),
                "data_type": "rgb",
                "normalize": False,
            },
        )

        rgb_gripper = ObsTerm(
            func=image,
            params={
                "sensor_cfg": SceneEntityCfg("gripper_cam"),
                "data_type": "rgb",
                "normalize": False,
            },
        )

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = False

    visual: VisualCfg = VisualCfg()


@configclass
class MarkerTeleopEnvCfg(ManagerBasedRLEnvCfg):
    """Teleop/IL environment config for banana pick-place demo collection."""

    scene: MarkerSceneCfg = MarkerSceneCfg()

    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()

    events: EventCfg = EventCfg()
    rewards = None
    terminations = None

    def __post_init__(self):
        self.decimation = 2
        self.episode_length_s = 10.0

        self.scene.num_envs = 1

        self.sim.dt = 1 / 120
        self.sim.render_interval = self.decimation
        self.sim.physx.enable_ccd = True
        self.sim.physx.enable_stabilization = True

        self.viewer.eye = (0.75, -0.75, 1.25)
        self.viewer.lookat = (0.0, 0.0, 0.45)
