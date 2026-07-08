#include <Arduino.h>
#include "config.h"

static unsigned long lastHeartbeatMs = 0;
static bool faultLatched = true;

bool loopOk() {
  bool estopOk = digitalRead(PIN_ESTOP_NC) == HIGH;
  bool deadmanOk = digitalRead(PIN_DEADMAN_NC) == HIGH;
  bool leakOk = digitalRead(PIN_LEAK_OK) == HIGH;
  bool heartbeatOk = (millis() - lastHeartbeatMs) < WATCHDOG_TIMEOUT_MS;
  return estopOk && deadmanOk && leakOk && heartbeatOk && !faultLatched;
}

void setup() {
  pinMode(PIN_ESTOP_NC, INPUT_PULLUP);
  pinMode(PIN_DEADMAN_NC, INPUT_PULLUP);
  pinMode(PIN_LEAK_OK, INPUT_PULLUP);
  pinMode(PIN_CONTACTOR_ENABLE, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_CONTACTOR_ENABLE, LOW);
  Serial.begin(115200);
  Serial.println("Robotrola safety MCU boot: FAULT_LATCHED until RESET command");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "HEARTBEAT") lastHeartbeatMs = millis();
    if (cmd == "RESET" && digitalRead(PIN_ESTOP_NC) == HIGH) {
      faultLatched = false;
      lastHeartbeatMs = millis();
    }
    if (cmd == "FAULT") faultLatched = true;
  }
  bool ok = loopOk();
  digitalWrite(PIN_CONTACTOR_ENABLE, ok ? HIGH : LOW);
  digitalWrite(PIN_STATUS_LED, ok ? HIGH : (millis()/200)%2);
  if (!ok) faultLatched = true;
  delay(10);
}
