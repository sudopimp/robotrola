
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class RobotConfig:
    name: str
    owner_alias: str
    repo: str
    version: str
    height_m: float
    target_mass_kg: float
    dof_total_target: int


def load_robot_config(path: str | Path) -> RobotConfig:
    data = yaml.safe_load(Path(path).read_text())
    return RobotConfig(
        name=data["robot"]["name"],
        owner_alias=data["robot"]["owner_alias"],
        repo=data["robot"]["repo"],
        version=data["robot"]["version"],
        height_m=float(data["dimensions"]["height_m"]),
        target_mass_kg=float(data["dimensions"]["target_mass_kg"]),
        dof_total_target=int(data["dimensions"]["dof_total_target"]),
    )
