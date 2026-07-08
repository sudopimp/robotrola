# Roadmap

## Phase 0 — Complete open research platform (software package) ✅
- [x] Repo structure
- [x] Reference printable CAD + print manifest stages (bench / upper_body / full_body)
- [x] BOM and harness maps
- [x] Safety and privacy plan
- [x] Full-body 42-DOF URDF + joint limits + mesh wiring
- [x] Pure-Python safety supervisor + command path (`scripts/run_safety_path.py`)
- [x] ROS 2 packages with thin safety node (delegates to Python library)
- [x] Safety MCU firmware protocol (HEARTBEAT/RESET/FAULT/STATUS)
- [x] STM32 DYNAMIXEL bridge firmware sources (not README-only)
- [x] Completeness tests + `validate_repo` gates + CI hooks

## Phase 1 — Bench prototype (physical)
- [ ] Print non-load-bearing reference parts
- [ ] Build electronics tray only
- [ ] Flash/validate safety MCU, e-stop, watchdog, power cut on hardware
- [ ] Validate one DYNAMIXEL actuator on fixture via motor bridge
- [ ] Run perception node with RGB-D camera
- [ ] Record LeRobot-compatible bench dataset

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
