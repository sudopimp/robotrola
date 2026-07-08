
# Validation test plan

## Bench tests

- Safety MCU boot self-test.
- E-stop continuity and contactor cut time.
- Watchdog timeout.
- Power rail voltage/current/thermal limits.
- One actuator fixture speed/current/thermal tests.
- Camera frame timing.
- LeRobot dataset episode integrity.

## Upper-body tests

- Joint limit enforcement.
- Self-collision checks.
- Soft-contact low-force tests with instrumented dummy only.
- Thermal soak.
- Noise and vibration.
- Dock alignment with motors disabled.

## Release gates

- No human-contact test without written risk review.
- No battery operation without certified pack/BMS review.
- No UV-C operation without enclosure interlock validation.
- No fluid module without leak detector and isolation.
