# Claims matrix — what Robotrola Core actually is

Use this document in diligence. If a claim is not listed under **Proven today**, do not pitch it as shipped.

## Proven today (exercisable without hardware)

| Claim | Evidence |
|---|---|
| Full-body kinematic description (42 revolute DOF: head, torso, arms, hands, legs, feet) | `cad/urdf/…`, `configs/robot_description/joints.yaml`, `pytest` DOF gates |
| Estimated mass/inertia on URDF links (engineering estimates, not measured hardware) | `<inertial>` in `cad/urdf/…`, `scripts/generate_robot_description.py`, completeness tests |
| Joint limit safety supervisor rejects over-speed / out-of-range / wrong-mode commands | `robotrola/safety.py`, `tests/test_safety.py`, `scripts/run_safety_path.py` |
| Deterministic pure-Python command path (arm → activate → approve/reject) | `robotrola/command_path.py`, dual-run demo |
| Shared **joint command filter** used by demos and ROS nodes | `robotrola/joint_filter.py`, `tests/test_phase0_plus.py` |
| Safety MCU **serial** protocol implemented in firmware source (not README-only; not micro-ROS) | `firmware/esp32_safety_mcu/src/main.cpp` HEARTBEAT/RESET/FAULT/STATUS |
| Motor-bridge host protocol + local clamps in firmware source | `firmware/stm32_dynamixel_bridge/src/main.cpp` |
| Host-side protocol simulator + host_serial token lockstep | `robotrola/protocol_sim.py`, `robotrola/host_serial.py`, `scripts/check_firmware.py` |
| Firmware package structure gate (`make firmware`) | `scripts/check_firmware.py` → `FIRMWARE_CHECK_OK` |
| BOM with critical risk items + category coverage | `hardware/BOM.csv`, validator |
| Print manifest maps parts to bench / upper_body / full_body stages | `cad/print_manifest.csv` |
| Stage cost bands (low–high USD) derived from BOM text ranges | `scripts/bom_cost_model.py` |
| Dangerous features off by default | `configs/feature_flags.yaml`, validator |
| LeRobot-style **JSON scaffold** + **v3-layout** + official-package **bridge** (Hub upload never automatic) | `lerobot/official_adapter.py`, `scripts/record_lerobot_episode.py` → `LEROBOT_PATH_OK` |
| Hardware-free **sim smoke** (joint trajectory under safety filter) | `robotrola/sim_core.py`, `scripts/sim_smoke.py` → `SIM_SMOKE_OK` |
| Host serial **clients** for safety MCU + bridge (sim default; optional pyserial) | `robotrola/host_client.py`, `scripts/host_serial_demo.py` → `HOST_CLIENTS_OK` |
| MuJoCo **MJCF research export**; **mj_step** when `mujoco` extra installed | `scripts/sim_mujoco_smoke.py` → `MUJOCO_SMOKE_OK` + `MUJOCO_STEP_OK` or `MUJOCO_STEP_SKIP` |
| ROS 2 packages with **real nodes**: safety, joint filter, teleop, camera-config | `ros2_ws/src/robotrola_{safety,control,teleop,perception}/scripts/` |
| Typed message definitions (JointCommand, CommandResult, SafetyState, …) | `ros2_ws/src/robotrola_msgs/msg/` (+ `rosidl_interface_packages`) |
| Repo self-validation + CI (pytest, validate, smokes, demo, lerobot path) | `scripts/validate_repo.py`, `.github/workflows/ci.yml` |
| Optional CI: PlatformIO, ROS colcon, MuJoCo step | `firmware-optional.yml`, `ros-optional.yml`, `mujoco-optional.yml` |

## Lab next (designed, not yet proven on metal)

| Claim | What's missing |
|---|---|
| Flashed ESP32 cuts contactor on e-stop within watchdog budget | Bench bring-up `docs/builds/00_bench_safety_mcu.md` |
| One DYNAMIXEL on fixture tracks approved goals under bridge clamps | `docs/builds/01_one_actuator_fixture.md` |
| Upper-body stand teleop with force/speed limits measured | `docs/builds/02_upper_body_stand.md` |
| Full-body research rig / biped in cage | `docs/builds/03_full_body_research_rig.md` |
| **Measured** mass/inertia in URDF from physical robot (replace estimates) | Gap 1 in `docs/research/gap_closure_plan.md` |
| Full Hugging Face Hub LeRobotDataset v3 (videos + stats + streaming) | Local export + operator Hub steps; library never uploads |
| Gazebo/Isaac **validated** digital twin correlation | MuJoCo step is research scaffold, not measured twin |
| Trained imitation policy on Robotrola hardware | Gap 5 — collect data first |
| Battery pack thermal envelope under load | Gap 6 — start with bench PSU |

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
| micro-ROS / XRCE-DDS on the safety MCU | Serial line protocol only (`firmware/esp32_safety_mcu`) |
| Physics-accurate digital twin | Sim smoke ≠ Gazebo/MuJoCo validated plant model |

## One-line pitch-safe summary

> Robotrola Core is a **Phase-0+ open research humanoid package**: 42-DOF description with estimated inertias, printable reference CAD, BOM stage costs, layered safety + joint filter, serial MCU/bridge firmware, ROS nodes that delegate to the same Python library, hardware-free sim smoke, and a LeRobot v3-**layout** export — so a lab can go bench → upper body → full body without starting from a slide deck. It is **not** a certified consumer product or a trained walking robot.
