# Banana Pick Sim-to-Real + GR00T Plan

## Goal

Collect:

- 50 simulation episodes from Isaac Lab.
- 10 real robot episodes.
- Optional RL policy/checkpoints for banana picking.
- Convert sim + real demonstrations into a GR00T-compatible LeRobot dataset.
- Fine-tune GR00T N1.6.
- Deploy the policy on the real robot.

The important point: the current recorder saves `teleop_dataset.pt`. That is useful as a raw local format, but it is not the final training format for GR00T.

## Target Data Format

Use GR00T-flavored LeRobot v2 for GR00T N1.6 fine-tuning.

Expected structure:

```text
banana_pick_lerobot/
  meta/
    info.json
    episodes.jsonl
    tasks.jsonl
    modality.json
  data/
    chunk-000/
      episode_000000.parquet
      episode_000001.parquet
  videos/
    chunk-000/
      observation.images.env/
        episode_000000.mp4
      observation.images.gripper/
        episode_000000.mp4
```

LeRobot upstream v3 uses Parquet/MP4 plus relational metadata. GR00T currently expects LeRobot v2-style data plus `meta/modality.json`. If you collect or convert through LeRobot v3, add a final v3-to-v2 conversion step before GR00T.

## What Each Episode Needs

Each timestep should contain:

```text
timestamp
episode_index
frame_index
task_index
observation.state
action
observation.images.env
observation.images.gripper
```

For this SO100/SO101-style arm, use joint vectors:

```text
observation.state = current joint positions, shape (6,)
action = commanded target joint positions or relative joint deltas, shape (6,)
```

Joint order must stay identical everywhere:

```text
shoulder_pan
shoulder_lift
elbow_flex
wrist_flex
wrist_roll
gripper
```

Camera keys should be stable:

```text
observation.images.env
observation.images.gripper
```

Task language should be simple and repeated for all episodes:

```text
pick up the banana and place it in the cup
```

## Current Local Format

Your current script records:

```text
recordings/teleop_YYYYMMDD_HHMMSS/teleop_dataset.pt
```

Inside:

```python
data["fps"]
data["cameras"]
data["frames"][i]["action"]
data["frames"][i]["joint_pos"]
data["frames"][i]["images"]["env"]
data["frames"][i]["images"]["gripper"]
```

This is a good raw capture format. Keep it. Then convert it into LeRobot/GR00T format.

## Collection Workflow

### 1. Simulation demonstrations

Run:

```bash
/home/hassaan/robotics/IsaacLab/isaaclab.sh -p \
  02_Sim2Real/marker_pick_place/marker_pick_place.py \
  --teleop --record
```

Controls:

```text
R = start recording
Y = stop and save recording
T = reset environment and apply Isaac Lab domain randomization
```

For 50 sim episodes:

1. Press `T`.
2. Press `R`.
3. Teleoperate one banana-pick attempt.
4. Press `Y`.
5. Repeat until you have 50 saved episode folders.

Prefer short, clean episodes. Failed episodes can be useful later for DAgger or robustness, but your first GR00T fine-tune should mostly use successful demonstrations.

### 2. Real robot demonstrations

Use the same joint order, same two camera names, and same task language.

For 10 real episodes, record:

```text
joint_pos
action
env camera RGB
gripper camera RGB
timestamp
episode boundary
```

The real recorder should output either the same raw `.pt` schema as sim or directly write LeRobot format. The easiest short-term path is to make real recordings match the current `.pt` schema, then use one converter for both sim and real.

### 3. RL training data

RL is useful for:

- generating extra successful sim rollouts;
- improving scripted/autonomous behavior;
- measuring success rate in sim;
- producing additional trajectories if the policy is reliable.

But do not mix arbitrary RL exploration into GR00T training unless it is filtered. GR00T fine-tuning is behavior cloning / VLA post-training. Bad or random RL trajectories will teach bad behavior.

Use RL data only if:

- the rollout succeeds;
- state/action/camera keys match the demo schema;
- actions are smooth enough for the real robot;
- the episode has the same language task.

## Conversion Plan

Create a converter:

```text
raw teleop_dataset.pt -> GR00T LeRobot v2 dataset
```

Converter responsibilities:

1. Load each `teleop_dataset.pt`.
2. Assign a global `episode_index`.
3. Extract per-frame:
   - `joint_pos` -> `observation.state`
   - `action` -> `action`
   - `images.env` -> video `observation.images.env`
   - `images.gripper` -> video `observation.images.gripper`
4. Write one Parquet file per episode.
5. Encode camera streams to MP4.
6. Write metadata:
   - `meta/info.json`
   - `meta/episodes.jsonl`
   - `meta/tasks.jsonl`
   - `meta/modality.json`
7. Compute normalization statistics.

For GR00T, `meta/modality.json` is the critical extra file. It describes how state/action vectors split into named robot fields and which video streams exist.

## Sim + Real Mixing

Recommended first dataset:

```text
50 sim successful episodes
10 real successful episodes
```

Use one combined dataset with source tags in metadata if possible:

```text
episode metadata:
  source = "sim" or "real"
```

If the GR00T training script accepts multiple dataset paths, keep them separate:

```text
banana_pick_sim_lerobot/
banana_pick_real_lerobot/
```

Then pass both paths to training or combine after validation.

Training priority:

1. Start with sim-only to validate the pipeline.
2. Fine-tune with sim + real.
3. If real behavior is poor, increase real weighting or oversample real episodes.
4. Add DAgger-style correction episodes from real robot failures.

## GR00T Fine-Tuning

Use the official Isaac-GR00T repo/container for N1.6.

Conceptual command:

```bash
python scripts/gr00t_finetune.py \
  --dataset-path /path/to/banana_pick_lerobot \
  --base-model-path nvidia/GR00T-N1.6-3B \
  --embodiment-tag new_embodiment \
  --data-config <your_so100_data_config> \
  --output-dir /path/to/checkpoints/banana_pick_groot_n1_6
```

You will likely need a custom data config for this robot because the state/action dimension is 6 and your cameras are `env` and `gripper`.

For small datasets, start conservative:

```text
max_steps: 10k-30k
small learning rate
strong image augmentation
validate frequently
watch for overfitting
```

## Deployment

Deployment needs an adapter:

```text
real robot observations -> GR00T policy input
GR00T action output -> robot command
```

Input adapter:

- read current 6 joint positions;
- capture env camera image;
- capture gripper camera image;
- resize/format images exactly like training;
- attach language instruction.

Output adapter:

- map predicted action vector to the same joint order;
- clamp to real joint limits;
- rate-limit and smooth commands;
- enforce emergency stop;
- send to robot controller.

Start with very slow rollout:

```text
low command rate
small action scale
joint-limit clamp
workspace safety
human emergency stop
```

## Validation Checklist

Before training:

- `env` and `gripper` camera tensors are not white.
- Sim and real images have same orientation and similar framing.
- Joint order is identical in sim, real, and training.
- Actions match the intended action space.
- Episode boundaries are correct.
- Failed recordings are labeled or excluded.
- Dataset viewer can play every episode.

Before deployment:

- Replay dataset actions in sim.
- Run policy in sim first.
- Run policy on real robot with no object.
- Run policy near object with low speed.
- Only then attempt banana pick.

## Immediate Next Engineering Tasks

1. Keep recording raw `.pt` episodes until camera reliability is solved.
2. Add a converter from `.pt` to GR00T LeRobot v2.
3. Add a dataset validator that prints:
   - number of episodes;
   - frame count;
   - camera min/max/mean;
   - action min/max;
   - joint min/max;
   - missing camera frames.
4. Collect 5 sim episodes and convert them.
5. Train a tiny smoke-test model or load the dataset through GR00T.
6. Scale to 50 sim + 10 real episodes.

## References

- GR00T N1.6: https://research.nvidia.com/labs/gear/gr00t-n1_6
- Isaac-GR00T data preparation: https://github.com/NVIDIA/Isaac-GR00T/blob/main/getting_started/data_preparation.md
- LeRobot dataset v3 docs: https://huggingface.co/docs/lerobot/lerobot-dataset-v3
- NVIDIA sim-to-real SO-101 GR00T course: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html
