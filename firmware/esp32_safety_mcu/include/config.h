#pragma once

// Pin map for ESP32-S3 safety MCU prototype board (research bench).
// NC switches: HIGH = healthy (closed to VCC via pull-up, open/pressed pulls LOW).

#define PIN_ESTOP_NC          4
#define PIN_DEADMAN_NC        5
#define PIN_LEAK_OK           6
#define PIN_CONTACTOR_ENABLE  12
#define PIN_STATUS_LED        13

// Host must send HEARTBEAT within this window while path is active.
#define WATCHDOG_TIMEOUT_MS   250

// Main loop period (matches configs/safety_limits.yaml mcu_loop_period_ms)
#define MCU_LOOP_PERIOD_MS    10

// Serial protocol baud (matches configs/safety_limits.yaml protocol.serial_baud)
#define SAFETY_SERIAL_BAUD    115200
