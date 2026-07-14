"""LeRobotDataset v3-*layout* export (meta + tabular data).

This writes a **local dataset directory** inspired by Hugging Face LeRobot
Dataset v3 layout:

- ``meta/info.json`` — features, fps, robot type
- ``meta/episodes.jsonl`` — episode index
- ``data/chunk-000/file-000.parquet`` when ``pyarrow`` is installed
- ``data/chunk-000/file-000.jsonl`` always (portable fallback)

It is **not** a full Hub upload, video encoding, or ``lerobot`` package
integration. Claims must say "v3-layout export" not "Hub parity".

Only frames recorded after safety-approved ACTIVE path should be passed in.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import Any


CODEBASE_VERSION = "robotrola-v3-layout-0.1"


@dataclass
class V3Frame:
    timestamp: float
    observation: dict[str, Any]
    action: dict[str, Any]
    safety_state: str


@dataclass
class V3EpisodeBuilder:
    episode_id: str
    robot: str = "robotrola_r01"
    task: str = "bench_teleop"
    fps: int = 10
    frames: list[V3Frame] = field(default_factory=list)

    def add_frame(
        self,
        observation: dict[str, Any],
        action: dict[str, Any],
        safety_state: str,
        *,
        require_active: bool = True,
        timestamp: float | None = None,
    ) -> None:
        if require_active and safety_state != "ACTIVE":
            raise RuntimeError(
                f"refusing to log actuation frame while safety_state={safety_state}"
            )
        self.frames.append(
            V3Frame(
                timestamp if timestamp is not None else time(),
                observation,
                action,
                safety_state,
            )
        )

    def export(self, root: str | Path) -> dict[str, Any]:
        root = Path(root)
        meta = root / "meta"
        data_chunk = root / "data" / "chunk-000"
        meta.mkdir(parents=True, exist_ok=True)
        data_chunk.mkdir(parents=True, exist_ok=True)

        info = {
            "codebase_version": CODEBASE_VERSION,
            "robot_type": self.robot,
            "fps": self.fps,
            "total_episodes": 1,
            "total_frames": len(self.frames),
            "features": {
                "observation.state": {"dtype": "dict", "shape": None},
                "action": {"dtype": "dict", "shape": None},
                "timestamp": {"dtype": "float64", "shape": [1]},
                "safety_state": {"dtype": "string", "shape": [1]},
                "task": {"dtype": "string", "shape": [1]},
            },
            "splits": {"train": "0:1"},
            "data_path": "data/chunk-{chunk_index:03d}/file-{file_index:03d}",
            "note": (
                "Robotrola v3-layout export: local meta+tabular only. "
                "Not Hugging Face Hub upload; videos not included."
            ),
        }
        (meta / "info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

        ep_line = {
            "episode_index": 0,
            "episode_id": self.episode_id,
            "tasks": [self.task],
            "length": len(self.frames),
        }
        with (meta / "episodes.jsonl").open("w", encoding="utf-8") as f:
            f.write(json.dumps(ep_line) + "\n")

        # Always write JSONL (no extra deps)
        jsonl_path = data_chunk / "file-000.jsonl"
        rows: list[dict[str, Any]] = []
        with jsonl_path.open("w", encoding="utf-8") as f:
            for i, fr in enumerate(self.frames):
                row = {
                    "episode_index": 0,
                    "frame_index": i,
                    "timestamp": fr.timestamp,
                    "observation": fr.observation,
                    "action": fr.action,
                    "safety_state": fr.safety_state,
                    "task": self.task,
                }
                rows.append(row)
                f.write(json.dumps(row) + "\n")

        parquet_path = data_chunk / "file-000.parquet"
        parquet_written = False
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq

            # Flatten action joint if present for columnar storage
            table = pa.table(
                {
                    "episode_index": [r["episode_index"] for r in rows],
                    "frame_index": [r["frame_index"] for r in rows],
                    "timestamp": [r["timestamp"] for r in rows],
                    "safety_state": [r["safety_state"] for r in rows],
                    "task": [r["task"] for r in rows],
                    "action_json": [json.dumps(r["action"]) for r in rows],
                    "observation_json": [json.dumps(r["observation"]) for r in rows],
                }
            )
            pq.write_table(table, parquet_path)
            parquet_written = True
        except ImportError:
            parquet_path = None  # type: ignore

        return {
            "root": str(root),
            "frames": len(self.frames),
            "jsonl": str(jsonl_path),
            "parquet": str(parquet_path) if parquet_written else None,
            "info": str(meta / "info.json"),
            "codebase_version": CODEBASE_VERSION,
        }


def export_approved_episode(
    root: str | Path,
    *,
    episode_id: str = "ep_sim",
    joint: str = "neck_yaw",
    position_rad: float = 0.05,
    safety_state: str = "ACTIVE",
) -> dict[str, Any]:
    """Helper used by tests/sim: one approved frame → v3-layout dir."""
    b = V3EpisodeBuilder(episode_id=episode_id)
    b.add_frame(
        observation={"joints": {joint: position_rad}},
        action={"joint": joint, "position_rad": position_rad, "velocity_rad_s": 0.01},
        safety_state=safety_state,
    )
    return b.export(root)
