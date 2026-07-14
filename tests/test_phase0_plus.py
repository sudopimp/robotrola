"""Phase-0+ gates: joint filter, sim smoke, v3-layout export, firmware check, ROS nodes exist."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_joint_filter_demo_path():
    from robotrola.joint_filter import demo_filter_path

    r = demo_filter_path()
    assert r["dof"] == 42
    assert r["good_ok"] is True
    assert r["bad_ok"] is False
    assert r["hand_ok"] is False
    assert "human_contact_mode" in r["hand_reason"]


def test_joint_filter_uses_msgs():
    from robotrola.joint_filter import JointCommandFilter
    from robotrola.msgs import JointCommandMsg

    f = JointCommandFilter()
    f.arm()
    f.activate()
    ok = f.filter_command(JointCommandMsg("neck_yaw", 0.05, 0.05, 0.05))
    bad = f.filter_command(JointCommandMsg("neck_yaw", 0.0, 50.0, 0.0))
    assert ok.ok and not bad.ok
    assert "velocity" in bad.reason


def test_sim_smoke_script_and_core():
    from robotrola.sim_core import run_sim_smoke

    r = run_sim_smoke(steps=4)
    assert r.ok, r.errors
    assert r.approved > 0
    assert r.rejected >= 1

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sim_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "SIM_SMOKE_OK" in proc.stdout


def test_v3_layout_export_requires_active(tmp_path: Path):
    from lerobot.v3_layout import V3EpisodeBuilder, export_approved_episode

    b = V3EpisodeBuilder("ep_bad")
    with pytest.raises(RuntimeError, match="refusing"):
        b.add_frame({"x": 1}, {"a": 0}, safety_state="SAFE_IDLE")

    out = export_approved_episode(tmp_path / "ds", safety_state="ACTIVE")
    assert out["frames"] == 1
    info = json.loads(Path(out["info"]).read_text(encoding="utf-8"))
    assert info["codebase_version"].startswith("robotrola-v3-layout")
    assert "not Hugging Face Hub" in info["note"].lower() or "Not Hugging Face" in info["note"]
    assert Path(out["jsonl"]).is_file()
    assert (tmp_path / "ds" / "meta" / "episodes.jsonl").is_file()


def test_v3_layout_via_filter(tmp_path: Path):
    from robotrola.joint_filter import JointCommandFilter
    from robotrola.msgs import JointCommandMsg
    from lerobot.v3_layout import V3EpisodeBuilder

    f = JointCommandFilter()
    f.arm()
    f.activate()
    res = f.filter_command(JointCommandMsg("neck_yaw", 0.08, 0.05, 0.05))
    assert res.ok
    b = V3EpisodeBuilder("ep_filter")
    b.add_frame(
        observation={"joints": {"neck_yaw": 0.08}},
        action={"joint": "neck_yaw", "position_rad": 0.08},
        safety_state=res.mode,
    )
    meta = b.export(tmp_path / "ep")
    assert meta["frames"] == 1


def test_firmware_check_script():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_firmware.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "FIRMWARE_CHECK_OK" in proc.stdout


def test_host_serial_lockstep():
    from robotrola.host_serial import (
        SAFETY_CMDS,
        is_known_safety_cmd,
        is_known_bridge_cmd,
        parse_status_kv,
    )

    for c in SAFETY_CMDS:
        assert is_known_safety_cmd(c)
    assert is_known_bridge_cmd("GOAL id=1 pos=2048")
    assert is_known_bridge_cmd("HB")
    d = parse_status_kv("STATUS ok=1 estop=1 deadman=1")
    assert d["ok"] == "1" and d["estop"] == "1"


def test_ros_nodes_exist_not_stub_packages():
    control = ROOT / "ros2_ws/src/robotrola_control/scripts/joint_command_filter_node.py"
    teleop = ROOT / "ros2_ws/src/robotrola_teleop/scripts/keyboard_teleop_node.py"
    perception = ROOT / "ros2_ws/src/robotrola_perception/scripts/camera_config_node.py"
    assert control.is_file() and control.stat().st_size > 500
    assert teleop.is_file() and teleop.stat().st_size > 400
    assert perception.is_file() and perception.stat().st_size > 300

    # package.xml must not say empty stubs
    ctrl_xml = (ROOT / "ros2_ws/src/robotrola_control/package.xml").read_text()
    tele_xml = (ROOT / "ros2_ws/src/robotrola_teleop/package.xml").read_text()
    perc_xml = (ROOT / "ros2_ws/src/robotrola_perception/package.xml").read_text()
    assert "stub" not in ctrl_xml.lower()
    assert "stub" not in tele_xml.lower()
    assert "stub" not in perc_xml.lower()

    # Typed msgs present
    assert (ROOT / "ros2_ws/src/robotrola_msgs/msg/JointCommand.msg").is_file()
    assert (ROOT / "ros2_ws/src/robotrola_msgs/msg/CommandResult.msg").is_file()
    assert (ROOT / "ros2_ws/src/robotrola_msgs/msg/SafetyState.msg").is_file()


def test_msgs_csv_roundtrip():
    from robotrola.msgs import JointCommandMsg

    m = JointCommandMsg("neck_yaw", 0.1, 0.2, 0.3)
    m2 = JointCommandMsg.from_csv(m.to_csv())
    assert m2.name == m.name
    assert abs(m2.position_rad - 0.1) < 1e-9
