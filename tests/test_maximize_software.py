"""Maximize-software goal: lerobot official path, mujoco step, CI workflow honesty."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_host_serial_imports_without_yaml_stack():
    """Firmware CI path: host_serial must not require pyyaml via package __init__."""
    # Import submodule directly
    from robotrola import host_serial

    assert "HEARTBEAT" in host_serial.SAFETY_CMDS
    assert host_serial.is_known_bridge_cmd("GOAL id=1 pos=1")


def test_official_adapter_refuses_non_active(tmp_path: Path):
    from lerobot.official_adapter import SafetyGatedRecorder

    rec = SafetyGatedRecorder("ep_bad")
    with pytest.raises(RuntimeError, match="refusing"):
        rec.add_approved({"x": 1}, {"a": 0}, safety_state="SAFE_IDLE")


def test_official_adapter_filter_export(tmp_path: Path):
    from lerobot.official_adapter import record_filter_episode

    result = record_filter_episode(tmp_path / "ds", episode_id="ep_ok")
    assert result.ok
    assert result.frames >= 1
    assert result.hub_upload == "not_performed"
    info = json.loads((tmp_path / "ds" / "meta" / "info.json").read_text())
    assert info["total_frames"] >= 1
    assert (tmp_path / "ds" / "data" / "chunk-000" / "file-000.jsonl").is_file()


def test_record_lerobot_episode_script(tmp_path: Path):
    out = tmp_path / "ep"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/record_lerobot_episode.py"),
            "-o",
            str(out),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "LEROBOT_PATH_OK" in proc.stdout
    assert "not_performed" in proc.stdout


def test_mujoco_smoke_export_always():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sim_mujoco_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "MUJOCO_SMOKE_OK" in proc.stdout
    # STEP_OK if mujoco installed, else STEP_SKIP
    assert ("MUJOCO_STEP_OK" in proc.stdout) or ("MUJOCO_STEP_SKIP" in proc.stdout)


def test_mujoco_step_function_when_installed():
    pytest.importorskip("mujoco")
    # Drive shipped smoke entry for step token
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sim_mujoco_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "MUJOCO_STEP_OK" in proc.stdout
    # Also call step_model directly
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "sim_mujoco_smoke", ROOT / "scripts/sim_mujoco_smoke.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    xml = ROOT / "simulation/mujoco/robotrola_r01_research.xml"
    step = mod.step_model(xml)
    assert step["stepped"] is True
    assert step["nq"] >= 1


def test_optional_workflows_install_deps():
    fw = (ROOT / ".github/workflows/firmware-optional.yml").read_text()
    ros = (ROOT / ".github/workflows/ros-optional.yml").read_text()
    mj = (ROOT / ".github/workflows/mujoco-optional.yml").read_text()
    assert "pip install" in fw and "pyyaml" in fw.lower() or "pip install -e" in fw
    assert "rosidl_interface_packages" not in ros  # that's package.xml
    assert "colcon build" in ros
    assert "MUJOCO_STEP_OK" in mj
    msgs = (ROOT / "ros2_ws/src/robotrola_msgs/package.xml").read_text()
    assert "rosidl_interface_packages" in msgs
