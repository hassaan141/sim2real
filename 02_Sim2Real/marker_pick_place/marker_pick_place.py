import argparse

from isaaclab.app import AppLauncher

from marker_pick_place.teleop.dataset_recorder import RecorderConfig, TeleopDatasetRecorder
from marker_pick_place.teleop.lerobot_interface import SO100LeaderTeleop, SO100TeleopConfig


TASK_NAME = "Marker-PickPlace-Teleop"
HARD_CODED_PORT = "/dev/ttyACM0"
HARD_CODED_ID = "leader_arm_1"


parser = argparse.ArgumentParser(description="SO100 marker pick-place.")
parser.add_argument("--teleop", action="store_true", default=False)
parser.add_argument("--record", action="store_true", default=False)
parser.add_argument("--disable_fabric", action="store_true", default=False)
parser.add_argument("--num_envs", type=int, default=1)
parser.add_argument("--seed", type=int, default=101)
parser.add_argument("--debug-control", action="store_true", default=False)
parser.add_argument("--debug-control-interval", type=int, default=30)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

args_cli.enable_cameras = True

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
import isaaclab.sim as sim_utils
from isaaclab.sim import get_current_stage
from pxr import Usd, UsdPhysics, UsdShade

import isaaclab_tasks  # noqa: F401
from isaaclab_tasks.utils import parse_env_cfg
import marker_pick_place.tasks  # noqa: F401
from marker_pick_place.tasks.marker_env_cfg import refresh_config_cameras, sync_gripper_camera_to_frame


JOINT_NAMES = [
    "shoulder_pan",
    "shoulder_lift",
    "elbow_flex",
    "wrist_flex",
    "wrist_roll",
    "gripper",
]
CAMERA_SENSOR_NAMES = ["env_cam", "gripper_cam"]


def _print_robot_actuator_config(env) -> None:
    robot = env.unwrapped.scene["robot"]
    print("[INFO]: Loaded robot actuator config:")
    for actuator_name, actuator_cfg in robot.cfg.actuators.items():
        print(
            "[INFO]: "
            f"{actuator_name}: joints={actuator_cfg.joint_names_expr}, "
            f"effort={actuator_cfg.effort_limit_sim}, "
            f"velocity={actuator_cfg.velocity_limit_sim}, "
            f"stiffness={actuator_cfg.stiffness}, "
            f"damping={actuator_cfg.damping}"
        )
    print(f"[INFO]: Robot joint order: {robot.data.joint_names}")
    print(f"[INFO]: Action space: {env.action_space}")


def _format_joint_values(values: torch.Tensor, precision: int = 3) -> str:
    values_cpu = values.detach().cpu().tolist()
    return ", ".join(
        f"{name}={value:.{precision}f}" for name, value in zip(JOINT_NAMES, values_cpu)
    )


def _resolve_joint_indices(env) -> torch.Tensor:
    robot = env.unwrapped.scene["robot"]
    indices = []
    for joint_name in JOINT_NAMES:
        if joint_name not in robot.data.joint_names:
            raise RuntimeError(
                f"Joint '{joint_name}' not found in robot joints: {robot.data.joint_names}"
            )
        indices.append(robot.data.joint_names.index(joint_name))
    return torch.tensor(indices, dtype=torch.long, device=env.unwrapped.device)


def _print_runtime_joint_metadata(env, joint_indices: torch.Tensor) -> None:
    robot = env.unwrapped.scene["robot"]
    limits = robot.data.soft_joint_pos_limits[0, joint_indices].detach().cpu()
    print("[INFO]: Runtime joint position limits (rad):")
    for name, limit in zip(JOINT_NAMES, limits):
        print(f"[INFO]:   {name}: lower={limit[0]:.4f}, upper={limit[1]:.4f}")


def _print_physics_debug(env) -> None:
    stage = get_current_stage()
    robot = env.unwrapped.scene["robot"]
    print("[INFO]: Runtime physics debug:")
    print(
        "[INFO]:   robot self-collisions="
        f"{robot.cfg.spawn.articulation_props.enabled_self_collisions}, "
        f"contact_sensors={robot.cfg.spawn.activate_contact_sensors}"
    )

    paths = [
        "/World/envs/env_0/Robot/gripper/collisions/Fixed_Jaw/mesh",
        "/World/envs/env_0/Robot/jaw/collisions/Moving_Jaw/mesh",
    ]
    banana_prim = stage.GetPrimAtPath("/World/envs/env_0/Banana")
    if banana_prim.IsValid():
        for descendant in Usd.PrimRange(banana_prim):
            if descendant.GetTypeName() == "Mesh":
                paths.append(str(descendant.GetPath()))

    for prim_path in paths:
        prim = stage.GetPrimAtPath(prim_path)
        if not prim.IsValid():
            print(f"[WARN]:   missing physics prim: {prim_path}")
            continue
        collision = UsdPhysics.CollisionAPI(prim)
        mesh_collision = UsdPhysics.MeshCollisionAPI(prim)
        binding = UsdShade.MaterialBindingAPI(prim)
        material_rel = binding.GetDirectBindingRel("physics") if binding else None
        print(
            "[INFO]:   "
            f"{prim_path}: collision="
            f"{collision.GetCollisionEnabledAttr().Get() if collision else None}, "
            f"approx={mesh_collision.GetApproximationAttr().Get() if mesh_collision else None}, "
            f"physics_material={material_rel.GetTargets() if material_rel else []}"
        )


def _print_control_debug(
    step_count: int,
    sample,
    action: torch.Tensor,
    joint_pos: torch.Tensor,
    joint_vel: torch.Tensor,
) -> None:
    error = action - joint_pos
    print(f"[CONTROL DEBUG] step={step_count}")
    print(f"[CONTROL DEBUG] raw leader deg: {_format_joint_values(sample.raw_deg)}")
    print(f"[CONTROL DEBUG] normalized: {_format_joint_values(sample.normalized)}")
    print(f"[CONTROL DEBUG] target rad: {_format_joint_values(action)}")
    print(f"[CONTROL DEBUG] actual rad: {_format_joint_values(joint_pos)}")
    print(f"[CONTROL DEBUG] error rad: {_format_joint_values(error)}")
    print(f"[CONTROL DEBUG] velocity rad/s: {_format_joint_values(joint_vel)}")


def _disable_camera_pipeline(env_cfg) -> None:
    """Keep control-only runs from paying the camera sensor/render cost."""
    env_cfg.scene.env_cam = None
    env_cfg.scene.gripper_cam = None
    env_cfg.events.startup_refresh_camera_xforms = None
    env_cfg.events.refresh_camera_xforms = None
    env_cfg.events.reset_sync_gripper_camera = None
    env_cfg.events.sync_gripper_camera = None

    env_cfg.observations.visual.rgb_env = None
    env_cfg.observations.visual.rgb_gripper = None


def _warmup_render(steps: int = 12) -> None:
    sim = sim_utils.SimulationContext.instance()
    if sim is None:
        return
    for _ in range(steps):
        sim.render()


def _force_camera_refresh(env, cycles: int = 2) -> None:
    sim = sim_utils.SimulationContext.instance()
    for _ in range(cycles):
        refresh_config_cameras(env.unwrapped, None, ["env_cam"])
        sync_gripper_camera_to_frame(env.unwrapped, None)
        if sim is not None:
            sim.render()
        for name in CAMERA_SENSOR_NAMES:
            if name in env.unwrapped.scene.keys():
                env.unwrapped.scene[name].update(0.0, force_recompute=True)


def _camera_prim_path(env, camera_name: str) -> str:
    camera_cfg = getattr(env.unwrapped.scene.cfg, camera_name)
    return camera_cfg.prim_path.replace("{ENV_REGEX_NS}", "/World/envs/env_0")


def _rebind_viewport_cameras(env) -> None:
    try:
        from omni.kit.viewport.utility import get_active_viewport
    except Exception as exc:
        print(f"[WARN]: Could not import viewport utility for camera rebind: {exc}")
        return

    viewport = get_active_viewport()
    if viewport is None:
        return

    sim = sim_utils.SimulationContext.instance()
    previous_camera = viewport.camera_path
    for name in CAMERA_SENSOR_NAMES:
        viewport.set_active_camera(_camera_prim_path(env, name))
        if sim is not None:
            sim.render()
    if previous_camera:
        viewport.set_active_camera(previous_camera.pathString)


def _collect_cameras(env) -> dict:
    cameras = {}
    for obj in CAMERA_SENSOR_NAMES:
        if obj in env.unwrapped.scene.keys():
            camera_cfg = getattr(env.unwrapped.scene.cfg, obj)
            cameras[obj.removesuffix("_cam")] = {
                "height": camera_cfg.height,
                "width": camera_cfg.width,
            }
    return cameras


def _make_env():
    env_cfg = parse_env_cfg(
        TASK_NAME,
        device=args_cli.device,
        num_envs=args_cli.num_envs,
        use_fabric=not args_cli.disable_fabric,
    )
    env_cfg.seed = args_cli.seed
    if not args_cli.enable_cameras:
        _disable_camera_pipeline(env_cfg)

    env = gym.make(TASK_NAME, cfg=env_cfg)
    _print_robot_actuator_config(env)
    env.reset()
    joint_indices = _resolve_joint_indices(env)
    _print_runtime_joint_metadata(env, joint_indices)
    _print_physics_debug(env)
    if args_cli.enable_cameras:
        _force_camera_refresh(env)
        _rebind_viewport_cameras(env)
        _warmup_render()
    return env, joint_indices


def _run_viewer(env) -> None:
    actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)

    print("[INFO]: Marker pick-place environment running. Pass --teleop for leader-arm control.")
    while simulation_app.is_running():
        with torch.inference_mode():
            env.step(actions)


def _run_teleop(env, joint_indices: torch.Tensor) -> None:
    cameras = _collect_cameras(env) if args_cli.enable_cameras else {}
    if len(cameras) == 0:
        print("[INFO]: No cameras found - visual recording disabled")

    leader = SO100LeaderTeleop(
        device=env.unwrapped.device,
        config=SO100TeleopConfig(port=HARD_CODED_PORT, robot_id=HARD_CODED_ID),
    )
    leader.connect()

    recorder = TeleopDatasetRecorder(
        RecorderConfig(output_root="recordings", fps=30),
        cameras=cameras,
        device=env.unwrapped.device,
    )
    if args_cli.record:
        recorder.start()

    actions = torch.zeros(env.action_space.shape, device=env.unwrapped.device)

    print("[INFO]: Teleop running. Close the app to stop.")
    step_count = 0
    while simulation_app.is_running():
        with torch.inference_mode():
            sample = leader.read_sample()
            actions[0] = sample.target_rad
            obs, _, _, _, _ = env.step(actions)
            step_count += 1

            if (
                args_cli.debug_control
                and step_count % max(args_cli.debug_control_interval, 1) == 0
            ):
                robot = env.unwrapped.scene["robot"]
                joint_pos = robot.data.joint_pos[0, joint_indices]
                joint_vel = robot.data.joint_vel[0, joint_indices]
                _print_control_debug(
                    step_count,
                    sample,
                    actions[0],
                    joint_pos,
                    joint_vel,
                )

            if recorder.enabled:
                joint_pos = obs["policy"]["joint_pos_obs"][0]
                recorder.push(actions[0], joint_pos, obs.get("visual", {}))

    if recorder.enabled:
        recorder.stop()


def main() -> None:
    env, joint_indices = _make_env()
    try:
        if args_cli.teleop:
            _run_teleop(env, joint_indices)
        else:
            _run_viewer(env)
    finally:
        env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
