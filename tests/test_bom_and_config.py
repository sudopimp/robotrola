
from pathlib import Path
from robotrola.bom import load_bom, risk_counts
from robotrola.config import load_robot_config
from robotrola.validators import validate_repo

ROOT = Path(__file__).resolve().parents[1]

def test_bom_loads_with_critical_items():
    items = load_bom(ROOT / "hardware/BOM.csv")
    assert len(items) >= 15
    assert risk_counts(items)["critical"] >= 2


def test_config_loads():
    cfg = load_robot_config(ROOT / "configs/robotrola_v0.1.yaml")
    assert cfg.owner_alias == "sudopimp"
    assert cfg.height_m > 1.0


def test_repo_validator_clean():
    assert validate_repo(ROOT) == []
