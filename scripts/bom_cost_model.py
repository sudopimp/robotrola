#!/usr/bin/env python3
"""Print stage cost bands (bench / upper_body / full_body) from shipped BOM."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robotrola.cost_model import full_cost_model


def main() -> int:
    model = full_cost_model(ROOT / "hardware" / "BOM.csv")
    print(json.dumps(model, indent=2))
    stages = model["stages"]
    for name in ("bench", "upper_body", "full_body"):
        assert name in stages
        assert "low_usd" in stages[name] and "high_usd" in stages[name]
        assert stages[name]["high_usd"] >= stages[name]["low_usd"]
        assert stages[name]["line_count"] >= 1
    print("BOM_COST_MODEL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
