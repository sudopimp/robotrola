#!/usr/bin/env python3
"""Export MJCF then optionally load in MuJoCo. Always exports; load is optional."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import importlib.util  # noqa: E402


def _load_export_mod():
    path = ROOT / "scripts" / "export_mujoco_model.py"
    spec = importlib.util.spec_from_file_location("export_mujoco_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load export_mujoco_model")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    exp = _load_export_mod()
    out = ROOT / "simulation/mujoco/robotrola_r01_research.xml"
    exp.write_mjcf(out)
    if not out.is_file() or out.stat().st_size < 500:
        print("MUJOCO_SMOKE_FAIL export")
        return 1
    # Structural: must mention hinge joints from joint map
    text = out.read_text(encoding="utf-8")
    if "neck_yaw" not in text or "joint" not in text:
        print("MUJOCO_SMOKE_FAIL content")
        return 1
    info = exp.try_load(out)
    print({"export": str(out.relative_to(ROOT)), "size": out.stat().st_size, **info})
    print("MUJOCO_SMOKE_OK")  # export is enough for Phase 0.5 without mujoco pip
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
