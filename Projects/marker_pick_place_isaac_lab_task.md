# Marker Pick-Place Isaac Lab Task

Goal: convert the current scratch scene in `02_Sim2Real/design_setup.py` into a proper Isaac Lab teleop task that can record LeRobot-style episodes.

## Current State

`02_Sim2Real/design_setup.py` is a visual prototype.

It is useful for:

```text
checking wall placement
checking table size
checking cup position
checking marker physics
checking robot placement
```

It is not yet useful for:

```text
teleop recording
episode resets
observations
actions
success checks
domain randomization
```

## Target Structure

Create a package similar to the SO-101 workshop:

```text
source/marker_pick_place/
  marker_pick_place/
    assets/
      so101_proxy.py
    tasks/
      __init__.py
      marker_env_cfg.py
    mdp/
      __init__.py
      resets.py
      observations.py
      terms.py
```

## Step 1: Robot Config

Create:

```text
source/marker_pick_place/marker_pick_place/assets/so101_proxy.py
```

Use the SO-101 repo pattern:

```python
SO101_PROXY_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(...),
    init_state=...,
    actuators=...,
)
```

This replaces the manual `spawn_so101_proxy()` function.

## Step 2: Scene Config

Create:

```text
source/marker_pick_place/marker_pick_place/tasks/marker_env_cfg.py
```

Convert scene pieces from `design_setup.py` into named Isaac Lab configs:

```python
@configclass
class MarkerSceneCfg(InteractiveSceneCfg):
    robot = SO101_PROXY_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    table = AssetBaseCfg(...)
    walls = AssetBaseCfg(...)
    cup = AssetBaseCfg(...)
    marker = RigidObjectCfg(...)
```

Keep walls/table/cup fixed at first.

## Step 3: Marker As RigidObjectCfg

The marker is the important dynamic object.

Use:

```python
marker = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/Marker",
    spawn=sim_utils.CuboidCfg(
        size=(0.152, 0.008, 0.008),
        rigid_props=...,
        mass_props=...,
        collision_props=...,
        physics_material=...,
    ),
    init_state=RigidObjectCfg.InitialStateCfg(
        pos=(...),
    ),
)
```

This lets Isaac Lab reset it, observe it, and record it cleanly.

## Step 4: Actions

Start with joint position actions:

```text
Rotation
Pitch
Elbow
Wrist_Pitch
Wrist_Roll
Jaw
```

Same idea as the SO-101 workshop `ActionsCfg`.

## Step 5: Observations

Start simple:

```text
robot joint positions
robot joint velocities
marker pose
cup pose
end-effector pose
```

Add cameras after the state-based task works.

## Step 6: Reset Events

Create reset functions for:

```text
robot home pose
marker pose on table
optional small marker yaw randomization
optional small cup pose randomization
```

Use the SO-101 workshop style:

```python
EventTerm(
    func=reset_marker,
    mode="reset",
    params={...},
)
```

## Step 7: Register The Task

In:

```text
source/marker_pick_place/marker_pick_place/tasks/__init__.py
```

Register:

```python
gym.register(
    id="Marker-PickPlace-Teleop",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "marker_pick_place.tasks.marker_env_cfg:MarkerTeleopEnvCfg",
    },
)
```

## Step 8: Use The SO-101 Teleop Pattern

Once the task is registered, use the SO-101 repo's `lerobot_agent.py` pattern.

Expected command shape:

```bash
PYTHONPATH=$PWD/02_Sim2Real/marker_pick_place:$PWD/Sim-to-Real-SO-101-Workshop/source \
lerobot_agent \
  --task Marker-PickPlace-Teleop \
  --port /dev/ttyACM0 \
  --robot_id leader_arm_1 \
  --repo_id your_name/marker_pick_place \
  --repo_root ./datasets/marker_pick_place \
  --task_name "Pick marker and place in black cup"
```

Keyboard controls:

```text
S = start/stop recording
R = reset world
C = cancel current recording
```

The marker task uses two fixed RGB cameras:

```text
top
side
```

The real setup should use the same two camera views.

## First Milestone

The first real milestone is:

```text
Isaac Lab task loads
SO-101 proxy robot moves with teleop
marker and cup appear in correct places
pressing S records an episode
dataset files are written
```

Do not start RL before this works.
