import gymnasium as gym


gym.register(
    id="Isaac-Stack-Cube-CustomArm-IK-Abs-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": "custom_arm_stack_env_cfg:CustomArmCubeStackEnvCfg",
    },
    disable_env_checker=True,
)

gym.register(
    id="Isaac-Stack-Cube-CustomArm-IK-Rel-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    kwargs={
        "env_cfg_entry_point": "custom_arm_stack_env_cfg:CustomArmCubeStackRelEnvCfg",
    },
    disable_env_checker=True,
)
