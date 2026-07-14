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


_INERTIAL_RE = re.compile(r"<inertial\b", re.I)
_MASS_RE = re.compile(r'<mass\s+value="([^"]+)"')


def parse_link_names(urdf_path: str | Path = DEFAULT_URDF) -> list[str]:
    """Return unique link names in document order."""
    text = Path(urdf_path).read_text(encoding="utf-8")
    names: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r'<link\s+name="([^"]+)"', text):
        name = m.group(1)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def inertial_coverage(urdf_path: str | Path = DEFAULT_URDF) -> dict:
    """Count links vs inertial/mass blocks in the shipped URDF (real file parse)."""
    text = Path(urdf_path).read_text(encoding="utf-8")
    links = parse_link_names(urdf_path)
    inertial_n = len(_INERTIAL_RE.findall(text))
    masses = [float(x) for x in _MASS_RE.findall(text)]
    return {
        "link_count": len(links),
        "inertial_count": inertial_n,
        "mass_count": len(masses),
        "masses": masses,
        "links": links,
        "ok": inertial_n >= len(links)
        and len(masses) >= len(links)
        and all(m > 0 for m in masses)
        and inertial_n > 0,
    }


def urdf_limits_align_with_safety(
    urdf_path: str | Path = DEFAULT_URDF,
    limits_path: str | Path | None = None,
    core_joints: tuple[str, ...] = (
        "neck_yaw",
        "left_knee",
        "right_index_curl",
        "waist_yaw",
        "left_shoulder_pitch",
        "right_hip_pitch",
    ),
) -> dict:
    """Compare revolute URDF limit tags to configs/safety_limits.yaml for core joints.

    Drives the shipped files — does not re-implement limit policy.
    """
    import yaml

    if limits_path is None:
        limits_path = ROOT / "configs" / "safety_limits.yaml"
    limits = yaml.safe_load(Path(limits_path).read_text(encoding="utf-8")).get(
        "joint_limits", {}
    )
    revs = {j.name: j for j in revolute_joints(urdf_path)}
    mismatches: list[str] = []
    checked: list[str] = []
    for name in core_joints:
        if name not in revs:
            mismatches.append(f"urdf_missing:{name}")
            continue
        if name not in limits:
            mismatches.append(f"safety_missing:{name}")
            continue
        j = revs[name]
        lim = limits[name]
        checked.append(name)
        if j.lower is None or abs(j.lower - float(lim["position_min_rad"])) > 1e-9:
            mismatches.append(f"{name}:lower")
        if j.upper is None or abs(j.upper - float(lim["position_max_rad"])) > 1e-9:
            mismatches.append(f"{name}:upper")
        if j.velocity is None or abs(j.velocity - float(lim["velocity_max_rad_s"])) > 1e-9:
            mismatches.append(f"{name}:velocity")
        if j.effort is None or abs(j.effort - float(lim["effort_max_nm"])) > 1e-9:
            mismatches.append(f"{name}:effort")
    return {
        "checked": checked,
        "mismatches": mismatches,
        "ok": not mismatches and len(checked) == len(core_joints),
    }
