
from pathlib import Path
from robotrola.features import FeatureFlags

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
