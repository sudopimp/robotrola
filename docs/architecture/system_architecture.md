
# System architecture

```mermaid
flowchart TD
  U[Adult user / operator] --> UI[Local consent and control UI]
  UI --> Task[Task planner]
  CAM[RGB-D cameras] --> Perception[Perception: RGB-D, pose, segmentation]
  MIC[Mic array] --> Voice[Local voice ASR/TTS]
  Perception --> World[Local world model]
  Voice --> Task
  World --> Task
  Task --> Safety[ROS safety supervisor]
  Safety --> Control[Whole-body controller]
  Control --> MCU[Safety MCU + watchdog]
  MCU --> Power[Actuator power contactor]
  Power --> Actuators[Actuators]
  Sensors[Force, tactile, IMU, thermal, battery] --> Safety
  Dock[Dock/hygiene/beverage modules] --> Safety
```

## Compute split

- **Edge AI computer:** perception, local language/voice, policy inference, logs, UI.
- **ROS computer/processes:** transforms, planning, state estimation, controllers.
- **Safety MCU:** e-stop, deadman, watchdog, actuator power, interlocks, power isolation.
- **Motor controllers:** current/torque/speed limits, thermal limits, hardware IDs.

## Data split

- `/sensors/*`: raw observations.
- `/robot/state`: joint state, battery, thermal, safety state.
- `/policy/action_proposal`: AI or teleop action proposal.
- `/safety/approved_action`: hard-gated action forwarded to controllers.
- `/audit/local_event`: local, user-owned event log.
