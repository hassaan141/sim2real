# Learning:
# - Spawn a cartpole articulation
# - Create two copies using prim path regex
# - Reset root and joint states
# - Apply random joint efforts

import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Spawn and control a cartpole articulation.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation # imports isaac lab topics like robot mechanisms with joints
from isaaclab.sim import SimulationContext # imports stuff related to sim like step, reset etc
from isaaclab_assets import CARTPOLE_CFG

def design_scene():
    ground_cfg = sim_utils.GroundPlaneCfg() # This describes the asset
    ground_cfg.func("/World/defaultGroundPlane", ground_cfg) # This spawns it in the USD

    light_cfg = sim_utils.DomeLightCfg(
        intensity=3000.0,
        color=(0.75, 0.75, 0.75),
    )
    light_cfg.func("/World/Light", light_cfg)

    origins = [
        [0.0, 0.0, 0.0],
        [-1.0, 0.0, 0.0],
    ]

    sim_utils.create_prim("/World/Origin1", "Xform", translation=origins[0])
    sim_utils.create_prim("/World/Origin2", "Xform", translation=origins[1])

    cartpole_cfg = CARTPOLE_CFG.copy()

    cartpole_cfg.prim_path = "/World/Origin.*/Robot"

    cartpole = Articulation(cfg=cartpole_cfg)

    return {"cartpole": cartpole}, origins

def reset_cartpole(robot: Articulation, origins: torch.Tensor):
    root_state = robot.data.default_root_state.clone()

    # Default root state is local. Add env origins to place each copy correctly.
    root_state[:, :3] += origins

    robot.write_root_pose_to_sim(root_state[:, :7])
    robot.write_root_velocity_to_sim(root_state[:, 7:])

    joint_pos = robot.data.default_joint_pos.clone()
    joint_vel = robot.data.default_joint_vel.clone()

    joint_pos += torch.rand_like(joint_pos) * 0.1

    robot.write_joint_state_to_sim(joint_pos, joint_vel)
    robot.reset()

def run_simulator(sim: SimulationContext, entities: dict[str, Articulation], origins: torch.Tensor):
    robot = entities["cartpole"]

    sim_dt = sim.get_physics_dt()
    count = 0

    while simulation_app.is_running():
        if count % 500 == 0:
            count = 0
            reset_cartpole(robot, origins)
            print("[INFO]: Resetting cartpole state...")

        efforts = torch.randn_like(robot.data.joint_pos) * 5.0

        robot.set_joint_effort_target(efforts)
        robot.write_data_to_sim()

        sim.step()
        count += 1

        robot.update(sim_dt)

def main():
    sim_cfg = sim_utils.SimulationCfg(device=args_cli.device)
    sim = SimulationContext(sim_cfg)

    sim.set_camera_view(
        eye=[2.5, 0.0, 4.0],
        target=[0.0, 0.0, 2.0],
    )

    scene_entities, scene_origins = design_scene()
    scene_origins = torch.tensor(scene_origins, device=sim.device)

    sim.reset()
    print("[INFO]: Setup complete...")

    run_simulator(sim, scene_entities, scene_origins)


if __name__ == "__main__":
    main()
    simulation_app.close()
