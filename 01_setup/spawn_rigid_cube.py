import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Spawn Rigid Cube")
parser.add_argument("--steps", type=int, default=300, help="Number of sim steps")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import isaaclab.sim as sim_utils


def design_scene():
    # TODO: ground
    ground_cfg = sim_utils.GroundPlaneCfg()
    ground_cfg.func(
        "/World/defaultGroundPlane",
        ground_cfg
    )

    light_cfg = sim_utils.DistantLightCfg(
        intensity=3000.0,
        color=(0.75, 0.75, 0.75),
    )
    light_cfg.func(
        "/World/Light",
        light_cfg,
        translation=(1.0, 0.0, 10.0),
    )

    sim_utils.create_prim(
        "/World/Objects",
        "Xform",
    )

    cube_cfg = sim_utils.CuboidCfg(
        size=(0.4, 0.4, 0.4),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(),
        mass_props=sim_utils.MassPropertiesCfg(mass=1.0),
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(
            diffuse_color=(0.1, 0.8, 0.1),
        ),
    )
    cube_cfg.func(
        "/World/Objects/FallingCube",
        cube_cfg,
        translation=(0.0, 0.0, 2.0),
    )


def main():
    # TODO: sim cfg
    sim_cfg = sim_utils.SimulationCfg(
        dt=0.01, device=args_cli.device
    )
    

    # TODO: simulation context
    sim = sim_utils.SimulationContext(sim_cfg)

    # TODO: camera
    sim.set_camera_view(
        eye=[2.0, 0.0, 2.0],
        target=[0.0, 0.0, 0.5]
    )

    # TODO: design_scene
    design_scene()

    # TODO: reset
    sim.reset()

    # TODO: step loop
    print("[INFO] Setup complete. Cube should fall onto the ground.")
    
    for step in range(args_cli.steps):
        if not simulation_app.is_running():
            break
            
        sim.step()

        if step % 60 == 0:
            sim_time = step * sim_cfg.dt
            print(f"[STEP {step}] simulated time = {sim_time:.2f}s")

    print("[INFO] Done.") 


if __name__ == "__main__":
    main()
    simulation_app.close()