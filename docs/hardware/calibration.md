
# Calibration

## Required calibration records

- Camera intrinsics/extrinsics.
- Joint zero offsets.
- Actuator current-to-torque estimates.
- Foot force sensor offsets.
- Tactile baseline/noise floor.
- Thermal sensor calibration.
- Docking alignment error.
- Battery voltage/current telemetry.

Store calibration in `configs/calibration/*.yaml`; never hardcode offsets in source code.
