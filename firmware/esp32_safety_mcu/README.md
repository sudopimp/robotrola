# ESP32 safety MCU (serial interlock supervisor)

Research firmware for the R-01 **safety microcontroller** (ESP32-S3 class).

## What this is

- Independent e-stop / deadman / leak interlocks
- Contactor enable only when path healthy + fault latch clear
- Host serial protocol at 115200 baud: `HEARTBEAT`, `RESET`, `FAULT`, `STATUS`, `PING`

## What this is **not**

- **Not micro-ROS.** There is no XRCE-DDS agent, no ROS 2 graph membership, and no micro-ROS client stack in this package.
- Not a certified functional-safety (SIL) product.

The directory was previously named `micro_ros_safety_esp32` by mistake; the implementation has always been a plain Arduino serial protocol.

## Build

```bash
pio run
```

See `include/config.h` for pin map and watchdog timing. Host tests mirror this protocol in `robotrola/protocol_sim.py`.
