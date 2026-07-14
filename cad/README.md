# CAD — reference geometry only

| Path | Role |
|------|------|
| `scad/robotrola_parametric_reference.scad` | Parametric OpenSCAD source (mm) |
| `stl/` | Exported reference meshes (non-load-bearing) |
| `glb/` | Lightweight GLB previews |
| `urdf/robotrola_r01_reference.urdf.xacro` | Full-body 42-DOF research description |
| `print_manifest.csv` | Print stage map (`bench` / `upper_body` / `full_body`) |

## Regenerate STLs

```bash
python tools/generate_reference_stl.py          # workflow + check
python tools/generate_reference_stl.py --list
python tools/generate_reference_stl.py --check
```

Requires [OpenSCAD](https://openscad.org/) only if you re-export meshes. The repo ships pre-exported STLs so CI and diligence do not depend on OpenSCAD.

## Regenerate URDF + joint limits

```bash
python scripts/generate_robot_description.py
```

Single source: `joint_map()` in that script. Emits estimated `<inertial>` blocks (not measured hardware mass).

## Honesty

- Shells and fixtures are **reference** geometry — not certified load paths.
- Mass/inertia in the URDF are **engineering estimates** for sim scaffolding; replace after physical measurement (see `docs/CLAIMS_MATRIX.md`).
