# Isaac Lab Masters Internship Interview Prep - Kelly Guo

This document is a living technical prep file for discussing the SO-101 sim-to-real project with Kelly Guo, one of the main maintainers/authors of Isaac Lab. The goal is to be accurate with Isaac Lab terminology, clear about what has actually been implemented versus what is planned, and able to connect the project directly to the internship requirements.

## Status Legend

- **Completed:** Work I have actually implemented or verified.
- **In progress:** Work I am actively setting up now.
- **Planned:** Work I intend to do next in this project.
- **Conceptual / workshop reference:** Material I understand from the NVIDIA workshop or docs, but have not yet implemented myself in this project.

## Role Requirements Anchor

### What You'll Be Doing

- Develop the next features for the platform, such as integration with Newton simulation, scalable perception-in-the-loop reinforcement learning, and learning from demonstration via tele-operation.
- Participate in open-source development of Isaac Lab, including engaging with the robotics industrial and research communities.
- Scale training massively in the cloud, while ensuring the highest performance with extensive benchmarking, profiling, and optimizations.
- Build and improve the robot asset pipeline, importing URDF/MJCF models, authoring new environments, and validating physical fidelity against real-world hardware.
- Bridge the sim-to-real gap by working on domain randomization, system identification, and transfer techniques that move policies from simulation onto physical robots.

### What They Need To See

- Pursuing MS or PhD degree in Computer Science, Mechanical Engineering, Robotics, or similar program area.
- Experience in software development with Python and the deep-learning software stack: PyTorch, TensorFlow, JAX, etc.
- Experience with robotics and simulation workflows, including reinforcement learning and imitation learning in simulators such as Isaac Lab, Isaac Gym, MuJoCo, or other physics-based simulators.

### Ways To Stand Out

- Experience training a robot in simulation and deploying the policy sim-to-real.
- Publications in major AI and robotics conferences.

## Resume Anchors To Reference

- Developed a **Quest2** teleop pipeline that streamed **ROS2** commands to sim/real robots via rosbridge in **Isaac Sim**.
- Collected **120** demos and fine-tuned an **ACT** policy in **LeRobot** for a letter-drawing task on an SO-100 arm.
- Converted a custom arm from **URDF** to **USD** and authored a drawer-opening task environment in **Isaac Lab**.
- Trained the custom arm with **PPO** in **Isaac Lab** for drawer-opening manipulation in simulation.
- Implemented IK solver in **Isaac Lab** with **MuJoCo** solver, converging a 21-DOF hand to **0.1 mm** tolerance.
- Optimized depth estimation with **ONNX** and **TensorRT**, reducing latency **29%** and increasing from **85 to 120 FPS**.

## Honest One-Minute Project Summary

I am at the environment-alignment stage of a sim-to-real learning project around the SO-101/SO-100 style low-cost robot arm. Right now, I am duplicating the real workspace in Isaac Lab so that the simulated follower arm, camera views, object geometry, and task setup match the real follower arm setup as closely as possible.

The intended pipeline is to use a physical leader arm to teleoperate both a simulated follower in Isaac Lab and a real follower arm through LeRobot. The eventual goal is to collect many sim demonstrations and fewer real demonstrations, then train or evaluate policies on a mixed sim+real dataset. I have not completed that full loop yet; the current focus is making the sim environment faithful enough that future demonstrations will have the same observation/action structure as the real setup.

The key technical concern at this stage is distribution alignment. Before collecting data, I need sim and real to agree on robot asset structure, camera viewpoints, image resolution, joint ordering, action convention, task geometry, and episode semantics. Otherwise, any later imitation learning or sim-to-real transfer result would be hard to interpret.

## Current Project Status

### Completed

- Set up a local Isaac Lab marker pick/place environment around the SO-101 USD asset.
- Verified that my local SO-101 USD is byte-for-byte identical to the official workshop `SO-ARM101-USD.usd`.
- Inspected the official workshop camera config and copied the ego/gripper camera pose into my local marker environment.
- Added `camera_ego` / `rgb_ego` to the local visual observation config.
- Confirmed the workshop policy-facing camera resolution is `640x480`, not `1280x720`, even though the physical Logitech C270 supports 720p.
- Understood that the official sim camera path is `Robot/gripper/gripper_cam`, which is semantically the wrist/gripper camera.

### In Progress

- Matching the simulated camera view to the real wrist-mounted Logitech C270 camera.
- Duplicating the real workspace geometry in sim: table, walls, task objects, cup/marker/placement surfaces.
- Keeping the simulated policy-visible camera views aligned with the views used during real teleoperation.
- Setting up the environment so leader-follower teleoperation can collect meaningful sim demonstrations.

### Planned

- Collect sim demonstrations through leader-to-sim-follower teleoperation.
- Collect real demonstrations through leader-to-real-follower teleoperation.
- Validate that sim and real datasets share the same camera keys, image shapes, joint names, action order, and task labels.
- Train or fine-tune an imitation policy on sim-only, real-only, and mixed sim+real data.
- Evaluate policies in sim first, then on the real robot.
- Add domain randomization once the non-randomized environment is aligned.

### Conceptual / Workshop Reference

- Domain randomization, sim+real co-training, Cosmos augmentation, SAGE, and GapONet are currently concepts and reference strategies from the workshop notes. I should discuss them as future directions or as techniques I understand, not as work already completed in this project.

## Precise Technical Framing

This is not "I already trained and deployed a full policy." The accurate framing is:

- **Embodiment:** SO-101/SO-100 style 6-DoF arm including gripper/jaw joint.
- **Control interface:** Leader-follower teleoperation, where the leader's calibrated joint states are mapped to follower joint targets.
- **Current simulation stack:** Isaac Lab environment built on Isaac Sim/PhysX, using USD robot assets, `ArticulationCfg`, `InteractiveSceneCfg`, `ManagerBasedRLEnvCfg`, `ObservationTermCfg`, `EventTermCfg`, and `TiledCameraCfg`.
- **Current focus:** environment and camera alignment between sim and real.
- **Planned dataset format:** LeRobot-style episodic demonstrations with joint state/action and camera observations.
- **Planned learning mode:** learning from demonstration / behavior cloning, potentially using GR00T/VLA post-training or LeRobot policy training.
- **Planned transfer methods:** domain randomization, sim+real co-training, Cosmos video augmentation, and eventually actuation gap modeling through SAGE/GapONet.
- **Planned evaluation:** closed-loop policy rollout in sim and then on physical hardware, checking task success, failure modes, camera alignment, action smoothness, and sim-real gap symptoms.

## Current Local Implementation Notes

My local marker pick-place environment is in:

- `02_Sim2Real/marker_pick_place/marker_pick_place/tasks/marker_env_cfg.py`
- `02_Sim2Real/marker_pick_place/marker_pick_place/assets/so101_proxy.py`
- `02_Sim2Real/marker_pick_place/assets/usd/SO-ARM101-USD.usd`

The official workshop repo is available locally at:

- `isaac_tuts/Sim-to-Real-SO-101-Workshop`

Important camera alignment work already done:

- The workshop `SO-ARM101-USD.usd` and my copied USD are byte-for-byte identical.
- The official workshop ego camera config is:

```python
camera_ego.prim_path = "{ENV_REGEX_NS}/Robot/gripper/gripper_cam"
camera_ego.offset.pos = (-0.005, 0.06, -0.062)
camera_ego.offset.rot = euler_angles_to_quat(np.array([-45, 0, 0]), degrees=True)
```

- The policy-facing camera resolution in the workshop is `640x480`, not `1280x720`, even if the Logitech C270 supports 720p. For workshop compatibility, use `640x480 @ 30 fps`.
- The naming convention used by the workshop evaluation maps sim camera names to real/policy names, e.g. `ego -> wrist`, `external_D455 -> front`.

## Target System Architecture

This is the architecture I am building toward, not a claim that every box is already complete.

### Target High-Level Data Flow

```text
Physical SO-101 Leader
        |
        | calibrated joint positions
        v
Teleoperation Interface
        |
        +------------------------------+
        |                              |
        v                              v
Isaac Lab Sim Follower          Real SO-101 Follower
        |                              |
        | sim observations/actions      | real observations/actions
        v                              v
LeRobot Episode Dataset         LeRobot Episode Dataset
        |                              |
        +---------------+--------------+
                        |
                        v
              Mixed Sim+Real Dataset
                        |
                        v
        Behavior Cloning / VLA Post-Training
                        |
                        v
        Closed-Loop Evaluation in Sim and Real
```

### Current Isaac Lab Environment Architecture

The current local sim environment is built around Isaac Lab's config-driven design:

- `ArticulationCfg`: robot asset, USD path, initial state, actuator properties, root fixation.
- `InteractiveSceneCfg`: robot, table/workspace objects, cameras, lights, markers, rack/cup/task objects.
- `ManagerBasedRLEnvCfg`: high-level environment definition connecting scene, observations, actions, events, rewards, and terminations.
- `ObservationGroupCfg`: separates policy observations and visual observations.
- `ObservationTermCfg`: declares each observation function and its `SceneEntityCfg`.
- `EventTermCfg`: reset-time randomization and setup logic.
- `TiledCameraCfg`: GPU camera sensor used for policy-facing visual observations.
- `SceneEntityCfg`: symbolic reference from observations/events to named scene entities.

The key Isaac Lab concept to explain is that task behavior is composed declaratively through config objects. Instead of writing one monolithic `step()` function, the environment is assembled from managers: scene entities, action terms, observation terms, event terms, reward terms, and termination terms.

### Target Observation Schema

For future imitation learning and VLA evaluation, the important observations are:

- Joint positions or joint position deltas.
- Wrist/ego RGB image.
- External/front RGB image.
- Optional depth and segmentation in sim for augmentation or diagnostics.
- Language instruction, e.g. "Pick up the vial and place it in the rack."

The real and sim schemas must align before training. If a policy expects `wrist` and `front`, then sim keys like `ego` and `external_D455` must be renamed consistently.

### Target Action Schema

The SO-101 task uses joint-space actions rather than Cartesian end-effector deltas:

- `Rotation`
- `Pitch`
- `Elbow`
- `Wrist_Pitch`
- `Wrist_Roll`
- `Jaw`

In LeRobot/GR00T language this maps to shoulder pan/lift, elbow flex, wrist flex/roll, and gripper/jaw. A good interview answer should emphasize that action-space consistency is just as important as camera consistency. If sim action scaling, joint order, or offset convention differs from real, the dataset is not directly compatible.

## Learning From Demonstration Via Teleoperation

This is the planned data collection path and the part of the project that directly connects to "learning from demonstration via tele-operation."

### Why Teleoperation

Teleoperation gives supervised trajectories for tasks that are hard to reward-shape. For contact-rich manipulation like picking a vial and placing it in a rack, sparse rewards are possible but inefficient; human demonstrations encode grasp approach, contact timing, placement alignment, and recovery behaviors.

### Target Leader-Follower Setup

The leader arm acts as a low-cost kinesthetic input device. The follower is either:

- the simulated SO-101 articulation in Isaac Lab, or
- the physical SO-101 robot controlled through LeRobot.

The key calibration dependency is that leader and follower joint ranges and zero offsets must match. Bad calibration shows up as systematic pose mismatch, unsafe startup motion, or invalid recorded action labels.

### Demonstration Quality Criteria

High-quality demos should be:

- smooth and deliberate,
- successful,
- recorded only during the actual task execution,
- collected while watching only policy-visible cameras,
- diverse across object poses and approach paths.

The subtle point: if I teleoperate by looking at the real robot directly or using a privileged simulator viewport, I inject information into the actions that the policy will not have at inference time. That creates a covariate mismatch between demonstrator and learned policy.

## Sim-To-Real Gap: Taxonomy

### Perception Gap

- Real camera noise, exposure, motion blur, compression, rolling shutter.
- Lens distortion and focus differences.
- Camera extrinsic mismatch between sim and physical mount.
- Lighting and material mismatch.
- Background clutter and cable visibility.

### Actuation Gap

- Servo backlash.
- Motor saturation.
- Latency between command and motion.
- Calibration offset.
- Unmodeled compliance.
- Gearbox/friction effects.
- Payload-dependent dynamics.

### Contact/Physics Gap

- Object friction coefficients.
- Restitution/contact softness.
- Gripper-object contact patch geometry.
- Rack/vial geometry mismatch.
- Tolerances from 3D printed or assembled parts.

### Asset Gap

- URDF/MJCF/USD conversion errors.
- Incorrect inertial tensors.
- Simplified collision meshes.
- Wrong joint axes, limits, damping, or friction.
- Missing cables/mounts/extra camera mass.

## Domain Randomization

Domain randomization is the first sim-to-real strategy in the workshop. In this project it is planned after the base sim/real environment is aligned. The core idea is not to make simulation perfectly match reality; it is to train over a distribution broad enough that the real world is inside that distribution.

### What Gets Randomized In The Workshop Reference

In the workshop-style SO-101 task:

- object poses,
- rack pose,
- vial pre-placement,
- light exposure,
- color temperature,
- HDRI / environment map,
- robot material/color,
- mat orientation,
- external camera pose,
- camera focal length.

### Isaac Lab Implementation Pattern

In the workshop, domain randomization is implemented through reset events:

```python
reset_camera_external_pose = EventTerm(
    func=randomize_camera_pose,
    mode="reset",
    params={
        "prim_path_pattern": "{ENV_REGEX_NS}/LightStudio/LightBox/camera_mount",
        "pos_range": {"x": (-0.02, 0.02), "y": (-0.02, 0.02), "z": (-0.01, 0.01)},
        "rot_range": {"roll": (-0.05, 0.05), "pitch": (-0.05, 0.05), "yaw": (-0.05, 0.05)},
    },
)
```

The important Isaac Lab terminology is `EventTermCfg` with `mode="reset"`. Each environment reset samples a new configuration and writes it into the sim through scene entities or USD prim attributes.

### Technical Tradeoff

Too little randomization leads to overfitting to clean sim. Too much randomization creates unrealistic samples and can make the task harder than necessary. The right range should be based on measured real variation when possible: camera mount tolerance, lighting range, object placement range, friction uncertainty, and actuator uncertainty.

## Co-Training With Sim And Real Data

Co-training is the planned training strategy once sim and real demonstrations exist. It combines abundant simulation data with limited real demonstrations.

The workshop recipe references a small amount of real data, e.g. 5 real episodes, mixed with 70-100 sim episodes. The exact numbers are not universal; the principle is that real data is expensive but high-fidelity, while sim data is cheap but approximate.

### Why It Should Work

- Sim data teaches task structure and broad visual/action coverage.
- Real data anchors the distribution to actual camera appearance and robot dynamics.
- Mixed training reduces the residual gap that domain randomization alone cannot cover.

### Dataset Compatibility Requirements

The mixed dataset must have:

- same feature names,
- same image resolution,
- same camera order/semantics,
- same joint ordering,
- same action scaling,
- same language task labels,
- compatible control frequency and action horizon.

### Interview-Level Framing After Data Collection

"The way I am approaching this is to treat sim and real as two domains of the same supervised learning problem. The first hard part is not training; it is enforcing a common embodiment schema: camera naming, image resolution, joint order, action convention, and episode semantics. Once those are aligned, sim+real co-training becomes a practical way to trade off scale and fidelity."

## GR00T / VLA Policy Discussion

GR00T is a vision-language-action model family for robot foundation policies. I have not trained GR00T for this custom setup yet. For this project, the useful conceptual model is:

```text
camera frames + language instruction + robot state
        |
        v
vision-language backbone / fusion
        |
        v
action decoder
        |
        v
chunk of future joint actions
```

### Action Chunking

The policy can predict an action horizon, e.g. 16 future actions. This improves temporal smoothness and reduces the need to run a large VLA every control tick. The tradeoff is reactivity:

- shorter horizon: more reactive, potentially less smooth;
- longer horizon: smoother, but slower correction after perception or contact error.

### Why VLA Instead Of Classical RL Only

For this kind of tabletop manipulation, the VLA setup can leverage pretrained visual-language representations, language-conditioned task specification, and demonstration data. Classical RL is still useful, but exploration in contact-rich manipulation with sparse success signals can be expensive.

The strongest framing is not "VLA replaces RL." It is "VLA/behavior cloning gives a strong imitation prior; RL or residual correction can later improve robustness or optimize task-specific success."

## Cosmos Augmentation

Cosmos is NVIDIA's world foundation model family for physical AI. In the SO-101 workshop, Cosmos is used as a dataset augmentation strategy after DR and co-training. In my current project this is a future direction, not something already implemented.

### Difference From Domain Randomization

Domain randomization varies parameters explicitly represented in the simulator:

- light intensity,
- camera pose,
- object pose,
- textures/materials,
- robot color.

Cosmos-style augmentation modifies demonstration videos using a generative world model:

- photorealistic lighting/background variations,
- altered textures and visual conditions,
- plausible visual changes while preserving task structure,
- optional control signals such as depth, edges, segmentation, or visibility masks.

### How To Explain It Carefully

Cosmos augmentation is not a replacement for physics simulation. It is a way to expand visual diversity in the dataset, especially for perception-heavy policies, without requiring every visual variant to be manually authored in USD or physically collected on hardware.

Good caveat for Kelly:

"I would treat Cosmos-generated data as visual-domain augmentation and validate it carefully, because policy learning can be sensitive to whether augmented videos preserve action-observation consistency. If the augmentation changes object geometry or contact timing in a way that conflicts with the recorded action labels, it can harm training."

## SAGE And GapONet

SAGE stands for Sim-to-Real Actuation Gap Estimation. It is about measuring and closing the actuation side of the sim-to-real gap. In my current project this is a technique I want to understand and potentially apply after I have paired sim/real trajectories.

### SAGE Workflow

```text
motion/action sequence
        |
        +-------------------+
        |                   |
        v                   v
real robot rollout     sim rollout
        |                   |
        v                   v
real joint traces      sim joint traces
        |                   |
        +---------+---------+
                  |
                  v
       per-joint gap analysis
                  |
                  v
 parameter tuning or learned gap model
```

SAGE compares paired sim and real trajectories for the same commanded motion. The output is a quantitative view of where the gap is largest: position error, velocity error, torque/effort error if available, and joint-specific bias/delay/backlash effects.

### GapONet

GapONet is a learned gap-bridging model. The useful mental model:

```text
policy intended action
        |
        v
GapONet compensation
        |
        v
robot command that better produces intended motion
```

Or, for sim fidelity:

```text
commanded action sequence -> learned actual resulting motion model
```

### How This Applies To SO-101

The SO-101 uses low-cost servos, so backlash and compliance can be significant. That makes it a good candidate for:

- measuring joint-level lag and hysteresis,
- comparing sim replay against real encoder traces,
- deciding whether simple parameter tuning is enough,
- adding a learned residual/gap model if the error is nonlinear.

### Interview-Level Statement

"I see SAGE as moving sim-to-real from anecdotal failure analysis to measured system identification. Instead of saying 'the sim is off,' I can collect paired trajectories, quantify which joints contribute most to the gap, then decide whether to tune actuator parameters, improve inertials/collisions, or use a learned compensation model like GapONet."

## Newton Simulation

Newton is NVIDIA/Google DeepMind/Disney Research's open-source, GPU-accelerated, extensible physics engine built on NVIDIA Warp and OpenUSD, managed by the Linux Foundation. NVIDIA describes it as compatible with robot learning frameworks including MuJoCo Playground and Isaac Lab.

### Why Newton Matters For Isaac Lab

For an Isaac Lab role, the relevant points are:

- Newton is positioned as a next-generation physics backend for robotics.
- It is built on Warp, which supports GPU-accelerated differentiable computation patterns.
- It uses OpenUSD, aligning with the Isaac asset ecosystem.
- It opens the door to scalable and potentially more data-efficient or gradient-based robot learning workflows.

### How To Connect To My Experience

My relevant experience:

- I have authored Isaac Lab environments and assets.
- I have converted URDF to USD and debugged the robot asset pipeline.
- I have trained PPO policies in Isaac Lab.
- I have used MuJoCo solver concepts for IK on a 21-DoF hand.

Good interview phrasing:

"I have not contributed to Newton itself, but the parts of my experience that transfer are asset ingestion, solver-interface thinking, and environment validation. I would approach Newton integration by first preserving the Isaac Lab task abstraction: the same `ArticulationCfg`, observations, actions, resets, and benchmarks should be runnable across physics backends where possible. Then I would compare stability, throughput, contact behavior, and policy performance under controlled benchmarks."

### Questions To Ask Kelly

- "For Newton integration, where do you see the main abstraction boundary in Isaac Lab: asset import, articulation API, contact reporting, or the simulation context?"
- "How are you thinking about maintaining backend-agnostic task definitions while still exposing Newton-specific capabilities?"
- "Are current priorities more around feature parity with PhysX, differentiability, performance, or coverage of difficult robotics contacts?"

## Scalable Perception-In-The-Loop RL

This role mentions scalable perception-in-the-loop reinforcement learning. For this project, the connection is that the policy uses camera observations, not privileged simulator state.

### Difference From State-Based RL

State-based RL:

- observes object poses, joint states, sometimes privileged ground truth;
- trains faster;
- may not transfer directly if the real robot cannot observe those states.

Perception-in-the-loop RL:

- observes rendered camera images, depth, segmentation, or point clouds;
- includes rendering/sensor cost in the loop;
- more realistic for deployment;
- harder to scale because visual observations are high-bandwidth.

### Scaling Concerns

- GPU memory pressure from image observations.
- Rendering throughput.
- Sensor update frequency versus control frequency.
- Data transfer overhead from GPU tensors to CPU or recorder.
- Vectorized environment count versus camera resolution.
- Profiling simulation, rendering, policy inference, and logging separately.

### Connection To My Resume

The TensorRT/ONNX depth-estimation optimization is relevant here. It shows that I care about perception latency, inference throughput, and deployment performance. In perception-in-the-loop systems, the bottleneck is often not only physics; it can be rendering, model inference, data marshaling, video encoding, or CPU-GPU synchronization.

## Asset Pipeline And Physical Fidelity

This maps directly to the job requirement:

"Build and improve the robot asset pipeline, importing URDF/MJCF models, authoring new environments, and validating physical fidelity against real-world hardware."

### Asset Pipeline Concepts

- URDF/MJCF describe robot kinematics/dynamics, joints, links, inertials, collisions, and visuals.
- USD is the scene representation used in Isaac Sim/Isaac Lab.
- Conversion is not purely syntactic; physical fidelity can degrade if inertials, joint axes, limits, mimic joints, collision approximations, or actuator models are wrong.

### Validation Checklist

- Joint axes match real motion.
- Joint limits match calibrated hardware range.
- Link dimensions and collision meshes approximate real contact surfaces.
- Inertial tensors are reasonable, not default or nonsensical.
- Actuator stiffness/damping/effort limits match observed behavior.
- Camera prims have correct extrinsics and intrinsics.
- Object mass/friction parameters match manipulation behavior.
- Reset states are safe and reproducible.

### My Experience To Mention

- Converted a custom arm from URDF to USD.
- Authored a drawer-opening Isaac Lab task.
- Trained PPO in Isaac Lab for drawer manipulation.
- Currently aligning the SO-101 USD, wrist/ego camera, and real camera setup against the workshop.

## Benchmarking, Profiling, And Cloud Scaling

For the "scale training massively in the cloud" requirement, the credible discussion points are:

### Metrics

- simulation steps per second,
- environment steps per second,
- policy updates per second,
- GPU utilization,
- CPU utilization,
- rendering frame time,
- physics step time,
- dataloader throughput,
- memory bandwidth and VRAM usage,
- rollout storage overhead,
- success rate versus wall-clock time.

### Profiling Targets

- PhysX/Newton simulation step.
- RTX rendering / camera sensor updates.
- PyTorch forward/backward.
- CPU-GPU synchronization points.
- video encoding / dataset recording.
- environment reset overhead.
- Python manager overhead.

### Good Answer

"For large-scale training I would separate the bottlenecks: physics, rendering, policy inference/training, and logging. In Isaac Lab, the vectorized environment abstraction gives scale, but perception-in-the-loop tasks change the bottleneck because camera rendering and tensor movement become first-class costs. I would benchmark with and without cameras, vary resolution and sensor update period, and profile GPU traces before optimizing."

## Likely Interview Questions And Strong Answers

### "What exactly did you do in Isaac Lab?"

I authored and modified task environments using Isaac Lab's config system. I worked with `ArticulationCfg` for robot assets, `InteractiveSceneCfg` for scene composition, `ManagerBasedRLEnvCfg` for environment wiring, and manager terms for observations, actions, and reset events. I also worked on camera sensor placement using `TiledCameraCfg`, and aligned an SO-101 ego camera with the official workshop setup.

### "Why use sim data if real data is what matters?"

Sim data is scalable, safe, and controllable. It lets me cover object poses, lighting, and failure conditions that are expensive to collect on hardware. But sim data is approximate, so I use real data to anchor the policy to real sensor and actuator distributions. The goal is not sim-only purity; it is the best tradeoff between scale and fidelity.

### "What is the biggest sim-to-real risk in your setup?"

For SO-101, I would separate perception and actuation. Perception risks are camera extrinsics, lighting, and visual domain shift. Actuation risks are servo backlash, calibration offsets, latency, and contact behavior. The wrist/ego camera alignment is especially important because the policy's grasp behavior is tightly coupled to that viewpoint.

### "How would you know whether a failure is perception or actuation?"

I would log synchronized camera frames, joint targets, joint states, and task events. If visual localization is wrong before motion starts, it is likely perception. If the policy selects a reasonable target but the arm undershoots, overshoots, or shows repeatable joint-dependent error, it is likely actuation. Paired sim-real trajectory replay and SAGE-style analysis would make that quantitative.

### "What would you improve next?"

I would add a more rigorous calibration/validation loop:

- verify camera extrinsics with AprilTag or checkerboard,
- collect paired sim-real joint trajectories,
- quantify per-joint tracking error,
- tune actuator and contact parameters,
- evaluate sim-only, sim+real, and augmented policies on the same real task success metric.

### "How does this connect to Isaac Lab open source?"

The project exercises exactly the areas Isaac Lab cares about: environment authoring, asset fidelity, teleoperation-based demonstration collection, camera sensors, domain randomization, vectorized training/evaluation, and real-hardware deployment. The kind of contribution I could make is not just a new task, but better examples, validation utilities, camera/asset pipeline documentation, or benchmark scripts for sim-to-real workflows.

## Things To Be Careful Not To Overclaim

- Do not say I trained GR00T from scratch unless I actually did.
- Do not say Cosmos physically simulates the robot; describe it as world-model/video augmentation for visual diversity.
- Do not say the Logitech C270 is the same as the workshop camera unless the resolution and mount are aligned. Say I matched the policy-facing schema to the workshop: `640x480`, `wrist/front` camera semantics.
- Do not say the camera is on `wrist` in the official workshop config. The config path is `Robot/gripper/gripper_cam`; semantically it is the wrist/gripper ego camera.
- Do not claim Newton experience beyond what I have. Say I understand the integration concerns and have relevant Isaac Lab/MuJoCo/asset experience.
- Do not claim sim-to-real success until I have actually deployed and measured the policy on the real arm.

## Source References

- Local notes: `/home/hassaan/robotics/isaac_tuts/Knowledge/sim2real.md`
- Local workshop repo: `/home/hassaan/robotics/isaac_tuts/Sim-to-Real-SO-101-Workshop`
- Official NVIDIA SO-101 learning path: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html
- Isaac Lab overview: https://developer.nvidia.com/isaac/lab
- Newton Physics: https://developer.nvidia.com/newton-physics
- Isaac Lab research page: https://research.nvidia.com/publication/2025-09_isaac-lab-gpu-accelerated-simulation-framework-multi-modal-robot-learning
- GR00T SO-101 module: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/10-groot.html
- Cosmos augmentation module: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/14-strategy3-cosmos.html
- SAGE + GapONet module: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/15-strategy4-sage.html
