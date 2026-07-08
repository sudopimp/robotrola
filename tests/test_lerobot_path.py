import pytest
from pathlib import Path

from robotrola.command_path import Platform
from lerobot.robotrola_lerobot_adapter import (
    RobotrolaEpisodeWriter,
    record_approved_command,
)


def test_writer_requires_active_for_actuation_frames():
    w = RobotrolaEpisodeWriter("ep_block")
    with pytest.raises(RuntimeError, match="refusing"):
        w.add_frame({"x": 1}, {"a": 0}, safety_state="SAFE_IDLE")


def test_writer_records_when_active_and_validates_schema(tmp_path: Path):
    p = Platform()
    p.boot()
    p.arm()
    p.activate()
    w = RobotrolaEpisodeWriter("ep_ok", task="unit_test")
    record_approved_command(
        w,
        "neck_yaw",
        0.05,
        0.01,
        safety_state=p.supervisor.mode.value,
    )
    assert w.validate_against_schema() == []
    out = w.write_json(tmp_path / "ep.json")
    assert out.exists()
    text = out.read_text()
    assert "neck_yaw" in text
    assert "ACTIVE" in text


def test_only_approved_command_logged():
    p = Platform()
    p.boot()
    p.arm()
    p.activate()
    good = p.command("neck_yaw", 0.05, 0.02, 0.05)
    bad = p.command("neck_yaw", 0.05, 99.0, 0.05)
    assert good.ok and not bad.ok
    w = RobotrolaEpisodeWriter("ep_filter")
    if good.ok:
        record_approved_command(
            w, "neck_yaw", 0.05, 0.02, safety_state=p.supervisor.mode.value
        )
    # bad must not be logged
    assert len(w.to_dict()["frames"]) == 1
