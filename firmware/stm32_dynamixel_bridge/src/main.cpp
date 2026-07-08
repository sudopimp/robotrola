/**
 * Robotrola R-01 STM32 DYNAMIXEL / motor-bus bridge
 * -------------------------------------------------
 * Separates motor-bus timing from Linux/ROS. Receives *approved* commands
 * from the host after the safety MCU has enabled the contactor path.
 *
 * Hardware assumptions (research bench):
 *   - STM32F4/F7 class MCU with USART for host + USART/TTL for DYNAMIXEL
 *   - Optional GPIO PIN_SAFETY_OK driven by safety MCU contactor-enable mirror
 *   - DYNAMIXEL Protocol 2.0 X-series (or compatible) on half-duplex bus
 *
 * This firmware is a complete, buildable reference implementation of the
 * host protocol and local safety clamps. DYNAMIXEL register writes are
 * gated behind DXL_HARDWARE=1; without hardware the bridge still exercises
 * the protocol, clamps, and fault state machine (HOST_SIM mode).
 *
 * Build: PlatformIO env `stm32_bridge` (see platformio.ini) or any STM32
 * Arduino-compatible core. Not a certified functional-safety product.
 */

#include <Arduino.h>
#include "protocol.h"

// ---- board pins (override in build flags if needed) ------------------------
#ifndef PIN_SAFETY_OK
#define PIN_SAFETY_OK 7
#endif
#ifndef PIN_STATUS_LED
#define PIN_STATUS_LED 13
#endif

// Set to 1 when DYNAMIXEL SDK / Dynamixel2Arduino is linked on real hardware
#ifndef DXL_HARDWARE
#define DXL_HARDWARE 0
#endif

#if DXL_HARDWARE
#include <Dynamixel2Arduino.h>
// Use Serial1 for DXL bus on typical STM32 boards — adjust in platformio.ini
Dynamixel2Arduino dxl(Serial1, -1);
#endif

// ---- state -----------------------------------------------------------------
static unsigned long lastHostHbMs = 0;
static bool safetyOk = false;
static bool faultLatched = true;
static BridgeFault lastFault = BRIDGE_FAULT_SAFETY;
static uint8_t knownIds[DXL_MAX_IDS];
static uint8_t nKnownIds = 0;
static uint32_t cmdCount = 0;
static uint32_t rejectCount = 0;

// Simulated present positions when DXL_HARDWARE=0
static int32_t simPos[DXL_MAX_IDS];
static bool simTorque[DXL_MAX_IDS];

void setFault(BridgeFault f, const char *reason) {
  faultLatched = true;
  lastFault = f;
  safetyOk = (f == BRIDGE_OK) ? safetyOk : false;
  Serial.print(F("EVENT FAULT reason="));
  Serial.println(reason);

  // Best-effort torque-off
#if DXL_HARDWARE
  for (uint8_t i = 0; i < nKnownIds; i++) {
    dxl.torqueOff(knownIds[i]);
  }
#else
  for (uint8_t i = 0; i < DXL_MAX_IDS; i++) {
    simTorque[i] = false;
  }
#endif
}

bool pathReady() {
  unsigned long age = millis() - lastHostHbMs;
  bool hbOk = (lastHostHbMs != 0) && (age < BRIDGE_HB_TIMEOUT_MS);
  // Prefer hard GPIO if wired; fall back to host SAFETY line
  bool gpioSafety = digitalRead(PIN_SAFETY_OK) == HIGH;
  bool ok = (gpioSafety || safetyOk) && hbOk && !faultLatched;
  return ok;
}

int findIdSlot(uint8_t id) {
  for (uint8_t i = 0; i < nKnownIds; i++) {
    if (knownIds[i] == id) return i;
  }
  return -1;
}

void ensureId(uint8_t id) {
  if (findIdSlot(id) >= 0) return;
  if (nKnownIds >= DXL_MAX_IDS) return;
  knownIds[nKnownIds] = id;
  simPos[nKnownIds] = 2048;
  simTorque[nKnownIds] = false;
  nKnownIds++;
}

bool parseKvInt(const String &line, const char *key, long &out) {
  String token = String(key) + "=";
  int idx = line.indexOf(token);
  if (idx < 0) return false;
  int start = idx + token.length();
  int end = start;
  while (end < (int)line.length() && (isDigit(line[end]) || line[end] == '-' || line[end] == '+')) {
    end++;
  }
  out = line.substring(start, end).toInt();
  return true;
}

void printStatus() {
  unsigned long age = (lastHostHbMs == 0) ? 99999UL : (millis() - lastHostHbMs);
  bool gpioSafety = digitalRead(PIN_SAFETY_OK) == HIGH;
  Serial.print(F("STATUS ok="));
  Serial.print(pathReady() ? 1 : 0);
  Serial.print(F(" safety="));
  Serial.print((gpioSafety || safetyOk) ? 1 : 0);
  Serial.print(F(" gpio_safety="));
  Serial.print(gpioSafety ? 1 : 0);
  Serial.print(F(" fault="));
  Serial.print(faultLatched ? 1 : 0);
  Serial.print(F(" last_fault="));
  Serial.print((int)lastFault);
  Serial.print(F(" hb_age_ms="));
  Serial.print(age);
  Serial.print(F(" dxl_hw="));
  Serial.print(DXL_HARDWARE);
  Serial.print(F(" n_ids="));
  Serial.print(nKnownIds);
  Serial.print(F(" cmds="));
  Serial.print(cmdCount);
  Serial.print(F(" rejects="));
  Serial.println(rejectCount);
}

void cmdTorque(uint8_t id, bool on) {
  ensureId(id);
#if DXL_HARDWARE
  if (on) dxl.torqueOn(id);
  else dxl.torqueOff(id);
#else
  int slot = findIdSlot(id);
  if (slot >= 0) simTorque[slot] = on;
#endif
}

void cmdGoal(uint8_t id, int32_t pos) {
  ensureId(id);
  int slot = findIdSlot(id);
  if (slot < 0) return;

  // Local step clamp (prevents single-packet jerks)
  int32_t cur;
#if DXL_HARDWARE
  cur = dxl.getPresentPosition(id);
#else
  cur = simPos[slot];
#endif
  int32_t delta = pos - cur;
  if (delta > BRIDGE_MAX_GOAL_DELTA) pos = cur + BRIDGE_MAX_GOAL_DELTA;
  if (delta < -BRIDGE_MAX_GOAL_DELTA) pos = cur - BRIDGE_MAX_GOAL_DELTA;

#if DXL_HARDWARE
  dxl.setGoalPosition(id, pos);
#else
  if (simTorque[slot]) simPos[slot] = pos;
#endif
}

void handleLine(String line) {
  line.trim();
  if (line.length() == 0) return;
  cmdCount++;

  if (line == "HB" || line == "HEARTBEAT") {
    lastHostHbMs = millis();
    // First heartbeat after boot does not clear fault alone — need SAFETY
    return;
  }

  if (line == "PING") {
    Serial.println(F("PONG bridge=stm32-dxl"));
    return;
  }

  if (line == "STATUS") {
    printStatus();
    return;
  }

  if (line == "STOP") {
    // Hold position: leave torque on if path ready, else disable
    if (!pathReady()) {
      setFault(BRIDGE_FAULT_SAFETY, "stop_while_unsafe");
    }
    Serial.println(F("EVENT STOP"));
    return;
  }

  if (line == "DISABLE") {
#if DXL_HARDWARE
    for (uint8_t i = 0; i < nKnownIds; i++) dxl.torqueOff(knownIds[i]);
#else
    for (uint8_t i = 0; i < DXL_MAX_IDS; i++) simTorque[i] = false;
#endif
    Serial.println(F("EVENT DISABLE"));
    return;
  }

  if (line == "SCAN") {
#if DXL_HARDWARE
    nKnownIds = 0;
    for (int id = 1; id < 253 && nKnownIds < DXL_MAX_IDS; id++) {
      if (dxl.ping(id)) {
        knownIds[nKnownIds++] = (uint8_t)id;
      }
    }
#else
    // Simulated default research map: IDs 1..12 (upper-body bench)
    nKnownIds = 0;
    for (uint8_t id = 1; id <= 12; id++) {
      knownIds[nKnownIds] = id;
      simPos[nKnownIds] = 2048;
      simTorque[nKnownIds] = false;
      nKnownIds++;
    }
#endif
    Serial.print(F("EVENT SCAN n_ids="));
    Serial.println(nKnownIds);
    return;
  }

  if (line.startsWith("SAFETY")) {
    long v = 0;
    if (parseKvInt(line, "ok", v)) {
      safetyOk = (v != 0);
      if (safetyOk && digitalRead(PIN_SAFETY_OK) == HIGH) {
        faultLatched = false;
        lastFault = BRIDGE_OK;
      }
      if (!safetyOk) {
        setFault(BRIDGE_FAULT_SAFETY, "host_safety_ok=0");
      }
    }
    return;
  }

  if (line.startsWith("ENALL")) {
    if (!pathReady()) {
      rejectCount++;
      Serial.println(F("EVENT REJECT reason=path_not_ready cmd=ENALL"));
      return;
    }
    long t = 0;
    parseKvInt(line, "torque", t);
    for (uint8_t i = 0; i < nKnownIds; i++) {
      cmdTorque(knownIds[i], t != 0);
    }
    Serial.println(F("EVENT ENALL ok=1"));
    return;
  }

  if (line.startsWith("EN ")) {
    if (!pathReady()) {
      rejectCount++;
      Serial.println(F("EVENT REJECT reason=path_not_ready cmd=EN"));
      return;
    }
    long id = 0, t = 0;
    if (!parseKvInt(line, "id", id) || !parseKvInt(line, "torque", t)) {
      Serial.println(F("EVENT REJECT reason=bad_args cmd=EN"));
      return;
    }
    cmdTorque((uint8_t)id, t != 0);
    Serial.println(F("EVENT EN ok=1"));
    return;
  }

  if (line.startsWith("GOAL")) {
    if (!pathReady()) {
      rejectCount++;
      Serial.println(F("EVENT REJECT reason=path_not_ready cmd=GOAL"));
      return;
    }
    long id = 0, pos = 0;
    if (!parseKvInt(line, "id", id) || !parseKvInt(line, "pos", pos)) {
      Serial.println(F("EVENT REJECT reason=bad_args cmd=GOAL"));
      return;
    }
    cmdGoal((uint8_t)id, (int32_t)pos);
    Serial.println(F("EVENT GOAL ok=1"));
    return;
  }

  if (line.startsWith("VEL")) {
    if (!pathReady()) {
      rejectCount++;
      Serial.println(F("EVENT REJECT reason=path_not_ready cmd=VEL"));
      return;
    }
    long id = 0, vel = 0;
    if (!parseKvInt(line, "id", id) || !parseKvInt(line, "vel", vel)) {
      Serial.println(F("EVENT REJECT reason=bad_args cmd=VEL"));
      return;
    }
    if (vel > BRIDGE_MAX_PROFILE_VEL) vel = BRIDGE_MAX_PROFILE_VEL;
    if (vel < 0) vel = 0;
#if DXL_HARDWARE
    dxl.writeControlTableItem(DXL_ADDR_PROFILE_VELOCITY, (uint8_t)id, (int32_t)vel);
#else
    (void)id;
#endif
    Serial.println(F("EVENT VEL ok=1"));
    return;
  }

  if (line == "CLEAR") {
    // Clear software fault only if GPIO safety is healthy
    if (digitalRead(PIN_SAFETY_OK) == HIGH) {
      faultLatched = false;
      lastFault = BRIDGE_OK;
      safetyOk = true;
      lastHostHbMs = millis();
      Serial.println(F("EVENT CLEAR ok=1"));
    } else {
      Serial.println(F("EVENT CLEAR ok=0 reason=gpio_safety_low"));
    }
    return;
  }

  Serial.print(F("EVENT UNKNOWN_CMD cmd="));
  Serial.println(line);
}

void setup() {
  pinMode(PIN_SAFETY_OK, INPUT_PULLDOWN);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_STATUS_LED, LOW);

  Serial.begin(BRIDGE_SERIAL_BAUD);
  delay(50);

#if DXL_HARDWARE
  dxl.begin(DXL_BAUDRATE);
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
#endif

  faultLatched = true;
  lastFault = BRIDGE_FAULT_SAFETY;
  lastHostHbMs = 0;
  nKnownIds = 0;

  Serial.println(F("Robotrola STM32 DYNAMIXEL bridge boot"));
  Serial.println(F("POLICY motion blocked until SAFETY_OK + HB; local clamps active"));
  Serial.println(F("CMDS HB|SAFETY|EN|ENALL|GOAL|VEL|STOP|DISABLE|SCAN|STATUS|CLEAR|PING"));
}

void loop() {
  while (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    handleLine(line);
  }

  // Independent watchdog: host HB loss freezes bus
  if (lastHostHbMs != 0 && (millis() - lastHostHbMs) >= BRIDGE_HB_TIMEOUT_MS) {
    if (!faultLatched) {
      setFault(BRIDGE_FAULT_HEARTBEAT, "host_heartbeat_timeout");
    }
  }

  // GPIO safety drops instantly
  if (digitalRead(PIN_SAFETY_OK) == LOW && safetyOk) {
    setFault(BRIDGE_FAULT_SAFETY, "gpio_safety_dropped");
  }

  bool ready = pathReady();
  digitalWrite(PIN_STATUS_LED, ready ? HIGH : ((millis() / 250) % 2));

  delay(5);
}
