"""Bridge Robotrola safety-approved frames → local LeRobot-oriented datasets.

Priority:
1. Always can export via ``v3_layout`` (no extra deps).
2. If the official ``lerobot`` package is importable, attempt a best-effort
   conversion/note using its public API surface (version-tolerant).
3. Hub upload is **never** performed here — see docs for operator steps.

ACTIVE safety_state gate is enforced on every frame (same policy as JSON scaffold).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lerobot.v3_layout import V3EpisodeBuilder, CODEBASE_VERSION


@dataclass
class OfficialExportResult:
    ok: bool
    mode: str  # "v3_layout" | "lerobot_package" | "hybrid"
    root: str
    frames: int
    details: dict[str, Any] = field(default_factory=dict)
    hub_upload: str = "not_performed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "mode": self.mode,
            "root": self.root,
            "frames": self.frames,
            "details": self.details,
            "hub_upload": self.hub_upload,
            "codebase_version": CODEBASE_VERSION,
        }


def detect_lerobot_package() -> dict[str, Any]:
    """Probe for the **official Hugging Face** ``lerobot`` PyPI package.

    This repo also has a local ``lerobot/`` package for Robotrola adapters.
    That local tree must not be reported as the official HF install.
    """
    local_dir = Path(__file__).resolve().parent
    # 1) PyPI distribution named lerobot (may be absent)
    pypi_version = None
    try:
        import importlib.metadata as md

        for dist in md.distributions():
            name = (dist.metadata.get("Name") or "").lower()
            if name == "lerobot":
                pypi_version = dist.version
                break
    except Exception:
        pypi_version = None

    # 2) Official modules live under lerobot.common or lerobot.datasets with
    #    LeRobotDataset — not under our local adapter modules.
    has_dataset = False
    dataset_name = None
    if pypi_version is not None:
        try:
            from lerobot.common.datasets.lerobot_dataset import (  # type: ignore
                LeRobotDataset,
            )

            has_dataset = True
            dataset_name = "lerobot.common.datasets.lerobot_dataset.LeRobotDataset"
            _ = LeRobotDataset
        except Exception:
            try:
                from lerobot.datasets.lerobot_dataset import (  # type: ignore
                    LeRobotDataset,
                )

                has_dataset = True
                dataset_name = "lerobot.datasets.lerobot_dataset.LeRobotDataset"
                _ = LeRobotDataset
            except Exception:
                pass

    official = pypi_version is not None and has_dataset
    return {
        "installed": official,
        "version": pypi_version if official else None,
        "has_dataset_api": has_dataset,
        "dataset_symbol": dataset_name,
        "local_robotrola_lerobot_dir": str(local_dir),
        "pypi_lerobot_version": pypi_version,
        "hint": (
            None
            if official
            else 'pip install -e ".[lerobot]"  # optional heavy HF stack (torch)'
        ),
    }


@dataclass
class SafetyGatedRecorder:
    """Record frames only after safety filter approval (ACTIVE)."""

    episode_id: str
    robot: str = "robotrola_r01"
    task: str = "bench_teleop"
    fps: int = 10
    _builder: V3EpisodeBuilder = field(init=False)

    def __post_init__(self) -> None:
        self._builder = V3EpisodeBuilder(
            episode_id=self.episode_id,
            robot=self.robot,
            task=self.task,
            fps=self.fps,
        )

    def add_approved(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        safety_state: str,
    ) -> None:
        self._builder.add_frame(
            observation, action, safety_state, require_active=True
        )

    def export_local(self, root: str | Path) -> OfficialExportResult:
        root = Path(root)
        layout = self._builder.export(root)
        probe = detect_lerobot_package()
        details: dict[str, Any] = {
            "v3_layout": layout,
            "lerobot_package": probe,
        }
        mode = "v3_layout"
        if probe.get("installed") and probe.get("has_dataset_api"):
            # Best-effort: write a conversion manifest the operator can feed
            # into official tooling — do not pretend Dataset.create always matches.
            manifest = {
                "note": (
                    "Official lerobot package detected. Local v3-layout written. "
                    "Use docs/software/lerobot_dataset.md Hub section for upload. "
                    "Robotrola does not call Hub APIs from this adapter."
                ),
                "local_root": str(root),
                "frames": layout["frames"],
                "package_version": probe.get("version"),
                "dataset_symbol": probe.get("dataset_symbol"),
            }
            man_path = root / "meta" / "official_lerobot_bridge.json"
            man_path.parent.mkdir(parents=True, exist_ok=True)
            man_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            details["bridge_manifest"] = str(man_path)
            mode = "hybrid"
        return OfficialExportResult(
            ok=layout["frames"] >= 0 and Path(layout["info"]).is_file(),
            mode=mode,
            root=str(root),
            frames=int(layout["frames"]),
            details=details,
            hub_upload="not_performed",
        )


def record_filter_episode(
    root: str | Path,
    *,
    episode_id: str = "ep_filter",
    joint: str = "neck_yaw",
    position_rad: float = 0.05,
) -> OfficialExportResult:
    """Arm/activate filter, approve one joint cmd, export gated episode."""
    from robotrola.joint_filter import JointCommandFilter
    from robotrola.msgs import JointCommandMsg

    filt = JointCommandFilter()
    assert filt.arm() and filt.activate()
    res = filt.filter_command(
        JointCommandMsg(joint, position_rad, 0.05, 0.05)
    )
    if not res.ok:
        raise RuntimeError(f"filter rejected command: {res.reason}")
    rec = SafetyGatedRecorder(episode_id=episode_id)
    rec.add_approved(
        observation={"joints": {joint: position_rad}},
        action={
            "joint": joint,
            "position_rad": position_rad,
            "velocity_rad_s": 0.05,
        },
        safety_state=res.mode,
    )
    return rec.export_local(root)
