     

Sim-to-Real Strategy 1: Domain Randomization

Hands-on. You’ll need the teleop-docker container, the SO-101 teleop arm, and an NVIDIA GPU for Isaac Lab simulation.

Now that you’ve done teleoperation on a real robot, let’s try it in simulation with Isaac Lab.

In this module, you’ll use the teleop arm to drive a simulated SO-101 robot, allowing us to collect demonstrations with Isaac Lab.

Because it’s simulation, we have control of the world and can manipulate it in interesting ways, like using domain randomization to ensure our dataset will be sufficiently varied.
Teleoperation in Simulation

Teleoperation in Simulation
Learning Objectives

By the end of this session, you’ll be able to:

    Explain domain randomization and why it improves sim-to-real transfer

    Collect demonstration data through teleoperation, in simulation

    Apply domain randomization to augment demonstrations

What Is Domain Randomization?

Domain randomization (DR) is a sim-to-real strategy based on this idea: instead of making simulation perfectly match reality, randomize simulation parameters during training so the policy becomes robust to any value in the range, including real-world values.

Put in simple terms: think about how you might learn to catch a ball.

If you always catch it in the same pose, you might not learn to reach and catch the ball, or hold the glove in different orientations. By varying where the ball is thrown to you when you practice, you will likely learn a better “policy” for catching the ball.

Domain Randomization Example

Teleoperation: Collecting Human Demonstrations

In this lesson we’ll apply domain randomization during teleoperation. We will use these to perform a kind of robot learning known as imitation learning.

Hands-On: Collecting Demonstrations

Here is a video of the task:
Teleoperation example in the LeRobot Dataset Visualizer

Example: Teleoperation of SO-101, being replayed through the LeRobot Dataset Visualizer.

On top are the observations from cameras, and below are the positions of robot joints.

See this dataset on Hugging Face, using the Dataset Visualizer

Tip

Having trouble with cameras or robot connection? See the Troubleshooting Guide.
Launch Simulation Environment (Docker)

    If you still have the teleop-docker container’s terminal open from the last module, you can skip this step. If not, expand the dropdown and run the command.

Practice Teleoperation in Simulation

Let’s launch the simulation environment to practice teleoperation without recording.

This is a good way to get familiar with the teleop controls and camera views before collecting data.

    (Optional) Run this quick sanity check to make sure your environment variables are set correctly.

echo "Teleop port is ${TELEOP_PORT} with id ${TELEOP_ID}"

If they aren’t set, find the ports using lerobot-find-port and assign them again:

    Move the teleop arm to a packed position. If the robot is in a strange starting position, it may run into items in simulation on startup.

    Run the following command to open Isaac Lab, with our pre-configured simulation environment. You can choose between two options: Lerobot-So101-Teleop-Vials-To-Rack which has no domain randomization or Lerobot-So101-Teleop-Vials-To-Rack-DR, which has domain randomization enabled.

lerobot_agent --task Lerobot-So101-Teleop-Vials-To-Rack-DR

This will launch Isaac Sim and load the training environment.

Note

The first time this launches, it will take about 2 minutes to load.

If it gets stuck, check the console for errors. It’s likely the robot isn’t fully connected. Power cycle the robot (plug/replug power on the back) if you have issues.

    Keep Isaac Lab open for the next step.

Setup Cameras

We need our simulation to show us the same camera views our AI model will use.

When doing teleoperation for training VLAs, it’s crucial that we use the same camera views for teleoperation that the model will use for autonomous operation.

Otherwise, we may introduce biases or advantages the model won’t have.

Important

Only look through the gripper and external cameras when teleoperating.

When looking at the scene with your own eyes, or other cameras in the simulation scene, you may introduce perceptual affordances that the model will not have access to during inference.

The policy will only see what the cameras see. Train yourself to rely solely on the camera views displayed on your screen. This ensures your demonstrations reflect what the policy can actually perceive.

By default you’ll just see the general perspective camera. Let’s fix that.

    Go to Window > Viewports, and enable both viewport Viewport 1 and Viewport 2 so we can see two cameras rendered at once.

    In one viewport, go to the camera menu, and choose the gripper_cam.

    In the other viewport, go to the camera menu, and choose the Camera_OmniVision_9782_Color camera.

For each viewport, set the aspect ratio to 4:3 to match the cameras.

    Go to the settings menu in the viewport.

    Under Viewport > Aspect Ratio on the right side you’ll see 16:9. Change it to 4:3.

    Now try teleoperating, and take some time to get familiar with the teleop controls and camera views before collecting data in episodic format.

    Press R to reset the environment with domain randomization. If it doesn’t work, click on the viewport to give the application focus, and try again.

    Notice in the terminal, you will see status updates about the subtask success, such as when the vials are grasped or placed in the rack.

Controls (click in Viewport to use these commands)

    Press R to reset the environment (also stops recording)

    Episodes are queued for processing while you continue working

    When finished, stop Isaac Lab by pressing CTRL+C in the terminal.

Start Recording Demonstrations

When ready to collect data, we’ll add a few extra arguments for where to save the data we collect.

Before launching the teleop agent, set your Hugging Face username as an environment variable. This is used to organize your datasets in a unique namespace.

If you don’t have one, or don’t want to login, you can make up a username for local data collection.

    Run this, replacing your-hf-username with your actual Hugging Face username:

export HF_USER=your-hf-username

You only need to do this once per terminal session before running the following commands. Feel free to use a made up username if you don’t want to login and upload your demos.
Overall Flow

For each episode we will:

    Reset the environment: Press R to randomize vial positions, rack position, camera poses, and lighting. You can do this every episode, or every few episodes.

    Record: Press S to start recording.

    Execute: Immediately begin the demonstration. For each episode, perform one pick-and-place operation, which means picking up one vial and placing it into one open slot on the rack.

    Complete: Press S to stop recording

How many demonstrations should you collect? If you’re going to train your own policy, try collecting at least 70 demonstrations based on our experience. More could be better. If you’re just exploring, you can collect less.

Demonstration Quality Guidelines:

Good demonstrations:

    Smooth, deliberate motions

    Clear grasp contact with vial

    Successful placement in rack

Avoid:

    Jerky, hesitant motions

    Missed grasps or drops

    Including more than the actual task execution

Recording Demonstrations

    Launch recording session. This will be just like the environment before, but we have additional controls to cancel, start recording, and stop recording.

lerobot_agent --task Lerobot-So101-Teleop-Vials-To-Rack-DR \
    --repo_id ${HF_USER}/so101_teleop_vials \
    --repo_root $(pwd)/datasets/so101_teleop_vials \
    --task_name "Pick up the vial and place it in the rack"

    Set up the window, viewports, and cameras (same as in Practice Teleoperation):

        Window > Viewport: Enable both viewports so you see two camera views at once.

        In one viewport, open the camera menu and choose gripper_cam.

        In the other viewport, open the camera menu and choose Camera_OmniVision_9782_Color.

        For each viewport: open the viewport settings, go to Viewport > Aspect Ratio, and set to 4:3 (instead of 16:9).

    Recording Controls: Isaac Sim viewport must be in “focus” (click the app’s UI)

    Press S to start/stop recording an episode

    Press C to cancel the current recording (useful for mistakes)

    Press R to reset the environment (also stops recording)

    Completed episodes are queued for processing so you can continue working.

Example terminal output:

[INFO]: Started recording.
[INFO]: Stopped recording.
[INFO]: Copy episode to CPU...
[INFO]: Episode added to queue.
[INFO]: [ASYNC] received episode from queue...
[INFO]: Cleared buffers

    Repeat the recording process until you have collected the desired number of demonstrations.

    When completely finished with all demonstrations, make sure you see the message [INFO]: No More episodes in queue. Wait a few seconds if you don’t see it. This means all the episodes have been processed and saved.

    Stop Isaac Lab by pressing CTRL+C in the terminal.

Review Collected Data

    Optional: if you recorded a demonstration, use the LeRobot dataset visualizer to review your recorded episodes:

lerobot-dataset-viz \
    --repo-id ${HF_USER}/so101_teleop_vials \
    --root $(pwd)/datasets/so101_teleop_vials \
    --episode-index 0

Change --episode-index to view different episodes.
Domain Randomization in Simulation

To maximize domain randomization benefits, collect demonstrations across multiple sessions. The environment randomizes conditions between episodes automatically.

Let’s take a look at the code.
Code Tour: Domain Randomization Implementation

The Isaac Lab environment implements DR through reset event handlers. Here’s a tour of the key randomization methods from the teleop environment codebase.

In the workshop repo, these randomizations are applied in DR task variants (for example, Lerobot-So101-Teleop-Vials-To-Rack-DR). The base Lerobot-So101-Teleop-Vials-To-Rack task keeps the sky light off and uses a fixed orange robot color.

Lighting Randomization (randomize_sky_light)

File: sim_to_real_so101/source/sim_to_real_so101/mdp/resets.py

Randomizes the environment’s dome light on each reset—exposure, color temperature, and HDRI texture:

def randomize_sky_light(
    env,
    env_ids: torch.Tensor | None,
    exposure_range: tuple[float, float],
    temperature_range: tuple[float, float],
    textures_root: str,
    asset_cfg: SceneEntityCfg = None,
):
    # Sample random exposure and color temperature
    exposure = math_utils.sample_uniform(*exposure_range, (1,), device="cpu").item()
    temperature = math_utils.sample_uniform(*temperature_range, (1,), device="cpu").item()

    # Select random HDRI texture from available options
    textures = glob.glob(os.path.join(textures_root, "*.exr"))
    texture = textures[torch.randint(0, len(textures), (1,)).item()]

    # Apply to the dome light
    prim.GetAttribute("inputs:exposure").Set(exposure)
    prim.GetAttribute("inputs:colorTemperature").Set(temperature)
    prim.GetAttribute("inputs:texture:file").Set(Sdf.AssetPath(texture))

Camera Pose Randomization (randomize_camera_pose)

File: sim_to_real_so101/source/sim_to_real_so101/mdp/resets.py

Adds small position and rotation offsets to the external camera:

def randomize_camera_pose(
    env,
    env_ids: torch.Tensor | None,
    prim_path_pattern: str,
    pos_range: dict[str, tuple[float, float]] = None,  # e.g., {"x": (-0.02, 0.02)}
    rot_range: dict[str, tuple[float, float]] = None,  # e.g., {"pitch": (-0.05, 0.05)}
):
    # Sample random offsets relative to USD default pose
    x = base_pos[0] + math_utils.sample_uniform(*pos_range.get("x", (0, 0)), (1,)).item()
    y = base_pos[1] + math_utils.sample_uniform(*pos_range.get("y", (0, 0)), (1,)).item()
    z = base_pos[2] + math_utils.sample_uniform(*pos_range.get("z", (0, 0)), (1,)).item()
    
    # Combine base quaternion with random delta rotation
    delta_quat = math_utils.quat_from_euler_xyz(roll, pitch, yaw)
    final_quat = math_utils.quat_mul(base_quat_tensor, delta_quat)

Object Pose Randomization (reset_vials_rack)

File: sim_to_real_so101/source/sim_to_real_so101/mdp/resets.py

Randomizes vial and rack positions, with probability of pre-placing vials in slots:

def reset_vials_rack(
    env,
    env_ids: torch.Tensor,
    vials: list[str],
    rack: str,
    rack_pose_range: dict[str, tuple[float, float]],
    pose_range: dict[str, tuple[float, float]],
    rack_placement_prob: float = 0.33,
):
    # Randomize rack position and orientation
    new_rack_positions, new_rack_orientations = random_asset_pose(
        env, env_ids, rack, rack_pose_range, {}
    )
    
    # With some probability, pre-place a vial in a random slot
    if torch.rand(1).item() < rack_placement_prob:
        vial_idx = torch.randint(0, len(vial_objects), (1,)).item()
        slot_idx = torch.randint(0, total_slots, (1,)).item()
        # Transform slot position from rack local frame to world frame
        slot_position, slot_orientation = math_utils.combine_frame_transforms(
            new_rack_positions, new_rack_orientations, 
            slot_position_local, slot_orientation_local
        )
        vial.write_root_pose_to_sim(slot_pose, env_ids=env_ids)

Wiring It Up: Event Configuration

File: sim_to_real_so101/source/sim_to_real_so101/tasks/task_env_cfg.py

These randomization functions are registered as reset events in the environment config:

@configclass
class TaskEventCfg(EventCfg):
    
    reset_sky_light = EventTerm(
        func=randomize_sky_light,
        mode="reset",
        params={
            "exposure_range": (-4.0, 3.0),
            "temperature_range": (2500.0, 9500.0),
            "textures_root": f"{assets_path}/hdri",
            "asset_cfg": SceneEntityCfg("sky_light"),
        },
    )

    reset_camera_external_pose = EventTerm(
        func=randomize_camera_pose,
        mode="reset",
        params={
            "prim_path_pattern": "{ENV_REGEX_NS}/LightStudio/LightBox/camera_mount",
            "pos_range": {"x": (-0.02, 0.02), "y": (-0.02, 0.02), "z": (-0.01, 0.01)},
            "rot_range": {"roll": (-0.05, 0.05), "pitch": (-0.05, 0.05), "yaw": (-0.05, 0.05)},
        },
    )

Every time an episode resets, Isaac Lab calls each registered EventTerm with mode="reset", applying fresh randomization.

For this workshop migration, the mat yaw randomization range is tightened to (-0.1, 0.1) in DR task configs.

Tip

You can experiment with domain randomization by changing the ranges or which resets run. In task_env_cfg.py, the TaskEventCfg class registers each randomization as an EventTerm with a params dict. For example, adjust exposure_range or temperature_range in reset_sky_light, or pos_range / rot_range in reset_camera_external_pose, to widen or narrow variation. Commenting out an EventTerm disables that randomization.

Note where you’re editing - if inside the container, changes might be lost on restart.
Subtask Rating

Notice in the terminal output, that our simulation can detect when the vial is grasped, and when it is placed in the rack.

[GRASP] Vial grasped in env(s): [0]
[RELEASE] Vial released in env(s): [0]
[RACK] vial_2 placed in rack in env(s): [0]

This strategy is useful when we start policy inference, because we can automatically score how well the policy is performing.
Sim vs. Real Teleoperation Comparison

Aspect
	

Simulation
	

Real Robot

Domain randomization
	

Automatic
	

Manual, limited to what you can physically change in the environment

Data collection speed
	

Faster reset, parallel envs possible
	

Real-time only

Hardware wear
	

None
	

Accumulates over time

Visual diversity
	

Procedural generation
	

Requires manual variation

Physics accuracy
	

Approximated
	

Ground truth
When to Use Each

Use simulation when:

    Building initial dataset with DR

    Hardware is limited or shared

    Exploring task or policy variations quickly and safely

    Real environment isn’t ready, accessible, or during development

Use real robot when:

    Collecting high-quality ground truth

    Validating sim-trained policies

    Capturing real-world nuances (friction, lighting)

Key Takeaways

    Domain randomization makes policies robust by training on varied conditions

    Teleoperation captures human expertise in demonstration form

    Always teleoperate using only camera views—not your eyes

    DR augmentation multiplies your dataset with varied conditions

    Combined real demonstrations + DR augmentation is a powerful baseline

What’s Next?

With augmented demonstrations collected, learn how policies are trained and served. In the next session, Isaac GR00T: Vision-Language-Action Models, you’ll study VLAs and the GR00T architecture 

Isaac GR00T: Vision-Language-Action Models

Mostly theory with code examples. No additional hardware is required beyond a computer with the real-robot container built.

In this session, we’ll explore the VLA model called NVIDIA Isaac GR00T, how it works, and see examples of it in action.
Learning Objectives

By the end of this session, you’ll be able to:

    Explain what vision-language-action models are and why they’re powerful

    Describe the GR00T architecture and its components

    Understand how VLAs differ from traditional robot learning approaches

What Is GR00T?

NVIDIA Isaac GR00T is a research initiative and development platform for developing general-purpose robot foundation models and data pipelines to accelerate humanoid robotics research and development.

It provides:

    Pre-trained visual understanding from large-scale data

    Language-conditioned behavior for flexible task specification

    Action generation suitable for real-time robot control

In this course, we’ll use GR00T N1.6 models post-trained for the SO-101 robot.

Note

Training time in this course

GR00T post-training requires several hours on GPU hardware—longer than this course allows in a single sitting. We have pre-trained a set of policies on various datasets that you will use throughout the day. This lets you focus on understanding the workflow, evaluating results, and iterating on strategies rather than waiting for training jobs to complete.

The commands and scripts shown here are the same ones used to produce those policies, so you can replicate the process on your own hardware after you finish this learning path.
What’s New in GR00T N1.6

GR00T N1.6 represents a significant upgrade over N1.5, with improvements in both model architecture and data.

Architectural Changes:

Component
	

N1.5
	

N1.6

Base VLM
	

Standard
	

Cosmos-Reason-2B variant with flexible resolution

DiT layers
	

16
	

32 (2x larger)

Post-VLM adapter
	

4-layer transformer
	

Removed; unfreezes top 4 VLM layers

Action format
	

Absolute joint angles/EEF
	

State-relative action chunks
Case Study: Zero-Shot Transfer Improvement

GR00T has already released several iterations, each with significant improvements. Let’s look at an SO-101 case study as an example of how N1.6 translates to measurable real-world gains.

Task: Pick vials from a mat and place them on a rack (sim-only training data)
N1.5 vs N1.6 zero-shot transfer comparison

[Placeholder: Side-by-side comparison of N1.5 and N1.6 attempting the mat-to-rack task]

This demonstrates how foundation model improvements can reduce the sim-to-real gap even without task-specific real data.
What Is a Vision-Language-Action Model?

Vision-Language-Action (VLA) models are foundation models that take visual input and language instructions and output low-level or mid-level actions for an embodied agent, such as a robot.

Input: Camera image (1 or more) + "Pick up the red vial and place it in the rack"
Output: Sequence of joint positions/velocities to execute the task

Training Stages

VLAs are typically trained in stages:

    Large-scale pretraining: Internet-scale multimodal data (images, text, video) builds general visual and language understanding

    Supervised imitation/behavior cloning: Robot demonstrations teach the model to map observations to actions

    Optional reinforcement learning: Fine-tunes behavior through real-world interaction and feedback

Architecture Overview

VLA Model Architecture
Key Components

Vision Encoder: Processes camera images into rich feature representations

    Pre-trained on large image datasets (ImageNet, etc.)

    Understands objects, spatial relationships, affordances

Language Encoder: Processes task instructions

    Maps natural language to task embeddings

    Enables zero-shot generalization to new task descriptions

Cross-Modal Fusion: Combines vision and language

    Attention mechanisms to relate visual features to language

    Grounds language concepts in visual observations

Action Decoder: Generates robot actions

    Conditioned on fused visual-language features

    Outputs appropriate action representation (joint positions, velocities, etc.)

Action Space and Control
Action Representations

GR00T supports several action representations:

Joint Position Actions

    Direct control over robot configuration

    Requires learning full arm coordination

End-Effector Actions

    Inverse kinematics computes joint commands

    Abstracts away arm configuration

Action Chunking

    Predict multiple future actions at once

    Smoother execution, temporal consistency

In this course, we use joint position actions with action chunking.
Action Horizon Parameter

The action_horizon parameter controls how many future actions the model predicts at once. This is a critical hyperparameter that affects both training and deployment.

What it controls:

    Training: The model learns to predict action_horizon timesteps into the future

    Inference: The model outputs a chunk of action_horizon actions per forward pass

Trade-offs:

Horizon
	

Pros
	

Cons

Short (4-8)
	

More reactive, corrects quickly
	

Choppy motion, frequent replanning

Medium (16)
	

Balanced smoothness and reactivity
	

Good default for most tasks

Long (32+)
	

Very smooth trajectories
	

Slow to correct errors, may overshoot

Tip

Start with the default action_horizon=16. Only adjust if you observe specific issues: reduce if the robot overshoots targets, increase if motion is too jerky.
Example: GR00T in Action
Post-Training GR00T

set -x -e

export NUM_GPUS=1

DATASET_PATH= #set path to your model

# torchrun --nproc_per_node=$NUM_GPUS --master_port=29500 \
CUDA_VISIBLE_DEVICES=0 python \
    gr00t/experiment/launch_finetune.py \
    --base_model_path nvidia/GR00T-N1.6-3B \
    --dataset_path $DATASET_PATH \
    --modality_config_path examples/SO100/so100_config.py \
    --embodiment_tag NEW_EMBODIMENT \
    --num_gpus $NUM_GPUS \
    --output_dir /tmp/so100_finetune \
    --save_steps 1000 \
    --save_total_limit 5 \
    --max_steps 10000 \
    --warmup_ratio 0.05 \
    --weight_decay 1e-5 \
    --learning_rate 1e-4 \
    --use_wandb \
    --global_batch_size 32 \
    --color_jitter_params brightness 0.3 contrast 0.4 saturation 0.5 hue 0.08 \
    --dataloader_num_workers 4

Practical Considerations
Data Requirements

VLA training typically requires:

    50-200 demonstrations per task for basic competence

    Language annotations describing each demonstration

    Diverse conditions to enable generalization

Tip

Quality matters more than quantity. 50 high-quality, diverse demonstrations often outperform 500 redundant ones.
Compute Requirements

GR00T training benefits from:

    GPU memory: 24GB+ for full model training

    Training time: 2-8 hours depending on dataset size

    Inference: Real-time on modern GPUs (RTX 3080+)

Key Takeaways

    VLA models combine vision, language, and action in a unified architecture

    GR00T provides pre-trained components for accelerated learning

    Language conditioning enables flexible task specification

    Action chunking provides smooth, temporally consistent control

    Pre-trained vision encoders enable visual generalization

Resources

    NVIDIA Isaac GR00T GitHub — Source code, model weights, and documentation

    Cosmos Cookbook — Recipes and examples for Cosmos world foundation models

What’s Next?

Now that you understand VLAs conceptually, run policy evaluation in simulation. In the next session, Sim Evaluation, you’ll compare policies in sim using open-loop and closed-loop evaluation.

Sim Evaluation

In this session, you’ll run policy evaluation in simulation using the same GR00T-based setup you’ll use later on the real robot.
Learning Objectives

By the end of this session, you’ll be able to:

    Run policy evaluation in simulation using the GR00T server + client (Docker) setup

    Compare how policies trained with different data quantities and augmentation behave

    Identify common failure modes in simulation

What Policy Are We Going to Evaluate?

You’ll have the choice of either using policies we trained for you, or training your own. If you use ours, make sure the workspace is set up correctly and the robot is carefully calibrated.

Tip

To use GR00T with LeRobot, follow the official LeRobot GR00T documentation for setup and integration guides. GR00T N1.5 models are natively supported and can be evaluated directly within the LeRobot framework. For GR00T N1.6, integration into LeRobot is still in progress. In the meantime, you’ll need to run training and inference using the official Isaac GR00T repository or provided Docker images for the latest model features.

We used this dataset of 75 sim demonstrations. View it on Hugging Face with the dataset visualizer. This is a sim only dataset, meaning it was trained entirely in simulation, without any real-world data. Our first strategy is to rely solely on simulation and domain randomization.
Visualization of the SO-101 sim teleop vials-to-rack-left dataset

Sample episodes visualized from the sim-only demonstration dataset used for training evaluation policies.
Running Policy Evaluation in Simulation

Throughout this course, when we run evaluations there will be two terminals involved:

    The host terminal, where we will start the GR00T container and policy server

    The client terminal, where we will run the evaluation rollout and actually control the robot

For sim, the client is our simulator. For the real robot, our client is the robot itself.
Terminal 1 (real-robot container) — Start the GR00T policy server

    Open a new terminal window (CTRL+ALT+T).

    Run the docker real-robot container.

xhost +
docker run -it --rm --name real-robot --network host --privileged --gpus all \
    -e DISPLAY \
    -v /dev:/dev \
    -v /run/udev:/run/udev:ro \
    -v $HOME/.Xauthority:/root/.Xauthority \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/.cache/huggingface/lerobot/calibration:/root/.cache/huggingface/lerobot/calibration \
    -v ~/sim2real/models:/workspace/models \
    -v ~/sim2real/Sim-to-Real-SO-101-Workshop/docker/env:/root/env \
    -v ~/sim2real/Sim-to-Real-SO-101-Workshop/docker/real/scripts:/Isaac-GR00T/gr00t/eval/real_robot/SO100 \
    real-robot \
    /bin/bash

    Inside this container, run the following to set which model to evaluate.

export MODEL=aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left/checkpoint-10000

    Run the policy server with that model.

python Isaac-GR00T/gr00t/eval/run_gr00t_server.py \
    --model-path /workspace/models/$MODEL

    When you see Server is ready and listening on tcp://0.0.0.0:5555 the policy server is ready to accept connections.

Terminal 2 (teleop-docker container) — Evaluation rollout

    If you still have the teleop-docker container’s terminal open from the last module, you can skip this step. If not, expand the dropdown and run the command.

    This command will begin moving the robot in simulation, using an environment with less lighting variation to start.

lerobot_eval \
    --task Lerobot-So101-Teleop-Vials-To-Rack-Eval \
    --rename_map '{"external_D455": "front", "ego": "wrist"}' \
    --action_horizon 16 \
    --lang_instruction "Pick up the vial and place it in the yellow rack" \
    --rerun

This will launch both Isaac Sim, and Rerun.

Note

The --rerun flag is optional.

It adds Rerun into the loop for debugging, so you can see joint actions and the camera feeds while the policy is running. This lets you confirm the camera views are reasonable and the assignments are correct.

    (Alternatively) You can run the evaluation headlessly, meaning there is no Isaac Sim UI or Rerun visualization:

lerobot_eval \
    --task Lerobot-So101-Teleop-Vials-To-Rack-Eval \
    --rename_map '{"external_D455": "front", "ego": "wrist"}' \
    --action_horizon 16 \
    --lang_instruction "Pick up the vial and place it in the yellow rack" \
    --headless

Watching the Evaluation

Watch the terminal for evaluation of the model’s performance. The scene resets either after a timeout, or when the vial starts to enter the rack slots.

Depending on how much the vials roll around, and how dark the lighting is, expect the evaluation success rate to be between 50-70%.

Remember this dataset has a fairly low number of demonstrations (75 pick and place demos), so the policy may not be able to generalize as much as we’d ultimately need.
Visualization of the Evaluation rollout

Example output:

Rollout (ep 7, success: 66.7%):  33%|█████████████████████▉                                             | 131/400 [00:06<00:15][GRASP] Vial grasped in env(s): [0]
Rollout (ep 7, success: 66.7%):  70%|██████████████████████████████████████████████▉                    | 280/400 [00:14<00:06][RACK] vial_1 placed in rack in env(s): [0]
Rollout (ep 7, success: 66.7%):  70%|███████████████████████████████████████████████▏                   | 282/400 [00:14<00:06]
Rollout (ep 8, success: 71.4%):  34%|

Testing Against More Lighting Variation

We’ve preconfigured another environment with more lighting randomization. This is an example of how you can use simulation to stress test a policy against different conditions, by changing just a bit of code.

You can use that evaluation environment by running this command instead:

lerobot_eval \
    --task Lerobot-So101-Teleop-Vials-To-Rack-DR-Eval \
    --rename_map '{"external_D455": "front", "ego": "wrist"}' \
    --action_horizon 16 \
    --lang_instruction "Pick up the vial and place it in the yellow rack"

Cleanup

When you’re done trying model evaluations:

    In the teleop-docker container, press CTRL+C to stop Isaac Lab.

    In the same terminal, type exit and press Enter to exit the teleop-docker container.

    In the real-robot container, press CTRL+C to stop the policy server. You can leave this terminal open.

Tip

If you want to see which containers are running, you can run docker ps to list all containers.
Common Failure Modes

When observing evaluation runs, notice the failure modes. Remember that this policy was trained from a limited amount of data, only 75 demonstrations (~1 hour of teleoperation time for a seasoned operator).
Key Takeaways

    Policies trained on few demonstrations aren’t able to generalize

    Domain randomization is essential for robust policies

    More diverse training data beats more identical training data

    These sim-only policies provide a baseline for comparison when you run on the real robot

What’s Next?

Confirm your physical setup still matches Building the Workspace, then continue with Real Evaluation to run the same policy on the physical SO-101 and observe the sim-to-real gap.

Real Evaluation

In this session, you’ll run policy evaluation on the physical SO-101 robot using the same GR00T-based setup you used in simulation.

The client is now the real robot instead of the simulator!
Learning Objectives

By the end of this session, you’ll be able to:

    Run policy evaluation on the real robot using the GR00T server + client (Docker) setup

    Observe the sim-to-real gap firsthand

    Stop and restart the evaluation safely

What Policy Are We Running?

We use the same policy you evaluated in simulation. The exact MODEL (checkpoint path) is set in the commands below.
Running Policy Evaluation on the Real Robot

Throughout this course, when we run evaluations there will be two terminals involved:

    The host terminal, where we start the GR00T container and policy server

    The client terminal, where we run the evaluation rollout and actually control the robot

For sim, the client is our simulator. For the real robot, our client is the robot itself.
Terminal 1 (real-robot container) — Start the GR00T policy server

    Locate the terminal already running the real-robot container.

    Inside this container, run the following. This is where we choose which model to evaluate.

export MODEL=aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left/checkpoint-10000

    Run the policy server with that model.

python Isaac-GR00T/gr00t/eval/run_gr00t_server.py \
    --model-path /workspace/models/$MODEL

Terminal 2 (real-robot container) — Evaluation rollout

Open a second terminal. You will attach to the same real-robot container and run the robot client. This step assumes your robot has been calibrated already (likely you already did this).

    Attach a second terminal to the real-robot container.

docker exec -it real-robot /bin/bash

    Once inside the container, run the evaluation script:

python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py \
  --robot.type=so101_follower \
  --robot.port="$ROBOT_PORT" \
  --robot.id="$ROBOT_ID" \
  --robot.cameras="{
      wrist:  {type: opencv, index_or_path: $CAMERA_GRIPPER, width: 640, height: 480, fps: 30},
      front:  {type: opencv, index_or_path: $CAMERA_EXTERNAL, width: 640, height: 480, fps: 30}
  }" \
  --policy_host=localhost \
  --policy_port=5555 \
  --lang_instruction="Pick up the vial and place it in the yellow rack" \
  --rerun True

Note

The --rerun flag is optional.

It adds Rerun into the loop for debugging, so you can see joint actions and the camera feeds while the policy is running. This lets you confirm the camera views are reasonable and the assignments are correct.
Watching the Evaluation

Watch the robot and the terminal during execution. The policy will run until you stop it or it completes the evaluation. Watch closely but stay clear; note any unexpected behavior and be ready to intervene.

To stop the robot: Press CTRL+C in Terminal 2 (robot client). The policy server in Terminal 1 keeps running.

To run again: Simply run the command again python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py ... in Terminal 2

To switch model or fully restart:

    Stop both terminals’ commands (CTRL+C)

    Set MODEL environment variable to the model you want to evaluate

    Restart the commands for each terminal (model server, robot client)

Note

    At evaluation start, the robot will slowly rise to its initial pose, then enter into inference mode.

    At robot stop (CTRL+C), it will slowly drive itself back to its home pose.

Tip

Keep the policy server running between evaluation attempts. Only restart it if you want to load a different model checkpoint.
Common Failure Modes

When observing real evaluation runs, notice how perception and actuation differ from simulation. The same policy may miss grasps, overshoot, or behave differently under real lighting and dynamics. These differences are the sim-to-real gap you’ll address with the strategies in the modules that follow.
Key Takeaways

    Real robot evaluation uses the same GR00T server + client architecture as sim evaluation; only the client (robot vs. simulator) changes

    The gap between sim and real performance is often visible immediately—perception and actuation both matter

    Safe shutdown is CTRL+C in the robot client terminal first

What’s Next?

Continue with Strategy 2: Co-Training With Real Data, where you’ll deploy policies trained on mixed simulation and real data to the physical robot.

Sim-to-Real Strategy 2: Co-Training With Real Data

In this session, you’ll learn the theory of co-training approaches and then deploy your first policy to the physical robot.
Learning Objectives

By the end of this session, you’ll be able to:

    Explain co-training strategies for mixing sim and real data

    Deploy trained policies safely to the physical SO-101 robot

    Observe and document real-world policy behavior

    Identify initial sim-to-real gap symptoms

What Is Co-Training?

Co-training combines data from multiple sources—simulation and real-world—during policy training.

In our examples, we’ll show the power of combining a small amount of real demonstration data (5 episodes) with a much larger set of simulation demonstrations (70-100).

You’ll have a chance to experience policies trained with various mixes of data.
Physical demonstration

Physical demonstration of the task with teleoperation.

Tip

View a dataset of real-only demonstrations using the Hugging Face Dataset Visualizer here.
The Data Challenge

Data Source
	

Quantity
	

Quality
	

Reality Match

Simulation
	

Abundant
	

Consistent
	

Approximate

Real teleop
	

Limited
	

Variable
	

Exact

Neither source alone is ideal:

    Sim-only: Abundant but doesn’t match real-world distribution

    Real-only: Matches reality but quantity is limited

Co-training leverages both.
(Optional) Collecting Real Demonstrations With LeRobot

We will provide both a real dataset and a post-trained GR00T model trained on this sim+real dataset. But if you’d like, you can collect your own real demonstrations below.

Note

Since you’ll likely use our dataset / model, for now this section is a bit less detailed.

    Run the teleop-docker container.

    Log into the hf cli application: hf auth login

    Set your Hugging Face username as an environment variable.

export HF_USER=your-hf-username

    Run the following command - make sure to set the dataset.repo_id argument.

lerobot-record \
  --robot.type=so101_follower \
  --robot.port=$ROBOT_PORT \
  --robot.id=$ROBOT_ID \
  --robot.cameras='{
    "wrist": {
      "type": "opencv",
      "index_or_path": '"$CAMERA_GRIPPER"',
      "width": 640,
      "height": 480,
      "fps": 30
    },
    "front": {
      "type": "opencv",
      "index_or_path": '"$CAMERA_EXTERNAL"',
      "width": 640,
      "height": 480,
      "fps": 30
    }
  }' \
  --teleop.type=so101_leader \
  --teleop.port=$TELEOP_PORT \
  --teleop.id=$TELEOP_ID \
  --display_data=true \
  --dataset.repo_id=${HF_USER}/so101-teleop-vials-to-rack-real \
  --dataset.num_episodes=5 \
  --dataset.single_task="Pick up the vial and place it in the yellow rack" \
  --play_sounds=false

    Use these controls to control recording:

    Press Right Arrow (→): Early stop the current episode or reset time and move to the next.

    Press Left Arrow (←): Cancel the current episode and re-record it.

    Press Escape (ESC): Immediately stop the session, encode videos, and upload the dataset.

Read more about LeRobot Record here: lerobot-record

    Upload this dataset to the Hugging Face Hub: hf upload ${HF_USER}/so101-teleop-vials-to-rack-real

    Merge this dataset with your simulation dataset.

    Train GR00T on this merged dataset.

Hands-On: Deploy Co-Trained Policy to Robot

Now let’s deploy the sim-and-real co-trained policy to the physical robot—the same two-terminal GR00T server + client setup you used for sim and real evaluation earlier.

Tip

For hardware issues or unexpected policy behavior, consult the Troubleshooting Guide.
What Policy Are We Running?

We use the sim-and-real co-trained checkpoint: trained on both simulation demonstrations and a small set of real teleoperation episodes. The exact MODEL (checkpoint path) is set in the commands below; you can change it to evaluate a different strategy or checkpoint.
Workspace Prep

Review the Safety protocol before proceeding.

    Verify robot connection: lerobot-find-port

    Place 1–3 vials randomly on the foam mat; position the rack in its designated location

    Ensure cameras have clear view of workspace and clear any obstacles

    Turn on the lightbox to suitable brightness (see Building the Workspace if needed)

Running Policy Evaluation on the Real Robot

Throughout this course, when we run evaluations there will be two terminals involved:

    The host terminal, where we start the GR00T container and policy server

    The client terminal, where we run the evaluation rollout and control the robot

For real robot evaluation, the client is the physical robot.
Terminal 1 (real-robot container) — Start the GR00T policy server

    Locate the terminal already running the real-robot container.

    Inside this container, run the following. This is where we choose which model to evaluate (co-trained for Strategy 2).

export MODEL=aravindhs-NV/grootn16-finetune_sreetz-so101_teleop_vials_rack_left_sim_and_real/checkpoint-10000

    Run the policy server with that model.

python Isaac-GR00T/gr00t/eval/run_gr00t_server.py \
    --model-path /workspace/models/$MODEL

Terminal 2 (real-robot container) — Evaluation rollout

    Open a second terminal. You will attach to the same real-robot container and run the robot client.

    On the host, attach to the container you started in the last step:

docker exec -it real-robot /bin/bash

    Inside the container, run the evaluation script:

python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py \
  --robot.type=so101_follower \
  --robot.port="$ROBOT_PORT" \
  --robot.id="$ROBOT_ID" \
  --robot.cameras="{
      wrist:  {type: opencv, index_or_path: $CAMERA_GRIPPER, width: 640, height: 480, fps: 30},
      front:  {type: opencv, index_or_path: $CAMERA_EXTERNAL, width: 640, height: 480, fps: 30}
  }" \
  --policy_host=localhost \
  --policy_port=5555 \
  --lang_instruction="Pick up the vial and place it in the yellow rack" \
  --rerun True

Note

The --rerun flag is optional.

It adds Rerun into the loop for debugging, so you can see joint actions and the camera feeds while the policy is running. This lets you confirm the camera views are reasonable and the assignments are correct.
Watching the Evaluation

Watch the robot and the terminal during execution. The policy will run until you stop it or it completes the evaluation. Watch closely but stay clear; note any unexpected behavior and be ready to intervene.

To stop the robot: Press CTRL+C in Terminal 2 (robot client). The policy server in Terminal 1 keeps running.

To run again: Simply run the command again python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py ... in Terminal 2

To switch model or fully restart:

    Stop both terminals’ commands (CTRL+C)

    Set MODEL environment variable to the model you want to evaluate

    Restart the commands for each terminal (model server, robot client)

Note

    At evaluation start, the robot will slowly rise to its initial pose, then enter into inference mode.

    At robot stop (CTRL+C), it will slowly drive itself back to its home pose.

Tip

Keep the policy server running between evaluation attempts. Only restart it if you want to load a different model checkpoint.
Key Takeaways

    Co-training combines sim and real data for better policies

    Safety is paramount when deploying to real hardware

    Document observations systematically—they guide improvement

    The sim-to-real gap is real and often significant

    Different policies exhibit different failure modes

Resources

    Isaac-GR00T Repository — Source code for GR00T deployment including SO-101 evaluation scripts

    SO-101 Finetuning Guide — Full instructions for finetuning and evaluation

    Sim-and-Real Co-Training: A Simple Recipe for Vision-Based Robotic Manipulation — RSS 2025 paper on co-training strategies

What’s Next?

Let’s try another strategy to address the sim-to-real gap. In the next session, Sim-to-Real Strategy 3: Augmenting with Cosmos, you’ll learn about synthetic data augmentation using Cosmos Transfer 2.5.

Sim-to-Real Strategy 3: Augmenting Datasets With Cosmos

In this session, you’ll learn how Cosmos can create diverse synthetic training data and deploy Cosmos-augmented policies to the real robot.
Learning Objectives

By the end of this session, you’ll be able to:

    Explain how Cosmos and world models generate synthetic robot data

    Deploy policies trained with Cosmos augmentation

    Compare performance across different training data strategies

Beyond Domain Randomization and Co-Training

In Strategy 1, you used domain randomization to vary simulation parameters. This is effective, but limited:

    Only varies what you explicitly randomize

    Simulation rendering still looks “synthetic”

    Can’t generate truly novel scenarios

Cosmos addresses these limitations through generative modeling.
What Is Cosmos?

Cosmos is NVIDIA’s world foundation model for physical AI. It can:

    Generate realistic video sequences from prompts or initial frames

    Simulate plausible physical interactions

    Augment robot training data with diverse synthetic scenarios

How Cosmos Works

Input: Robot demonstration video + prompt
       "Same task, different lighting, different vial positions"

Cosmos generates: Multiple variations of the scenario
                  with consistent physics and new visual appearance

Output: Augmented training data with diverse conditions

Prompt:

prompt: Photorealistic first-person view from a robotic arm's orange claw-like gripper. The prongs are visible at the bottom edge, hovering over a heavily corroded, textured rusty steel plate showing oxidation and wear mat. To the left is a yellow rectangular vial rack; to the right, two white opaque centrifuge tubes with blue caps, filled with a white substance, lie horizontally. Plain white wall background with {bright, diffused clinical LED lighting. Sharp macro focus, realistic plastic finishes, and fluid mechanical motion.
{
  "name": "so101",
  "prompt_path": "prompt_test2.txt",
  "video_path": "ego_rgb_001.mp4",
  "guidance": 3,
  "depth": {
    "control_weight": 0.2,
    "control_path": "ego_depth_001.mp4"
  },
  "edge": {
    "control_weight": 1.0
  },
  "seg": {
    "control_weight": 0.3,
    "control_path": "ego_instance_id_segmentation_001.mp4"
  },
  "vis": {
    "control_weight": 0.1
  }
}

Cosmos Augmentation Example 1

Cosmos Augmentation Example 1
Key Capabilities

Visual Diversity

    Photorealistic rendering variations

    Natural lighting changes

    Background and texture diversity

Scenario Variation

    Object position changes

    Different object instances

    Environmental modifications

Physical Consistency

    Maintains plausible physics

    Preserves task structure

    Coherent object interactions

Hands-On: Using Cosmos-Augmented Data

We’ve pre-generated Cosmos-augmented datasets for this learning path.

Compare to the DR-augmented data:

    Notice the visual difference in rendering

    Observe lighting and texture variations

    Check for physical plausibility

Policies to Evaluate

Deploy a policy trained with Cosmos-augmented data using the same two-terminal GR00T server + client setup as in Strategy 2 and Real Evaluation.

Tip

See the Troubleshooting Guide for help with deployment issues.
What Policy Are We Running?

We have two Cosmos-augmented policies to test. Set MODEL in Terminal 1 to the checkpoint you want to evaluate:

Training Data Mix
	

Visualize Dataset
	

Model Checkpoint

75 sim episodes + 7 Cosmos-augmented episodes
	

visualize on Hugging Face
	

aravindhs-NV/sreetz-so101_teleop_vials_rack_left_augment_02/

75 sim episodes + 70 Cosmos-augmented episodes
	

visualize on Hugging Face
	

aravindhs-NV/so100-orig-groot-vials-rack-left-cosmos-70
Workspace Prep

Same as Strategy 2: verify robot connection, place vials and rack, ensure cameras have a clear view, turn on the lightbox. See Building the Workspace, Strategy 2: Workspace prep, and Real Evaluation: Workspace prep.
Running Policy Evaluation on the Real Robot

Throughout this course, when we run evaluations there will be two terminals involved:

    The host terminal, where we start the GR00T container and policy server

    The client terminal, where we run the evaluation rollout and control the robot

For real robot evaluation, the client is the physical robot.
Terminal 1 (real-robot container) — Start the GR00T policy server

    Locate the terminal already running the real-robot container.

    Inside this container, run the following. Set MODEL to the Cosmos-augmented checkpoint you want to test (e.g. 75+70 Cosmos).

export MODEL=aravindhs-NV/so100-orig-groot-vials-rack-left-cosmos-70

    Run the policy server with that model.

python Isaac-GR00T/gr00t/eval/run_gr00t_server.py \
    --model-path /workspace/models/$MODEL

Terminal 2 (real-robot container) — Evaluation rollout

Open a second terminal. You will attach to the same real-robot container and run the robot client.

    On the host, attach to the container:

docker exec -it real-robot /bin/bash

    Inside the container, run the evaluation script:

python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py \
  --robot.type=so101_follower \
  --robot.port="$ROBOT_PORT" \
  --robot.id="$ROBOT_ID" \
  --robot.cameras="{
      wrist:  {type: opencv, index_or_path: $CAMERA_GRIPPER, width: 640, height: 480, fps: 30},
      front:  {type: opencv, index_or_path: $CAMERA_EXTERNAL, width: 640, height: 480, fps: 30}
  }" \
  --policy_host=localhost \
  --policy_port=5555 \
  --lang_instruction="Pick up the vial and place it in the yellow rack" \
  --rerun True

Note

The --rerun flag is optional.

It adds Rerun into the loop for debugging, so you can see joint actions and the camera feeds while the policy is running. This lets you confirm the camera views are reasonable and the assignments are correct.
Watching the Evaluation

Watch the robot and the terminal during execution. Compare behavior to the sim-only and co-trained policies: Cosmos-augmented policies may show different robustness to lighting and visual variation.

To stop the robot: Press CTRL+C in Terminal 2 (robot client). The policy server in Terminal 1 keeps running.

To run again: Simply run the command again python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py ... in Terminal 2

To switch model or fully restart:

    Stop both terminals’ commands (CTRL+C)

    Set MODEL environment variable to the model you want to evaluate

    Restart the commands for each terminal (model server, robot client)

To Try the Other Policy Trained on Cosmos-Augmented Data

    In terminal 1, press CTRL+C to stop the policy server.

    In terminal 2, press CTRL+C to stop the robot client.

    Set MODEL environment variable to the model you want to evaluate.

export MODEL=aravindhs-NV/sreetz-so101_teleop_vials_rack_left_augment_02/checkpoint-10000

    Restart the policy server by running the same command again.

python Isaac-GR00T/gr00t/eval/run_gr00t_server.py --model-path /workspace/models/$MODEL

    Run the robot client again by running the same command again.

python Isaac-GR00T/gr00t/eval/real_robot/SO100/so101_eval.py \
  --robot.type=so101_follower \
  --robot.port="$ROBOT_PORT" \
  --robot.id="$ROBOT_ID" \
  --robot.cameras="{
      wrist:  {type: opencv, index_or_path: $CAMERA_GRIPPER, width: 640, height: 480, fps: 30},
      front:  {type: opencv, index_or_path: $CAMERA_EXTERNAL, width: 640, height: 480, fps: 30}
  }" \
  --policy_host=localhost \
  --policy_port=5555 \
  --lang_instruction="Pick up the vial and place it in the yellow rack" \
  --rerun True

Note

    At evaluation start, the robot will slowly rise to its initial pose, then enter into inference mode.

    At robot stop (CTRL+C), it will slowly drive itself back to its home pose.

Tip

Keep the policy server running between evaluation attempts. Only restart it when you want to load a different model checkpoint.
Comparing Policies

After running the Cosmos-augmented policy, compare with your notes from Strategy 2 (co-trained) and your earlier real evaluation baseline (sim-only policy). Note whether Cosmos augmentation improves consistency, grasp success, or placement accuracy on the real robot.
Key Takeaways

    Cosmos generates photorealistic synthetic data beyond DR capabilities

    Different approaches address different aspects of the sim-to-real gap

    Combining strategies often works better than any single approach

    Visual diversity from Cosmos can unlock performance gains

Resources

    Cosmos Transfer 2.5 — NVIDIA Research page on Cosmos video-to-video transfer capabilities

    Cosmos Cookbook — Recipes and examples for Cosmos world foundation models

Sim-to-Real Strategy 4: Measuring and Closing the Gap With SAGE + GapONet
SAGE GapONet Comparison

SAGE GapONet Comparison

In this session, you’ll learn how to quantify the actuation gap precisely using SAGE, and how GapONet can model complex actuation dynamics that aren’t captured by simple parameter tuning.
Learning Objectives

By the end of this session, you’ll be able to:

    Explain how SAGE quantifies the sim-to-real gap per joint

    Interpret SAGE analysis results to guide improvement

    Describe how GapONet models complex actuation dynamics

The Problem: Unknown Gap Sources

You’ve seen the improvements made by these strategies so far:

    Domain randomization (Strategy 1)

    Co-training with real data (Strategy 2)

    Cosmos augmentation (Strategy 3)

But we haven’t addressed actuation gaps yet. To close them systematically, let’s first understand some of the sources:
Sources of the Sim-to-Real Gap

During Sensing:

    Simplified or inaccurate sensor models for cameras

    Physics modeling gaps in the simulator

During Actuation:

    Inaccurate or missing actuator models

    Physics modeling gaps (contact nuances, friction, closed-loop linkages)

    Uncharacterized dynamic effects at system level (changing inertial behavior with payload, varying friction)

    Inaccurate URDF (missing component details, missing properties, user input error)

    CAD → URDF → USD format conversion errors

To close these gaps, you need to know:

    Where exactly are the gaps?

    How large are they?

    What causes them?

Specifically for the SO-101, one challenge is that the actuators are hobby servos that can introduce significant backlash into the system, and this backlash adds up through the kinematic chain of the robot.

SAGE can help us visualize and collect data related to this gap.
What Is SAGE?

SAGE (Sim-to-Real Actuation Gap Estimation) is a collaborative project by Tongji University (TJU), Peking University (PKU), and NVIDIA to demonstrate an approach for sim-to-real gap perception, measurement, and bridging.

SAGE provides a systematic way of collecting real and sim paired datasets, analyzing, estimating, and visualizing the sim-to-real gap.

Repository: isaac-sim2real/sage

SAGE systematically:

    Collects paired real and simulation data for the same motions

    Compares position, velocity, and torque across domains

    Quantifies the gap per joint

    Visualizes where the gap is largest

    Enables targeted improvement via GapONet or parameter tuning

SAGE Overview

SAGE pipeline overview: from diverse motion sources through gap estimation to gap bridging.
SAGE Workflow

┌─────────────────┐     ┌─────────────────┐
│  Motion Files   │     │  Real Robot     │
│  (retargeted    │────▶│  Data Collection│
│   sequences)    │     │  (pos, vel, τ)  │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
┌─────────────────┐     ┌─────────────────┐
│  Same Motions   │     │   Simulation    │
│   in Isaac Sim  │────▶│  Data Collection│
│                 │     │  (pos, vel, τ)  │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Gap Analysis   │
                        │  Per-Joint      │
                        │  Visualization  │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  Gap Bridging   │
                        │  (GapONet, etc.)│
                        └─────────────────┘

Case Study: SO-101 SAGE Pipeline Overview

The following gives you an intuitive overview of the full pipeline; the step-by-step walkthrough comes later in this document.

Pipeline in brief. For the SO-101 we (1) collect sim data, (2) collect real robot data, and (3) train a gap-bridging model (GapONet; its details are covered later). Our SO-101 setup collected 8 hours of real trajectory data for such training.
SO-101 during real-robot data collection

SO-101 during real-robot data collection.

Below we show two ways to see the effect of GapONet after it is trained.

1. Visual comparison in the simulation environment.
In Isaac Sim we overlay real-robot motion with sim replay. The GUI screenshot below shows: top — real result vs sim without GapONet; bottom — real result vs sim with GapONet. With GapONet, the sim trace matches the real motion much more closely.
Real vs sim without GapONet (top) and real vs sim with GapONet (bottom) in Isaac Sim

Top: real vs sim without GapONet. Bottom: real vs sim with GapONet.

2. Quantitative joint-level error.
We measure error between real and sim at each joint. In the plot below, orange is the error for real vs sim without GapONet; green is the error for real vs sim with GapONet. Lower green bars show that GapONet reduces the gap.
Joint-level error: orange = real vs sim without GapONet, green = real vs sim with GapONet

Joint error: orange = real vs sim without GapONet; green = real vs sim with GapONet.
SAGE Repository Structure

Understanding the file layout helps navigate the framework. See the SAGE repository for the current structure; a simplified overview:

sage/
├── assets/                    # Robot USD files
│   └── {robot_name}/
├── configs/
│   ├── {robot_name}_joints.yaml       # Complete joint list
│   └── {robot_name}_valid_joints.txt  # Motion-relevant joints
├── docs/                      # Robot-specific guides (e.g. LEROBOT_REAL for SO-101)
├── motion_files/
│   └── {robot_name}/{source}/         # Retargeted motion files
├── output/
│   ├── sim/{robot_name}/{source}/{motion_name}/   # Simulation results
│   └── real/{robot_name}/{source}/{motion_name}/  # Real robot results
├── sage/                      # Python package
│   ├── assets.py              # Robot configuration (USD path, PD gains, etc.)
│   ├── simulation.py          # Isaac Sim simulation code
│   ├── analysis.py            # Sim vs. real comparison and metrics
│   ├── real_unitree/          # Unitree H1-2 real robot code
│   ├── real_realman/          # Realman WR75S real robot code
│   └── real_so101/            # LeRobot SO-101 real robot code
└── scripts/
    ├── run_simulation.py      # Run simulation data collection
    ├── run_analysis.py        # Compare sim vs real, generate metrics and plots
    └── run_real.py            # Run real robot data collection

Walkthrough: Running SAGE on an Action Sequence in Simulation

This walkthrough demonstrates the complete SAGE pipeline: running the same motion in simulation and on real hardware, then analyzing the gap.

Important

This walkthrough is for reference; we won’t be doing this hands-on today for time.
Startup

    First, clone the SAGE repository:

git clone git@github.com:isaac-sim2real/sage.git
cd sage

    Start the SAGE container:

xhost +
docker run --name isaac-lab --entrypoint bash -it --gpus all -e "ACCEPT_EULA=Y" --rm --network=host \
   -e "PRIVACY_CONSENT=Y" \
   -e DISPLAY \
   -v /tmp/.X11-unix:/tmp/.X11-unix \
   -v $HOME/.Xauthority:/root/.Xauthority \
   -v ~/docker/isaac-sim/cache/kit:/isaac-sim/kit/cache:rw \
   -v ~/docker/isaac-sim/cache/ov:/root/.cache/ov:rw \
   -v ~/docker/isaac-sim/cache/pip:/root/.cache/pip:rw \
   -v ~/docker/isaac-sim/cache/glcache:/root/.cache/nvidia/GLCache:rw \
   -v ~/docker/isaac-sim/cache/computecache:/root/.nv/ComputeCache:rw \
   -v ~/docker/isaac-sim/logs:/root/.nvidia-omniverse/logs:rw \
   -v ~/docker/isaac-sim/data:/root/.local/share/ov/data:rw \
   -v ~/docker/isaac-sim/documents:/root/Documents:rw \
   -v $(pwd):/app:rw \
   sage

Choose Motion File

Motion files contain retargeted action sequences. SAGE supports diverse motion sources:

    Teleoperation: Human-guided motions

    Remote control: Joystick or keyboard controlled

    Retargeted motions: From motion capture or other robots

For SO-101, motion files live under motion_files/so101/custom/, including pick-and-place and other trajectories:

# Motion files location
ls motion_files/so101/custom/

# Example output (subset):
# actuator_bandwidth.txt
# pick_place.txt
# oscillation_low_freq.txt
# random_waypoints.txt
# ...

Each .txt file contains joint angle positions over time (format: first line joint names, then comma-separated angles in radians per line).
Verify the Robot Configuration

Verifying robot configuration in sage/assets.py:

# SO-101 entry in ROBOT_CONFIGS
"so101": {
    "usd_path": "assets/so101/SO-ARM101-USD.usd",
    "offset": (0.0, 0.0, 0.0),
    "default_kp": 100.0,   # PD controller stiffness
    "default_kd": 2.0,     # PD controller damping
    "default_control_freq": 50.0,  # Control frequency (Hz)
}

Verifying the valid joints list:

cat configs/so101_valid_joints.txt

# Example output:
# Rotation
# Pitch
# Elbow
# Wrist_Pitch
# Wrist_Roll
# Jaw

Run Simulation Data Collection

From within the same terminal in the SAGE container, we’d now execute the motion sequence in Isaac Sim:

${ISAACSIM_PATH}/python.sh scripts/run_simulation.py \
    --robot-name so101 \
    --motion-source custom \
    --motion-files motion_files/so101/custom/pick_place.txt \
    --valid-joints-file configs/so101_valid_joints.txt \
    --output-folder output \
    --fix-root \
    --physics-freq 200 \
    --render-freq 200 \
    --control-freq 50 \
    --kp 100 \
    --kd 2

This collects:

    Commanded joint positions

    Actual joint positions (from simulation)

    Joint velocities

    Joint torques

Run Real Robot Data Collection

Now to create a paired dataset, we’ll execute the same motion on the physical SO-101. This will actually move the robot and record data.

Follow the instructions here: LEROBOT_REAL.md
Analyze the Gap

Compare the paired sim-real data:

python scripts/run_analysis.py \
    --robot-name so101 \
    --motion-source custom \
    --motion-names "pick_place" \
    --output-folder output \
    --valid-joints-file configs/so101_valid_joints.txt

SAGE Elbow Axis Analysis

Analysis of SAGE data to quantify the gap for a given axis, and a given motion.
Using Paired Data for Gap Bridging

Once you have sim-real paired data, you can train a neural network that bridges the actuation gap. This gap-bridging model can be used in two ways:

1. Integrate into the simulation environment.
Use the model inside sim so that the environment better matches real actuation. Policies trained in this gap-corrected sim are more likely to achieve seamless sim-to-real deployment. The figure below illustrates this use.

2. Use at real-robot deployment.
Apply the model on the real robot at inference time so that the policy’s actions are corrected for the actuation gap before execution. This is the idea behind the future work on GapONet + GR00T integration: a policy trained in sim benefits from gap bridging when deployed on hardware.
Gap-bridging model inside simulation

Using a gap-bridging model inside the simulation environment so that policies are trained with more realistic actuation.
What Is GapONet?

GapONet, developed by Peking University (PKU), learns a neural network model of actuator behavior that captures effects not easily modeled analytically. GapONet is part of the SAGE ecosystem, and its integration in SAGE is in progress.
How GapONet Works

Training Phase:
  Input:  Commanded action sequences (from motions)
  Target: Actual resulting motion (from real robot)
  Learns: Mapping from command → actual behavior

Inference Phase:
  Input:  Policy's intended action
  Output: Compensated action that achieves intended behavior

Training GapONet

Note

This section is for reference; we won’t be doing this training hands-on today for time.

The GapONet repository provides an Isaac Lab–based implementation with DeepONet, Transformer, and MLP architectures for sim-to-real humanoid control. After installing the repo and required assets (see the repo README), train with the operator environment:

python scripts/rsl_rl/train.py --task Isaac-Humanoid-Operator-Delta-Action \
  --num_envs=4080 --max_iterations 100000 --experiment_name Sim2Real \
  --letter amass --run_name delta_action_mlp_payload --device cuda env.mode=train --headless

Adjust --num_envs, --max_iterations, and --run_name as needed. For other architectures or tasks, see the repo’s Usage and Adding a New Robot sections.

Evaluation and export. Evaluate a checkpoint:

python scripts/rsl_rl/play.py --task Isaac-Humanoid-Operator-Delta-Action \
   --model ./model/model_17950.pt --num_envs 20 --headless

Export to JIT for lightweight inference without Isaac Sim:

python scripts/rsl_rl/inference_jit.py \
    --export \
    --checkpoint ./model/model_17950.pt \
    --task Isaac-Humanoid-Operator-Delta-Action \
    --output ./model/policy.pt \
    --device cuda:0 \
    --num_envs 20

Then run inference on test data (no Isaac Sim required):

python scripts/rsl_rl/deploy.py \
    --model ./model/policy.pt \
    --test_data ./source/sim2real/sim2real/tasks/humanoid_operator/motions/motion_amass/edited_27dof/test.npz

For SO-101 or other arms, SAGE’s gap-bridging training typically focuses on joints with the largest sim-to-real gaps (e.g. gripper, wrist) using paired SAGE data; the exact scripts depend on the SAGE repository and any GapONet integration there.
Pre-Collected Dataset

For humanoid research, SAGE provides pre-collected datasets:

Unitree Dataset (H1-2 humanoid):

    Upper-body motions under varying payloads (0-3 kg)

    Motions adapted from AMASS dataset

    Paired sim-real data

RealMan Dataset (WR75S arms):

    Four arms tested under four payload conditions

    Cross-robot generalization studies

The PKU Disk link for downloading these datasets is in the SAGE repository’s Processed Sim2Real Datasets section.
Community-Driven Future

SAGE is designed to become a community-driven effort where roboticists around the world come together to collectively work on solutions.

Community Contributions:

    Paired datasets: Real-sim motion data for new robots and tasks

    Sim-Ready assets: Robot USD files calibrated for accurate simulation

    Novel NN architectures: New models for gap estimation and compensation

    Hybrid solutions: Combinations of analytical and learned approaches

Planned Community Features:

    Leaderboards: Rank trained networks by quality, enabled task space, and robot models

    OEM Feedback: Guide humanoid manufacturers in improving their assets and APIs

Contributing your own data and models helps the entire robotics community close the sim-to-real gap faster.
Future Work: GapONet + GR00T Integration

A key next step is integrating GapONet inference directly into the GR00T deployment loop for our SO-101 task:

GR00T Policy → Action Command → GapONet Compensation → Robot Execution

This would allow the VLA policy to output its intended actions while GapONet automatically compensates for actuator dynamics in real-time—combining the generalization of foundation models with the precision of learned actuator models.

This integration is under active development.
Key Takeaways

    SAGE provides quantitative, per-joint gap analysis

    The pipeline: same motion → sim + real → compare → quantify

    Knowing where gaps are enables targeted improvement

    Small gaps: tune parameters; large gaps: use GapONet

    GapONet models complex dynamics that resist simple tuning

    Isaac Lab integration enables direct use in simulation workflows

Resources

    SAGE Repository: isaac-sim2real/sage

    GapONet Repository: jiemingcui/gaponet

What’s Next?

Continue to the Conclusion for a summary of what you’ve learned and next steps.

Conclusion

This session provides time for remaining questions, continued experimentation, and a conclusion for this learning path.
Learning Path Summary
What You Accomplished

    Learned why simulation matters and what the sim-to-real gap is

    Built and standardized the physical lightbox workspace to match the sim task

    Got hands-on time with the SO-101 robot and LeRobot tools

    Applied Strategy 1: Domain randomization with teleoperation

    Explored NVIDIA GR00T, vision-language-action models

    Evaluated policies in simulation and on the real robot (sim-to-real gap)

    Applied Strategy 2: Co-training with real data, deployed to robot

    Applied Strategy 3: Cosmos synthetic data augmentation

    Explored Strategy 4: SAGE + GapONet (actuator gap estimation)

The Four Strategies We Covered

Strategy
	

Approach18:30:56 [teleop_se3_agent.py] ERROR: Failed to create environment: Failed to create frame transformer for frame 'None' with path '/World/envs/env_.*/Robot/base_link'. No matching prims were found.
	

Key Benefit

1. Domain Randomization
	

Vary simulation parameters
	

Robust to physics variations

2. Co-training
	

Mix sim and real data
	

Better real-world distribution

3. Cosmos Augmentation
	

Synthetic visual diversity
	

Robust to visual variations

4. SAGE + GapONet
	

Measure and model the gap
	

Targeted actuation fixes
Key Lessons

    The gap is real — simulation success doesn’t guarantee real-world success

    Multiple strategies combine — no single approach solves everything

    Measurement enables improvement — SAGE shows you where to focus

    Iteration is essential — systematic improvement beats one-shot attempts

    Documentation matters — recorded observations guide decisions

Resources
Courses

    Getting Started with Isaac Lab - Transferring Robot Learning Policies from Simulation to Reality

Documentation

    LeRobot Documentation

    Isaac Sim Documentation

    Isaac Lab Documentation

    GR00T Developer Guide

    SAGE Repository

Community

    Hugging Face Discord

    NVIDIA Developer Forums

    LeRobot GitHub

Papers

    The Reality Gap in Robotics: Challenges, Solutions, and Best Practices

Conclusion

Congratulations on finishing this course “Train an SO-101 Robot From Sim-to-Real With NVIDIA Isaac.”

We hope this will enable and inspire you to keep learning and practicing your skills in Physical AI!
Feedback

Taking a few minutes to fill out our survey gives us valuable feedback to improve the course for future participants.

If you have any feedback, suggestions, or ran into issues, please visit this s