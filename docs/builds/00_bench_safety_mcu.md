# Build 00 — Safety MCU bench rig

Goal: prove that actuator power can be disabled without Linux, ROS, AI, Wi-Fi, or cloud.

## Required parts

- ESP32-S3 or STM32H7 board
- normally-closed e-stop
- normally-closed deadman switch
- dummy load lamp or resistor
- low-current relay or contactor test module
- bench power supply with current limit

## Acceptance criteria

- e-stop opens → contactor output drops
- deadman opens while armed → fault latch
- heartbeat missing for 250 ms → fault latch
- manual reset required after fault
- status LED indicates safe/armed/fault
