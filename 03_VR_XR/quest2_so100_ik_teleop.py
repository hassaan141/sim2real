import argparse
import threading
from dataclasses import dataclass

from isaaclab.app import AppLauncher


TASK_NAME = "Quest-SO100-Marker-PickPlace-Teleop-v0"
ARM_JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
]
GRIPPER_JOINT_NAME = "gripper"
END_EFFECTOR_BODY = "gripper"


parser = argparse.ArgumentParser(description="ROS2 Quest2/SO100 end-effector IK teleop in Isaac Lab.")
parser.add_argument("--source", choices=["quest_pose", "cmd_pose"], default="quest_pose")
parser.add_argument("--task", default=TASK_NAME)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=101)
parser.add_argument("--disable_fabric", action="store_true", default=False)
parser.add_argument("--right-pose-topic", default="/q2r_right_hand_pose")
parser.add_argument("--right-input-topic", default="/q2r_right_hand_inputs")
parser.add_argument("--cmd-pose-topic", default="/robot/cmd_pose")
parser.add_argument("--enable-button", default="button_lower")
parser.add_argument("--reset-button", default="button_upper")
parser.add_argument("--position-scale", type=float, default=0.45)
parser.add_argument("--twist-scale", type=float, default=1.0)
parser.add_argument("--max-step", type=float, default=0.025)
parser.add_argument("--ik-damping", type=float, default=0.05)
parser.add_argument("--close-threshold", type=float, default=0.35)
parser.add_argument("--debug-control", action="store_true", default=False)
parser.add_argument("--debug-control-interval", type=int, default=60)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
args_cli.enable_cameras = True

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

import isaaclab_tasks  # noqa: F401
from isaaclab.controllers import DifferentialIKController, DifferentialIKControllerCfg
from isaaclab.managers import SceneEntityCfg
from isaaclab_tasks.utils import parse_env_cfg
from isaaclab.utils import math as math_utils

import so100_marker_pick_place.tasks  # noqa: F401


@dataclass
class QuestPoseSample:
    position: tuple[float, float, float] | None = None
    button_lower: bool = False
    button_upper: bool = False
    press_index: float = 0.0
    press_middle: float = 0.0
    stamp_ns: int = 0


@dataclass
class TwistSample:
    linear: tuple[float, float, float] | None = None
    angular: tuple[float, float, float] | None = None
    stamp_ns: int = 0


class Ros2TeleopState:
    """Small ROS2 subscriber wrapper used from Isaac's simulation loop."""

    def __init__(self) -> None:
        import rclpy
        from geometry_msgs.msg import PoseStamped, Twist

        try:
            from quest2ros2_msgs.msg import OVR2ROSInputs
        except Exception:
            OVR2ROSInputs = None

        self.rclpy = rclpy
        self.node = rclpy.create_node("quest2_so100_ik_teleop")
        self.lock = threading.Lock()
        self.quest = QuestPoseSample()
        self.twist = TwistSample()

        self.node.create_subscription(PoseStamped, args_cli.right_pose_topic, self._on_pose, 10)
        self.node.create_subscription(Twist, args_cli.cmd_pose_topic, self._on_twist, 10)
        if OVR2ROSInputs is not None:
            self.node.create_subscription(OVR2ROSInputs, args_cli.right_input_topic, self._on_inputs, 10)
        else:
            self.node.get_logger().warn(
                "quest2ros2_msgs is not sourced; Quest buttons/triggers are disabled. "
                "Build/source 03_VR_XR/quest2ros2_msgs for full Quest2 control."
            )

    def _now_ns(self) -> int:
        return self.node.get_clock().now().nanoseconds

    def _on_pose(self, msg) -> None:
        with self.lock:
            self.quest.position = (msg.pose.position.x, msg.pose.position.y, msg.pose.position.z)
            self.quest.stamp_ns = self._now_ns()

    def _on_inputs(self, msg) -> None:
        with self.lock:
            self.quest.button_lower = bool(msg.button_lower)
            self.quest.button_upper = bool(msg.button_upper)
            self.quest.press_index = float(msg.press_index)
            self.quest.press_middle = float(msg.press_middle)

    def _on_twist(self, msg) -> None:
        with self.lock:
            self.twist.linear = (msg.linear.x, msg.linear.y, msg.linear.z)
            self.twist.angular = (msg.angular.x, msg.angular.y, msg.angular.z)
            self.twist.stamp_ns = self._now_ns()

    def spin_once(self) -> None:
        self.rclpy.spin_once(self.node, timeout_sec=0.0)

    def read_quest(self) -> QuestPoseSample:
        with self.lock:
            return QuestPoseSample(**self.quest.__dict__)

    def read_twist(self) -> TwistSample:
        with self.lock:
            return TwistSample(**self.twist.__dict__)

    def close(self) -> None:
        self.node.destroy_node()


def _make_env():
    env_cfg = parse_env_cfg(
        args_cli.task,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )
    env_cfg.seed = args_cli.seed
    env = gym.make(args_cli.task, cfg=env_cfg)
    env.reset()
    return env


def _resolve_robot_handles(env):
    robot = env.unwrapped.scene["robot"]
    entity = SceneEntityCfg("robot", joint_names=ARM_JOINT_NAMES, body_names=[END_EFFECTOR_BODY])
    entity.resolve(env.unwrapped.scene)
    gripper_id = robot.data.joint_names.index(GRIPPER_JOINT_NAME)
    ee_body_id = entity.body_ids[0]
    ee_jacobi_idx = ee_body_id - 1 if robot.is_fixed_base else ee_body_id
    print(f"[INFO]: Robot joints: {robot.data.joint_names}")
    print(f"[INFO]: Robot bodies: {robot.data.body_names}")
    print(f"[INFO]: IK joints: {ARM_JOINT_NAMES} ids={entity.joint_ids}")
    print(f"[INFO]: IK body: {END_EFFECTOR_BODY} id={ee_body_id}, jacobian_index={ee_jacobi_idx}")
    return robot, entity.joint_ids, gripper_id, ee_body_id, ee_jacobi_idx


def _ee_pose_in_base(robot, ee_body_id: int):
    ee_pos_w = robot.data.body_pos_w[:, ee_body_id]
    ee_quat_w = robot.data.body_quat_w[:, ee_body_id]
    root_pos_w = robot.data.root_pos_w
    root_quat_w = robot.data.root_quat_w
    return math_utils.subtract_frame_transforms(root_pos_w, root_quat_w, ee_pos_w, ee_quat_w)


def _jacobian_in_base(robot, ee_jacobi_idx: int, joint_ids: list[int]):
    jacobian = robot.root_physx_view.get_jacobians()[:, ee_jacobi_idx, :, joint_ids]
    base_rot = robot.data.root_quat_w
    base_rot_matrix = math_utils.matrix_from_quat(math_utils.quat_inv(base_rot))
    jacobian[:, :3, :] = torch.bmm(base_rot_matrix, jacobian[:, :3, :])
    jacobian[:, 3:, :] = torch.bmm(base_rot_matrix, jacobian[:, 3:, :])
    return jacobian


def _quest_to_robot_delta(current: tuple[float, float, float], anchor: tuple[float, float, float]) -> torch.Tensor:
    dx = current[0] - anchor[0]
    dy = current[1] - anchor[1]
    dz = current[2] - anchor[2]
    # Quest2ROS commonly reports x=right, y=up, z=forward. The SO100 base frame
    # is treated here as x=forward, y=left, z=up.
    return torch.tensor(
        [dz, -dx, dy],
        dtype=torch.float32,
        device=args_cli.device,
    ) * args_cli.position_scale


def _limit_target_step(target: torch.Tensor, current: torch.Tensor) -> torch.Tensor:
    delta = target - current
    norm = torch.linalg.vector_norm(delta, dim=1, keepdim=True)
    scale = torch.clamp(args_cli.max_step / torch.clamp(norm, min=1.0e-6), max=1.0)
    return current + delta * scale


def _button(sample: QuestPoseSample, name: str) -> bool:
    if name in {"always", "none"}:
        return True
    return bool(getattr(sample, name, False))


def _run_teleop(env) -> None:
    import rclpy

    rclpy.init(args=None)
    ros = Ros2TeleopState()

    robot, arm_joint_ids, gripper_id, ee_body_id, ee_jacobi_idx = _resolve_robot_handles(env)
    ik_cfg = DifferentialIKControllerCfg(
        command_type="position",
        use_relative_mode=False,
        ik_method="dls",
        ik_params={"lambda_val": args_cli.ik_damping},
    )
    ik = DifferentialIKController(ik_cfg, num_envs=env.unwrapped.num_envs, device=env.unwrapped.device)

    joint_limits = robot.data.soft_joint_pos_limits[0]
    arm_lower = joint_limits[arm_joint_ids, 0]
    arm_upper = joint_limits[arm_joint_ids, 1]
    gripper_lower = joint_limits[gripper_id, 0]
    gripper_upper = joint_limits[gripper_id, 1]

    actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)
    current_ee_pos_b, current_ee_quat_b = _ee_pose_in_base(robot, ee_body_id)
    target_pos_b = current_ee_pos_b.clone()
    quest_anchor = None
    ee_anchor = target_pos_b.clone()
    previous_reset_pressed = False
    previous_twist_stamp = 0
    step_count = 0

    print("[INFO]: ROS2 IK teleop running.")
    print("[INFO]: Quest mode: hold lower button to move, press upper button to re-anchor.")
    print("[INFO]: cmd_pose mode: consuming geometry_msgs/Twist deltas from /robot/cmd_pose.")

    try:
        while simulation_app.is_running():
            ros.spin_once()
            current_ee_pos_b, current_ee_quat_b = _ee_pose_in_base(robot, ee_body_id)

            if args_cli.source == "quest_pose":
                sample = ros.read_quest()
                reset_pressed = _button(sample, args_cli.reset_button)
                enable_pressed = _button(sample, args_cli.enable_button)

                if sample.position is not None and (quest_anchor is None or reset_pressed and not previous_reset_pressed):
                    quest_anchor = sample.position
                    ee_anchor = current_ee_pos_b.clone()
                    target_pos_b = ee_anchor.clone()
                    print("[INFO]: Quest teleop anchor reset.")

                if sample.position is not None and quest_anchor is not None and enable_pressed:
                    delta = _quest_to_robot_delta(sample.position, quest_anchor).reshape(1, 3)
                    target_pos_b = ee_anchor + delta
                previous_reset_pressed = reset_pressed
                gripper_target = gripper_lower if sample.press_index > args_cli.close_threshold else gripper_upper

            else:
                sample = ros.read_twist()
                if sample.linear is not None and sample.stamp_ns != previous_twist_stamp:
                    previous_twist_stamp = sample.stamp_ns
                    delta = torch.tensor(
                        sample.linear,
                        dtype=torch.float32,
                        device=env.unwrapped.device,
                    ).reshape(1, 3) * args_cli.twist_scale
                    target_pos_b = target_pos_b + delta
                gripper_target = robot.data.joint_pos[0, gripper_id]

            target_pos_b = _limit_target_step(target_pos_b, current_ee_pos_b)
            ik.set_command(target_pos_b, ee_quat=current_ee_quat_b)
            jacobian = _jacobian_in_base(robot, ee_jacobi_idx, arm_joint_ids)
            joint_pos = robot.data.joint_pos[:, arm_joint_ids]
            joint_pos_des = ik.compute(current_ee_pos_b, current_ee_quat_b, jacobian, joint_pos)
            joint_pos_des = torch.clamp(joint_pos_des, arm_lower, arm_upper)

            actions[0, : len(arm_joint_ids)] = joint_pos_des[0]
            actions[0, len(arm_joint_ids)] = torch.clamp(gripper_target, gripper_lower, gripper_upper)
            env.step(actions)
            step_count += 1

            if args_cli.debug_control and step_count % max(args_cli.debug_control_interval, 1) == 0:
                err = target_pos_b - current_ee_pos_b
                print(
                    "[CONTROL DEBUG] "
                    f"target_pos_b={target_pos_b[0].detach().cpu().tolist()} "
                    f"ee_pos_b={current_ee_pos_b[0].detach().cpu().tolist()} "
                    f"err_norm={torch.linalg.vector_norm(err).item():.4f} "
                    f"action={actions[0].detach().cpu().tolist()}"
                )
    finally:
        ros.close()
        rclpy.shutdown()


def main() -> None:
    env = _make_env()
    try:
        _run_teleop(env)
    finally:
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
