Teleoperation and Imitation Learning with Isaac Lab Mimic
Teleoperation

We provide interfaces for providing commands in SE(2) and SE(3) space for robot control. In case of SE(2) teleoperation, the returned command is the linear x-y velocity and yaw rate, while in SE(3), the returned command is a 6-D vector representing the change in pose.

Note

Presently, Isaac Lab Mimic is only supported in Linux.

To play inverse kinematics (IK) control with a keyboard device:

./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --num_envs 1 --teleop_device keyboard

For smoother operation and off-axis operation, we recommend using a SpaceMouse as the input device. Providing smoother demonstrations will make it easier for the policy to clone the behavior. To use a SpaceMouse, simply change the teleop device accordingly:

./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --num_envs 1 --teleop_device spacemouse

Note

If the SpaceMouse is not detected, you may need to grant additional user permissions by running sudo chmod 666 /dev/hidraw<#> where <#> corresponds to the device index of the connected SpaceMouse.

To determine the device index, list all hidraw devices by running ls -l /dev/hidraw*. Identify the device corresponding to the SpaceMouse by running cat /sys/class/hidraw/hidraw<#>/device/uevent on each of the devices listed from the prior step.

We recommend using local deployment of Isaac Lab to use the SpaceMouse. If using container deployment (Docker Guide), you must manually mount the SpaceMouse to the isaac-lab-base container by adding a devices attribute with the path to the device in your docker-compose.yaml file:

devices:
   - /dev/hidraw<#>:/dev/hidraw<#>

where <#> is the device index of the connected SpaceMouse.

If you are using the IsaacLab + CloudXR container deployment (Setting up CloudXR Teleoperation), you can add the devices attribute under the services -> isaac-lab-base section of the docker/docker-compose.cloudxr-runtime.patch.yaml file.

Isaac Lab is only compatible with the SpaceMouse Wireless and SpaceMouse Compact models from 3Dconnexion.

For tasks that benefit from the use of an extended reality (XR) device with hand tracking, Isaac Lab supports using NVIDIA CloudXR to immersively stream the scene to compatible XR devices for teleoperation. Note that when using hand tracking we recommend using the absolute variant of the task (Isaac-Stack-Cube-Franka-IK-Abs-v0), which requires the handtracking device:

./isaaclab.sh -p scripts/environments/teleoperation/teleop_se3_agent.py --task Isaac-Stack-Cube-Franka-IK-Abs-v0 --teleop_device handtracking --device cpu

Note

See Setting up CloudXR Teleoperation to learn how to use CloudXR and experience teleoperation with Isaac Lab.

The script prints the teleoperation events configured. For keyboard, these are as follows:

Keyboard Controller for SE(3): Se3Keyboard
   Reset all commands: R
   Toggle gripper (open/close): K
   Move arm along x-axis: W/S
   Move arm along y-axis: A/D
   Move arm along z-axis: Q/E
   Rotate arm along x-axis: Z/X
   Rotate arm along y-axis: T/G
   Rotate arm along z-axis: C/V

For SpaceMouse, these are as follows:

SpaceMouse Controller for SE(3): Se3SpaceMouse
   Reset all commands: Right click
   Toggle gripper (open/close): Click the left button on the SpaceMouse
   Move arm along x/y-axis: Tilt the SpaceMouse
   Move arm along z-axis: Push or pull the SpaceMouse
   Rotate arm: Twist the SpaceMouse

The next section describes how teleoperation devices can be used for data collection for imitation learning.
Imitation Learning with Isaac Lab Mimic

Using the teleoperation devices, it is also possible to collect data for learning from demonstrations (LfD). For this, we provide scripts to collect data into the open HDF5 format.
Collecting demonstrations

To collect demonstrations with teleoperation for the environment Isaac-Stack-Cube-Franka-IK-Rel-v0, use the following commands:

# step a: create folder for datasets
mkdir -p datasets
# step b: collect data with a selected teleoperation device. Replace <teleop_device> with your preferred input device.
# Available options: spacemouse, keyboard, handtracking
./isaaclab.sh -p scripts/tools/record_demos.py --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --device cpu --teleop_device <teleop_device> --dataset_file ./datasets/dataset.hdf5 --num_demos 10
# step a: replay the collected dataset
./isaaclab.sh -p scripts/tools/replay_demos.py --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --device cpu --dataset_file ./datasets/dataset.hdf5

Note

The order of the stacked cubes should be blue (bottom), red (middle), green (top).

Tip

When using an XR device, we suggest collecting demonstrations with the Isaac-Stack-Cube-Frank-IK-Abs-v0 version of the task and --teleop_device handtracking, which controls the end effector using the absolute position of the hand.

About 10 successful demonstrations are required in order for the following steps to succeed.

Here are some tips to perform demonstrations that lead to successful policy training:

    Keep demonstrations short. Shorter demonstrations mean fewer decisions for the policy, making training easier.

    Take a direct path. Do not follow along arbitrary axis, but move straight toward the goal.

    Do not pause. Perform smooth, continuous motions instead. It is not obvious for a policy why and when to pause, hence continuous motions are easier to learn.

If, while performing a demonstration, a mistake is made, or the current demonstration should not be recorded for some other reason, press the R key to discard the current demonstration, and reset to a new starting position.

Note

Non-determinism may be observed during replay as physics in IsaacLab are not determimnistically reproducible when using env.reset.
Pre-recorded demonstrations

We provide a pre-recorded dataset.hdf5 containing 10 human demonstrations for Isaac-Stack-Cube-Franka-IK-Rel-v0 here: [Franka Dataset]. This dataset may be downloaded and used in the remaining tutorial steps if you do not wish to collect your own demonstrations.

Note

Use of the pre-recorded dataset is optional.
Generating additional demonstrations with Isaac Lab Mimic

Additional demonstrations can be generated using Isaac Lab Mimic.

Isaac Lab Mimic is a feature in Isaac Lab that allows generation of additional demonstrations automatically, allowing a policy to learn successfully even from just a handful of manual demonstrations.

In the following example, we will show how to use Isaac Lab Mimic to generate additional demonstrations that can be used to train either a state-based policy (using the Isaac-Stack-Cube-Franka-IK-Rel-Mimic-v0 environment) or visuomotor policy (using the Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Mimic-v0 environment).

Note

The following commands are run using CPU mode as a small number of envs are used which are I/O bound rather than compute bound.

Important

All commands in the following sections must keep a consistent policy type. For example, if choosing to use a state-based policy, then all commands used should be from the “State-based policy” tab.

In order to use Isaac Lab Mimic with the recorded dataset, first annotate the subtasks in the recording:
State-based policy

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
--device cpu --task Isaac-Stack-Cube-Franka-IK-Rel-Mimic-v0 --auto \
--input_file ./datasets/dataset.hdf5 --output_file ./datasets/annotated_dataset.hdf5

Visuomotor policy

Then, use Isaac Lab Mimic to generate some additional demonstrations:
State-based policy

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu --num_envs 10 --generation_num_trials 10 \
--input_file ./datasets/annotated_dataset.hdf5 --output_file ./datasets/generated_dataset_small.hdf5

Visuomotor policy

Note

The output_file of the annotate_demos.py script is the input_file to the generate_dataset.py script

Inspect the output of generated data (filename: generated_dataset_small.hdf5), and if satisfactory, generate the full dataset:
State-based policy

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu --headless --num_envs 10 --generation_num_trials 1000 \
--input_file ./datasets/annotated_dataset.hdf5 --output_file ./datasets/generated_dataset.hdf5

Visuomotor policy

The number of demonstrations can be increased or decreased, 1000 demonstrations have been shown to provide good training results for this task.

Additionally, the number of environments in the --num_envs parameter can be adjusted to speed up data generation. The suggested number of 10 can be executed on a moderate laptop GPU. On a more powerful desktop machine, use a larger number of environments for a significant speedup of this step.
Robomimic setup

As an example, we will train a BC agent implemented in Robomimic to train a policy. Any other framework or training method could be used.

To install the robomimic framework, use the following commands:

# install the dependencies
sudo apt install cmake build-essential
# install python module (for robomimic)
./isaaclab.sh -i robomimic

Training an agent

Using the Mimic generated data we can now train a state-based BC agent for Isaac-Stack-Cube-Franka-IK-Rel-v0, or a visuomotor BC agent for Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-v0:
State-based policy

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-Stack-Cube-Franka-IK-Rel-v0 --algo bc \
--dataset ./datasets/generated_dataset.hdf5

Visuomotor policy

Note

By default the trained models and logs will be saved to IssacLab/logs/robomimic.
Visualizing results

Tip

Important: Testing Multiple Checkpoint Epochs

When evaluating policy performance, it is common for different training epochs to yield significantly different results. If you don’t see the expected performance, always test policies from various epochs (not just the final checkpoint) to find the best-performing model. Model performance can vary substantially across training, and the final epoch is not always optimal.

By inferencing using the generated model, we can visualize the results of the policy:
State-based policy

./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu --task Isaac-Stack-Cube-Franka-IK-Rel-v0 --num_rollouts 50 \
--checkpoint /PATH/TO/desired_model_checkpoint.pth

Visuomotor policy

Tip

If you don’t see expected performance results: Test policies from multiple checkpoint epochs, not just the final one. Policy performance can vary significantly across training epochs, and intermediate checkpoints often outperform the final model.

Note

Expected Success Rates and Timings for Franka Cube Stack Task

    Data generation success rate: ~50% (for both state + visuomotor)

    Data generation time: ~30 mins for state, ~4 hours for visuomotor (varies based on num envs the user runs)

    BC RNN training time: 1000 epochs + ~30 mins (for state), 600 epochs + ~6 hours (for visuomotor)

    BC RNN policy success rate: ~40-60% (for both state + visuomotor)

    Recommendation: Evaluate checkpoints from various epochs throughout training to identify the best-performing model

Demo 1: Data Generation and Policy Training for a Humanoid Robot
GR-1 humanoid robot performing a pick and place task

Isaac Lab Mimic supports data generation for robots with multiple end effectors. In the following demonstration, we will show how to generate data to train a Fourier GR-1 humanoid robot to perform a pick and place task.
Optional: Collect and annotate demonstrations
Collect human demonstrations

Note

Data collection for the GR-1 humanoid robot environment requires use of an Apple Vision Pro headset. If you do not have access to an Apple Vision Pro, you may skip this step and continue on to the next step: Generate the dataset. A pre-recorded annotated dataset is provided in the next step.

Tip

The GR1 scene utilizes the wrist poses from the Apple Vision Pro (AVP) as setpoints for a differential IK controller (Pink-IK). The differential IK controller requires the user’s wrist pose to be close to the robot’s initial or current pose for optimal performance. Rapid movements of the user’s wrist may cause it to deviate significantly from the goal state, which could prevent the IK controller from finding the optimal solution. This may result in a mismatch between the user’s wrist and the robot’s wrist. You can increase the gain of all the Pink-IK controller’s FrameTasks to track the AVP wrist poses with lower latency. However, this may lead to more jerky motion. Separately, the finger joints of the robot are retargeted to the user’s finger joints using the dex-retargeting library.

Set up the CloudXR Runtime and Apple Vision Pro for teleoperation by following the steps in Setting up CloudXR Teleoperation. CPU simulation is used in the following steps for better XR performance when running a single environment.

Collect a set of human demonstrations. A success demo requires the object to be placed in the bin and for the robot’s right arm to be retracted to the starting position.

The Isaac Lab Mimic Env GR-1 humanoid robot is set up such that the left hand has a single subtask, while the right hand has two subtasks. The first subtask involves the right hand remaining idle while the left hand picks up and moves the object to the position where the right hand will grasp it. This setup allows Isaac Lab Mimic to interpolate the right hand’s trajectory accurately by using the object’s pose, especially when poses are randomized during data generation. Therefore, avoid moving the right hand while the left hand picks up the object and brings it to a stable position.

GR-1 humanoid robot performing a good pick and place demonstration GR-1 humanoid robot performing a bad pick and place demonstration

Left: A good human demonstration with smooth and steady motion. Right: A bad demonstration with jerky and exaggerated motion.

Collect five demonstrations by running the following command:

./isaaclab.sh -p scripts/tools/record_demos.py \
--device cpu \
--task Isaac-PickPlace-GR1T2-Abs-v0 \
--teleop_device handtracking \
--dataset_file ./datasets/dataset_gr1.hdf5 \
--num_demos 5 --enable_pinocchio

Note

We also provide a GR-1 pick and place task with waist degrees-of-freedom enabled Isaac-PickPlace-GR1T2-WaistEnabled-Abs-v0 (see Available Environments for details on the available environments, including the GR1 Waist Enabled variant). The same command above applies but with the task name changed to Isaac-PickPlace-GR1T2-WaistEnabled-Abs-v0.

Tip

If a demo fails during data collection, the environment can be reset using the teleoperation controls panel in the XR teleop client on the Apple Vision Pro or via voice control by saying “reset”. See Teleoperate an Isaac Lab Robot with Apple Vision Pro for more details.

The robot uses simplified collision meshes for physics calculations that differ from the detailed visual meshes displayed in the simulation. Due to this difference, you may occasionally observe visual artifacts where parts of the robot appear to penetrate other objects or itself, even though proper collision handling is occurring in the physics simulation.

You can replay the collected demonstrations by running the following command:

./isaaclab.sh -p scripts/tools/replay_demos.py \
--device cpu \
--task Isaac-PickPlace-GR1T2-Abs-v0 \
--dataset_file ./datasets/dataset_gr1.hdf5 --enable_pinocchio

Note

Non-determinism may be observed during replay as physics in IsaacLab are not determimnistically reproducible when using env.reset.
Annotate the demonstrations

Unlike the prior Franka stacking task, the GR-1 pick and place task uses manual annotation to define subtasks.

The pick and place task has one subtask for the left arm (pick) and two subtasks for the right arm (idle, place). Annotations denote the end of a subtask. For the pick and place task, this means there are no annotations for the left arm and one annotation for the right arm (the end of the final subtask is always implicit).

Each demo requires a single annotation between the first and second subtask of the right arm. This annotation (“S” button press) should be done when the right robot arm finishes the “idle” subtask and begins to move towards the target object. An example of a correct annotation is shown below:
../../../_images/gr-1_pick_place_annotation.jpg

Annotate the demonstrations by running the following command:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
--device cpu \
--task Isaac-PickPlace-GR1T2-Abs-Mimic-v0 \
--input_file ./datasets/dataset_gr1.hdf5 \
--output_file ./datasets/dataset_annotated_gr1.hdf5 --enable_pinocchio

Note

The script prints the keyboard commands for manual annotation and the current subtask being annotated:

Annotating episode #0 (demo_0)
   Playing the episode for subtask annotations for eef "right".
   Subtask signals to annotate:
      - Termination:      ['idle_right']

   Press "N" to begin.
   Press "B" to pause.
   Press "S" to annotate subtask signals.
   Press "Q" to skip the episode.

Tip

If the object does not get placed in the bin during annotation, you can press “N” to replay the episode and annotate again. Or you can press “Q” to skip the episode and annotate the next one.
Generate the dataset

If you skipped the prior collection and annotation step, download the pre-recorded annotated dataset dataset_annotated_gr1.hdf5 from here: [Annotated GR1 Dataset]. Place the file under IsaacLab/datasets and run the following command to generate a new dataset with 1000 demonstrations.

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu --headless --num_envs 20 --generation_num_trials 1000 --enable_pinocchio \
--input_file ./datasets/dataset_annotated_gr1.hdf5 --output_file ./datasets/generated_dataset_gr1.hdf5

Train a policy

Use Robomimic to train a policy for the generated dataset.

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-PickPlace-GR1T2-Abs-v0 --algo bc \
--normalize_training_actions \
--dataset ./datasets/generated_dataset_gr1.hdf5

The training script will normalize the actions in the dataset to the range [-1, 1]. The normalization parameters are saved in the model directory under PATH_TO_MODEL_DIRECTORY/logs/normalization_params.txt. Record the normalization parameters for later use in the visualization step.

Note

By default the trained models and logs will be saved to IssacLab/logs/robomimic.
Visualize the results

Visualize the results of the trained policy by running the following command, using the normalization parameters recorded in the prior training step:

./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu \
--enable_pinocchio \
--task Isaac-PickPlace-GR1T2-Abs-v0 \
--num_rollouts 50 \
--horizon 400 \
--norm_factor_min <NORM_FACTOR_MIN> \
--norm_factor_max <NORM_FACTOR_MAX> \
--checkpoint /PATH/TO/desired_model_checkpoint.pth

Note

Change the NORM_FACTOR in the above command with the values generated in the training step.

Tip

If you don’t see expected performance results: It is critical to test policies from various checkpoint epochs. Performance can vary significantly between epochs, and the best-performing checkpoint is often not the final one.
GR-1 humanoid robot performing a pick and place task

The trained policy performing the pick and place task in Isaac Lab.

Note

Expected Success Rates and Timings for Pick and Place GR1T2 Task

    Success rate for data generation depends on the quality of human demonstrations (how well the user performs them) and dataset annotation quality. Both data generation and downstream policy success are sensitive to these factors and can show high variance. See Common Pitfalls when Generating Data for tips to improve your dataset.

    Data generation success for this task is typically 65-80% over 1000 demonstrations, taking 18-40 minutes depending on GPU hardware and success rate (19 minutes on a RTX ADA 6000 @ 80% success rate).

    Behavior Cloning (BC) policy success is typically 75-86% (evaluated on 50 rollouts) when trained on 1000 generated demonstrations for 2000 epochs (default), depending on demonstration quality. Training takes approximately 29 minutes on a RTX ADA 6000.

    Recommendation: Train for 2000 epochs with 1000 generated demonstrations, and evaluate multiple checkpoints saved between the 1000th and 2000th epochs to select the best-performing policy. Testing various epochs is essential for finding optimal performance.

Demo 2: Data Generation and Policy Training for Humanoid Robot Locomanipulation with Unitree G1

In this demo, we showcase the integration of locomotion and manipulation capabilities within a single humanoid robot system. This locomanipulation environment enables data collection for complex tasks that combine navigation and object manipulation. The demonstration follows a multi-step process: first, it generates pick and place tasks similar to Demo 1, then introduces a navigation component that uses specialized scripts to generate scenes where the humanoid robot must move from point A to point B. The robot picks up an object at the initial location (point A) and places it at the target destination (point B).
G1 humanoid robot with locomanipulation performing a pick and place task

Note

Locomotion policy training

The locomotion policy used in this integration example was trained using the AGILE framework. AGILE is an officially supported humanoid control training pipeline that leverages the manager based environment in Isaac Lab. It will also be seamlessly integrated with other evaluation and deployment tools across Isaac products. This allows teams to rely on a single, maintained stack covering all necessary infrastructure and tooling for policy training, with easy export to real-world deployment. The AGILE repository contains updated pre-trained policies with separate upper and lower body policies for flexibtility. They have been verified in the real world and can be directly deployed. Users can also train their own locomotion or whole-body control policies using the AGILE framework.
Generate the manipulation dataset

The same data generation and policy training steps from Demo 1.0 can be applied to the G1 humanoid robot with locomanipulation capabilities. This demonstration shows how to train a G1 robot to perform pick and place tasks with full-body locomotion and manipulation.

The process follows the same workflow as Demo 1.0, but uses the Isaac-PickPlace-Locomanipulation-G1-Abs-v0 task environment.

Follow the same data collection, annotation, and generation process as demonstrated in Demo 1.0, but adapted for the G1 locomanipulation task.

Hint

If desired, data collection and annotation can be done using the same commands as the prior examples for validation of the dataset.

The G1 robot with locomanipulation capabilities combines full-body locomotion with manipulation to perform pick and place tasks.

Note that the following commands are only for your reference and dataset validation purposes - they are not required for this demo.

To collect demonstrations:

./isaaclab.sh -p scripts/tools/record_demos.py \
--device cpu \
--task Isaac-PickPlace-Locomanipulation-G1-Abs-v0 \
--teleop_device handtracking \
--dataset_file ./datasets/dataset_g1_locomanip.hdf5 \
--num_demos 5 --enable_pinocchio

Note

Depending on how the Apple Vision Pro app was initialized, the hands of the operator might be very far up or far down compared to the hands of the G1 robot. If this is the case, you can click Stop AR in the AR tab in Isaac Lab, and move the AR Anchor prim. Adjust it down to bring the hands of the operator lower, and up to bring them higher. Click Start AR to resume teleoperation session. Make sure to match the hands of the robot before clicking Play in the Apple Vision Pro, otherwise there will be an undesired large force generated initially.

You can replay the collected demonstrations by running:

./isaaclab.sh -p scripts/tools/replay_demos.py \
--device cpu \
--task Isaac-PickPlace-Locomanipulation-G1-Abs-v0 \
--dataset_file ./datasets/dataset_g1_locomanip.hdf5 --enable_pinocchio

To annotate the demonstrations:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
--device cpu \
--task Isaac-Locomanipulation-G1-Abs-Mimic-v0 \
--input_file ./datasets/dataset_g1_locomanip.hdf5 \
--output_file ./datasets/dataset_annotated_g1_locomanip.hdf5 --enable_pinocchio

If you skipped the prior collection and annotation step, download the pre-recorded annotated dataset dataset_annotated_g1_locomanip.hdf5 from here: [Annotated G1 Dataset]. Place the file under IsaacLab/datasets and run the following command to generate a new dataset with 1000 demonstrations.

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu --headless --num_envs 20 --generation_num_trials 1000 --enable_pinocchio \
--input_file ./datasets/dataset_annotated_g1_locomanip.hdf5 --output_file ./datasets/generated_dataset_g1_locomanip.hdf5

Train a manipulation-only policy

At this point you can train a policy that only performs manipulation tasks using the generated dataset:

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-PickPlace-Locomanipulation-G1-Abs-v0 --algo bc \
--normalize_training_actions \
--dataset ./datasets/generated_dataset_g1_locomanip.hdf5

Visualize the results

Visualize the trained policy performance:

./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu \
--enable_pinocchio \
--task Isaac-PickPlace-Locomanipulation-G1-Abs-v0 \
--num_rollouts 50 \
--horizon 400 \
--norm_factor_min <NORM_FACTOR_MIN> \
--norm_factor_max <NORM_FACTOR_MAX> \
--checkpoint /PATH/TO/desired_model_checkpoint.pth

Note

Change the NORM_FACTOR in the above command with the values generated in the training step.

Tip

If you don’t see expected performance results: Always test policies from various checkpoint epochs. Different epochs can produce significantly different results, so evaluate multiple checkpoints to find the optimal model.
G1 humanoid robot performing a pick and place task

The trained policy performing the pick and place task in Isaac Lab.

Note

Expected Success Rates and Timings for Locomanipulation Pick and Place Task

    Success rate for data generation depends on the quality of human demonstrations (how well the user performs them) and dataset annotation quality. Both data generation and downstream policy success are sensitive to these factors and can show high variance. See Common Pitfalls when Generating Data for tips to improve your dataset.

    Data generation success for this task is typically 65-82% over 1000 demonstrations, taking 18-40 minutes depending on GPU hardware and success rate (18 minutes on a RTX ADA 6000 @ 82% success rate).

    Behavior Cloning (BC) policy success is typically 75-85% (evaluated on 50 rollouts) when trained on 1000 generated demonstrations for 2000 epochs (default), depending on demonstration quality. Training takes approximately 40 minutes on a RTX ADA 6000.

    Recommendation: Train for 2000 epochs with 1000 generated demonstrations, and evaluate multiple checkpoints saved between the 1000th and 2000th epochs to select the best-performing policy. Testing various epochs is essential for finding optimal performance.

Generate the dataset with manipulation and point-to-point navigation

To create a comprehensive locomanipulation dataset that combines both manipulation and navigation capabilities, you can generate a navigation dataset using the manipulation dataset from the previous step as input.
G1 humanoid robot combining navigation with locomanipulation

G1 humanoid robot performing locomanipulation with navigation capabilities.

The locomanipulation dataset generation process takes the previously generated manipulation dataset and creates scenarios where the robot must navigate from one location to another while performing manipulation tasks. This creates a more complex dataset that includes both locomotion and manipulation behaviors.

To generate the locomanipulation dataset, use the following command:

./isaaclab.sh -p \
    scripts/imitation_learning/locomanipulation_sdg/generate_data.py \
    --device cpu \
    --kit_args="--enable isaacsim.replicator.mobility_gen" \
    --task="Isaac-G1-SteeringWheel-Locomanipulation" \
    --dataset ./datasets/generated_dataset_g1_locomanip.hdf5 \
    --num_runs 1 \
    --lift_step 60 \
    --navigate_step 130 \
    --enable_pinocchio \
    --output_file ./datasets/generated_dataset_g1_locomanipulation_sdg.hdf5 \
    --enable_cameras

Note

The input dataset (--dataset) should be the manipulation dataset generated in the previous step. You can specify any output filename using the --output_file_name parameter.

The key parameters for locomanipulation dataset generation are:

    --lift_step 70: Number of steps for the lifting phase of the manipulation task. This should mark the point immediately after the robot has grasped the object.

    --navigate_step 120: Number of steps for the navigation phase between locations. This should make the point where the robot has lifted the object and is ready to walk.

    --output_file: Name of the output dataset file

This process creates a dataset where the robot performs the manipulation task at different locations, requiring it to navigate between points while maintaining the learned manipulation behaviors. The resulting dataset can be used to train policies that combine both locomotion and manipulation capabilities.

Note

You can visualize the robot trajectory results with the following script command:

./isaaclab.sh -p scripts/imitation_learning/locomanipulation_sdg/plot_navigation_trajectory.py --input_file datasets/generated_dataset_g1_locomanipulation_sdg.hdf5 --output_dir /PATH/TO/DESIRED_OUTPUT_DIR

The data generated from this locomanipulation pipeline can also be used to finetune an imitation learning policy using GR00T N1.5. To do this, you may convert the generated dataset to LeRobot format as expected by GR00T N1.5, and then run the finetuning script provided in the GR00T N1.5 repository. An example closed-loop policy rollout is shown in the video below:
Simulation rollout of GR00T N1.5 policy finetuned for locomanipulation

Simulation rollout of GR00T N1.5 policy finetuned for locomanipulation.

The policy shown above uses the camera image, hand poses, hand joint positions, object pose, and base goal pose as inputs. The output of the model is the target base velocity, hand poses, and hand joint positions for the next several timesteps.
Demo 3: Visuomotor Policy for a Humanoid Robot
GR-1 humanoid robot performing a pouring task
Download the Dataset

Download the pre-generated dataset from here and place it under IsaacLab/datasets/generated_dataset_gr1_nut_pouring.hdf5 (Note: The dataset size is approximately 12GB). The dataset contains 1000 demonstrations of a humanoid robot performing a pouring/placing task that was generated using Isaac Lab Mimic for the Isaac-NutPour-GR1T2-Pink-IK-Abs-Mimic-v0 task.

Hint

If desired, data collection, annotation, and generation can be done using the same commands as the prior examples.

The robot first picks up the red beaker and pours the contents into the yellow bowl. Then, it drops the red beaker into the blue bin. Lastly, it places the yellow bowl onto the white scale. See the video in the Visualize the results section below for a visual demonstration of the task.

The success criteria for this task requires the red beaker to be placed in the blue bin, the green nut to be in the yellow bowl, and the yellow bowl to be placed on top of the white scale.

Attention

The following commands are only for your reference and are not required for this demo.

To collect demonstrations:

./isaaclab.sh -p scripts/tools/record_demos.py \
--device cpu \
--task Isaac-NutPour-GR1T2-Pink-IK-Abs-v0 \
--teleop_device handtracking \
--dataset_file ./datasets/dataset_gr1_nut_pouring.hdf5 \
--num_demos 5 --enable_pinocchio

Since this is a visuomotor environment, the --enable_cameras flag must be added to the annotation and data generation commands.

To annotate the demonstrations:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
--device cpu \
--enable_cameras \
--rendering_mode balanced \
--task Isaac-NutPour-GR1T2-Pink-IK-Abs-Mimic-v0 \
--input_file ./datasets/dataset_gr1_nut_pouring.hdf5 \
--output_file ./datasets/dataset_annotated_gr1_nut_pouring.hdf5 --enable_pinocchio

Warning

There are multiple right eef annotations for this task. Annotations for subtasks for the same eef cannot have the same action index. Make sure to annotate the right eef subtasks with different action indices.

To generate the dataset:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu \
--headless \
--enable_pinocchio \
--enable_cameras \
--rendering_mode balanced \
--task Isaac-NutPour-GR1T2-Pink-IK-Abs-Mimic-v0 \
--generation_num_trials 1000 \
--num_envs 5 \
--input_file ./datasets/dataset_annotated_gr1_nut_pouring.hdf5 \
--output_file ./datasets/generated_dataset_gr1_nut_pouring.hdf5

Train a policy

Use Robomimic to train a visuomotor BC agent for the task.

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-NutPour-GR1T2-Pink-IK-Abs-v0 --algo bc \
--normalize_training_actions \
--dataset ./datasets/generated_dataset_gr1_nut_pouring.hdf5

The training script will normalize the actions in the dataset to the range [-1, 1]. The normalization parameters are saved in the model directory under PATH_TO_MODEL_DIRECTORY/logs/normalization_params.txt. Record the normalization parameters for later use in the visualization step.

Note

By default the trained models and logs will be saved to IsaacLab/logs/robomimic.

You can also post-train a GR00T foundation model to deploy a Vision-Language-Action policy for the task.

Please refer to the IsaacLabEvalTasks repository for more details.
Visualize the results

Visualize the results of the trained policy by running the following command, using the normalization parameters recorded in the prior training step:

./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu \
--enable_pinocchio \
--enable_cameras \
--rendering_mode balanced \
--task Isaac-NutPour-GR1T2-Pink-IK-Abs-v0 \
--num_rollouts 50 \
--horizon 350 \
--norm_factor_min <NORM_FACTOR_MIN> \
--norm_factor_max <NORM_FACTOR_MAX> \
--checkpoint /PATH/TO/desired_model_checkpoint.pth

Note

Change the NORM_FACTOR in the above command with the values generated in the training step.

Tip

If you don’t see expected performance results: Test policies from various checkpoint epochs, not just the final one. Policy performance can vary substantially across training, and intermediate checkpoints often yield better results.
GR-1 humanoid robot performing a pouring task

The trained visuomotor policy performing the pouring task in Isaac Lab.

Note

Expected Success Rates and Timings for Visuomotor Nut Pour GR1T2 Task

    Success rate for data generation depends on the quality of human demonstrations (how well the user performs them) and dataset annotation quality. Both data generation and downstream policy success are sensitive to these factors and can show high variance. See Common Pitfalls when Generating Data for tips to improve your dataset.

    Data generation for 1000 demonstrations takes approximately 10 hours on a RTX ADA 6000.

    Behavior Cloning (BC) policy success is typically 50-60% (evaluated on 50 rollouts) when trained on 1000 generated demonstrations for 600 epochs (default). Training takes approximately 15 hours on a RTX ADA 6000.

    Recommendation: Train for 600 epochs with 1000 generated demonstrations, and evaluate multiple checkpoints saved between the 300th and 600th epochs to select the best-performing policy. Testing various epochs is critical for achieving optimal performance.

Common Pitfalls when Generating Data

Demonstrations are too long:

    Longer time horizon is harder to learn for a policy

    Start close to the first object and minimize motions

Demonstrations are not smooth:

    Irregular motion is hard for policy to decipher

    Better teleop devices result in better data (i.e. SpaceMouse is better than Keyboard)

Pauses in demonstrations:

    Pauses are difficult to learn

    Keep the human motions smooth and fluid

Excessive number of subtasks:

    Minimize the number of defined subtasks for completing a given task

    Less subtacks results in less stitching of trajectories, yielding higher data generation success rate

Lack of action noise:

    Action noise makes policies more robust

Recording cropped too tight:

    If recording stops on the frame the success term triggers, it may not re-trigger during replay

    Allow for some buffer at the end of recording

Non-deterministic replay:

    Physics in IsaacLab are not deterministically reproducible when using env.reset so demonstrations may fail on replay

    Collect more human demos than needed, use the ones that succeed during annotation

    All data in Isaac Lab Mimic generated HDF5 file represent a successful demo and can be used for training (even if non-determinism causes failure when replayed)

Creating Your Own Isaac Lab Mimic Compatible Environments
How it works

Isaac Lab Mimic works by splitting the input demonstrations into subtasks. Subtasks are user-defined segments in the demonstrations that are common to all demonstrations. Examples for subtasks are “grasp an object”, “move end effector to some pre-defined position”, “release object” etc.. Note that most subtasks are defined with respect to some object that the robot interacts with.

Subtasks need to be defined, and then annotated for each input demonstration. Annotation can either happen algorithmically by defining heuristics for subtask detection, as was done in the example above, or it can be done manually.

With subtasks defined and annotated, Isaac Lab Mimic utilizes a small number of helper methods to then transform the subtask segments, and generate new demonstrations by stitching them together to match the new task at hand.

For each thusly generated candidate demonstration, Isaac Lab Mimic uses a boolean success criteria to determine whether the demonstration succeeded in performing the task, and if so, add it to the output dataset. Success rate of candidate demonstrations can be as high as 70% in simple cases, and as low as <1%, depending on the difficulty of the task, and the complexity of the robot itself.
Configuration and subtask definition

Subtasks, among other configuration settings for Isaac Lab Mimic, are defined in a Mimic compatible environment configuration class that is created by extending the existing environment config with additional Mimic required parameters.

All Mimic required config parameters are specified in the MimicEnvCfg class.

The config class FrankaCubeStackIKRelMimicEnvCfg serves as an example of creating a Mimic compatible environment config class for the Franka stacking task that was used in the examples above.

The DataGenConfig member contains various parameters that influence how data is generated. It is initially sufficient to just set the name parameter, and revise the rest later.

Subtasks are a list of SubTaskConfig objects, of which the most important members are:

    object_ref is the object that is being interacted with. This will be used to adjust motions relative to this object during data generation. Can be None if the current subtask does not involve any object.

    subtask_term_signal is the ID of the signal indicating whether the subtask is active or not.

For multi end-effector environments, subtask ordering between end-effectors can be enforced by specifying subtask constraints. These constraints are defined in the SubTaskConstraintConfig class.
Subtask annotation

Once the subtasks are defined, they need to be annotated in the source data. There are two methods to annotate source demonstrations for subtask boundaries: Manual annotation or using heuristics.

It is often easiest to perform manual annotations, since the number of input demonstrations is usually very small. To perform manual annotations, use the annotate_demos.py script without the --auto flag. Then press B to pause, N to continue, and S to annotate a subtask boundary.

For more accurate boundaries, or to speed up repeated processing of a given task for experiments, heuristics can be implemented to perform the same task. Heuristics are observations in the environment. An example how to add subtask terms can be found in source/isaaclab_tasks/isaaclab_tasks/manager_based/manipulation/stack/stack_env_cfg.py, where they are added as an observation group called SubtaskCfg. This example is using prebuilt heuristics, but custom heuristics are easily implemented.
Helpers for demonstration generation

Helpers needed for Isaac Lab Mimic are defined in the environment. All tasks that are to be used with Isaac Lab Mimic are derived from the ManagerBasedRLMimicEnv base class, and must implement the following functions:

    get_robot_eef_pose: Returns the current robot end effector pose in the same frame as used by the robot end effector controller.

    target_eef_pose_to_action: Takes a target pose and a gripper action for the end effector controller and returns an action which achieves the target pose.

    action_to_target_eef_pose: Takes an action and returns a target pose for the end effector controller.

    actions_to_gripper_actions: Takes a sequence of actions and returns the gripper actuation part of the actions.

    get_object_poses: Returns the pose of each object in the scene that is used for data generation.

    get_subtask_term_signals: Returns a dictionary of binary flags for each subtask in a task. The flag of true is set when the subtask has been completed and false otherwise.

The class FrankaCubeStackIKRelMimicEnv shows an example of creating a Mimic compatible environment from an existing Isaac Lab environment.
Registering the environment

Once both Mimic compatible environment and environment config classes have been created, a new Mimic compatible environment can be registered using gym.register. For the Franka stacking task in the examples above, the Mimic environment is registered as Isaac-Stack-Cube-Franka-IK-Rel-Mimic-v0.

The registered environment is now ready to be used with Isaac Lab Mimic.
Tips for Successful Data Generation with Isaac Lab Mimic
Splitting subtasks

A general rule of thumb is to split the task into as few subtasks as possible, while still being able to complete the task. Isaac Lab Mimic data generation uses linear interpolation to bridge and stitch together subtask segments. More subtasks result in more stitching of trajectories which can result in less smooth motions and more failed demonstrations. For this reason, it is often best to annoatate subtask boundaries where the robot’s motion is unlikely to collide with other objects.

For example, in the scenario below, there is a subtask partition after the robot’s left arm grasps the object. On the left, the subtask annotation is marked immediately after the grasp, while on the right, the annotation is marked after the robot has grasped and lifted the object. In the left case, the interpolation causes the robot’s left arm to collide with the table and it’s motion lags while on the right the motion is continuous and smooth.
Subtask splitting example

Motion lag/collision caused by poor subtask splitting (left)
Selecting number of interpolation steps

The number of interpolation steps between subtask segments can be specified in the SubTaskConfig class. Once transformed, the subtask segments don’t start/end at the same spot, thus to create a continuous motion, Isaac Lab Mimic will apply linear interpolation between the last point of the previous subtask and the first point of the next subtask.

The number of interpolation steps can be tuned to control the smoothness of the generated demonstrations during this stitching process. The appropriate number of interpolation steps depends on the speed of the robot and the complexity of the task. A complex task with a large object reset distribution will have larger gaps between subtask segments and require more interpolation steps to create a smooth motion. Alternatively, a task with small gaps between subtask segments should use a small number of interpolation steps to avoid unnecessary motion lag caused by too many steps.

An example of how the number of interpolation steps can affect the generated demonstrations is shown below. In the example, an interpolation is applied to the right arm of the robot to bridge the gap between the left arm’s grasp and the right arm’s placement. With 0 steps, the right arm exhibits a jerky jump in motion while with 20 steps, the motion is laggy. With 5 steps, the motion is smoot

Augmented Imitation Learning

This section describes how to use Isaac Lab’s imitation learning capabilities with the visual augmentation capabilities of Cosmos models to generate demonstrations at scale to train visuomotor policies robust against visual variations.
Generating Demonstrations

We use the Isaac Lab Mimic feature that allows the generation of additional demonstrations automatically from a handful of annotated demonstrations.

Note

This section assumes you already have an annotated dataset of collected demonstrations. If you don’t, you can follow the instructions in Teleoperation and Imitation Learning with Isaac Lab Mimic to collect and annotate your own demonstrations.

In the following example, we will show you how to use Isaac Lab Mimic to generate additional demonstrations that can be used to train a visuomotor policy directly or can be augmented with visual variations using Cosmos (using the Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0 environment).

Note

The Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0 environment is similar to the standard visuomotor environment (Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Mimic-v0), but with the addition of segmentation masks, depth maps, and normal maps in the generated dataset. These additional modalities are required to get the best results from the visual augmentation done using Cosmos.

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu --enable_cameras --headless --num_envs 10 --generation_num_trials 1000 \
--input_file ./datasets/annotated_dataset.hdf5 --output_file ./datasets/mimic_dataset_1k.hdf5 \
--task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0 \
--rendering_mode performance

The number of demonstrations can be increased or decreased, 1000 demonstrations have been shown to provide good training results for this task.

Additionally, the number of environments in the --num_envs parameter can be adjusted to speed up data generation. The suggested number of 10 can be executed on a moderate laptop CPU. On a more powerful desktop machine, use a larger number of environments for a significant speedup of this step.
Cosmos Augmentation
HDF5 to MP4 Conversion

The hdf5_to_mp4.py script converts camera frames stored in HDF5 demonstration files to MP4 videos. It supports multiple camera modalities including RGB, segmentation, depth and normal maps. This conversion is necessary for visual augmentation using Cosmos as it only works with video files rather than HDF5 data.

Required Arguments

--input_file
	

Path to the input HDF5 file.

--output_dir
	

Directory to save the output MP4 files.

Optional Arguments

--input_keys
	

List of input keys to process from the HDF5 file. (default: [“table_cam”, “wrist_cam”, “table_cam_segmentation”, “table_cam_normals”, “table_cam_shaded_segmentation”, “table_cam_depth”])

--video_height
	

Height of the output video in pixels. (default: 704)

--video_width
	

Width of the output video in pixels. (default: 1280)

--framerate
	

Frames per second for the output video. (default: 30)

Note

The default input keys cover all camera modalities as per the naming convention followed in the Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-Mimic-v0 environment. We include an additional modality “table_cam_shaded_segmentation” which is not a part of the generated modalities from simulation in the HDF5 data file. Instead, it is automatically generated by this script using a combination of the segmentation and normal maps to get a pseudo-textured segmentation video for better controlling the Cosmos augmentation.

Note

We recommend using the default values given above for the output video height, width and framerate for the best results with Cosmos augmentation.

Example usage for the cube stacking task:

python scripts/tools/hdf5_to_mp4.py \
--input_file datasets/mimic_dataset_1k.hdf5 \
--output_dir datasets/mimic_dataset_1k_mp4

Running Cosmos for Visual Augmentation

After converting the demonstrations to MP4 format, you can use a Cosmos model to visually augment the videos. Follow the Cosmos documentation for details on the augmentation process. Visual augmentation can include changes to lighting, textures, backgrounds, and other visual elements while preserving the essential task-relevant features.

We use the RGB, depth and shaded segmentation videos from the previous step as input to the Cosmos model as seen below:
RGB, depth and segmentation control inputs to Cosmos

We provide an example augmentation output from Cosmos Transfer1 below:
Cosmos Transfer1 augmentation output

We recommend using the Cosmos Transfer1 model for visual augmentation as we found it to produce the best results in the form of a highly diverse dataset with a wide range of visual variations. You can refer to the installation instructions, the checkpoint download instructions and this example for reference on how to use Transfer1 for this usecase. We further recommend the following settings to be used with the Transfer1 model for this task:

Note

This workflow has been tested with commit e4055e39ee9c53165e85275bdab84ed20909714a of the Cosmos Transfer1 repository, and it is the recommended version to use. After cloning the Cosmos Transfer1 repository, checkout to this specific commit by running git checkout e4055e39ee9c53165e85275bdab84ed20909714a.

Hyperparameters

negative_prompt
	

“The video captures a game playing, with bad crappy graphics and cartoonish frames. It represents a recording of old outdated games. The images are very pixelated and of poor CG quality. There are many subtitles in the footage. Overall, the video is unrealistic and appears cg. Plane background.”

sigma_max
	

50

control_weight
	

“0.3,0.3,0.6,0.7”

hint_key
	

“blur,canny,depth,segmentation”

Another crucial aspect to get good augmentations is the set of prompts used to control the Cosmos generation. We provide a script, cosmos_prompt_gen.py, to construct prompts from a set of carefully chosen templates that handle various aspects of the augmentation process.

Required Arguments

--templates_path
	

Path to the file containing templates for the prompts.

Optional Arguments

--num_prompts
	

Number of prompts to generate (default: 1).

--output_path
	

Path to the output file to write generated prompts. (default: prompts.txt)

python scripts/tools/cosmos/cosmos_prompt_gen.py \
--templates_path scripts/tools/cosmos/transfer1_templates.json \
--num_prompts 10 --output_path prompts.txt

In case you want to create your own prompts, we suggest you refer to the following guidelines:

    Keep the prompts as detailed as possible. It is best to have some instruction on how the generation should handle each visible object/region of interest. For instance, the prompts that we provide cover explicit details for the table, lighting, background, robot arm, cubes, and the general setting.

    Try to keep the augmentation instructions as realistic and coherent as possible. The more unrealistic or unconventional the prompt is, the worse the model does at retaining key features of the input control video(s).

    Keep the augmentation instructions in-sync for each aspect. What we mean by this is that the augmentation for all the objects/regions of interest should be coherent and conventional with respect to each other. For example, it is better to have a prompt such as “The table is of old dark wood with faded polish and food stains and the background consists of a suburban home” instead of something like “The table is of old dark wood with faded polish and food stains and the background consists of a spaceship hurtling through space”.

    It is vital to include details on key aspects of the input control video(s) that should be retained or left unchanged. In our prompts, we very clearly mention that the cube colors should be left unchanged such that the bottom cube is blue, the middle is red and the top is green. Note that we not only mention what should be left unchanged but also give details on what form that aspect currently has.

Example command to use the Cosmos Transfer1 model for this usecase:

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:=0}"
export CHECKPOINT_DIR="${CHECKPOINT_DIR:=./checkpoints}"
export NUM_GPU="${NUM_GPU:=1}"
PYTHONPATH=$(pwd) torchrun --nproc_per_node=$NUM_GPU --nnodes=1 --node_rank=0 cosmos_transfer1/diffusion/inference/transfer.py \
    --checkpoint_dir $CHECKPOINT_DIR \
    --video_save_folder outputs/cosmos_dataset_1k_mp4 \
    --controlnet_specs ./controlnet_specs/demo_0.json \
    --offload_text_encoder_model \
    --offload_guardrail_models \
    --num_gpus $NUM_GPU

Example ./controlnet_specs/demo_0.json json file to use with the above command:

{
    "prompt": "A robotic arm is picking up and stacking cubes inside a foggy industrial scrapyard at dawn, surrounded by piles of old robotic parts and twisted metal. The background includes large magnetic cranes, rusted conveyor belts, and flickering yellow floodlights struggling to penetrate the fog. The robot arm is bright teal with a glossy surface and silver stripes on the outer edges; the joints rotate smoothly and the pistons reflect a pale cyan hue. The robot arm is mounted on a table that is light oak wood with a natural grain pattern and a glossy varnish that reflects overhead lights softly; small burn marks dot one corner. The arm is connected to the base mounted on the table. The bottom cube is deep blue, the second cube is bright red, and the top cube is vivid green, maintaining their correct order after stacking. Sunlight pouring in from a large, open window bathes the table and robotic arm in a warm golden light. The shadows are soft, and the scene feels natural and inviting with a slight contrast between light and shadow.",
    "negative_prompt": "The video captures a game playing, with bad crappy graphics and cartoonish frames. It represents a recording of old outdated games. The images are very pixelated and of poor CG quality. There are many subtitles in the footage. Overall, the video is unrealistic and appears cg. Plane background.",
    "input_video_path" : "mimic_dataset_1k_mp4/demo_0_table_cam.mp4",
    "sigma_max": 50,
    "vis": {
        "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam.mp4",
        "control_weight": 0.3
    },
    "edge": {
        "control_weight": 0.3
    },
    "depth": {
        "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam_depth.mp4",
        "control_weight": 0.6
    },
    "seg": {
        "input_control": "mimic_dataset_1k_mp4/demo_0_table_cam_shaded_segmentation.mp4",
        "control_weight": 0.7
    }
}

MP4 to HDF5 Conversion

The mp4_to_hdf5.py script converts the visually augmented MP4 videos back to HDF5 format for training. This step is crucial as it ensures the augmented visual data is in the correct format for training visuomotor policies in Isaac Lab and pairs the videos with the corresponding demonstration data from the original dataset.

Required Arguments

--input_file
	

Path to the input HDF5 file containing the original demonstrations.

--videos_dir
	

Directory containing the visually augmented MP4 videos.

--output_file
	

Path to save the new HDF5 file with augmented videos.

Note

The input HDF5 file is used to preserve the non-visual data (such as robot states and actions) while replacing the visual data with the augmented versions.

Important

The visually augmented MP4 files must follow the naming convention demo_{demo_id}_*.mp4, where:

    demo_id matches the demonstration ID from the original MP4 file

    * signifies that the file name can be as per user preference starting from this point

This naming convention is required for the script to correctly pair the augmented videos with their corresponding demonstrations.

Example usage for the cube stacking task:

python scripts/tools/mp4_to_hdf5.py \
--input_file datasets/mimic_dataset_1k.hdf5 \
--videos_dir datasets/cosmos_dataset_1k_mp4 \
--output_file datasets/cosmos_dataset_1k.hdf5

Pre-generated Dataset

We provide a pre-generated dataset in HDF5 format containing visually augmented demonstrations for the cube stacking task. This dataset can be used if you do not wish to run Cosmos locally to generate your own augmented data. The dataset is available on Hugging Face and contains both (as separate dataset files), original and augmented demonstrations, that can be used for training visuomotor policies.
Merging Datasets

The merge_hdf5_datasets.py script combines multiple HDF5 datasets into a single file. This is useful when you want to combine the original demonstrations with the augmented ones to create a larger, more diverse training dataset.

Required Arguments

--input_files
	

A list of paths to HDF5 files to merge.

Optional Arguments

--output_file
	

File path to merged output. (default: merged_dataset.hdf5)

Tip

Merging datasets can help improve policy robustness by exposing the model to both original and augmented visual conditions during training.

Example usage for the cube stacking task:

python scripts/tools/merge_hdf5_datasets.py \
--input_files datasets/mimic_dataset_1k.hdf5 datasets/cosmos_dataset_1k.hdf5 \
--output_file datasets/mimic_cosmos_dataset.hdf5

Model Training and Evaluation
Robomimic Setup

As an example, we will train a BC agent implemented in Robomimic to train a policy. Any other framework or training method could be used.

To install the robomimic framework, use the following commands:

# install the dependencies
sudo apt install cmake build-essential
# install python module (for robomimic)
./isaaclab.sh -i robomimic

Training an agent

Using the generated data, we can now train a visuomotor BC agent for Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0:

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0 --algo bc \
--dataset ./datasets/mimic_cosmos_dataset.hdf5 \
--name bc_rnn_image_franka_stack_mimic_cosmos

Note

By default the trained models and logs will be saved to IssacLab/logs/robomimic.
Evaluation

The robust_eval.py script evaluates trained visuomotor policies in simulation. This evaluation helps assess how well the policy generalizes to different visual variations and whether the visually augmented data has improved the policy’s robustness.

Below is an explanation of the different settings used for evaluation:

Evaluation Settings

Vanilla
	

Exact same setting as that used during Mimic data generation.

Light Intensity
	

Light intensity/brightness is varied, all other aspects remain the same.

Light Color
	

Light color is varied, all other aspects remain the same.

Light Texture (Background)
	

Light texture/background is varied, all other aspects remain the same.

Table Texture
	

Table’s visual texture is varied, all other aspects remain the same.

Robot Arm Texture
	

Robot arm’s visual texture is varied, all other aspects remain the same.

Required Arguments

--task
	

Name of the environment.

--input_dir
	

Directory containing the model checkpoints to evaluate.

Optional Arguments

--start_epoch
	

Epoch of the checkpoint to start the evaluation from. (default: 100)

--horizon
	

Step horizon of each rollout. (default: 400)

--num_rollouts
	

Number of rollouts per model per setting. (default: 15)

--num_seeds
	

Number of random seeds to evaluate. (default: 3)

--seeds
	

List of specific seeds to use instead of random ones.

--log_dir
	

Directory to write results to. (default: /tmp/policy_evaluation_results)

--log_file
	

Name of the output file. (default: results)

--norm_factor_min
	

Minimum value of the action space normalization factor.

--norm_factor_max
	

Maximum value of the action space normalization factor.

--disable_fabric
	

Whether to disable fabric and use USD I/O operations.

--enable_pinocchio
	

Whether to enable Pinocchio for IK controllers.

Note

The evaluation results will help you understand if the visual augmentation has improved the policy’s performance and robustness. Compare these results with evaluations on the original dataset to measure the impact of augmentation.

Example usage for the cube stacking task:

./isaaclab.sh -p scripts/imitation_learning/robomimic/robust_eval.py \
--task Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0 \
--input_dir logs/robomimic/Isaac-Stack-Cube-Franka-IK-Rel-Visuomotor-Cosmos-v0/bc_rnn_image_franka_stack_mimic_cosmos/*/models \
--log_dir robust_results/bc_rnn_image_franka_stack_mimic_cosmos \
--log_file result \
--enable_cameras \
--seeds 0 \
--num_rollouts 15 \
--rendering_mode performance

Note

This script can take over a day or even longer to run (depending on the hardware being used). This behavior is expected.

We use the above script to compare models trained with 1000 Mimic-generated demonstrations, 2000 Mimic-generated demonstrations and 2000 Cosmos-Mimic-generated demonstrations (1000 original mimic + 1000 Cosmos augmented) respectively. We use the same seeds (0, 1000 and 5000) for all three models and provide the metrics (averaged across best checkpoints for each seed) below:

Model Comparison

Evaluation Setting
	

Mimic 1k Baseline
	

Mimic 2k Baseline
	

Cosmos-Mimic 2k

Vanilla
	

62%
	

96.6%
	

86.6%

Light Intensity
	

11.1%
	

20%
	

62.2%

Light Color
	

24.6%
	

30%
	

77.7%

Light Texture (Background)
	

16.6%
	

20%
	

68.8%

Table Texture
	

0%
	

0%
	

20%

Robot Arm Texture
	

0%
	

0%
	

4.4%

The above trained models’ checkpoints can be accessed here in case you wish to use the models directly.


SkillGen for Automated Demonstration Generation

SkillGen is an advanced demonstration generation system that enhances Isaac Lab Mimic by integrating motion planning. It generates high-quality, adaptive, collision-free robot demonstrations by combining human-provided subtask segments with automated motion planning.
What is SkillGen?

SkillGen addresses key limitations in traditional demonstration generation:

    Motion Quality: Uses cuRobo’s GPU-accelerated motion planner to generate smooth, collision-free trajectories

    Validity: Generates kinematically feasible plans between skill segments

    Diversity: Generates varied demonstrations through configurable sampling and planning parameters

    Adaptability: Generates demonstrations that can be adapted to new object placements and scene configurations during data generation

The system works by taking manually annotated human demonstrations, extracting localized subtask skills (see Subtasks in SkillGen), and using cuRobo to plan feasible motions between these skill segments while respecting robot kinematics and collision constraints.
Prerequisites

Before using SkillGen, you must understand:

    Teleoperation: How to control robots and record demonstrations using keyboard, SpaceMouse, or hand tracking

    Isaac Lab Mimic: The complete workflow including data collection, annotation, generation, and policy training

Important

Review the Teleoperation and Imitation Learning with Isaac Lab Mimic documentation thoroughly before proceeding with SkillGen.
Installation

SkillGen requires Isaac Lab, Isaac Sim, and cuRobo. Follow these steps in your Isaac Lab conda environment.
Step 1: Install and verify Isaac Sim and Isaac Lab

Follow the official Isaac Sim and Isaac Lab installation guide here.
Step 2: Install cuRobo

cuRobo provides the motion planning capabilities for SkillGen. This installation is tested to work with Isaac Lab’s PyTorch and CUDA requirements:

# One line installation of cuRobo (formatted for readability)
conda install -c nvidia cuda-toolkit=12.8 -y && \
export CUDA_HOME="$CONDA_PREFIX" && \
export PATH="$CUDA_HOME/bin:$PATH" && \
export LD_LIBRARY_PATH="$CUDA_HOME/lib:$LD_LIBRARY_PATH" && \
export TORCH_CUDA_ARCH_LIST="8.0+PTX" && \
pip install -e "git+https://github.com/NVlabs/curobo.git@ebb71702f3f70e767f40fd8e050674af0288abe8#egg=nvidia-curobo" --no-build-isolation

Note

    The commit hash ebb71702f3f70e767f40fd8e050674af0288abe8 is tested with Isaac Lab - using other versions may cause compatibility issues. This commit has the support for quad face mesh triangulation, required for cuRobo to parse usds as collision objects.

    cuRobo is installed from source and is editable installed. This means that the cuRobo source code will be cloned in the current directory under src/nvidia-curobo. Users can choose their working directory to install cuRobo.

    TORCH_CUDA_ARCH_LIST in the above command should match your GPU’s CUDA compute capability (e.g., 8.0 for A100, 8.6 for many RTX 30‑series, 8.9 for RTX 4090); the +PTX suffix embeds PTX for forward compatibility so newer GPUs can JIT‑compile when native SASS isn’t included.

Warning

cuRobo installation may fail if Isaac Sim environment scripts are sourced

Sourcing Omniverse Kit/Isaac Sim environment scripts (for example, setup_conda_env.sh) exports PYTHONHOME and PYTHONPATH to the Kit runtime and its pre-bundled Python packages. During cuRobo installation this can cause conda to import Omniverse’s bundled libraries (e.g., requests/urllib3) before initialization, resulting in a crash (often seen as a TypeError referencing omni.kit.pip_archive).

Do one of the following:

    Install cuRobo from a clean shell that has not sourced any Omniverse/Isaac Sim scripts.

    Temporarily reset or ignore inherited Python environment variables (notably PYTHONPATH and PYTHONHOME) before invoking Conda, so Kit’s Python does not shadow your Conda environment.

    Use Conda mechanisms that do not rely on shell activation and avoid inheriting the current shell’s Python variables.

After installation completes, you may source Isaac Lab/Isaac Sim scripts again for normal use.
Step 3: Install Rerun

For trajectory visualization during development:

pip install rerun-sdk==0.23

Note

Rerun Visualization Setup:

    Rerun is optional but highly recommended for debugging and validating planned trajectories during development

    Enable trajectory visualization by setting visualize_plan = True in the cuRobo planner configuration

    When enabled, cuRobo planner interface will stream planned end-effector trajectories, waypoints, and collision data to Rerun for interactive inspection

    Visualization helps identify planning issues, collision problems, and trajectory smoothness before full dataset generation

    Can also be ran with --headless to disable isaacsim visualization but still visualize and debug end effector trajectories

Step 4: Verify Installation

Test that cuRobo works with Isaac Lab:

# This should run without import errors
python -c "import curobo; print('cuRobo installed successfully')"

Tip

If you run into libstdc++.so.6: version 'GLIBCXX_3.4.30' not found error, you can try these commands to fix it:

conda config --env --set channel_priority strict
conda config --env --add channels conda-forge
conda install -y -c conda-forge "libstdcxx-ng>=12" "libgcc-ng>=12"

Download the SkillGen Dataset

We provide a pre-annotated dataset to help you get started quickly with SkillGen.
Dataset Contents

The dataset contains:

    Human demonstrations of Franka arm cube stacking

    Manually annotated subtask boundaries for each demonstration

    Compatible with both basic cube stacking and adaptive bin cube stacking tasks

Download and Setup

    Download the pre-annotated dataset by clicking here.

    Prepare the datasets directory and move the downloaded file:

# Make sure you are in the root directory of your Isaac Lab workspace
cd /path/to/your/IsaacLab

# Create the datasets directory if it does not exist
mkdir -p datasets

# Move the downloaded dataset into the datasets directory
mv /path/to/annotated_dataset_skillgen.hdf5 datasets/annotated_dataset_skillgen.hdf5

Tip

A major advantage of SkillGen is that the same annotated dataset can be reused across multiple related tasks (e.g., basic stacking and adaptive bin stacking). This avoids collecting and annotating new data per variant.

{Optional for the tasks in this tutorial} Collect a fresh dataset (source + annotated)

    If you want to collect a fresh source dataset and then create an annotated dataset for SkillGen, follow these commands. The user is expected to have knowledge of the Isaac Lab Mimic workflow.

Important pointers before you begin

    Using the provided annotated dataset is the fastest path to get started with SkillGen tasks in this tutorial.

    If you create your own dataset, SkillGen requires manual annotation of both subtask start and termination boundaries (no auto-annotation).

    Start boundary signals are mandatory for SkillGen; use --annotate_subtask_start_signals during annotation or data generation will fail.

    Keep your subtask definitions (object_ref, subtask_term_signal) consistent with the SkillGen environment config.

Record demonstrations (any teleop device is supported; replace spacemouse if needed):

./isaaclab.sh -p scripts/tools/record_demos.py \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--teleop_device spacemouse \
--dataset_file ./datasets/dataset_skillgen.hdf5 \
--num_demos 10

Annotate demonstrations for SkillGen (writes both term and start boundaries):

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/annotate_demos.py \
--device cpu \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--input_file ./datasets/dataset_skillgen.hdf5 \
--output_file ./datasets/annotated_dataset_skillgen.hdf5 \
--annotate_subtask_start_signals

Understanding Dataset Annotation

SkillGen requires datasets with annotated subtask start and termination boundaries. Auto-annotation is not supported.
Subtasks in SkillGen

Technical definition: A subtask is a contiguous demo segment that achieves a manipulation objective, defined via SubTaskConfig:

    object_ref: the object (or None) used as the spatial reference for this subtask

    subtask_term_signal: the binary termination signal name (transitions 0 to 1 when the subtask completes)

    subtask_start_signal: the binary start signal name (transitions 0 to 1 when the subtask begins; required for SkillGen)

The subtask localization process performs:

    detection of signal transition points (0 to 1) to identify subtask boundaries [t_start, t_end];

    extraction of the subtask segment between boundaries;

    computation of end-effector trajectories and key poses in an object- or task-relative frame (using object_ref if provided);

This converts absolute, scene-specific motions into object-relative skill segments that can be adapted to new object placements and scene configurations during data generation.
Manual Annotation Workflow

Contrary to the Isaac Lab Mimic workflow, SkillGen requires manual annotation of subtask start and termination boundaries. For example, for grasping a cube, the start signal is right before the gripper closes and the termination signal is right after the object is grasped. You can adjust the start and termination signals to fit your subtask definition.

Tip

Manual Annotation Controls:

    Press N to start/continue playback

    Press B to pause

    Press S to mark subtask boundary

    Press Q to skip current demonstration

When annotating the start and end signals for a skill segment (e.g., grasp, stack, etc.), pause the playback using B a few steps before the skill, annotate the start signal using S, and then resume playback using N. After the skill is completed, pause again a few steps later to annotate the end signal using S.
Data Generation with SkillGen

SkillGen transforms annotated demonstrations into diverse, high-quality datasets using motion planning.
How SkillGen Works

The SkillGen pipeline uses your annotated dataset and the environment’s Mimic API to synthesize new demonstrations:

    Subtask boundary use: Reads per-subtask start and termination indices from the annotated dataset

    Goal sampling: Samples target poses per subtask according to task constraints and datagen config

    Trajectory planning: Plans collision-free motions between subtask segments using cuRobo (when --use_skillgen)

    Trajectory stitching: Stitches skill segments and planned trajectories into complete demonstrations.

    Success evaluation: Validates task success terms; only successful trials are written to the output dataset

Usage Parameters

Key parameters for SkillGen data generation:

    --use_skillgen: Enables SkillGen planner (required)

    --generation_num_trials: Number of demonstrations to generate

    --num_envs: Parallel environments (tune based on GPU memory)

    --device: Computation device (cpu/cuda). Use cpu for stable physics

    --headless: Disable visualization for faster generation

Task 1: Basic Cube Stacking

Generate demonstrations for the standard Isaac Lab Mimic cube stacking task. In this task, the Franka robot must:

    Pick up the red cube and place it on the blue cube

    Pick up the green cube and place it on the red cube

    Final stack order: blue (bottom), red (middle), green (top).

Cube stacking task generated with SkillGen

Cube stacking dataset example.
Small-Scale Generation

Start with a small dataset to verify everything works:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu \
--num_envs 1 \
--generation_num_trials 10 \
--input_file ./datasets/annotated_dataset_skillgen.hdf5 \
--output_file ./datasets/generated_dataset_small_skillgen_cube_stack.hdf5 \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--use_skillgen

Full-Scale Generation

Once satisfied with small-scale results, generate a full training dataset:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu \
--headless \
--num_envs 1 \
--generation_num_trials 1000 \
--input_file ./datasets/annotated_dataset_skillgen.hdf5 \
--output_file ./datasets/generated_dataset_skillgen_cube_stack.hdf5 \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--use_skillgen

Note

    Use --headless to disable visualization for faster generation. Rerun visualization can be enabled by setting visualize_plan = True in the cuRobo planner configuration with --headless enabled as well for debugging.

    Adjust --num_envs based on your GPU memory (start with 1, increase gradually). The performance gain is not very significant when num_envs is greater than 1. A value of 5 seems to be a sweet spot for most GPUs to balance performance and memory usage between cuRobo instances and simulation environments.

    Generation time: ~90 to 120 minutes for one environment with --headless enabled for 1000 demonstrations on a RTX 6000 Ada GPU. Time depends on the GPU, the number of environments, and the success rate of the demonstrations (which depends on quality of the annotated dataset).

    cuRobo planner interface and configurations are described in cuRobo Interface Features.

Task 2: Adaptive Cube Stacking in a Bin

SkillGen can also be used to generate datasets for adaptive tasks. In this example, we generate a dataset for adaptive cube stacking in a narrow bin. The bin is placed at a fixed position and orientation in the workspace and a blue cube is placed at the center of the bin. The robot must generate successful demonstrations for stacking the red and green cubes on the blue cube without colliding with the bin.
Adaptive bin cube stacking task generated with SkillGen

Adaptive bin stacking data generation example.
Small-Scale Generation

Test the adaptive stacking setup:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu \
--num_envs 1 \
--generation_num_trials 10 \
--input_file ./datasets/annotated_dataset_skillgen.hdf5 \
--output_file ./datasets/generated_dataset_small_skillgen_bin_cube_stack.hdf5 \
--task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
--use_skillgen

Full-Scale Generation

Generate the complete adaptive stacking dataset:

./isaaclab.sh -p scripts/imitation_learning/isaaclab_mimic/generate_dataset.py \
--device cpu \
--headless \
--num_envs 1 \
--generation_num_trials 1000 \
--input_file ./datasets/annotated_dataset_skillgen.hdf5 \
--output_file ./datasets/generated_dataset_skillgen_bin_cube_stack.hdf5 \
--task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
--use_skillgen

Warning

Adaptive tasks typically have lower success rates and higher data generation time due to increased complexity. The time taken to generate the dataset is also longer due to lower success rates than vanilla cube stacking and difficult planning problems.

Note

If the pre-annotated dataset is used and the data generation command is run with --headless enabled, the generation time is typically around ~220 minutes for 1000 demonstrations for a single environment on a RTX 6000 Ada GPU.

Note

VRAM usage and GPU recommendations

Figures measured over 10 generated demonstrations on an RTX 6000 Ada.

        Vanilla Cube Stacking: 1 env ~9.3–9.6 GB steady; 5 envs ~21.8–22.2 GB steady (briefly higher during initialization).

        Adaptive Bin Cube Stacking: 1 env ~9.3–9.6 GB steady; 5 envs ~22.0–22.3 GB steady (briefly higher during initialization).

        Minimum recommended GPU: ≥24 GB VRAM for --num_envs 1–2; ≥48 GB VRAM for --num_envs up to ~5.

        To reduce VRAM: prefer --headless and keep --num_envs modest. Numbers can vary with scene assets and number of demonstrations.

Learning Policies from SkillGen Data

Similar to the Isaac Lab Mimic workflow, you can train imitation learning policies using the generated SkillGen datasets with Robomimic.
Basic Cube Stacking Policy

Train a state-based policy for the basic cube stacking task:

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--algo bc \
--dataset ./datasets/generated_dataset_skillgen_cube_stack.hdf5

Adaptive Bin Cube Stacking Policy

Train a policy for the more complex adaptive bin stacking:

./isaaclab.sh -p scripts/imitation_learning/robomimic/train.py \
--task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
--algo bc \
--dataset ./datasets/generated_dataset_skillgen_bin_cube_stack.hdf5

Note

The training script will save the model checkpoints in the model directory under IssacLab/logs/robomimic.
Evaluating Trained Policies

Test your trained policies:

# Basic cube stacking evaluation
./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu \
--task Isaac-Stack-Cube-Franka-IK-Rel-Skillgen-v0 \
--num_rollouts 50 \
--checkpoint /path/to/model_checkpoint.pth

# Adaptive bin cube stacking evaluation
./isaaclab.sh -p scripts/imitation_learning/robomimic/play.py \
--device cpu \
--task Isaac-Stack-Cube-Bin-Franka-IK-Rel-Mimic-v0 \
--num_rollouts 50 \
--checkpoint /path/to/model_checkpoint.pth

Note

Expected Success Rates and Recommendations for Cube Stacking and Bin Cube Stacking Tasks

    SkillGen data generation and downstream policy success are sensitive to the task and the quality of dataset annotation, and can show high variance.

    For cube stacking and bin cube stacking, data generation success is typically 40% to 70% when the dataset is properly annotated per the instructions.

    Behavior Cloning (BC) policy success from 1000 generated demonstrations trained for 2000 epochs (default) is typically 40% to 85% for these tasks, depending on data quality.

    Training the policy with 1000 demonstrations and for 2000 epochs takes about 30 to 35 minutes on a RTX 6000 Ada GPU. Training time increases with the number of demonstrations and epochs.

    For dataset generation time, see Task 1: Basic Cube Stacking and Task 2: Adaptive Cube Stacking in a Bin.

    Recommendation: Train for the default 2000 epochs with about 1000 generated demonstrations, and evaluate multiple checkpoints saved after the 1000th epoch to select the best-performing policy.

cuRobo Interface Features

This section summarizes the cuRobo planner interface and features. The SkillGen pipeline uses the cuRobo planner to generate collision-free motions between subtask segments. However, the user can use cuRobo as a standalone motion planner for your own tasks. The user can also implement their own motion planner by subclassing the base motion planner and implementing the same API.
Base Motion Planner (Extensible)

    Location: isaaclab_mimic/motion_planners/base_motion_planner.py

    Purpose: Uniform interface for all motion planners used by SkillGen

    Extensibility: New planners can be added by subclassing and implementing the same API; SkillGen consumes the API without code changes

cuRobo Planner (GPU, collision-aware)

    Location: isaaclab_mimic/motion_planners/curobo

    Multi-phase planning:

        Retreat → Contact → Approach phases per subtask

        Configurable collision filtering in contact phases

        For SkillGen, retreat and approach phases are collision-free. The transit phase is collision-checked.

    World synchronization:

        Updates robot state, attached objects, and collision spheres from the Isaac Lab scene each trial

        Dynamic attach/detach of objects during grasp/place

    Collision representation:

        Contact-aware sphere sets with per-phase enables/filters

    Outputs:

        Time-parameterized, collision-checked trajectories for stitching

    Tests:

        source/isaaclab_mimic/test/test_curobo_planner_cube_stack.py

        source/isaaclab_mimic/test/test_curobo_planner_franka.py

        source/isaaclab_mimic/test/test_generate_dataset_skillgen.py

cuRobo planner test on cube stack using Franka Panda robot

Cube stack planner test.
	
cuRobo planner test on obstacle avoidance using Franka Panda robot

Franka planner test.

These tests can also serve as a reference for how to use cuRobo as a standalone motion planner.

Note

For detailed cuRobo config creation and parameters, please see the file isaaclab_mimic/motion_planners/curobo/curobo_planner_config.py.
Generation Pipeline Integration

When --use_skillgen is enabled in generate_dataset.py, the following pipeline is executed:

    Randomize subtask boundaries: Randomize per-demo start and termination indices for each subtask using task-configured offset ranges.

    Build per-subtask trajectories: For each end-effector and subtask:

        Select a source demonstration segment (strategy-driven; respects coordination/sequential constraints)

        Transform the segment to the current scene (object-relative or coordination delta; optional first-pose interpolation)

        Wrap the transformed segment into a waypoint trajectory

    Transition between subtasks: - Plan a collision-aware transition with cuRobo to the subtask’s first waypoint (world sync, optional attach/detach), execute the planned waypoints, then resume the subtask trajectory

    Execute with constraints: - Execute waypoints step-by-step across end-effectors while enforcing subtask constraints (sequential, coordination with synchronous steps); optionally update planner visualization if enabled

    Record and export: - Accumulate states/observations/actions, set the episode success flag, and export the episode (the outer pipeline filters/consumes successes)

Visualization and Debugging

Users can visualize the planned trajectories and debug for collisions using Rerun-based plan visualizer. This can be enabled by setting visualize_plan = True in the cuRobo planner configuration. Note that rerun needs to be installed to visualize the planned trajectories. Refer to Step 3 in Installation for installation instructions.