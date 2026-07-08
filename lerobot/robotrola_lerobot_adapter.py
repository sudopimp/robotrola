
"""LeRobot adapter scaffold for Robotrola.

This module intentionally avoids controlling hardware directly. It converts approved
observations/actions into a dataset-friendly structure.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from time import time

@dataclass
class RobotrolaFrame:
    timestamp: float
    observation: dict
    action: dict
    safety_state: str

class RobotrolaEpisodeWriter:
    def __init__(self, episode_id: str, robot: str, calibration_hash: str, task: str):
        self.episode = {
            "episode_id": episode_id,
            "robot": robot,
            "calibration_hash": calibration_hash,
            "task": task,
            "frames": [],
        }

    def add_frame(self, observation: dict, approved_action: dict, safety_state: str) -> None:
        self.episode["frames"].append(asdict(RobotrolaFrame(time(), observation, approved_action, safety_state)))

    def to_dict(self) -> dict:
        return self.episode
