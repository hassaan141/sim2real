import os
import numpy as np

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.sim.spawners.from_files import spawn_from_usd
from isaaclab.sim.utils import bind_physics_material, clone, get_current_stage
from isaacsim.core.utils.rotations import euler_angles_to_quat


HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "../.."))
GRIPPER_PHYSICS_MATERIAL = sim_utils.RigidBodyMaterialCfg(
    static_friction=2.0,
    dynamic_friction=1.4,
    restitution=0.0,
    friction_combine_mode="max",
    restitution_combine_mode="min",
)


@clone
def spawn_so100_with_gripper_physics(
    prim_path: str,
    cfg: sim_utils.UsdFileCfg,
    translation: tuple[float, float, float] | None = None,
    orientation: tuple[float, float, float, float] | None = None,
    **kwargs,
):
    prim = spawn_from_usd(prim_path, cfg, translation=translation, orientation=orientation, **kwargs)
    stage = get_current_stage()
    material_path = f"{prim_path}/gripperPhysicsMaterial"
    GRIPPER_PHYSICS_MATERIAL.func(material_path, GRIPPER_PHYSICS_MATERIAL)

    # Support both raw and baked USD collider layouts.
    fingertip_meshes = [
        f"{prim_path}/gripper/collisions/Fixed_Jaw/mesh",
        f"{prim_path}/jaw/collisions/Moving_Jaw/mesh",
        f"{prim_path}/colliders/gripper/Fixed_Jaw/mesh",
        f"{prim_path}/colliders/jaw/Moving_Jaw/mesh",
    ]
    for mesh_path in fingertip_meshes:
        if stage.GetPrimAtPath(mesh_path).IsValid():
            try:
                bind_physics_material(mesh_path, material_path, stage=stage)
            except Exception as exc:
                print(f"[WARN]: Could not bind fingertip material on instance proxy {mesh_path}: {exc}")
        else:
            print(f"[WARN]: Expected SO100 fingertip collider not found: {mesh_path}")
    return prim

SO100_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        func=spawn_so100_with_gripper_physics,
        usd_path=os.path.join(
            PROJECT_ROOT,
            "assets",
            "so100.usd",
        ),
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=0.5,
        ),
        collision_props=sim_utils.CollisionPropertiesCfg(
            contact_offset=0.002,
            rest_offset=0.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=48,
            solver_velocity_iteration_count=8,
            fix_root_link=True,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.26, 0.0, 0.45),
        rot=euler_angles_to_quat(np.array([0, 0, 270]), degrees=True),
        joint_pos={
            "shoulder_pan": 0.0,
            "shoulder_lift": 1.57,
            "elbow_flex": -1.57,
            "wrist_flex": 1.0,
            "wrist_roll": -1.57,
            "gripper": 0.0,
        },
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["shoulder_.*", "elbow_flex", "wrist_.*"],
            effort_limit_sim=15.0,
            velocity_limit_sim=8.0,
            stiffness={
                "shoulder_pan": 600.0,
                "shoulder_lift": 500.0,
                "elbow_flex": 360.0,
                "wrist_flex": 240.0,
                "wrist_roll": 160.0,
            },
            damping={
                "shoulder_pan": 120.0,
                "shoulder_lift": 100.0,
                "elbow_flex": 70.0,
                "wrist_flex": 45.0,
                "wrist_roll": 30.0,
            },
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["gripper"],
            effort_limit_sim=10.0,
            velocity_limit_sim=5.0,
            stiffness=180.0,
            damping=50.0,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
