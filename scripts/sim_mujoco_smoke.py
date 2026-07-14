#!/usr/bin/env python3
"""Export MJCF; if mujoco is installed, load model and run mj_step.

Always proves export. Prints:
  MUJOCO_SMOKE_OK   — export valid
  MUJOCO_STEP_OK    — real dynamics step ran (requires mujoco)
  MUJOCO_STEP_SKIP  — mujoco not installed (export still OK)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_export_mod():
    path = ROOT / "scripts" / "export_mujoco_model.py"
    spec = importlib.util.spec_from_file_location("export_mujoco_model", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load export_mujoco_model")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def step_model(path: Path) -> dict:
    """Load MJCF and run one mj_step. Raises if mujoco missing or load fails."""
    import mujoco  # type: ignore

    model = mujoco.MjModel.from_xml_path(str(path))
    data = mujoco.MjData(model)
    # zero ctrl; step dynamics
    mujoco.mj_step(model, data)
    return {
        "stepped": True,
        "nq": int(model.nq),
        "nv": int(model.nv),
        "nu": int(model.nu),
        "nbody": int(model.nbody),
        "time": float(data.time),
        "qpos0": float(data.qpos[0]) if model.nq else 0.0,
    }


def main() -> int:
    exp = _load_export_mod()
    out = ROOT / "simulation/mujoco/robotrola_r01_research.xml"
    exp.write_mjcf(out)
    if not out.is_file() or out.stat().st_size < 500:
        print("MUJOCO_SMOKE_FAIL export")
        return 1
    text = out.read_text(encoding="utf-8")
    if "neck_yaw" not in text or "joint" not in text:
        print("MUJOCO_SMOKE_FAIL content")
        return 1

    info = exp.try_load(out)
    print({"export": str(out.relative_to(ROOT)), "size": out.stat().st_size, **info})
    print("MUJOCO_SMOKE_OK")

    if not info.get("loaded"):
        print("MUJOCO_STEP_SKIP", info.get("reason", "not_loaded"))
        return 0

    try:
        step = step_model(out)
        print(step)
        if step.get("stepped") and step.get("nq", 0) >= 1:
            print("MUJOCO_STEP_OK")
            return 0
        print("MUJOCO_STEP_FAIL", step)
        return 1
    except Exception as exc:
        print("MUJOCO_STEP_FAIL", type(exc).__name__, exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
