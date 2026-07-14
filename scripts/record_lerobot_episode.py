#!/usr/bin/env python3
"""Record a safety-gated episode and export LeRobot-oriented local layout.

Does **not** upload to Hugging Face Hub.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lerobot.official_adapter import (  # noqa: E402
    detect_lerobot_package,
    record_filter_episode,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "artifacts" / "lerobot_episode_demo"),
    )
    ap.add_argument("--episode-id", default="ep_demo")
    args = ap.parse_args(argv)

    probe = detect_lerobot_package()
    print("lerobot_package:", json.dumps(probe))

    out = Path(args.output)
    if out.exists():
        # keep deterministic demo dir
        import shutil

        shutil.rmtree(out)
    result = record_filter_episode(out, episode_id=args.episode_id)
    print(json.dumps(result.to_dict(), indent=2))
    if result.ok and result.frames >= 1 and result.hub_upload == "not_performed":
        print("LEROBOT_PATH_OK")
        return 0
    print("LEROBOT_PATH_FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
