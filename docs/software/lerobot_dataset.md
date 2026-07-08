
# LeRobot dataset path

Robotrola uses a LeRobot-compatible schema to avoid bespoke robot-learning dead ends.

Episode fields:

- RGB frames from head camera.
- Depth frames or point clouds.
- Joint positions, velocities, efforts.
- Safety state.
- Operator command.
- Approved action.
- Task metadata.
- Calibration hash.

See `lerobot/dataset_schema.json`.
