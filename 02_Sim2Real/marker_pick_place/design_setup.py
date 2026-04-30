import os
import numpy as np

from isaacsim.core.utils.rotations import euler_angles_to_quat

import isaaclab.sim as sim_utils


AA_BATTERY_RADIUS = 0.0145 / 2.0
AA_BATTERY_LENGTH = 0.0505
AA_BATTERY_MASS = 0.0235


def spawn_box(prim_path, size, pos, color, mass=None, static=False):
    rigid_props = None if static else sim_utils.RigidBodyPropertiesCfg()
    mass_props = None if static or mass is None else sim_utils.MassPropertiesCfg(mass=mass)

    cfg = sim_utils.CuboidCfg(
        size=size,
        rigid_props=rigid_props,
        mass_props=mass_props,
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=color),
    )
    cfg.func(prim_path, cfg, translation=pos)


def spawn_aa_battery(prim_path, pos):
    battery_cfg = sim_utils.CylinderCfg(
        radius=AA_BATTERY_RADIUS,
        height=AA_BATTERY_LENGTH,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=1.0,
            max_linear_velocity=1.0,
            max_angular_velocity=720.0,
            solver_position_iteration_count=16,
            solver_velocity_iteration_count=4,
            linear_damping=0.02,
            angular_damping=0.02,
            enable_gyroscopic_forces=True,
            sleep_threshold=0.001,
            stabilization_threshold=0.0001,
        ),
        mass_props=sim_utils.MassPropertiesCfg(
            mass=AA_BATTERY_MASS,
        ),
        collision_props=sim_utils.CollisionPropertiesCfg(
            collision_enabled=True,
            contact_offset=0.002,
            rest_offset=0.0,
        ),
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=0.55,
            dynamic_friction=0.4,
            restitution=0.02,
            friction_combine_mode="average",
            restitution_combine_mode="average",
        ),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.15, 0.15, 0.15),
            metallic=0.1,
            roughness=0.45,
        ),
    )

    battery_cfg.func(
        prim_path,
        battery_cfg,
        translation=pos,
        orientation=(1.0, 0.0, 0.0, 0.0),
    )


def spawn_so100():
    usd_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "assets",
        "so100.usd",
    )

    robot_cfg = sim_utils.UsdFileCfg(
        usd_path=usd_path,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        collision_props=sim_utils.CollisionPropertiesCfg(
            contact_offset=0.002,
            rest_offset=0.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=32,
            solver_velocity_iteration_count=1,
            fix_root_link=True,
        ),
    )
    robot_cfg.func(
        "/World/RealWorld/Robot",
        robot_cfg,
        translation=(0.26, 0.0, 0.45),
        orientation=euler_angles_to_quat(np.array([0, 0, 270]), degrees=True),
    )


def design_scene():
    ground_cfg = sim_utils.GroundPlaneCfg()
    ground_cfg.func("/World/Ground", ground_cfg)

    light_cfg = sim_utils.DomeLightCfg(
        intensity=2800.0,
        color=(0.85, 0.85, 0.85),
    )
    light_cfg.func("/World/Light", light_cfg)

    sim_utils.create_prim("/World/RealWorld", "Xform")

    # Coordinate convention:
    # x = out from the back wall into the room
    # y = left/right along the back wall
    # z = up
    #
    # Table is 55 cm x 55 cm, and table center is (0, 0).
    # Table right edge is y=0.275.
    # The right wall is 25 cm from the table, so its inside face is y=0.525.
    # With a 4 cm wall thickness, the right wall centerline is y=0.545.
    # The 155 cm back wall ends at that right wall, so its center is y=-0.23.
    #
    # Main back wall centerline:
    # left end  y = -1.005
    # right end y =  0.545
    #
    # Back wall is therefore at x=-0.295:
    # - table half-depth is 0.275 m
    # - wall thickness is 0.04 m, so wall center is -0.275 - 0.02

    spawn_box(
        "/World/RealWorld/Floor",
        size=(1.80, 2.60, 0.01),
        pos=(0.25, 0.0, -0.005),
        color=(0.6, 0.6, 0.6),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/BackWall",
        size=(0.04, 1.55, 1.40),
        pos=(-0.295, -0.23, 0.70),
        color=(0.90, 0.90, 0.86),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightWall",
        size=(0.35, 0.04, 1.40),
        pos=(-0.295 + 0.35 / 2.0, 0.545, 0.70),
        color=(0.82, 0.82, 0.78),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightWallFace",
        size=(0.04, 0.35, 1.40),
        pos=(0.055, 0.545 + 0.35 / 2.0, 0.70),
        color=(0.86, 0.86, 0.82),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightWallUp",
        size=(0.35, 0.04, 1.40),
        pos=(0.055 - 0.35 / 2.0, 0.545 + 0.35, 0.70),
        color=(0.90, 0.90, 0.86),
        static=True,
    )

    # Left-side wall jog from the sketch:
    # from left end of main wall: 42.5 cm down, 21 cm left, then 100 cm down.
    spawn_box(
        "/World/RealWorld/LeftJogWall42_5",
        size=(0.425, 0.04, 1.40),
        pos=(-0.295 + 0.425 / 2.0, -1.005, 0.70),
        color=(0.90, 0.90, 0.86),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/LeftJogWall21",
        size=(0.04, 0.21, 1.40),
        pos=(-0.295 + 0.425, -1.005 - 0.21 / 2.0, 0.70),
        color=(0.86, 0.86, 0.82),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/LeftLongWall100",
        size=(1.00, 0.04, 1.40),
        pos=(-0.295 + 0.425 + 1.00 / 2.0, -1.005 - 0.21, 0.70),
        color=(0.90, 0.90, 0.86),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/BackBaseboard",
        size=(0.035, 1.55, 0.07),
        pos=(-0.270, -0.23, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightBaseboard",
        size=(0.35, 0.035, 0.07),
        pos=(-0.295 + 0.35 / 2.0, 0.520, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightFaceBaseboard",
        size=(0.035, 0.35, 0.07),
        pos=(0.030, 0.545 + 0.35 / 2.0, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/RightUpBaseboard",
        size=(0.35, 0.035, 0.07),
        pos=(0.055 - 0.35 / 2.0, 0.545 + 0.35 - 0.025, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/LeftJogBaseboard42_5",
        size=(0.425, 0.035, 0.07),
        pos=(-0.295 + 0.425 / 2.0, -0.980, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/LeftJogBaseboard21",
        size=(0.035, 0.21, 0.07),
        pos=(-0.295 + 0.400, -1.005 - 0.21 / 2.0, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/LeftLongBaseboard100",
        size=(1.00, 0.035, 0.07),
        pos=(-0.295 + 0.425 + 1.00 / 2.0, -1.005 - 0.185, 0.035),
        color=(0.94, 0.93, 0.90),
        static=True,
    )

    # Black table top: 55 cm x 55 cm, top surface at 45 cm high
    spawn_box(
        "/World/RealWorld/TableTop",
        size=(0.55, 0.55, 0.04),
        pos=(0.0, 0.0, 0.45 - 0.04 / 2.0),
        color=(0.005, 0.005, 0.004),
        static=True,
    )

    # Table legs
    spawn_box(
        "/World/RealWorld/TableLegFrontLeft",
        size=(0.055, 0.055, 0.43),
        pos=(0.23, 0.23, 0.43 / 2.0),
        color=(0.005, 0.005, 0.004),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/TableLegFrontRight",
        size=(0.055, 0.055, 0.43),
        pos=(0.23, -0.23, 0.43 / 2.0),
        color=(0.005, 0.005, 0.004),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/TableLegBackLeft",
        size=(0.055, 0.055, 0.43),
        pos=(-0.23, 0.23, 0.43 / 2.0),
        color=(0.005, 0.005, 0.004),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/TableLegBackRight",
        size=(0.055, 0.055, 0.43),
        pos=(-0.23, -0.23, 0.43 / 2.0),
        color=(0.005, 0.005, 0.004),
        static=True,
    )

    # Black cup with handle.
    # Placement is measured from the tabletop:
    # - 12 cm from the left side of the table
    # - 23 cm from the top/back side of the table
    #
    # Table spans x=-0.275..0.275 and y=-0.275..0.275.
    # Left side is y=-0.275, so mug center y = -0.275 + 0.12.
    # Top/back side is x=-0.275, so mug center x = -0.275 + 0.23.
    # Mug diameter is 8 cm and height is 9.5 cm.
    spawn_box(
        "/World/RealWorld/Cup/Bottom",
        size=(0.08, 0.08, 0.008),
        pos=(-0.275 + 0.23, -0.275 + 0.12, 0.45 + 0.004),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/FrontWall",
        size=(0.006, 0.08, 0.095),
        pos=(-0.275 + 0.23 + 0.04, -0.275 + 0.12, 0.45 + 0.095 / 2.0),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/BackWall",
        size=(0.006, 0.08, 0.095),
        pos=(-0.275 + 0.23 - 0.04, -0.275 + 0.12, 0.45 + 0.095 / 2.0),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/LeftWall",
        size=(0.08, 0.006, 0.095),
        pos=(-0.275 + 0.23, -0.275 + 0.12 + 0.04, 0.45 + 0.095 / 2.0),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/RightWall",
        size=(0.08, 0.006, 0.095),
        pos=(-0.275 + 0.23, -0.275 + 0.12 - 0.04, 0.45 + 0.095 / 2.0),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    # Handle as a squared ring on the right side.
    spawn_box(
        "/World/RealWorld/Cup/HandleTop",
        size=(0.012, 0.045, 0.010),
        pos=(-0.275 + 0.23, -0.275 + 0.12 - 0.065, 0.45 + 0.072),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/HandleBottom",
        size=(0.012, 0.045, 0.010),
        pos=(-0.275 + 0.23, -0.275 + 0.12 - 0.065, 0.45 + 0.032),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    spawn_box(
        "/World/RealWorld/Cup/HandleOuter",
        size=(0.012, 0.010, 0.050),
        pos=(-0.275 + 0.23, -0.275 + 0.12 - 0.085, 0.45 + 0.052),
        color=(0.1, 0.3, 0.8),
        static=True,
    )

    cup_center = (-0.275 + 0.23, -0.275 + 0.12)
    x_min, x_max = -0.02, 0.08
    y_min, y_max = -0.22, 0.05
    min_cup_clearance = 0.09

    num_batteries = int(np.random.randint(2, 4))
    battery_positions = []
    while len(battery_positions) < num_batteries:
        x = float(np.random.uniform(x_min, x_max))
        y = float(np.random.uniform(y_min, y_max))
        if np.hypot(x - cup_center[0], y - cup_center[1]) < min_cup_clearance:
            continue
        battery_positions.append((x, y, 0.45 + AA_BATTERY_RADIUS))

    for idx, pos in enumerate(battery_positions):
        spawn_aa_battery(
            f"/World/RealWorld/Battery_{idx}",
            pos=pos,
        )

    spawn_so100()
