# Gap closure plan: from concept to reality

This document exists because a convincing humanoid image is not a buildable robot. The project is organized to close the real gaps systematically.

## Gap 1 — Load-bearing mechanics

**Current state:** reference printable shells and fixtures exist.  
**Gap:** load paths, finite-element validation, actuator torque sizing, fatigue testing, and manufacturing drawings are not complete.  
**Closure path:**

1. build one-actuator fixture
2. measure torque/current/temperature curves
3. select metal load-bearing frame members
4. update URDF mass/inertia from real measurements
5. create production CAD branch after physical measurements

## Gap 2 — Safety certification

**Current state:** safety architecture, safety MCU scaffold, e-stop, deadman, interlock model.  
**Gap:** not certified under machinery/collaborative robot standards.  
**Closure path:**

1. lab safety review
2. hazard analysis and FMEA
3. contact-force measurements with instrumented dummy
4. independent electrical review
5. external robotics-safety audit

## Gap 3 — Human-adjacent operation

**Current state:** feature flags keep all high-risk modules off by default.  
**Gap:** no human-contact validation.  
**Closure path:** bench tests → upper-body stand → dummy-only tests → independent review → limited adult-user study if legal and approved.

## Gap 4 — Adult companion boundaries

**Current state:** non-explicit adult-only governance docs.  
**Gap:** consent UX, privacy policy, local memory controls, and jurisdiction-specific legal review are not complete.  
**Closure path:** implement local control UI, adult-only gate, consent state machine, local deletion, and legal review before any user study.

## Gap 5 — AI reliability

**Current state:** LeRobot adapter and local-first policy path.  
**Gap:** no trained policy for Robotrola hardware.  
**Closure path:** collect bench datasets, train imitation policies offline, test in sim, run shadow-mode only, then safety-gated actions on fixtures.

## Gap 6 — Power and thermal

**Current state:** power tree and safety rules.  
**Gap:** real battery, BMS, thermal envelope, fusing, and enclosure are not selected.  
**Closure path:** use bench PSU first, then certified pack, thermal soak, fuse validation, and charge/dock validation.
