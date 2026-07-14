# MuJoCo research scaffold

| File | Role |
|------|------|
| `robotrola_r01_research.xml` | Generated MJCF from joint map (hinge chain + estimated inertias) |

```bash
python scripts/export_mujoco_model.py
python scripts/sim_mujoco_smoke.py
# optional load:
python scripts/export_mujoco_model.py --load   # requires: pip install mujoco
```

**Honesty:** not a validated digital twin. Mass/inertia are estimates. Prefer measured URDF before policy training.
