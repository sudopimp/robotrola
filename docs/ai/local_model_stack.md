# Local AI stack

Default posture: local-first, no cloud actuation.

## Candidate roles

- perception: RGB-D driver + YOLO11/segmentation/pose estimation
- speech: local ASR/TTS with no always-on recording
- policy learning: imitation learning on recorded episodes (JSON scaffold today)
- high-level planning: local planner that proposes tasks only
- safety: deterministic supervisor and MCU gates, not AI

## Rules

1. AI may propose actions.
2. Safety supervisor must approve actions.
3. MCU can cut power regardless of AI state.
4. No cloud model can command motors.
5. User can delete local memory.
