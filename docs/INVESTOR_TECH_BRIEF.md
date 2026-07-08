# Robotrola Core — technical brief for investors & diligence engineers

**Status:** complete open research / lab-build platform (software + docs + firmware sources)  
**Not:** certified consumer product, factory SKU, or trained biped demo robot  
**Repo role:** open engineering core (`sudopimp/robotrola`)  
**Product site:** [robotrola.com](https://robotrola.com) · **X:** [@sudopimp](https://x.com/sudopimp) · **TikTok:** [@robotrola](https://www.tiktok.com/@robotrola)

## Problem framing (technical)

Building a human-adjacent companion humanoid fails when teams start from marketing renders and reverse-engineer safety later. Credible open humanoid projects (Berkeley Humanoid Lite, ToddlerBot, Reachy-class platforms) ship **description + BOM + printable/fixture path + safety gates + data path** before policies and skins.

Robotrola Core is that package for a non-explicit adult companion research line: privacy-first, feature-flagged modules, hard safety below AI.

## What you can demo in 90 seconds (no hardware)

```bash
pip install -e ".[dev]"
python scripts/demo_investor.py
```

Expected: `dof=42`, legal joint approved, over-velocity rejected, e-stop latches fault, protocol sim STATUS, stage cost bands, `INVESTOR_DEMO_OK`.

Also: `pytest -q` and `python scripts/validate_repo.py`.

## Architecture (layers investors should care about)

```text
Teleop / local policy proposal
        ↓
Feature flags (dangerous modules OFF by default)
        ↓
Safety supervisor (mode + joint limits + interlocks)   ← pure Python, tested
        ↓
Approved command stream only
        ↓
Motor bridge firmware (local clamps, HB, SAFETY_OK)    ← C++ source
        ↓
Safety MCU (e-stop, deadman, leak, contactor, watchdog)← C++ source
        ↓
Actuator power bus
```

AI never owns current. Safety MCU owns power isolation independently of Linux/ROS.

## Kinematic package

- **42 revolute DOF** full body (waist, neck, 2× arm+hand, 2× leg)
- URDF/xacro + joint map YAML + safety limits YAML generated together
- Mesh references map to shipped STL reference set
- Planar arm FK helper for fixture-level explanations

## Hardware package (research BOM)

| Stage | Intent | Cost band (BOM-derived, USD low–high) |
|---|---|---|
| Bench | Safety MCU, e-stop, tray, 1 actuator fixture, budget compute | see `python scripts/bom_cost_model.py` |
| Upper body | Torso/head/arms + sensors on stand | same script |
| Full body | Legs, pack, docking/service modules (flags off) | same script |

Critical-risk lines (battery, contactor, e-stop, deadman) are named in BOM and cannot be hand-waved away.

## Software / data

| Piece | Role |
|---|---|
| `robotrola/` | Safety, command path, description, validators, protocol sim, cost model |
| `ros2_ws/` | Thin ROS 2 wrappers; safety node **imports same library** |
| `lerobot/` | Episode writer schema-compatible with LeRobot-style datasets |
| `simulation/` | Gazebo/Isaac hooks — optional; not required for core gates |
| `firmware/` | Real serial protocols for safety MCU + DXL bridge |

## Competitive / positioning honesty

| Player class | We do **not** claim parity |
|---|---|
| Figure / Tesla Optimus / commercial bipeds | Walking product, factory scale |
| Retail “companion” gadgets | Certified consumer SKU |
| Pure web AI wrappers | Physical stack + safety ownership |

**We do claim:** a diligence-ready open research stack that a robotics hire can extend without rewriting the safety story.

## Material risks (open)

See `docs/risk_register.md`. Top: crush/pinch, battery thermal, privacy, AI unsafe action, fluid modules, non-load-bearing prints. Mitigations are architectural (flags off, contactor MCU, local-first); residual risk remains **Open** until lab validation.

## Licenses

- Software: Apache-2.0  
- Hardware docs/CAD intent: CERN-OHL-S-2.0  

## Diligence checklist

1. Read `docs/CLAIMS_MATRIX.md`  
2. Run `scripts/demo_investor.py`  
3. Run `pytest -q` + `scripts/validate_repo.py`  
4. Open firmware `main.cpp` files (protocol is in code)  
5. Open `hardware/BOM.csv` + cost model  
6. Confirm feature flags defaults  
7. Ask for lab Phase 1 schedule — that is the next capital-intensive proof  

## Capital use (suggested narrative)

1. Bench safety + one actuator (prove power cut + bus)  
2. Upper-body stand (teleop data + force limits)  
3. Only then full-body / biped R&D in cage  

Do not fund “full humanoid skin demo” before Phase 1 safety hardware closes.
