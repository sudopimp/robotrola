# FMEA — early failure-mode analysis

| Failure mode | Effect | Cause | Detection | Mitigation |
|---|---|---|---|---|
| E-stop wiring opens unintentionally | robot enters fault | cable break | NC loop state | fail-safe default off |
| Safety MCU lockup | possible stale output | firmware bug | hardware watchdog | watchdog reset + contactor off |
| Main compute hang | stale commands | OS/model failure | heartbeat timeout | MCU faults after timeout |
| Actuator overheats | burn/fire/motion fault | excessive current | temp telemetry | current derate + shutdown |
| Fluid leak | electrical hazard | tube/pump failure | leak sensor | disable pump/power, drip tray |
| UV-C interlock failure | exposure hazard | switch/wiring fault | dual interlock | no UV-C until enclosure certified |
| Battery BMS fault | power loss/thermal risk | pack failure | BMS status | certified pack and fuse |
| AI command unsafe | collision | planner/model error | safety supervisor | proposal-only architecture |
