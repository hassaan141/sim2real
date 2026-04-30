# VR/XR Teleoperation Bringup

This folder tracks the VR teleop work from `tut.md`.

## Current local setup

- Isaac Lab exists at `/home/hassaan/robotics/IsaacLab`.
- The Isaac Lab checkout already has G1 humanoid XR teleop tasks:
  - `Isaac-PickPlace-FixedBaseUpperBodyIK-G1-Abs-v0`
  - `Isaac-PickPlace-Locomanipulation-G1-Abs-v0`
- Workstation LAN IP detected today: `10.0.0.31`.
- `isaacteleop` is installed in the Isaac Lab Python environment as `1.0.193`.
- `python -m isaacteleop.cloudxr --help` works through `isaaclab.sh`.
- VR launchers default to `DEVICE=cuda:0`. Override with `DEVICE=cpu ...` if needed.
- No `~/.cloudxr/run/cloudxr.env` exists yet, so CloudXR runtime startup is the first remaining external dependency.
- The install upgraded `scipy` to `1.15.3`, which pip reports conflicts with `osqp`'s declared `scipy<1.12.0` requirement. Keep an eye on cuRobo/OSQP flows later.

## Phase 1: humanoid first

If the G1 locomanipulation asset download is blocked, sanity-check the XR pipeline with Franka first:

```bash
03_VR_XR/run_franka_stack_handtracking.sh
```

For the official G1 inspire-hand pick/place task:

```bash
03_VR_XR/run_g1_inspire_handtracking.sh
```

Start with the fixed-base G1 task. It exercises the upper-body hand retargeter without also debugging locomotion anchoring:

```bash
03_VR_XR/run_g1_fixed_base_handtracking.sh
```

Then move to the full locomanipulation G1 task:

```bash
03_VR_XR/run_g1_locomanip_handtracking.sh
```

Both scripts use Isaac Lab's official teleop entrypoint:

```text
/home/hassaan/robotics/IsaacLab/scripts/environments/teleoperation/teleop_se3_agent.py
```

## Phase 2: Quest / CloudXR connection

Preferred first attempt from `tut.md`:

```bash
03_VR_XR/run_cloudxr.sh
```

Keep that terminal running. After it creates `~/.cloudxr/run/cloudxr.env`, the G1 launch scripts source it automatically.

Quest browser should connect to the workstation at:

```text
10.0.0.31
```

Firewall ports from the tutorial:

```bash
sudo ufw allow 47998/udp
sudo ufw allow 49100,48322/tcp
sudo ufw allow 8080,8443/tcp
```

Isaac Lab also ships Docker CloudXR runtime config in:

```text
/home/hassaan/robotics/IsaacLab/docker/docker-compose.cloudxr-runtime.patch.yaml
```

Keep that as fallback if the `isaacteleop` CloudXR runtime path is awkward.

## Phase 3: custom arm

After the G1 path works, port the manipulator pattern from Isaac Lab's Franka stack task:

```text
/home/hassaan/robotics/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/stack/config/franka/stack_ik_abs_env_cfg.py
```

The key pieces to copy conceptually are:

- `OpenXRDeviceCfg`
- `Se3AbsRetargeterCfg` or `Se3RelRetargeterCfg`
- `GripperRetargeterCfg`
- the task action space expected by `teleop_se3_agent.py`
