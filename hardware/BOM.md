# Bill of Materials

Generated from `hardware/BOM.csv`. Prices are rough planning bands, not procurement quotes.

| Category | Item | Candidate | Qty | Est. USD | Risk | Notes |
|---|---|---|---:|---:|---|---|
| compute | Edge AI computer | NVIDIA Jetson AGX Thor Developer Kit / T5000 module | 1 | 2999-3499 | medium | SOTA edge AI target; power/thermal heavy |
| compute | Budget dev computer | Jetson Orin Nano Super / Orin NX | 1 | 249-799 | low | Use for bench perception before Thor |
| mcu | Safety microcontroller | ESP32-S3 or STM32H7 safety board | 1 | 15-80 | medium | Owns e-stop/watchdog/contactor |
| vision | RGB-D camera | Intel RealSense D455 | 1 | 250-450 | low | Depth 1280x720 up to 90 FPS, USB 3.1 |
| vision | RGB-D alternative | Orbbec Gemini/Femto + Orbbec SDK v2 | 1 | 200-600 | low | Open SDK v2 support |
| actuation | Smart actuator prototype | ROBOTIS DYNAMIXEL X-Series | 12 | 80-800 | medium | Prototype joints, grippers, neck, fixture tests |
| actuation | Custom actuator R&D | 3D printed cycloidal actuator fixture | 2 | 50-200 | high | Fixture only until validated |
| hands | Dexterous hand placeholder | DYNAMIXEL/Feetech servo hand or commercial tactile hand | 2 | 300-8000 | high | Start with low-force test hand |
| audio | Mic array | USB/local mic array | 1 | 30-200 | medium | Local voice only, no cloud default |
| power | Battery | Certified 48V pack with BMS | 1 | 500-2000 | critical | Do not self-build pack without qualified review |
| power | Contactor/fuse/disconnect | DC contactor + fuse + service disconnect | 1 | 100-400 | critical | Safety MCU controls contactor |
| safety | Emergency stop | Normally-closed mushroom e-stop loop | 2 | 20-100 | critical | Hardware loop, not software only |
| safety | Deadman switch | Handheld/footswitch deadman | 1 | 20-100 | critical | Required for human-adjacent tests |
| sensing | Foot force sensors | 6-axis load cell or FSR matrix per foot | 2 | 50-500 | medium | Balance/ground contact |
| sensing | Tactile sensors | Capacitive/pressure tactile strips | 1 | 50-500 | medium | Distributed low-force contact sensing |
| docking | Wireless/contact docking | Renesas Ki wireless docking or contact dock | 1 | TBD | medium | Autonomous charging only after safety review |
| service | Idle hygiene dock | Sealed airflow + replaceable liners + optional interlocked UV-C | 1 | TBD | high | External sealed dock only; UV-C hazard |
| service | Beverage service pump | Food-grade peristaltic pump + leak detector | 1 | 20-200 | high | Manual-confirm service module; isolated from electronics |
| materials | Prototype filament | PETG / PLA+ / PA-CF | 1 | 100-400 | medium | See print profile |
| materials | Soft exterior skin | Medical-grade silicone research materials | 1 | TBD | medium | Use vendor MSDS/biocompat docs |
