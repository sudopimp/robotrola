"""Completeness gates: full humanoid description, firmware sources, command path."""
from __future__ import annotations

from pathlib import Path

from robotrola.description import (
    assert_full_humanoid,
    revolute_joints,
    mesh_filenames,
    TARGET_DOF,
    MIN_HUMANOID_DOF,
)
from robotrola.command_path import Platform, demo_safe_path
from robotrola.safety import SafetyMode, SafetyInputs
from robotrola.validators import validate_repo

ROOT = Path(__file__).resolve().parents[1]


def test_full_humanoid_dof():
    info = assert_full_humanoid()
    assert info["revolute_count"] >= MIN_HUMANOID_DOF
    assert info["revolute_count"] == TARGET_DOF
    assert info["missing_regions"] == []
    assert info["ok"] is True


def test_urdf_not_placeholder():
    urdf = ROOT / "cad/urdf/robotrola_r01_reference.urdf.xacro"
    text = urdf.read_text(encoding="utf-8")
    assert text.count("<joint") >= TARGET_DOF
    assert text.count("<link") >= TARGET_DOF
    assert len(text.splitlines()) > 100


def test_meshes_referenced_exist():
    meshes = mesh_filenames()
    assert len(meshes) >= 5
    for m in meshes:
        assert (ROOT / "cad/stl" / m).exists() or (
            ROOT / "ros2_ws/src/robotrola_description/meshes" / m
        ).exists(), m


def test_joint_map_matches_urdf():
    revs = {j.name for j in revolute_joints()}
    assert len(revs) == TARGET_DOF
    joints_yaml = (ROOT / "configs/robot_description/joints.yaml").read_text()
    for name in ("neck_yaw", "left_knee", "right_hip_pitch", "left_index_curl"):
        assert name in revs
        assert name in joints_yaml


def test_safety_mcu_protocol_complete():
    src = (ROOT / "firmware/micro_ros_safety_esp32/src/main.cpp").read_text()
    for token in ("HEARTBEAT", "RESET", "FAULT", "STATUS", "PIN_ESTOP", "WATCHDOG"):
        assert token in src
    assert len(src.splitlines()) >= 80


def test_motor_bridge_source_exists():
    main = ROOT / "firmware/stm32_dynamixel_bridge/src/main.cpp"
    proto = ROOT / "firmware/stm32_dynamixel_bridge/include/protocol.h"
    assert main.exists()
    assert proto.exists()
    text = main.read_text()
    assert "dynamixel" in text.lower() or "DXL" in text
    assert len(text.splitlines()) >= 40
    assert "GOAL" in text
    assert "HEARTBEAT" in text or "HB" in text


def test_print_manifest_has_stages():
    import csv

    rows = list(csv.DictReader(open(ROOT / "cad/print_manifest.csv", encoding="utf-8")))
    assert len(rows) >= 15
    assert "stage" in rows[0]
    stages = {r["stage"] for r in rows}
    for s in ("bench", "upper_body", "full_body"):
        assert s in stages, stages


def test_command_path_demo():
    r1 = demo_safe_path()
    r2 = demo_safe_path()
    assert r1["dof"] == TARGET_DOF
    assert r1["good_ok"] is True
    assert r1["bad_ok"] is False
    assert r1["bad_reason"] == "velocity_limit"
    assert r1["hand_ok"] is False
    assert "human_contact_mode" in r1["hand_reason"]
    assert r1 == r2  # dual-launch determinism


def test_platform_estop_and_reset():
    p = Platform()
    p.boot()
    assert p.arm()
    assert p.activate()
    mode = p.fault_from_estop()
    assert mode == SafetyMode.FAULT
    bad = p.command("neck_yaw", 0.0, 0.0, 0.0)
    assert not bad.ok
    assert p.reset_from_fault(SafetyInputs(estop_ok=True, deadman_ok=True))
    assert p.supervisor.mode == SafetyMode.SAFE_IDLE


def test_validator_clean():
    errors = validate_repo(ROOT)
    assert errors == [], errors
