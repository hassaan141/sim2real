from isaaclab.utils import configclass

from RL.banana_pick_env_cfg import BananaPickEnvCfg


@configclass
class BananaPickPlayEnvCfg(BananaPickEnvCfg):
    """Small eval / visualisation variant of the banana pick-place task.

    Reduces the number of environments and disables observation noise so
    you can watch a trained policy run cleanly.
    """

    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 16
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
