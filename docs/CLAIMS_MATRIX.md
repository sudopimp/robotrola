# Claims matrix — what Robotrola Core actually is

Use this document in diligence. If a claim is not listed under **Proven today**, do not pitch it as shipped.

## Proven today (exercisable without hardware)

| Claim | Evidence |
|---|---|
| Full-body kinematic description (42 revolute DOF: head, torso, arms, hands, legs, feet) | `cad/urdf/…`, `configs/robot_description/joints.yaml`, `pytest` DOF gates |
| Joint limit safety supervisor rejects over-speed / out-of-range / wrong-mode commands | `robotrola/safety.py`, `tests/test_safety.py`, `scripts/run_safety_path.py` |
| Deterministic pure-Python command path (arm → activate → approve/reject) | `robotrola/command_path.py`, dual-run demo |
| Safety MCU serial protocol implemented in firmware source (not README-only) | `firmware/micro_ros_safety_esp32/src/main.cpp` HEARTBEAT/RESET/FAULT/STATUS |
| Motor-bridge host protocol + local clamps in firmware source | `firmware/stm32_dynamixel_bridge/src/main.cpp` |
| Host-side protocol simulator matches safety MCU command set | `robotrola/protocol_sim.py`, `tests/test_protocol_sim.py` |
| BOM with critical risk items + category coverage | `hardware/BOM.csv`, validator |
| Print manifest maps parts to bench / upper_body / full_body stages | `cad/print_manifest.csv` |
| Stage cost bands (low–high USD) derived from BOM text ranges | `scripts/bom_cost_model.py` |
| Dangerous features off by default | `configs/feature_flags.yaml`, validator |
| LeRobot-compatible episode writer only accepts safety-approved path | `lerobot/`, `tests/test_lerobot_path.py` |
| Repo self-validation + CI hooks | `scripts/validate_repo.py`, `.github/workflows/ci.yml` |
| Thin ROS 2 safety node that **delegates** to the same Python library | `ros2_ws/src/robotrola_safety/scripts/safety_supervisor_node.py` |

## Lab next (designed, not yet proven on metal)

| Claim | What's missing |
|---|---|
| Flashed ESP32 cuts contactor on e-stop within watchdog budget | Bench bring-up `docs/builds/00_bench_safety_mcu.md` |
| One DYNAMIXEL on fixture tracks approved goals under bridge clamps | `docs/builds/01_one_actuator_fixture.md` |
| Upper-body stand teleop with force/speed limits measured | `docs/builds/02_upper_body_stand.md` |
| Full-body research rig / biped in cage | `docs/builds/03_full_body_research_rig.md` |
| Measured mass/inertia in URDF from physical robot | Gap 1 in `docs/research/gap_closure_plan.md` |
| Trained imitation policy on Robotrola hardware | Gap 5 — collect data first |
| Battery pack thermal envelope under load | Gap 6 — start with bench PSU |
| Gazebo/Isaac full digital twin correlation | Simulation notes exist; no sim success claimed without install |

## Not claimed (do not say this in a pitch)

| Anti-claim | Why |
|---|---|
| Certified collaborative / consumer companion robot | No CE/UL/ISO 10218 or 13482 certification |
| Factory-shippable SKU with unit economics at scale | R&D package, not manufacturing line |
| Biped walking policy ready for demo on hardware | Explicit non-goal / Phase 3 |
| Photoreal soft-skin biocompatible body | Materials research only |
| Cloud multi-user SaaS brain | Local-first by design; cloud flag off |
| Legal advice product / medical device | Companion research + contact-router docs only; not a regulated product |
| STL shells are load-bearing structure | Explicitly **not** — metal frame required for loads |

## One-line pitch-safe summary

> Robotrola Core is a **complete open research humanoid build package**: 42-DOF description, printable reference CAD, BOM with stage cost bands, layered safety software, and real MCU/bridge firmware protocols—engineered so a lab can go bench → upper body → full body without starting from a slide deck. It is **not** a certified consumer product.
