
from __future__ import annotations
from pathlib import Path
import csv, yaml

REQUIRED_PATHS = [
    "README.md",
    "SAFETY.md",
    "hardware/BOM.csv",
    "configs/feature_flags.yaml",
    "configs/safety_limits.yaml",
    "cad/print_manifest.csv",
    "ros2_ws/src/robotrola_description/package.xml",
]


def validate_repo(root: str | Path = ".") -> list[str]:
    root = Path(root)
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing:{rel}")
    flags_path = root / "configs/feature_flags.yaml"
    if flags_path.exists():
        flags = yaml.safe_load(flags_path.read_text()).get("feature_flags", {})
        for dangerous in ["autonomous_locomotion", "human_contact_mode", "cloud_connectivity"]:
            if flags.get(dangerous) is True:
                errors.append(f"dangerous_feature_enabled_by_default:{dangerous}")
    bom_path = root / "hardware/BOM.csv"
    if bom_path.exists():
        rows = list(csv.DictReader(open(bom_path, encoding="utf-8")))
        if len(rows) < 10:
            errors.append("bom_too_small")
        if not any(r["risk"] == "critical" for r in rows):
            errors.append("bom_missing_critical_risk_items")
    return errors
