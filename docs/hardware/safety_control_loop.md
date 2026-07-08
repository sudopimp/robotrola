
# Safety control loop

The safety MCU must be able to disable actuator power without Linux, ROS, Wi-Fi, cloud, or AI working.

## Safety MCU requirements

- Hardware watchdog.
- Normally-closed e-stop input.
- Normally-closed deadman input.
- Contactor output with feedback.
- Overtemperature input.
- Battery fault input.
- Leak detector input for any fluid module.
- Independent status LED/buzzer.

## Safety state transitions

```mermaid
stateDiagram-v2
  [*] --> BOOT
  BOOT --> SAFE_IDLE: self-test ok
  SAFE_IDLE --> ARMED: operator + deadman + no faults
  ARMED --> ACTIVE: controller heartbeat ok
  ACTIVE --> SAFE_IDLE: command stop
  ACTIVE --> FAULT: e-stop OR fault OR heartbeat timeout
  ARMED --> FAULT: e-stop OR fault
  SAFE_IDLE --> FAULT: e-stop OR fault
  FAULT --> SAFE_IDLE: manual reset + self-test ok
```
