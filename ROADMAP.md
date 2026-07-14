# Roadmap

## Phase 0 — Complete open research platform (software package) ✅
- [x] Repo structure
- [x] Reference printable CAD + print manifest stages (bench / upper_body / full_body)
- [x] BOM and harness maps
- [x] Safety and privacy plan
- [x] Full-body 42-DOF URDF + joint limits + mesh wiring + **estimated inertias**
- [x] Pure-Python safety supervisor + command path (`scripts/run_safety_path.py`)
- [x] Shared joint command filter (`robotrola/joint_filter.py`)
- [x] ROS 2 packages with **real nodes**: safety, control filter, teleop, camera-config
- [x] Typed `robotrola_msgs` (JointCommand, CommandResult, SafetyState, …)
- [x] Safety MCU serial firmware (`firmware/esp32_safety_mcu`, not micro-ROS)
- [x] STM32 DYNAMIXEL bridge firmware sources
- [x] Firmware structure gate (`make firmware` / `scripts/check_firmware.py`)
- [x] Hardware-free sim smoke (`scripts/sim_smoke.py`)
- [x] LeRobot JSON scaffold + v3-**layout** export (`lerobot/v3_layout.py`)
- [x] Completeness tests + `validate_repo` + CI (pytest, sim_smoke, firmware check)

## Phase 0.5 — Software hardening ✅ (software path)
- [x] Optional CI workflows: `colcon` (ros-optional) + PlatformIO (firmware-optional)
- [x] MuJoCo MJCF research export + smoke (export always; load if mujoco installed)
- [x] Host serial clients (sim default; `--safety-port` / `--bridge-port` for USB)
- [ ] Official `lerobot` package adapter + Hub push docs
- [ ] Run host client against **real** flashed MCU on bench (needs hardware)
- [ ] MuJoCo pip in CI + `mj_step` asserted (optional)

## Phase 1 — Bench prototype (physical)
- [ ] Print non-load-bearing reference parts
- [ ] Build electronics tray only
- [ ] Flash/validate safety MCU, e-stop, watchdog, power cut on hardware
- [ ] Validate one DYNAMIXEL actuator on fixture via motor bridge
- [ ] Run perception node with RGB-D camera
- [ ] Record LeRobot-style bench episodes (v3-layout → Hub later)

## Phase 2 — Upper-body test rig
- [ ] Head/neck, torso, arms on fixed stand
- [ ] Force-limited arm movement under safety supervisor
- [ ] Audio/voice local-only path
- [ ] Docking alignment target tests
- [ ] Idle hygiene dock as sealed external device only

## Phase 3 — Mobile/biped R&D branch
- [ ] Digital twin mass/inertia measured
- [ ] Sim-to-real locomotion only in safety cage
- [ ] Battery pack certification review
- [ ] Foot force sensor validation

## Phase 4 — Responsible adult companion research
- [ ] Legal review
- [ ] Privacy review
- [ ] Consent UX review
- [ ] Human factors review
- [ ] External safety audit
