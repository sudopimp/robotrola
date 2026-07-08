#pragma once

/**
 * Host ↔ STM32 motor-bridge line protocol (research).
 *
 * Frames are ASCII, newline-terminated, UTF-8. Numbers are decimal.
 * The bridge only accepts motion after SAFETY_OK was latched from the
 * independent safety MCU (GPIO or side-channel). On any fault the bridge
 * freezes or torque-disables all DYNAMIXEL IDs.
 *
 * Host → bridge commands:
 *   HB                     heartbeat (must arrive within BRIDGE_HB_TIMEOUT_MS)
 *   SAFETY ok=<0|1>        mirror of safety MCU path (optional; prefer GPIO)
 *   EN id=<n> torque=<0|1> enable/disable torque on one DXL ID
 *   ENALL torque=<0|1>     enable/disable all configured IDs
 *   GOAL id=<n> pos=<raw>  set goal position (protocol 2.0 units)
 *   VEL  id=<n> vel=<raw>  set profile velocity limit
 *   STOP                   freeze all (hold last position, torque on)
 *   DISABLE                torque off all
 *   STATUS                 dump bridge status line
 *   SCAN                   list discovered DXL IDs on bus
 *
 * Bridge → host events:
 *   PONG bridge=stm32-dxl
 *   STATUS ok=... safety=... hb_age_ms=... dxl_ok=... n_ids=...
 *   EVENT FAULT reason=...
 *   EVENT DXL id=<n> err=<code>
 */

#include <stdint.h>

#define BRIDGE_SERIAL_BAUD        115200
#define BRIDGE_HB_TIMEOUT_MS      250
#define DXL_PROTOCOL_VERSION      2.0f
#define DXL_BAUDRATE              57600
#define DXL_MAX_IDS               48

// Protocol 2.0 control table (X-series subset)
#define DXL_ADDR_TORQUE_ENABLE    64
#define DXL_ADDR_GOAL_POSITION    116
#define DXL_ADDR_PRESENT_POSITION 132
#define DXL_ADDR_PRESENT_CURRENT  126
#define DXL_ADDR_PRESENT_TEMP     146
#define DXL_ADDR_HARDWARE_ERROR   70
#define DXL_ADDR_PROFILE_VELOCITY 112

// Local software clamps (bridge-enforced, independent of host)
#define BRIDGE_MAX_PROFILE_VEL    50   // raw DXL units — conservative research default
#define BRIDGE_MAX_GOAL_DELTA     512  // max position step per command

enum BridgeFault : uint8_t {
  BRIDGE_OK = 0,
  BRIDGE_FAULT_SAFETY = 1,
  BRIDGE_FAULT_HEARTBEAT = 2,
  BRIDGE_FAULT_DXL_BUS = 3,
  BRIDGE_FAULT_HOST_CMD = 4,
};
