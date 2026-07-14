"""Phase 0.5: host clients, MuJoCo export, optional tooling paths."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_host_clients_sim_demo():
    from robotrola.host_client import demo_host_clients

    out = demo_host_clients()
    assert out["HOST_CLIENTS_OK"] is True
    assert out["safety"]["ok"] is True
    assert out["bridge"]["ok"] is True


def test_host_serial_demo_script():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/host_serial_demo.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "HOST_CLIENTS_OK" in proc.stdout


def test_mujoco_export_and_smoke():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sim_mujoco_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "MUJOCO_SMOKE_OK" in proc.stdout
    xml = ROOT / "simulation/mujoco/robotrola_r01_research.xml"
    assert xml.is_file()
    text = xml.read_text(encoding="utf-8")
    assert "neck_yaw" in text
    assert "estimated" in text.lower() or "research" in text.lower()
    assert text.count("joint") >= 10


def test_optional_workflows_exist():
    assert (ROOT / ".github/workflows/firmware-optional.yml").is_file()
    assert (ROOT / ".github/workflows/ros-optional.yml").is_file()
    fw = (ROOT / ".github/workflows/firmware-optional.yml").read_text()
    ros = (ROOT / ".github/workflows/ros-optional.yml").read_text()
    assert "platformio" in fw.lower() or "pio" in fw
    assert "colcon" in ros
