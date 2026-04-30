import gymnasium as gym


gym.register(
    id="Quest-SO100-Marker-PickPlace-Teleop-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "so100_marker_pick_place.tasks.marker_env_cfg:MarkerTeleopEnvCfg",
    },
)

gym.register(
    id="Quest-SO100-Marker-PickPlace-RL-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "so100_marker_pick_place.tasks.marker_rl_env_cfg:MarkerRLEnvCfg",
    },
)
