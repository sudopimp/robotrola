#!/usr/bin/env python3
"""Honest CAD regenerate guidance for Robotrola reference STLs.

The shipped meshes under ``cad/stl/`` are **reference geometry only**
(non-load-bearing shells/fixtures). They were produced from the OpenSCAD
source in ``cad/scad/robotrola_parametric_reference.scad`` (rounded blocks /
brackets — not production mechanical CAD).

This script does **not** invent a second geometry engine and does **not**
depend on absolute host paths. It:

1. Verifies the SCAD source and print manifest exist.
2. Optionally invokes ``openscad`` if installed to re-export a single module
   (best-effort; many modules are in one file).
3. Prints the documented SCAD → STL workflow for contributors.

Usage (from repo root)::

    python tools/generate_reference_stl.py
    python tools/generate_reference_stl.py --list
    python tools/generate_reference_stl.py --check
"""
from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAD = ROOT / "cad" / "scad" / "robotrola_parametric_reference.scad"
STL_DIR = ROOT / "cad" / "stl"
MANIFEST = ROOT / "cad" / "print_manifest.csv"


def list_stls() -> list[Path]:
    return sorted(STL_DIR.glob("*.stl"))


def check_repo() -> list[str]:
    errors: list[str] = []
    if not SCAD.is_file():
        errors.append(f"missing SCAD source: {SCAD.relative_to(ROOT)}")
    if not MANIFEST.is_file():
        errors.append(f"missing print manifest: {MANIFEST.relative_to(ROOT)}")
    if not STL_DIR.is_dir():
        errors.append(f"missing STL dir: {STL_DIR.relative_to(ROOT)}")
        return errors
    stls = list_stls()
    if len(stls) < 15:
        errors.append(f"too few STLs under cad/stl: {len(stls)}")
    if MANIFEST.is_file():
        rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
        for row in rows:
            rel = (row.get("file") or "").strip()
            if not rel:
                continue
            path = ROOT / rel
            if not path.is_file():
                errors.append(f"manifest missing file: {rel}")
            status = (row.get("status") or "").strip().lower()
            if status and status != "reference":
                errors.append(f"unexpected status for {rel}: {status}")
    return errors


def print_workflow() -> None:
    print(
        """
Robotrola reference CAD workflow
================================
Source of truth (parametric, mm):  cad/scad/robotrola_parametric_reference.scad
Shipped meshes (reference only):   cad/stl/*.stl
Stage map:                         cad/print_manifest.csv

Export a part with OpenSCAD CLI (example)::

  openscad -o cad/stl/servo_bracket_x_series.stl \\
    -D 'part="servo_bracket"' \\
    cad/scad/robotrola_parametric_reference.scad

If your SCAD build does not define a part selector, open the .scad in the
OpenSCAD GUI, isolate the module, and export STL manually. Keep units in
millimeters; URDF scales meshes by 0.001 (mm → m).

Honesty:
  - STLs are NOT load-bearing structure.
  - Do not regenerate hero marketing images from this tool.
  - Prefer updating SCAD + re-export over hand-editing binary STLs.
""".strip()
    )


def try_openscad_help() -> int:
    openscad = shutil.which("openscad") or shutil.which("OpenSCAD")
    if not openscad:
        print("openscad not on PATH — install OpenSCAD to re-export meshes.")
        print_workflow()
        return 0
    # Smoke: openscad can parse the file (syntax). Do not overwrite STLs by default.
    cmd = [openscad, "-o", "/dev/null", str(SCAD)]
    # Some OpenSCAD builds require a real output; write to scratch under tools if needed.
    out = ROOT / "tools" / ".scad_parse_smoke.stl"
    cmd = [openscad, "-o", str(out), str(SCAD)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"openscad invoke failed: {exc}")
        print_workflow()
        return 0
    if out.exists():
        out.unlink(missing_ok=True)
    if r.returncode != 0:
        print("openscad parse returned non-zero (file may be multi-module GUI-only).")
        if r.stderr:
            print(r.stderr[:500])
        print_workflow()
        return 0
    print(f"openscad parsed {SCAD.relative_to(ROOT)} successfully.")
    print_workflow()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list", action="store_true", help="list shipped STLs")
    p.add_argument("--check", action="store_true", help="validate SCAD + manifest + STLs")
    p.add_argument(
        "--openscad-smoke",
        action="store_true",
        help="if openscad is installed, try a parse smoke (does not replace STLs)",
    )
    args = p.parse_args(argv)

    if args.list:
        for stl in list_stls():
            print(stl.relative_to(ROOT))
        return 0

    if args.check:
        errs = check_repo()
        if errs:
            print("CHECK FAILED:")
            for e in errs:
                print(f"  - {e}")
            return 1
        print(f"CHECK OK: {len(list_stls())} STLs, SCAD + print_manifest present")
        return 0

    if args.openscad_smoke:
        return try_openscad_help()

    # Default: honest guidance + structural check
    errs = check_repo()
    print_workflow()
    if errs:
        print("\nCHECK FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"\nCHECK OK: {len(list_stls())} reference STLs under cad/stl/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
