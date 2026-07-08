
from pathlib import Path
from robotrola.safety import SafetySupervisor, SafetyInputs, JointCommand, SafetyMode

ROOT = Path(__file__).resolve().parents[1]

def test_safety_blocks_when_not_active():
    sup = SafetySupervisor(ROOT / "configs/safety_limits.yaml")
    sup.self_test()
    ok, reason = sup.approve_joint_command(JointCommand("neck_yaw", 0, 0.1, 0.1))
    assert not ok
    assert "mode_not_active" in reason


def test_safety_approves_limited_command_when_active():
    sup = SafetySupervisor(ROOT / "configs/safety_limits.yaml")
    sup.self_test()
    inputs = SafetyInputs(estop_ok=True, deadman_ok=True)
    assert sup.arm(inputs)
    assert sup.activate(inputs)
    ok, reason = sup.approve_joint_command(JointCommand("neck_yaw", 0.1, 0.1, 0.1))
    assert ok, reason


def test_safety_rejects_velocity_limit():
    sup = SafetySupervisor(ROOT / "configs/safety_limits.yaml")
    sup.self_test()
    inputs = SafetyInputs(estop_ok=True, deadman_ok=True)
    sup.arm(inputs); sup.activate(inputs)
    ok, reason = sup.approve_joint_command(JointCommand("neck_yaw", 0.1, 99, 0.1))
    assert not ok
    assert reason == "velocity_limit"


def test_estop_faults():
    sup = SafetySupervisor(ROOT / "configs/safety_limits.yaml")
    sup.self_test()
    mode = sup.evaluate_inputs(SafetyInputs(estop_ok=False, deadman_ok=True))
    assert mode == SafetyMode.FAULT
    assert sup.last_fault == "estop_open"
