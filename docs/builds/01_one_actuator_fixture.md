# Build 01 — One actuator fixture

Goal: validate a single motor/joint safely before attaching it to a body.

## Steps

1. Print `servo_bracket_x_series.stl` or machine equivalent.
2. Mount actuator on fixture, not on humanoid body.
3. Wire through safety MCU-controlled power.
4. Set velocity and current limits below expected final values.
5. Run thermal and fault tests.
6. Record data into LeRobot-compatible episode format.

## Acceptance criteria

- command rejected when safety mode is not ACTIVE
- speed limit enforced
- current/effort limit enforced
- thermal warning stops motion
- e-stop cuts power
