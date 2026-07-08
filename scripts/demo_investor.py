#!/usr/bin/env python3
"""
90-second investor / diligence demo — no hardware, no ROS required.

Runs the real shipped libraries twice and prints evidence a technical
reviewer can re-run. Exit 0 only if all gates hold.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robotrola.command_path import Platform, demo_safe_path
from robotrola.description import assert_full_humanoid, TARGET_DOF
from robotrola.kinematics import PlanarArm, sample_joint_space_trajectory, trajectory_within_default_limits
from robotrola.protocol_sim import SafetyMcuSim, MotorBridgeSim
from robotrola.cost_model import full_cost_model
from robotrola.safety import SafetyInputs
from robotrola.validators import validate_repo
from lerobot.robotrola_lerobot_adapter import RobotrolaEpisodeWriter, record_approved_command


def _run_once() -> dict:
    return demo_safe_path()


def main() -> int:
    print("=== Robotrola Core — investor diligence demo ===\n")

    # 1) Description gate
    info = assert_full_humanoid()
    print(f"[description] revolute_dof={info['revolute_count']} ok={info['ok']}")
    assert info["ok"] and info["revolute_count"] == TARGET_DOF

    # 2) Dual safety path
    r1 = _run_once()
    r2 = _run_once()
    assert r1 == r2, "non-deterministic dual path"
    assert r1["good_ok"] and not r1["bad_ok"]
    assert r1["hand_ok"] is False
    print(
        f"[safety] dof={r1['dof']} good={r1['good_ok']} bad_rejected={not r1['bad_ok']} "
        f"hand_blocked={not r1['hand_ok']} reason={r1['hand_reason']}"
    )

    # 3) E-stop + reset
    p = Platform()
    p.boot()
    p.arm()
    p.activate()
    p.fault_from_estop()
    assert p.supervisor.mode.value == "FAULT"
    assert p.reset_from_fault(SafetyInputs(estop_ok=True, deadman_ok=True))
    print(f"[estop] fault_then_reset mode={p.supervisor.mode.value}")

    # 4) Protocol sim (mirrors firmware commands)
    mcu = SafetyMcuSim()
    assert "FAULT" in (mcu.handle("STATUS") or "") or "fault=1" in (mcu.handle("STATUS") or "")
    mcu.estop_ok = True
    print(mcu.handle("RESET"))
    mcu.handle("HEARTBEAT")
    mcu.tick(10)
    status = mcu.handle("STATUS")
    print(f"[mcu_sim] {status}")
    assert status and "ok=1" in status and "contactor=1" in status

    bridge = MotorBridgeSim()
    bridge.handle("SAFETY ok=1")
    bridge.handle("HB")
    bridge.handle("SCAN")
    ev = bridge.handle("GOAL id=1 pos=2100")
    print(f"[bridge_sim] {ev} | {bridge.handle('STATUS')}")
    assert "GOAL ok=1" in ev

    # 5) Kinematics sample
    arm = PlanarArm()
    x, z = arm.fk(0.4, -0.8)
    ik = arm.ik(x, z)
    assert ik is not None
    traj = sample_joint_space_trajectory(p.joint_names[:8], steps=5, amplitude_rad=0.08)
    assert trajectory_within_default_limits(traj)
    print(f"[kinematics] planar_fk=({x:.3f},{z:.3f}) traj_frames={len(traj)}")

    # 6) LeRobot path only when ACTIVE
    p2 = Platform()
    p2.boot()
    p2.arm()
    p2.activate()
    w = RobotrolaEpisodeWriter("demo_ep_001", task="investor_demo")
    record_approved_command(
        w,
        "neck_yaw",
        0.05,
        0.02,
        safety_state=p2.supervisor.mode.value,
        observation={"demo": True},
    )
    errs = w.validate_against_schema()
    assert not errs, errs
    print(f"[lerobot] frames={len(w.to_dict()['frames'])} schema_ok=True")

    # 7) Cost model
    costs = full_cost_model()
    for stage in ("bench", "upper_body", "full_body"):
        s = costs["stages"][stage]
        print(
            f"[bom:{stage}] low_usd={s['low_usd']:.0f} high_usd={s['high_usd']:.0f} "
            f"lines={s['line_count']}"
        )
        assert s["high_usd"] >= s["low_usd"] > 0

    # 8) Repo validator
    verr = validate_repo(ROOT)
    assert verr == [], verr
    print("[validate_repo] PASSED")

    print("\nINVESTOR_DEMO_OK")
    print(json.dumps({"dof": r1["dof"], "stages": list(costs["stages"].keys())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
