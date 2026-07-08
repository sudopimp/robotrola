
# STM32 / CAN / DYNAMIXEL bridge scaffold

This placeholder exists to separate motor-bus timing from Linux/ROS. Implement only after the safety MCU is validated.

Responsibilities:

- translate approved commands to motor bus
- enforce local speed/current limits
- report temperatures and faults
- drop to safe state on heartbeat loss
