
import pytest
from robotrola.kinematics import PlanarArm
from robotrola.privacy import RetentionPolicy, local_event


def test_planar_fk_reaches_forward():
    arm = PlanarArm(upper_m=1.0, forearm_m=1.0)
    x, z = arm.fk(0, 0)
    assert x == pytest.approx(2.0)
    assert z == pytest.approx(0.0)


def test_privacy_blocks_cloud_default():
    RetentionPolicy().validate()
    with pytest.raises(ValueError):
        RetentionPolicy(cloud_upload=True).validate()


def test_local_event_has_timestamp():
    evt = local_event("test", "ok")
    assert "ts" in evt and evt["event_type"] == "test"
