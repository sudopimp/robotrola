from pathlib import Path
from robotrola.features import FeatureFlags
from robotrola.command_path import Platform

ROOT = Path(__file__).resolve().parents[1]


def test_dangerous_features_default_off():
    flags = FeatureFlags(ROOT / "configs/feature_flags.yaml")
    assert not flags.enabled("autonomous_locomotion")
    assert not flags.enabled("human_contact_mode")
    assert not flags.enabled("cloud_connectivity")


def test_service_module_requires_interlocks():
    flags = FeatureFlags(ROOT / "configs/feature_flags.yaml")
    ok, missing = flags.can_enable("beverage_service_module", {"manual_confirm"})
    assert not ok
    assert "leak_sensor_ok" in missing


def test_hand_command_blocked_without_human_contact_flag():
    p = Platform()
    p.boot()
    p.arm()
    p.activate()
    r = p.command("left_index_curl", 0.2, 0.1, 0.05)
    assert not r.ok
    assert "human_contact_mode" in r.reason
    # non-hand research joint still allowed when ACTIVE
    neck = p.command("neck_yaw", 0.05, 0.05, 0.05)
    assert neck.ok, neck.reason
