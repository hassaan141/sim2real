"""Train the banana pick-and-place policy with RSL-RL PPO.

Run from the marker_pick_place/ directory:

    python RL/train.py

Optional flags:
    --num_envs 512        override the number of parallel environments
    --max_iterations 500  shorten training for a quick test
    --video               record rollout videos during training
"""
import argparse
import os
import sys
from datetime import datetime

# Make the marker_pick_place package and RL sub-package importable when the
# script is run from the marker_pick_place/ project root.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
for _p in (_PROJECT_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Train SO100 banana pick-place with RSL-RL PPO.")
parser.add_argument("--task", type=str, default="Banana-PickPlace-v0")
parser.add_argument("--num_envs", type=int, default=None)
parser.add_argument("--max_iterations", type=int, default=None)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--video", action="store_true", default=False)
parser.add_argument("--video_length", type=int, default=300)
parser.add_argument("--video_interval", type=int, default=2000)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.video:
    args_cli.enable_cameras = True

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

from rsl_rl.runners import OnPolicyRunner

from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_pickle, dump_yaml
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

import RL  # noqa: F401 — triggers gym.register for Banana-PickPlace-v0

from RL.banana_pick_env_cfg import BananaPickEnvCfg
from RL.config.HumanoidRLEnv.agents.rsl_rl_ppo_cfg import BananaPickPPORunnerCfg

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.deterministic = False
torch.backends.cudnn.benchmark = False


def main():
    env_cfg = BananaPickEnvCfg()
    agent_cfg = BananaPickPPORunnerCfg()

    if args_cli.num_envs is not None:
        env_cfg.scene.num_envs = args_cli.num_envs
    if args_cli.max_iterations is not None:
        agent_cfg.max_iterations = args_cli.max_iterations
    if args_cli.seed is not None:
        env_cfg.seed = args_cli.seed
        agent_cfg.seed = args_cli.seed

    env_cfg.sim.device = args_cli.device
    agent_cfg.device = args_cli.device

    log_root = os.path.abspath(os.path.join(_PROJECT_ROOT, "logs", "rsl_rl", agent_cfg.experiment_name))
    log_dir = os.path.join(log_root, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)

    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print("[INFO] Recording videos during training.")
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    env = RslRlVecEnvWrapper(env)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)

    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)
    dump_pickle(os.path.join(log_dir, "params", "env.pkl"), env_cfg)
    dump_pickle(os.path.join(log_dir, "params", "agent.pkl"), agent_cfg)

    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()


"""
Step 1 — Smoke test (no training, ~30 seconds)
Just checks the env loads and rewards don't crash:


cd 02_Sim2Real/marker_pick_place
python RL/train.py --num_envs 16 --max_iterations 5 --headless
If this exits cleanly without errors, the config, scene, observations, and rewards all wire up correctly.

Step 2 — Quick reward sanity run (~5–10 minutes)

python RL/train.py --num_envs 64 --max_iterations 100 --headless
Then in a second terminal:


tensorboard --logdir 02_Sim2Real/marker_pick_place/logs/rsl_rl/banana_grasp_so100
What you're looking for — not convergence, just signal shape:

Reward term	Expected in first 100 iters
reach_banana	Non-zero immediately, should trend up
gripper_orientation	Near 0 at start (random), should start rising
banana_height	Near 0 (hard to get early) — that's fine
grasp_confirmed	0 at start — that's fine
Any reward	NaN = something is broken
If reach_banana is going up and nothing is NaN, the reward pipeline is working.

Step 3 — Axis check for the orientation reward
This is the one thing you need to verify visually. Run with a small env and rendering:


python RL/train.py --num_envs 4 --max_iterations 200
Watch the gripper. If after ~100 iterations the gripper is rotating to approach the banana lengthwise instead of across the width, the axes are wrong. Fix by changing one line in rewards.py:


# Try this if orientation reward seems inverted:
_BANANA_LONG_AXIS_LOCAL = (0.0, 0.0, 1.0)   # or (0.0, 1.0, 0.0)
_GRIPPER_CLOSE_AXIS_LOCAL = (1.0, 0.0, 0.0)  # or (0.0, 0.0, 1.0)
What NOT to do
Don't run 2048 envs × 600 iterations until steps 1 and 2 pass
Don't judge convergence at 100 iters — only judge that signals are non-zero and trending correctly
The full 600-iter run should only happen once you've confirmed the reward shapes look right in TensorBoard`

"""