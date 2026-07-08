
# Assembly guide

## Build order

1. Print test coupon from `cad/stl/servo_bracket_x_series.stl` and validate tolerances.
2. Build safety MCU bench rig with e-stop, deadman, watchdog LED, and dummy load.
3. Build one-actuator fixture; validate torque/current limits and thermal behavior.
4. Assemble electronics tray outside robot body.
5. Mount cameras to head bar and validate calibration.
6. Assemble fixed upper-body stand: torso, head, one arm.
7. Run ROS smoke test with simulated joints only.
8. Enable one real actuator behind safety MCU.
9. Expand only after documented risk review.

## Torque/speed notes

Use conservative speed and current limits. Any human-adjacent movement must be force-limited, low-speed, observable, and emergency-stoppable.

## Quality gates

- No exposed sharp edges.
- No pinch points reachable during operation.
- No single software process can energize motors.
- No UV-C source can activate outside a sealed/interlocked enclosure.
- No beverage/fluid line shares volume with electronics.
