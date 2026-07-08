# STM32 / DYNAMIXEL motor bridge

Real firmware source for the R-01 motor-bus bridge. Separates DYNAMIXEL timing
from Linux/ROS and enforces local clamps even if the host misbehaves.

## Sources

| Path | Role |
|---|---|
| `src/main.cpp` | Host protocol, fault state machine, GOAL/VEL clamps, SCAN |
| `include/protocol.h` | Command set, control-table addresses, timeouts |
| `platformio.ini` | Nucleo-F401RE class Arduino build (sim + DXL envs) |

## Protocol summary

Host lines (115200 8N1, `\n` terminated):

- `HB` / `HEARTBEAT` — refresh bridge watchdog (250 ms)
- `SAFETY ok=1` — soft safety latch (prefer hard GPIO `PIN_SAFETY_OK`)
- `EN id=N torque=0|1` / `ENALL torque=0|1`
- `GOAL id=N pos=RAW` — clamped per-step position
- `VEL id=N vel=RAW` — clamped profile velocity
- `STOP` / `DISABLE` / `SCAN` / `STATUS` / `CLEAR` / `PING`

Motion is rejected unless **safety path + host heartbeat** are healthy.

## Bring-up order

1. Validate `firmware/micro_ros_safety_esp32` contactor path on the bench.
2. Wire safety contactor-enable mirror into `PIN_SAFETY_OK`.
3. Flash bridge with `pio run -e stm32_bridge` (protocol-only) or
   `pio run -e stm32_bridge_dxl` with Dynamixel2Arduino + bus wiring.
4. Host must send continuous `HB` and only stream goals already approved by
   the pure-Python / ROS safety supervisor.

## Not included

Certified functional-safety certification, production current-loop firmware,
or factory calibration tables. Those remain build-stage engineering work.
