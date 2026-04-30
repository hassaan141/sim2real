"""
create_scene.py

Combined Isaac Lab 00_sim tutorial:
- create_empty.py
- launch_app.py
- log_time.py
- set_rendering_mode.py
- spawn_prims.py

Run:
    $ISAACLAB_DIR/isaaclab.sh -p scripts/00_sim/create_scene.py

Headless:
    $ISAACLAB_DIR/isaaclab.sh -p scripts/00_sim/create_scene.py --headless --steps 300

With hospital scene:
    $ISAACLAB_DIR/isaaclab.sh -p scripts/00_sim/create_scene.py --load_hospital

With different cube size:
    $ISAACLAB_DIR/isaaclab.sh -p scripts/00_sim/create_scene.py --size 0.5
"""

"""Launch Isaac Sim Simulator first."""

import argparse
import os
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Combined Isaac Lab scene creation tutorial.")

parser.add_argument("--size", type=float, default=1.0, help="Side length of the white cuboid.")
parser.add_argument("--steps", type=int, default=-1, help="Number of sim steps. Use -1 to run forever.")
parser.add_argument("--log_time", action="store_true", help="Write sim time to logs/create_scene/log.txt.")
parser.add_argument("--load_hospital", action="store_true", help="Load the hospital USD scene.")
parser.add_argument("--render_mode", type=str, default="performance", choices=["performance", "balanced", "quality"])

parser.add_argument("--width", type=int, default=1280, help="Viewport width.")
parser.add_argument("--height", type=int, default=720, help="Viewport height.")

AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

def make_log_file():
    """Create logs/create_scene/log.txt if logging is enabled."""

    log_dir_path = os.path.abspath(os.path.join("logs", "create_scene"))
    os.makedirs(log_dir_path, exist_ok=True)

    log_file_path = os.path.join(log_dir_path, "log.txt")
    print(f"[INFO] Logging sim time to: {log_file_path}")

    return open(log_file_path, "w")

def design_scene():
    """Spawn ground, lights, primitive shapes, deformable objects, and USD assets."""

    # Ground plane
    cfg_ground = sim_utils.GroundPlaneCfg()
    cfg_ground.func("/World/defaultGroundPlane", cfg_ground)

    # Distant light
    cfg_light_distant = sim_utils.DistantLightCfg(
        intensity=3000.0,
        color=(0.75, 0.75, 0.75),
    )
    cfg_light_distant.func(
        "/World/lightDistant",
        cfg_light_distant,
        translation=(1.0, 0.0, 10.0),
    )

    # Grouping prim for objects
    sim_utils.create_prim("/World/Objects", "Xform")

    # White cuboid from launch_app.py idea
    cfg_cuboid = sim_utils.CuboidCfg(
        size=[args_cli.size] * 3,
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(1.0, 1.0, 1.0),
        ),
    )
    cfg_cuboid.func(
        "/World/Objects/WhiteCuboid",
        cfg_cuboid,
        translation=(0.8, 0.0, args_cli.size / 2.0),
    )

    # Red visual-only cones
    cfg_cone = sim_utils.ConeCfg(
        radius=0.15,
        height=0.5,
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(1.0, 0.0, 0.0),
        ),
    )
    cfg_cone.func(
        "/World/Objects/Cone1",
        cfg_cone,
        translation=(-1.0, 1.0, 1.0),
    )
    cfg_cone.func(
        "/World/Objects/Cone2",
        cfg_cone,
        translation=(-1.0, -1.0, 1.0),
    )

    # Green rigid cone with mass and collision
    cfg_cone_rigid = sim_utils.ConeCfg(
        radius=0.15,
        height=0.5,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(),
        mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.0, 1.0, 0.0),
        ),
    )
    cfg_cone_rigid.func(
        "/World/Objects/ConeRigid",
        cfg_cone_rigid,
        translation=(-0.2, 0.0, 2.0),
        orientation=(0.5, 0.0, 0.5, 0.0),
    )

    # Blue deformable cuboid
    cfg_cuboid_deformable = sim_utils.MeshCuboidCfg(
        size=(0.2, 0.5, 0.2),
        deformable_props=sim_utils.DeformableBodyPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.0, 0.0, 1.0),
        ),
        physics_material=sim_utils.DeformableBodyMaterialCfg(),
    )
    cfg_cuboid_deformable.func(
        "/World/Objects/CuboidDeformable",
        cfg_cuboid_deformable,
        translation=(0.15, 0.0, 2.0),
    )

    # Table USD asset
    table_usd_path = f"{ISAAC_NUCLEUS_DIR}/Props/Mounts/SeattleLabTable/table_instanceable.usd"
    cfg_table = sim_utils.UsdFileCfg(usd_path=table_usd_path)
    cfg_table.func(
        "/World/Objects/Table",
        cfg_table,
        translation=(0.0, 0.0, 1.05),
    )

    # Optional hospital USD scene
    if args_cli.load_hospital:
        hospital_usd_path = f"{ISAAC_NUCLEUS_DIR}/Environments/Hospital/hospital.usd"
        cfg_hospital = sim_utils.UsdFileCfg(usd_path=hospital_usd_path)
        cfg_hospital.func("/World/Hospital", cfg_hospital)

def main():
    """Main function."""

    # Render settings from set_rendering_mode.py
    render_cfg = sim_utils.RenderCfg(
        rendering_mode=args_cli.render_mode,
        carb_settings={
            "rtx.reflections.enabled": False,
        },
    )

    # Simulation context from create_empty.py
    sim_cfg = sim_utils.SimulationCfg(
        dt=0.01,
        device=args_cli.device,
        render=render_cfg,
    )
    sim = sim_utils.SimulationContext(sim_cfg)

    # Camera view
    if args_cli.load_hospital:
        sim.set_camera_view([-11.0, -0.5, 2.0], [0.0, 0.0, 0.5])
    else:
        sim.set_camera_view([2.0, 0.0, 2.5], [-0.5, 0.0, 0.5])

    # Spawn scene assets
    design_scene()

    # Initialize simulator after scene creation
    sim.reset()
    print("[INFO]: Setup complete...")

    sim_dt = sim.get_physics_dt()
    sim_time = 0.0
    count = 0

    log_file = make_log_file() if args_cli.log_time else None

    while simulation_app.is_running():
        if args_cli.steps > 0 and count >= args_cli.steps:
            break

        if log_file is not None:
            log_file.write(f"{sim_time}\n")

        sim.step()

        sim_time += sim_dt
        count += 1

    if log_file is not None:
        log_file.close()


if __name__ == "__main__":
    main()
    simulation_app.close()