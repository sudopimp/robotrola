#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from robotrola.bom import load_bom, risk_counts

if __name__ == "__main__":
    items = load_bom(ROOT / "hardware/BOM.csv")
    print(f"BOM items: {len(items)}")
    for risk, count in sorted(risk_counts(items).items()):
        print(f"{risk}: {count}")
