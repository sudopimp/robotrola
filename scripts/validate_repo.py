#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from robotrola.validators import validate_repo

if __name__ == "__main__":
    errors = validate_repo(ROOT)
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)
    print("VALIDATION PASSED")
