import os
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import torch


@dataclass
class RecorderConfig:
    output_root: str = "recordings"
    fps: int = 30


class TeleopDatasetRecorder:
    """Lightweight recorder for teleop data.

    Stores joint positions and RGB frames to a torch file per session.
    """

    def __init__(self, config: RecorderConfig, cameras: dict, device: str) -> None:
        self.config = config
        self.cameras = cameras
        self.device = device
        self._enabled = False
        self._frames = []
        self._output_dir = None

    def start(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._output_dir = os.path.join(self.config.output_root, f"teleop_{timestamp}")
        os.makedirs(self._output_dir, exist_ok=True)
        self._enabled = True
        self._frames = []
        print(f"[INFO]: Recording teleop dataset to {self._output_dir}")

    def stop(self) -> None:
        if not self._enabled:
            return
        data = {
            "fps": self.config.fps,
            "frames": self._frames,
            "cameras": self.cameras,
        }
        torch.save(data, os.path.join(self._output_dir, "teleop_dataset.pt"))
        self._enabled = False
        print("[INFO]: Teleop dataset saved")

    def push(self, action: torch.Tensor, joint_pos: torch.Tensor, visual_obs: dict) -> None:
        if not self._enabled:
            return
        frame = {
            "action": action.detach().cpu(),
            "joint_pos": joint_pos.detach().cpu(),
            "images": {},
        }
        for camera_name in self.cameras.keys():
            rgb_key = f"rgb_{camera_name}"
            if rgb_key in visual_obs:
                frame["images"][camera_name] = (
                    visual_obs[rgb_key][0].detach().cpu().to(torch.uint8)
                )
        self._frames.append(frame)

    @property
    def enabled(self) -> bool:
        return self._enabled
