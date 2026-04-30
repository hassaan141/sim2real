SO-100 Asset Pipeline
=====================

Goal
----

Build this pipeline end to end:

```text
open-source SO-100 URDF/MJCF
-> converted USD
-> Isaac Lab ArticulationCfg
-> spawn script
-> repeatable physical-fidelity validation script
```

This keeps asset import, robot configuration, and validation separate. That
matters because the same robot config should later be reused by IK, teleop, RL,
and drawer-opening environments.

Current Repository Layout
-------------------------

```text
assets/robots/so100/
  urdf/                 # put SO-100 URDF files here
  mjcf/                 # put SO-100 MJCF/XML files here
  usd/                  # generated USD output goes here

source/so100_tasks/so100_tasks/assets/
  so100.py              # Isaac Lab ArticulationCfg for the imported robot

scripts/assets/
  convert_so100_asset.py
  spawn_so100.py
  validate_so100_asset.py
```

Step 1: Add The Source Robot Model
----------------------------------

Put the open-source SO-100 robot description in one of these locations:

```text
assets/robots/so100/urdf/so100.urdf
assets/robots/so100/mjcf/so100.xml
```

URDF is usually the better first path for Isaac Lab because it maps directly to
robot links, joints, limits, and drives. MJCF is also useful if the source model
already has better MuJoCo-style inertial or actuator metadata.

Step 2: Convert URDF Or MJCF To USD
-----------------------------------

Run one of these from the Isaac Lab Python environment:

```bash
python scripts/assets/convert_so100_asset.py \
  --input assets/robots/so100/urdf/so100.urdf \
  --input-type urdf \
  --fix-base
```

or:

```bash
python scripts/assets/convert_so100_asset.py \
  --input assets/robots/so100/mjcf/so100.xml \
  --input-type mjcf \
  --fix-base
```

Expected output:

```text
assets/robots/so100/usd/so100.usd
```

Step 3: Spawn The Imported Robot
--------------------------------

```bash
python scripts/assets/spawn_so100.py --num_envs 1
```

This should:

```text
spawn ground + light + SO-100
print discovered joint names
move one joint at a time with a small position target
```

Step 4: Validate The Asset
--------------------------

```bash
python scripts/assets/validate_so100_asset.py --num_envs 1
```

The validation report should be compared with the real SO-100 hardware:

```text
joint names
joint order
joint direction/sign
joint limits
body/link names
gravity stability
small position-control response
collision behavior
mass/inertia sanity
```

Validation Checklist
--------------------

Fill this in as we test the asset:

```text
[ ] USD generated from URDF
[ ] USD generated from MJCF, if source is available
[ ] SO-100 spawns without errors
[ ] base is fixed when expected
[ ] all expected joints appear
[ ] joint order is documented
[ ] positive command direction matches hardware
[ ] joint limits match hardware or vendor docs
[ ] arm holds pose under gravity
[ ] small joint sweeps are smooth and stable
[ ] collision geometry is usable for manipulation
[ ] visual geometry is aligned with collision geometry
[ ] mass/inertia values are plausible
```

Next Implementation Target
--------------------------

After the first successful spawn, update `source/so100_tasks/so100_tasks/assets/so100.py`
with real joint groups instead of the broad `.*` actuator regex. For example:

```text
arm joints
wrist joints
gripper joint
```

Then tune:

```text
effort_limit_sim
velocity_limit_sim
stiffness
damping
```

based on observed sim behavior and the real servo specs.

Adding a New Robot to Isaac Lab

Simulating and training a new robot is a multi-step process that starts with importing the robot into Isaac Sim. This is covered in depth in the Isaac Sim documentation here. Once the robot is imported and tuned for simulation, we must define those interfaces necessary to clone the robot across multiple environments, drive its joints, and properly reset it, regardless of the chosen workflow or training framework.

In this tutorial, we will examine how to add a new robot to Isaac Lab. The key step is creating an AssetBaseCfg that defines the interface between the USD articulation of the robot and the learning algorithms available through Isaac Lab.
The Code

The tutorial corresponds to the add_new_robot script in the scripts/tutorials/01_assets directory.

# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import argparse

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(
    description="This script demonstrates adding a custom robot to an Isaac Lab environment."
)
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to spawn.")
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import numpy as np
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import AssetBaseCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

JETBOT_CONFIG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/NVIDIA/Jetbot/jetbot.usd"),
    actuators={"wheel_acts": ImplicitActuatorCfg(joint_names_expr=[".*"], damping=None, stiffness=None)},
)

DOFBOT_CONFIG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/Yahboom/Dofbot/dofbot.usd",
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True, solver_position_iteration_count=8, solver_velocity_iteration_count=0
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "joint1": 0.0,
            "joint2": 0.0,
            "joint3": 0.0,
            "joint4": 0.0,
        },
        pos=(0.25, -0.25, 0.0),
    ),
    actuators={
        "front_joints": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-2]"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
        "joint3_act": ImplicitActuatorCfg(
            joint_names_expr=["joint3"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
        "joint4_act": ImplicitActuatorCfg(
            joint_names_expr=["joint4"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
    },
)


class NewRobotsSceneCfg(InteractiveSceneCfg):
    """Designs the scene."""

    # Ground-plane
    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())

    # lights
    dome_light = AssetBaseCfg(
        prim_path="/World/Light", spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
    )

    # robot
    Jetbot = JETBOT_CONFIG.replace(prim_path="{ENV_REGEX_NS}/Jetbot")
    Dofbot = DOFBOT_CONFIG.replace(prim_path="{ENV_REGEX_NS}/Dofbot")


def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    sim_dt = sim.get_physics_dt()
    sim_time = 0.0
    count = 0

    while simulation_app.is_running():
        # reset
        if count % 500 == 0:
            # reset counters
            count = 0
            # reset the scene entities to their initial positions offset by the environment origins
            root_jetbot_state = scene["Jetbot"].data.default_root_state.clone()
            root_jetbot_state[:, :3] += scene.env_origins
            root_dofbot_state = scene["Dofbot"].data.default_root_state.clone()
            root_dofbot_state[:, :3] += scene.env_origins

            # copy the default root state to the sim for the jetbot's orientation and velocity
            scene["Jetbot"].write_root_pose_to_sim(root_jetbot_state[:, :7])
            scene["Jetbot"].write_root_velocity_to_sim(root_jetbot_state[:, 7:])
            scene["Dofbot"].write_root_pose_to_sim(root_dofbot_state[:, :7])
            scene["Dofbot"].write_root_velocity_to_sim(root_dofbot_state[:, 7:])

            # copy the default joint states to the sim
            joint_pos, joint_vel = (
                scene["Jetbot"].data.default_joint_pos.clone(),
                scene["Jetbot"].data.default_joint_vel.clone(),
            )
            scene["Jetbot"].write_joint_state_to_sim(joint_pos, joint_vel)
            joint_pos, joint_vel = (
                scene["Dofbot"].data.default_joint_pos.clone(),
                scene["Dofbot"].data.default_joint_vel.clone(),
            )
            scene["Dofbot"].write_joint_state_to_sim(joint_pos, joint_vel)
            # clear internal buffers
            scene.reset()
            print("[INFO]: Resetting Jetbot and Dofbot state...")

        # drive around
        if count % 100 < 75:
            # Drive straight by setting equal wheel velocities
            action = torch.Tensor([[10.0, 10.0]])
        else:
            # Turn by applying different velocities
            action = torch.Tensor([[5.0, -5.0]])

        scene["Jetbot"].set_joint_velocity_target(action)

        # wave
        wave_action = scene["Dofbot"].data.default_joint_pos
        wave_action[:, 0:4] = 0.25 * np.sin(2 * np.pi * 0.5 * sim_time)
        scene["Dofbot"].set_joint_position_target(wave_action)

        scene.write_data_to_sim()
        sim.step()
        sim_time += sim_dt
        count += 1
        scene.update(sim_dt)


def main():
    """Main function."""
    # Initialize the simulation context
    sim_cfg = sim_utils.SimulationCfg(device=args_cli.device)
    sim = sim_utils.SimulationContext(sim_cfg)
    sim.set_camera_view([3.5, 0.0, 3.2], [0.0, 0.0, 0.5])
    # Design scene
    scene_cfg = NewRobotsSceneCfg(args_cli.num_envs, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)
    # Play the simulator
    sim.reset()
    # Now we are ready!
    print("[INFO]: Setup complete...")
    # Run the simulator
    run_simulator(sim, scene)


if __name__ == "__main__":
    main()
    simulation_app.close()

The Code Explained

Fundamentally, a robot is an articulation with joint drives. To move a robot around in the simulation, we must apply targets to its drives and step the sim forward in time. However, to control a robot strictly through joint drives is tedious, especially if you want to control anything complex, and doubly so if you want to clone the robot across multiple environments.

To facilitate this, Isaac Lab provides a collection of configuration classes that define which parts of the USD need to be cloned, which parts are actuators to be controlled by an agent, how it should be reset, etc… There are many ways you can configure a single robot asset for Isaac Lab depending on how much fine tuning the asset requires. To demonstrate, the tutorial script imports two robots: The first robot, the Jetbot, is configured minimally while the second robot, the Dofbot, is configured with additional parameters.

The Jetbot is a simple, two wheeled differential base with a camera on top. The asset is used for a number of demonstrations and tutorials in Isaac Sim, so we know it’s good to go! To bring it into Isaac lab, we must first define one of these configurations. Because a robot is an articulation with joint drives, we define an ArticulationCfg that describes the robot.

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import AssetBaseCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.utils.assets import ISAAC_NUCLEUS_DIR

JETBOT_CONFIG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/NVIDIA/Jetbot/jetbot.usd"),
    actuators={"wheel_acts": ImplicitActuatorCfg(joint_names_expr=[".*"], damping=None, stiffness=None)},
)

This is the minimal configuration for a robot in Isaac Lab. There are only two required parameters: spawn and actuators.

The spawn parameter is looking for a SpawnerCfg, and is used to specify the USD asset that defines the robot in the sim. The Isaac Lab simulation utilities, isaaclab.sim, provides us with a USDFileCfg class that consumes a path to our USD asset, and generates the SpawnerCfg we need. In this case, the jetbot.usd is located with the Isaac Assets under Robots/Jetbot/jetbot.usd.

The actuators parameter is a dictionary of Actuator Configs and defines what parts of the robot we intend to control with an agent. There are many different ways to update the state of a joint in time towards some target. Isaac Lab provides a collection of actuator classes that can be used to match common actuator models or even implement your own! In this case, we are using the ImplicitActuatorCfg class to specify the actuators for the robot, because they are simple wheels and the defaults are fine.

Specifying joint name keys for this dictionary can be done to varying levels of specificity. The jetbot only has a few joints, and we are just going to use the defaults specified in the USD asset, so we can use a simple regex, .* to specify all joints. Other regex can also be used to group joints and associated configurations.

Note

Both stiffness and damping must be specified in the implicit actuator, but a value of None will use the defaults defined in the USD asset.

While this is the minimal configuration, there are a number of other parameters we could specify

DOFBOT_CONFIG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=f"{ISAAC_NUCLEUS_DIR}/Robots/Yahboom/Dofbot/dofbot.usd",
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True, solver_position_iteration_count=8, solver_velocity_iteration_count=0
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={
            "joint1": 0.0,
            "joint2": 0.0,
            "joint3": 0.0,
            "joint4": 0.0,
        },
        pos=(0.25, -0.25, 0.0),
    ),
    actuators={
        "front_joints": ImplicitActuatorCfg(
            joint_names_expr=["joint[1-2]"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
        "joint3_act": ImplicitActuatorCfg(
            joint_names_expr=["joint3"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
        "joint4_act": ImplicitActuatorCfg(
            joint_names_expr=["joint4"],
            effort_limit_sim=100.0,
            velocity_limit_sim=100.0,
            stiffness=10000.0,
            damping=100.0,
        ),
    },
)

This configuration can be used to add a Dofbot to the scene, and it contains some of those parameters. The Dofbot is a hobbiest robot arm with several joints, and so we have more options available for configuration. The two most notable differences though is the addition of configurations for physics properties, and the initial state of the robot, init_state.

The USDFileCfg has special parameters for rigid bodies and robots, among others. The rigid_props parameter expects a RigidBodyPropertiesCfg that allows you to specify body link properties of the robot being spawned relating to its behavior as a “physical object” in the simulation. The articulation_props meanwhile governs the properties relating to the solver being used to step the joints through time, and so it expects an ArticulationRootPropertiesCfg to be configured. There are many other physics properties and parameters that can be specified through configurations provided by isaaclab.sim.schemas.

The ArticulationCfg can optionally include the init_state parameter, that defines the initial state of the articulation. The initial state of an articulation is a special, user defined state that is used when the robot is spawned or reset by Isaac Lab. The initial joint state, joint_pos, is specified by a dictionary of floats with the USD joint names as keys (not the actuator names). Something else worth noting here is the coordinate system of the initial position, pos, which is that of the environment. In this case, by specifying a position of (0.25, -0.25, 0.0) we are offsetting the spawn position of the robot from the origin of the environment, and not the world.

Armed with the configurations for these robots, we can now add them to the scene and interact with them in the usual way for the direct workflow: by defining an InteractiveSceneCfg containing the articulation configs for the robots …

class NewRobotsSceneCfg(InteractiveSceneCfg):
    """Designs the scene."""

    # Ground-plane
    ground = AssetBaseCfg(prim_path="/World/defaultGroundPlane", spawn=sim_utils.GroundPlaneCfg())

    # lights
    dome_light = AssetBaseCfg(
        prim_path="/World/Light", spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75))
    )

    # robot
    Jetbot = JETBOT_CONFIG.replace(prim_path="{ENV_REGEX_NS}/Jetbot")
    Dofbot = DOFBOT_CONFIG.replace(prim_path="{ENV_REGEX_NS}/Dofbot")

…and then stepping the simulation while updating the scene entities appropriately.

def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    sim_dt = sim.get_physics_dt()
    sim_time = 0.0
    count = 0

    while simulation_app.is_running():
        # reset
        if count % 500 == 0:
            # reset counters
            count = 0
            # reset the scene entities to their initial positions offset by the environment origins
            root_jetbot_state = scene["Jetbot"].data.default_root_state.clone()
            root_jetbot_state[:, :3] += scene.env_origins
            root_dofbot_state = scene["Dofbot"].data.default_root_state.clone()
            root_dofbot_state[:, :3] += scene.env_origins

            # copy the default root state to the sim for the jetbot's orientation and velocity
            scene["Jetbot"].write_root_pose_to_sim(root_jetbot_state[:, :7])
            scene["Jetbot"].write_root_velocity_to_sim(root_jetbot_state[:, 7:])
            scene["Dofbot"].write_root_pose_to_sim(root_dofbot_state[:, :7])
            scene["Dofbot"].write_root_velocity_to_sim(root_dofbot_state[:, 7:])

            # copy the default joint states to the sim
            joint_pos, joint_vel = (
                scene["Jetbot"].data.default_joint_pos.clone(),
                scene["Jetbot"].data.default_joint_vel.clone(),
            )
            scene["Jetbot"].write_joint_state_to_sim(joint_pos, joint_vel)
            joint_pos, joint_vel = (
                scene["Dofbot"].data.default_joint_pos.clone(),
                scene["Dofbot"].data.default_joint_vel.clone(),
            )
            scene["Dofbot"].write_joint_state_to_sim(joint_pos, joint_vel)
            # clear internal buffers
            scene.reset()
            print("[INFO]: Resetting Jetbot and Dofbot state...")

        # drive around
        if count % 100 < 75:
            # Drive straight by setting equal wheel velocities
            action = torch.Tensor([[10.0, 10.0]])
        else:
            # Turn by applying different velocities
            action = torch.Tensor([[5.0, -5.0]])

        scene["Jetbot"].set_joint_velocity_target(action)

        # wave
        wave_action = scene["Dofbot"].data.default_joint_pos
        wave_action[:, 0:4] = 0.25 * np.sin(2 * np.pi * 0.5 * sim_time)
        scene["Dofbot"].set_joint_position_target(wave_action)

        scene.write_data_to_sim()
        sim.step()
        sim_time += sim_dt
        count += 1
        scene.update(sim_dt)
