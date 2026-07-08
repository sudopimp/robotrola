"""LeRobot-compatible episode writer for Robotrola.

Does not control hardware. Only records frames that were already safety-approved
(or explicitly marked as rejected for dataset negatives).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from time import time
from typing import Any


SCHEMA_PATH = Path(__file__).with_name("dataset_schema.json")


@dataclass
class RobotrolaFrame:
    timestamp: float
    observation: dict
    action: dict
    safety_state: str


class RobotrolaEpisodeWriter:
    def __init__(
        self,
        episode_id: str,
        robot: str = "robotrola_r01",
        calibration_hash: str = "uncalibrated",
        task: str = "bench_teleop",
    ):
        self.episode: dict[str, Any] = {
            "episode_id": episode_id,
            "robot": robot,
            "calibration_hash": calibration_hash,
            "task": task,
            "frames": [],
        }

    def add_frame(
        self,
        observation: dict,
        approved_action: dict,
        safety_state: str,
        *,
        require_active: bool = True,
    ) -> None:
        if require_active and safety_state != "ACTIVE":
            raise RuntimeError(
                f"refusing to log actuation frame while safety_state={safety_state}"
            )
        self.episode["frames"].append(
            asdict(
                RobotrolaFrame(
                    time(),
                    observation,
                    approved_action,
                    safety_state,
                )
            )
        )

    def to_dict(self) -> dict:
        return self.episode

    def validate_against_schema(self) -> list[str]:
        """Lightweight schema check without jsonschema dependency."""
        errors: list[str] = []
        ep = self.episode
        for key in ("episode_id", "robot", "calibration_hash", "frames"):
            if key not in ep:
                errors.append(f"missing:{key}")
        if not isinstance(ep.get("frames"), list):
            errors.append("frames_not_list")
            return errors
        for i, fr in enumerate(ep["frames"]):
            for key in ("timestamp", "observation", "action", "safety_state"):
                if key not in fr:
                    errors.append(f"frame[{i}].missing:{key}")
            if "timestamp" in fr and not isinstance(fr["timestamp"], (int, float)):
                errors.append(f"frame[{i}].timestamp_type")
            if "observation" in fr and not isinstance(fr["observation"], dict):
                errors.append(f"frame[{i}].observation_type")
            if "action" in fr and not isinstance(fr["action"], dict):
                errors.append(f"frame[{i}].action_type")
        return errors

    def write_json(self, path: str | Path) -> Path:
        errs = self.validate_against_schema()
        if errs:
            raise ValueError(f"episode schema invalid: {errs}")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.episode, indent=2), encoding="utf-8")
        return path


def record_approved_command(
    writer: RobotrolaEpisodeWriter,
    joint_name: str,
    position_rad: float,
    velocity_rad_s: float,
    safety_state: str,
    observation: dict | None = None,
) -> None:
    writer.add_frame(
        observation=observation or {"joints": {}},
        approved_action={
            "joint": joint_name,
            "position_rad": position_rad,
            "velocity_rad_s": velocity_rad_s,
        },
        safety_state=safety_state,
        require_active=True,
    )
