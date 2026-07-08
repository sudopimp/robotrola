
# Robotrola — SOTA 2026 Adult Companion Humanoid R&D

**Target private repository:** `sudopimp/robotrola`  
**Status:** fabrication-ready research scaffold, not a certified consumer product.  
**Scope:** hardware, 3D-print assets, electronics, firmware, ROS 2 software, simulation, safety, calibration, validation, and manufacturing docs.  
**Website:** intentionally excluded; landing page lives in a separate project.

Robotrola is a private, safety-first engineering repository for building a non-explicit adult companion humanoid research platform. It is designed as a realistic path from concept to lab prototype: printable mechanical references, modular electronics, ROS 2 bringup, safety supervision, privacy-first local AI, simulation hooks, and LeRobot-compatible data capture.

> This repo does **not** claim to be a finished robot. It is an engineering starting point that must be reviewed by mechanical, electrical, robotics-safety, privacy, and legal professionals before any human-contact operation.

## What is included

- **3D printable reference parts** in `cad/stl/` plus parametric OpenSCAD sources in `cad/scad/`.
- **URDF/Xacro-style robot description** and mesh references for simulation and ROS visualization.
- **BOM and sourcing matrix** with SOTA 2026 compute, sensing, actuation, power, safety, skin, docking, and service modules.
- **ROS 2 workspace** with description, bringup, safety, perception, control, teleop, and message package scaffolds.
- **Python library** for configuration, safety limits, feature flags, BOM parsing, simple kinematics, and validation.
- **Firmware scaffolds** for an ESP32-S3 micro-ROS safety board and STM32/CAN/DYNAMIXEL bridge.
- **Simulation plan** for Gazebo + Isaac Sim / Isaac Lab, including bridge configs and digital-twin notes.
- **LeRobot adapter** and dataset schema for reproducible data collection.
- **Safety and privacy docs**: risk register, adult-only policy, interlock model, validation plan, and manufacturing checklist.

## SOTA 2026 stack decision

| Layer | Baseline | Why |
|---|---|---|
| Robotics middleware | ROS 2 Jazzy baseline | Stable ROS 2 baseline with strong ecosystem and long support window. |
| Robot learning | LeRobot-compatible datasets | Publicly documented models/datasets/tools for real-world robotics in PyTorch. |
| Edge AI | Jetson AGX Thor / T5000 class | 2026 physical-AI edge compute target for humanoid-grade perception and local models. |
| Simulation | Gazebo + Isaac Sim/Isaac Lab | Open simulation plus high-fidelity GPU workflows for sim-to-real. |
| Manipulation | MoveIt 2 + local safety supervisor | Mature ROS 2 manipulation planning plus hard runtime gates. |
| Perception | RealSense D455 / Orbbec RGB-D + YOLO11 | Depth, RGB, pose/object detection, and local-first perception. |
| Actuation | DYNAMIXEL X-series + custom actuator R&D | Reliable networked smart actuators for prototypes; printable actuator experiments for cost-down. |
| Safety | E-stop, force limits, speed zones, interlocks | Required before any human-contact experimentation. |
| Privacy | Local-first voice and logs | No cloud by default; explicit user-controlled retention. |

## Repository layout

```text
cad/                 Parametric CAD, STL, URDF, drawings, print manifest
hardware/            BOM, wiring, power tree, harness maps, material guidance
firmware/            Safety MCU and motor bridge firmware scaffolds
ros2_ws/src/         ROS 2 packages for description, safety, perception, control, bringup
robotrola/           Python package used by tooling and tests
simulation/          Gazebo and Isaac Sim integration notes/configs
lerobot/             Dataset schema + adapter skeleton
docs/                Research, assembly, safety, validation, privacy, manufacturing
assets/              Visual references and brand assets for README/docs only
scripts/             Repo validation, BOM summary, GitHub upload helper
tests/               Python tests
.github/             CI, issue templates, PR template, dependabot
```

## Quick start: validate repo locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest -q
python scripts/validate_repo.py
python scripts/bom_summary.py
```

## Quick start: ROS 2 workspace

```bash
# Ubuntu 24.04 + ROS 2 Jazzy baseline
cd ros2_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
ros2 launch robotrola_bringup sim_smoke.launch.py
```

## Quick start: CAD assets

STLs are included in `cad/stl/`. They are **reference printable geometry**, not final production tooling. Use them to validate scale, packaging, cable routing, sensor placement, and test fixtures.

```bash
python tools/generate_reference_stl.py
python tools/render_cad_catalog.py
```

## Private GitHub upload

I could not create the private repo directly from this environment because the connected GitHub tool currently exposes repository read/search operations but no create-repository or push/commit action, and the container does not include authenticated `gh`. This repo includes a one-command helper for your machine:

```bash
bash scripts/create_private_github_repo.sh sudopimp robotrola
```

## Safety position

Robotrola is treated as an **adult-only, non-explicit, privacy-first humanoid R&D platform**. All high-risk physical modules are disabled by default in `configs/feature_flags.yaml`. Before enabling any actuator, docking, hygiene, beverage, or human-contact behavior, complete the risk register, electrical review, force-limit validation, thermal tests, and emergency-stop tests.

## Licenses

- Software: Apache-2.0, see `LICENSE_SOFTWARE`.
- Hardware docs/CAD: CERN-OHL-S-2.0 intent, see `LICENSE_HARDWARE`.
- Visual reference images: private project assets until you replace them with commissioned/owned assets.
