from robotrola.protocol_sim import SafetyMcuSim, MotorBridgeSim


def test_mcu_boot_fault_until_reset_and_heartbeat():
    mcu = SafetyMcuSim()
    st = mcu.handle("STATUS")
    assert "fault=1" in st
    assert "ok=0" in st
    mcu.handle("RESET")
    mcu.handle("HEARTBEAT")
    mcu.tick(10)
    st2 = mcu.handle("STATUS")
    assert "ok=1" in st2
    assert "contactor=1" in st2


def test_mcu_estop_latches_fault():
    mcu = SafetyMcuSim()
    mcu.handle("RESET")
    mcu.handle("HEARTBEAT")
    mcu.tick(5)
    assert mcu.path_healthy()
    mcu.estop_ok = False
    mcu.tick(5)
    assert mcu.fault_latched
    assert not mcu.contactor_enable()


def test_mcu_heartbeat_timeout():
    mcu = SafetyMcuSim(watchdog_timeout_ms=50)
    mcu.handle("RESET")
    mcu.handle("HEARTBEAT")
    mcu.tick(10)
    assert mcu.path_healthy()
    mcu.tick(100)  # exceed watchdog
    assert mcu.fault_latched


def test_mcu_ping_and_status_tokens():
    mcu = SafetyMcuSim()
    assert mcu.handle("PING") == "PONG robotrola-safety-mcu"
    for token in ("STATUS", "estop=", "deadman=", "fault=", "hb_age_ms="):
        assert token in mcu.handle("STATUS")


def test_bridge_rejects_without_safety():
    b = MotorBridgeSim()
    b.handle("HB")
    ev = b.handle("GOAL id=1 pos=2200")
    assert "REJECT" in ev
    assert b.rejects >= 1


def test_bridge_goal_when_ready_and_clamps_delta():
    b = MotorBridgeSim()
    b.handle("SAFETY ok=1")
    b.handle("HB")
    b.handle("SCAN")
    b.positions[1] = 2048
    ev = b.handle("GOAL id=1 pos=4000")  # delta > 512
    assert "GOAL ok=1" in ev
    assert b.positions[1] == 2048 + 512
