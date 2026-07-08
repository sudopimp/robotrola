# SPEC — Investor- & engineer-defensible Robotrola Core

## Intent

Make `robotrola-core` a package a technical founder can open in a diligence room and defend without hand-waving: every material claim is either (a) exercised by code/tests, (b) explicitly marked lab/physical next, or (c) explicitly out of scope.

This is **not** a claim of a certified consumer product or factory SKU.

## Completion conditions

| ID | Condition | verifyHint |
|---|---|---|
| C1 | **Claims matrix exists** and separates Proven / Lab-next / Not-claimed | `docs/CLAIMS_MATRIX.md` contains sections `## Proven today`, `## Lab next`, `## Not claimed`; `pytest -k claims` passes |
| C2 | **Investor tech brief** states architecture, stack, cost bands, risks, honest status | `docs/INVESTOR_TECH_BRIEF.md` exists; mentions 42 DOF, safety layers, BOM stage costs, not certified |
| C3 | **Pure-Python E2E demo** runs twice identically: boot→arm→activate→approve legal→reject illegal→estop→reset; prints joint-space sample + protocol sim | `python scripts/demo_investor.py` exit 0; stdout contains `INVESTOR_DEMO_OK` and `dof=42` |
| C4 | **Host firmware protocol simulator** mirrors safety MCU cmds HEARTBEAT/RESET/FAULT/STATUS with tests | `robotrola/protocol_sim.py` + `tests/test_protocol_sim.py`; pytest green |
| C5 | **BOM stage cost model** produces bench / upper_body / full_body low–high USD bands from shipped BOM | `python scripts/bom_cost_model.py` exit 0; JSON keys `bench`,`upper_body`,`full_body` with `low_usd`,`high_usd` |
| C6 | **LeRobot episode path** writes schema-valid episode via adapter after safety-approved action only | `tests/test_lerobot_path.py` passes; rejects write when not ACTIVE |
| C7 | **Feature flags gate** dangerous modules; command path refuses if human_contact_mode off for contact-tagged cmds | `tests/test_features.py` + command_path feature gate tests pass |
| C8 | **CI gates** install, pytest, validate_repo, demo_investor, bom_cost_model | `.github/workflows/ci.yml` includes those steps; local equivalent exit 0 |
| C9 | **Completeness suite** still green: 42 DOF, firmware sources, print stages, validator | `pytest -q` exit 0; `python scripts/validate_repo.py` → `VALIDATION PASSED` |
| C10 | **README** positions as complete open research platform + points to claims matrix and investor demo | README links/mentions `docs/CLAIMS_MATRIX.md` and `scripts/demo_investor.py` |

## Non-goals

- Physical robot assembly or certification
- Trained locomotion/manipulation policy weights
- Website redesign
- GitHub publish (user-gated)

## Evidence directory

CI and `make diligence` are the public evidence path.


## Evidence (filled)

| ID | Result |
|---|---|
| C1 | `docs/CLAIMS_MATRIX.md` sections present; `pytest -k claims` green |
| C2 | `docs/INVESTOR_TECH_BRIEF.md` shipped |
| C3 | `python scripts/demo_investor.py` → `INVESTOR_DEMO_OK` `dof=42` |
| C4 | `robotrola/protocol_sim.py` + `tests/test_protocol_sim.py` |
| C5 | `scripts/bom_cost_model.py` → bench/upper_body/full_body bands |
| C6 | `tests/test_lerobot_path.py` |
| C7 | hand cmds blocked without `human_contact_mode` |
| C8 | `.github/workflows/ci.yml` runs pytest, validate, bom_cost, safety, demo |
| C9 | full pytest + validate_repo green |
| C10 | README points to CLAIMS_MATRIX + demo_investor |

Re-run `make diligence` on any machine; CI mirrors the same gates.
