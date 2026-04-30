You should not try to do these as separate random tutorials. Build **one spine project** around your SO-100/custom arm, then add each job-description feature onto it.

# Spine Project: SO-100 Drawer Opening in Isaac Lab

## Phase 1: Asset pipeline first

Goal: get your real robot into Isaac Lab correctly.

Build:

```text
URDF/MJCF -> USD -> Isaac Lab ArticulationCfg -> validation script
```

Deliverables:

```text
scripts/assets/validate_so100_asset.py
source/so100_tasks/so100_tasks/assets/so100.py
```

Validate:

```text
joint names
joint axes
joint limits
collision shapes
mass/inertia
drive stiffness/damping
gravity stability
simple position control
```

Why first: if the asset is wrong, RL, teleop, sim-to-real, and Newton comparisons are all garbage.

---

## Phase 2: Simple Isaac Lab control script

Goal: control your arm before RL.

Build:

```text
spawn SO-100
reset joints
send joint position targets
send end-effector target through IK
print joint state / EE pose
```

Deliverables:

```text
scripts/assets/run_so100_articulation.py
scripts/assets/run_so100_ik.py
```

This connects to your resume point:

```text
Implemented IK solver in Isaac Lab with MuJoCo solver...
```

But you need a clean demo proving it.

---

## Phase 3: Drawer-opening environment

Goal: author a real Isaac Lab task.

Build:

```text
SO-100 + drawer asset + table
actions = joint position deltas or EE delta pose
observations = joint pos, joint vel, EE pose, drawer handle pose, drawer joint position
reward = drawer opening progress + reaching + grasp alignment
termination = timeout or drawer opened
reset = robot + drawer state randomized
```

Deliverables:

```text
source/so100_tasks/so100_tasks/tasks/manager_based/drawer/
  drawer_env_cfg.py
  mdp/rewards.py
  mdp/observations.py
  mdp/terminations.py
  mdp/events.py
```

Start state-based. Do **not** start with cameras.

---

## Phase 4: PPO training

Goal: train a policy in sim.

Build:

```text
train PPO
log rewards
load checkpoint
run policy inference
record video
benchmark samples/sec
```

Deliverables:

```text
scripts/train/train_so100_drawer_ppo.sh
scripts/eval/eval_so100_drawer_policy.py
logs/ppo_drawer/
```

This maps directly to:

```text
scalable reinforcement learning
cloud-scale training
benchmarking/profiling
```

---

## Phase 5: Teleop + demos

Goal: collect demonstrations from Quest2 or keyboard first.

Build in this order:

```text
keyboard teleop -> Quest2 teleop -> record demos -> replay demos
```

Deliverables:

```text
scripts/teleop/keyboard_teleop_drawer.py
scripts/teleop/quest2_teleop_drawer.py
scripts/demos/record_demos.py
scripts/demos/replay_demo.py
datasets/so100_drawer/
```

Do keyboard first because Quest2 adds networking/debugging noise.

For Quest2, the pipeline should be:

```text
Quest2 controller pose
-> ROS2 / rosbridge
-> target EE pose
-> IK
-> joint targets
-> Isaac Sim / real SO-100
```

This connects to your resume point:

```text
Quest2 teleop pipeline streamed ROS2 commands to sim/real robots via rosbridge in Isaac Sim.
```

---

## Phase 6: Imitation learning

Goal: use your demos.

Build:

```text
demo dataset
behavior cloning baseline
ACT policy training
policy replay in Isaac Lab
compare BC/ACT vs PPO
```

Deliverables:

```text
scripts/il/train_bc.py
scripts/il/train_act.py
scripts/il/eval_policy.py
```

For interview purposes, you need to explain:

```text
teleop creates expert state-action pairs
BC/ACT learns action distribution from demos
RL can fine-tune beyond demos
main failure is covariate shift
```

---

## Phase 7: Sim-to-real

Goal: transfer policy safely.

Do not transfer the full drawer policy first. First transfer smaller tests:

```text
1. joint position tracking
2. EE reaching
3. touch drawer handle
4. pull drawer slowly
5. full policy
```

Randomize:

```text
joint friction
armature
mass
inertia
joint damping
drawer friction
drawer mass
handle pose
camera/observation noise
action delay
PD gains
```

Deliverables:

```text
source/so100_tasks/.../events.py
configs/domain_randomization.yaml
scripts/real/run_policy_on_so100.py
docs/sim2real_checklist.md
```

Safety checklist:

```text
low speed
low torque/current limit
emergency stop
workspace bounds
policy action clipping
human hand outside workspace
start with one-step inference, not continuous rollout
```

---

## Phase 8: Newton comparison

Goal: show physics-backend awareness, not fake expertise.

Build a comparison script:

```text
same asset
same initial state
same action sequence
compare default backend vs Newton where supported
measure:
  stability
  contact behavior
  joint tracking
  drawer motion
  FPS / step time
```

Deliverables:

```text
scripts/physics/compare_newton_vs_default.py
docs/newton_comparison_report.md
```

Do this after the normal Isaac Lab task works. Newton debugging before your baseline works will waste time.

---

## Phase 9: Perception-in-the-loop RL

Goal: add cameras only after state-based task works.

Build:

```text
camera mounted above drawer
RGB/depth observation
tiled rendering if many envs
compare training speed:
  state obs vs depth obs
```

Deliverables:

```text
source/so100_tasks/.../drawer_camera_env_cfg.py
scripts/bench/benchmark_state_vs_depth.py
```

Metrics:

```text
FPS
env step time
samples/sec
GPU memory
training reward curve
```

---

# Best order

Do it in this order:

```text
1. SO-100 asset validation
2. SO-100 articulation control
3. drawer environment, state-based
4. PPO training
5. policy inference
6. keyboard teleop
7. Quest2 teleop
8. demo recording/replay
9. BC/ACT
10. domain randomization
11. cautious sim-to-real
12. Newton comparison
13. perception-in-the-loop RL
14. benchmarking/profiling report
```

Do not start with Quest2, Newton, or vision. Those are layers on top of a working asset + task.

# What we should do next

Next batch should be:

```text
SO-100 / custom arm asset validation in Isaac Lab
```

You should send either:

```text
your URDF/USD asset file structure
your existing ArticulationCfg
or the Isaac Lab script you already used to spawn the arm
```

Then we will build:

```text
validate_so100_asset.py
```

It will check joint names, limits, axes, collisions, inertia, drives, gravity stability, and simple joint commands.
