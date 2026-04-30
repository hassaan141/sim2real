import gymnasium as gym

gym.register(
    id="Banana-PickPlace-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "RL.banana_pick_env_cfg:BananaPickEnvCfg",
    },
)

gym.register(
    id="Banana-PickPlace-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": "RL.config.HumanoidRLEnv.joint_pos_env_cfg:BananaPickPlayEnvCfg",
    },
)
