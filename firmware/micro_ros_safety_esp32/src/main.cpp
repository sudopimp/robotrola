/**
 * Robotrola R-01 safety MCU (ESP32-S3 class)
 * ------------------------------------------------
 * Independent interlock supervisor for the research platform.
 * Host (Jetson/Linux) speaks a line-oriented serial protocol at 115200 baud.
 *
 * Protocol (newline-terminated commands, host → MCU):
 *   HEARTBEAT  — refresh watchdog timer (required while ACTIVE path is armed)
 *   RESET      — clear fault latch if e-stop NC is closed (healthy)
 *   FAULT      — force fault latch (contactor disable)
 *   STATUS     — print one STATUS line (MCU → host)
 *
 * STATUS response format:
 *   STATUS ok=<0|1> estop=<0|1> deadman=<0|1> leak=<0|1> fault=<0|1> hb_age_ms=<n> contactor=<0|1>
 *
 * Safety policy:
 *   - Contactor enable pin is HIGH only when ALL interlocks healthy AND fault latch clear.
 *   - Any interlock open or heartbeat timeout re-latches FAULT (safe = power disabled).
 *   - Boot starts FAULT_LATCHED until explicit RESET after interlocks are healthy.
 *
 * This is research firmware, not a certified functional-safety SIL product.
 */

#include <Arduino.h>
#include "config.h"

// ---- runtime state ---------------------------------------------------------
static unsigned long lastHeartbeatMs = 0;
static bool faultLatched = true;
static unsigned long bootMs = 0;
static unsigned long lastStatusAutoMs = 0;
static uint32_t loopCount = 0;
static uint32_t faultCount = 0;

// ---- interlock sampling ----------------------------------------------------
struct InterlockSnapshot {
  bool estopOk;
  bool deadmanOk;
  bool leakOk;
  bool heartbeatOk;
  unsigned long heartbeatAgeMs;
};

InterlockSnapshot sampleInterlocks() {
  InterlockSnapshot s;
  s.estopOk = digitalRead(PIN_ESTOP_NC) == HIGH;      // NC switch to GND when pressed → LOW
  s.deadmanOk = digitalRead(PIN_DEADMAN_NC) == HIGH;
  s.leakOk = digitalRead(PIN_LEAK_OK) == HIGH;
  s.heartbeatAgeMs = millis() - lastHeartbeatMs;
  s.heartbeatOk = s.heartbeatAgeMs < WATCHDOG_TIMEOUT_MS;
  return s;
}

bool pathHealthy(const InterlockSnapshot &s) {
  return s.estopOk && s.deadmanOk && s.leakOk && s.heartbeatOk && !faultLatched;
}

void enterFault(const char *reason) {
  if (!faultLatched) {
    faultCount++;
  }
  faultLatched = true;
  digitalWrite(PIN_CONTACTOR_ENABLE, LOW);
  Serial.print(F("EVENT FAULT reason="));
  Serial.println(reason);
}

void printStatus(const InterlockSnapshot &s, bool ok) {
  Serial.print(F("STATUS ok="));
  Serial.print(ok ? 1 : 0);
  Serial.print(F(" estop="));
  Serial.print(s.estopOk ? 1 : 0);
  Serial.print(F(" deadman="));
  Serial.print(s.deadmanOk ? 1 : 0);
  Serial.print(F(" leak="));
  Serial.print(s.leakOk ? 1 : 0);
  Serial.print(F(" fault="));
  Serial.print(faultLatched ? 1 : 0);
  Serial.print(F(" hb_age_ms="));
  Serial.print(s.heartbeatAgeMs);
  Serial.print(F(" contactor="));
  Serial.print(digitalRead(PIN_CONTACTOR_ENABLE) == HIGH ? 1 : 0);
  Serial.print(F(" loops="));
  Serial.print(loopCount);
  Serial.print(F(" faults="));
  Serial.println(faultCount);
}

void handleCommand(const String &cmd) {
  if (cmd.length() == 0) {
    return;
  }

  if (cmd == "HEARTBEAT") {
    lastHeartbeatMs = millis();
    return;
  }

  if (cmd == "RESET") {
    InterlockSnapshot s = sampleInterlocks();
    // Only clear latch when hard e-stop is healthy (operator intentional reset)
    if (s.estopOk) {
      faultLatched = false;
      lastHeartbeatMs = millis();
      Serial.println(F("EVENT RESET ok=1"));
    } else {
      Serial.println(F("EVENT RESET ok=0 reason=estop_open"));
    }
    return;
  }

  if (cmd == "FAULT") {
    enterFault("host_command");
    return;
  }

  if (cmd == "STATUS") {
    InterlockSnapshot s = sampleInterlocks();
    bool ok = pathHealthy(s);
    printStatus(s, ok);
    return;
  }

  if (cmd == "PING") {
    Serial.println(F("PONG robotrola-safety-mcu"));
    return;
  }

  Serial.print(F("EVENT UNKNOWN_CMD cmd="));
  Serial.println(cmd);
}

void setup() {
  pinMode(PIN_ESTOP_NC, INPUT_PULLUP);
  pinMode(PIN_DEADMAN_NC, INPUT_PULLUP);
  pinMode(PIN_LEAK_OK, INPUT_PULLUP);
  pinMode(PIN_CONTACTOR_ENABLE, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  digitalWrite(PIN_CONTACTOR_ENABLE, LOW);
  digitalWrite(PIN_STATUS_LED, LOW);

  Serial.begin(115200);
  bootMs = millis();
  lastHeartbeatMs = 0;  // force heartbeat timeout until first HEARTBEAT
  faultLatched = true;

  Serial.println(F("Robotrola safety MCU boot"));
  Serial.println(F("POLICY FAULT_LATCHED until RESET + healthy interlocks + HEARTBEAT"));
  Serial.println(F("CMDS HEARTBEAT|RESET|FAULT|STATUS|PING"));
}

void loop() {
  loopCount++;

  // Drain serial line commands
  while (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    // Accept CRLF and optional carriage returns
    if (cmd.endsWith("\r")) {
      cmd.remove(cmd.length() - 1);
    }
    handleCommand(cmd);
  }

  InterlockSnapshot s = sampleInterlocks();

  // Evaluate hard faults (independent of host)
  if (!s.estopOk) {
    enterFault("estop_open");
  } else if (!s.deadmanOk) {
    enterFault("deadman_open");
  } else if (!s.leakOk) {
    enterFault("leak_detected");
  } else if (!s.heartbeatOk && !faultLatched) {
    // Only timeout after a prior healthy heartbeat window was established
    if (lastHeartbeatMs != 0) {
      enterFault("heartbeat_timeout");
    }
  }

  bool ok = pathHealthy(s);
  digitalWrite(PIN_CONTACTOR_ENABLE, ok ? HIGH : LOW);

  // LED: solid when healthy, blink when faulted
  if (ok) {
    digitalWrite(PIN_STATUS_LED, HIGH);
  } else {
    digitalWrite(PIN_STATUS_LED, (millis() / 200) % 2);
  }

  // Periodic STATUS for host logging (every ~1s when faulted, every ~2s when ok)
  unsigned long interval = ok ? 2000UL : 1000UL;
  if (millis() - lastStatusAutoMs >= interval) {
    lastStatusAutoMs = millis();
    printStatus(s, ok);
  }

  delay(MCU_LOOP_PERIOD_MS);
}
