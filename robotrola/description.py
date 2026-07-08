"""Parse shipped R-01 URDF/xacro for joint inventory (no ROS required)."""
from __future__ import annotations

from pathlib import Path
import re
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URDF = ROOT / "cad" / "urdf" / "robotrola_r01_reference.urdf.xacro"
DEFAULT_JOINT_MAP = ROOT / "configs" / "robot_description" / "joints.yaml"

# Minimum revolute DOF for "full humanoid" gate
MIN_HUMANOID_DOF = 30
TARGET_DOF = 42


@dataclass(frozen=True)
class JointSpec:
    name: str
    joint_type: str
    lower: float | None = None
    upper: float | None = None
    effort: float | None = None
    velocity: float | None = None


_JOINT_RE = re.compile(
    r'<joint\s+name="([^"]+)"\s+type="([^"]+)"[^>]*>'
    r'(.*?)</joint>',
    re.S,
)
_LIMIT_RE = re.compile(
    r'<limit\s+lower="([^"]+)"\s+upper="([^"]+)"\s+effort="([^"]+)"\s+velocity="([^"]+)"',
)


def parse_urdf_joints(urdf_path: str | Path = DEFAULT_URDF) -> list[JointSpec]:
    text = Path(urdf_path).read_text(encoding="utf-8")
    joints: list[JointSpec] = []
    for m in _JOINT_RE.finditer(text):
        name, jtype, body = m.group(1), m.group(2), m.group(3)
        lim = _LIMIT_RE.search(body)
        if lim:
            joints.append(
                JointSpec(
                    name=name,
                    joint_type=jtype,
                    lower=float(lim.group(1)),
                    upper=float(lim.group(2)),
                    effort=float(lim.group(3)),
                    velocity=float(lim.group(4)),
                )
            )
        else:
            joints.append(JointSpec(name=name, joint_type=jtype))
    return joints


def revolute_joints(urdf_path: str | Path = DEFAULT_URDF) -> list[JointSpec]:
    return [j for j in parse_urdf_joints(urdf_path) if j.joint_type == "revolute"]


def assert_full_humanoid(urdf_path: str | Path = DEFAULT_URDF) -> dict:
    revs = revolute_joints(urdf_path)
    names = {j.name for j in revs}
    required_substrings = [
        "neck_",
        "waist_",
        "left_shoulder",
        "right_shoulder",
        "left_elbow",
        "right_elbow",
        "left_hip",
        "right_hip",
        "left_knee",
        "right_knee",
        "left_ankle",
        "right_ankle",
        "left_thumb",
        "right_thumb",
    ]
    missing = [s for s in required_substrings if not any(s in n for n in names)]
    return {
        "revolute_count": len(revs),
        "names": sorted(names),
        "missing_regions": missing,
        "ok": len(revs) >= MIN_HUMANOID_DOF and not missing and len(revs) == TARGET_DOF,
    }


def mesh_filenames(urdf_path: str | Path = DEFAULT_URDF) -> list[str]:
    text = Path(urdf_path).read_text(encoding="utf-8")
    return sorted(set(re.findall(r"/([A-Za-z0-9_]+\.stl)", text)))
