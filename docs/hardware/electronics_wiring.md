
# Electronics and wiring

## Power tree

```text
Certified 48 V battery / bench PSU
  ├── main fuse
  ├── service disconnect
  ├── safety contactor controlled by safety MCU
  │   ├── actuator bus 48 V
  │   └── high-current DC/DC 24 V
  ├── isolated DC/DC 12 V sensors/fans
  └── isolated DC/DC 5 V MCU/peripherals
```

## Signal buses

- CAN-FD: motor controllers and safety telemetry.
- RS-485/DYNAMIXEL: prototype smart actuators.
- USB 3.x: RGB-D cameras.
- I2C/SPI: local sensors only; avoid long unshielded runs.
- Ethernet: high-throughput sensor bridges and compute.

## Safety signals

- `ESTOP_NC`: normally-closed emergency stop loop.
- `DEADMAN_NC`: normally-closed deadman loop.
- `CONTACTOR_ENABLE`: safety MCU output only.
- `WATCHDOG_IN`: main computer heartbeat.
- `FAULT_LATCH`: hardware latch requiring manual reset.
