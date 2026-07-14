"""Pure-Python message shapes mirroring ``robotrola_msgs`` (no ROS required).

ROS nodes convert these to/from ``robotrola_msgs`` or JSON ``std_msgs/String``
when the workspace is built. Host tests and sim_smoke use these dataclasses
directly so diligence never depends on colcon.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class JointCommandMsg:
    """Typed joint command (name + setpoints)."""

    name: str
    position_rad: float = 0.0
    velocity_rad_s: float = 0.0
    effort_nm: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "JointCommandMsg":
        return cls(
            name=str(d["name"]),
            position_rad=float(d.get("position_rad", 0.0)),
            velocity_rad_s=float(d.get("velocity_rad_s", 0.0)),
            effort_nm=float(d.get("effort_nm", 0.0)),
        )

    def to_csv(self) -> str:
        """Legacy safety-node wire format: name,pos,vel,effort"""
        return f"{self.name},{self.position_rad},{self.velocity_rad_s},{self.effort_nm}"

    @classmethod
    def from_csv(cls, line: str) -> "JointCommandMsg":
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            raise ValueError(f"bad joint command csv: {line!r}")
        return cls(parts[0], float(parts[1]), float(parts[2]), float(parts[3]))


@dataclass
class SafetyStateMsg:
    mode: str
    estop_ok: bool = True
    deadman_ok: bool = True
    leak_ok: bool = True
    thermal_ok: bool = True
    last_fault: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SafetyStateMsg":
        return cls(
            mode=str(d.get("mode", "BOOT")),
            estop_ok=bool(d.get("estop_ok", True)),
            deadman_ok=bool(d.get("deadman_ok", True)),
            leak_ok=bool(d.get("leak_ok", True)),
            thermal_ok=bool(d.get("thermal_ok", True)),
            last_fault=str(d.get("last_fault") or ""),
        )


@dataclass
class FeatureCommandMsg:
    feature_name: str
    requested_state: bool = False
    interlocks_present: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommandResultMsg:
    ok: bool
    reason: str
    mode: str
    joint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def wire(self) -> str:
        status = "ok" if self.ok else "reject"
        return f"{status}:{self.reason}|mode={self.mode}|joint={self.joint}"
