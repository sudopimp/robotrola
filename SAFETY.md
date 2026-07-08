
# Safety Model

## Non-negotiables

1. Emergency stop must cut actuator power independently of the main compute stack.
2. Motion speed and torque limits must be enforced below ROS and below AI policy level.
3. No remote/cloud model may directly command actuators.
4. All human-contact experiments require a second trained observer and a physical deadman switch.
5. Idle hygiene and beverage modules require fluid isolation, leak detection, and electrical separation.
6. UV-C or other sterilization sources must be enclosed and interlocked; never expose people or pets.
7. Battery packs must be certified or professionally assembled with BMS, fusing, thermal monitoring, and charge supervision.

## Runtime safety layers

```text
User intent / teleop / policy
      ↓
Task planner
      ↓
Safety supervisor node: feature flags, limits, interlocks, operating mode
      ↓
Low-level controller: speed/torque/current limiting
      ↓
Safety MCU: e-stop, deadman, contactors, watchdog
      ↓
Actuator power bus
```

## Default feature flags

See `configs/feature_flags.yaml`. Human-contact, beverage, hygiene, legal-contact, autonomous locomotion, and cloud connectivity are disabled by default.
