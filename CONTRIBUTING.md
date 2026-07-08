# Contributing to Robotrola Core

Thanks for helping improve a **safety-first** open research humanoid stack.

## Ground rules

1. **Do not weaken safety defaults.** Feature flags for human contact, cloud, locomotion, hygiene, and beverage modules stay **off** unless the PR includes validation evidence and updates to the risk register.
2. **One source of truth for safety policy.** Prefer changing `robotrola/safety.py` / limits YAML; ROS nodes and firmware should mirror, not fork, semantics.
3. **Claims discipline.** If you expand a “works today” claim, update `docs/CLAIMS_MATRIX.md` and add a test or validator gate.
4. **No load-bearing fantasy.** Do not mark STLs as structural without FEA/physical coupon evidence.

## Development setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make diligence
```

## PR checklist

- [ ] Design intent (what / why) in the PR body  
- [ ] Risk impact (`docs/risk_register.md` if severity changes)  
- [ ] Affected subsystem listed  
- [ ] Tests or `validate_repo` coverage for new gates  
- [ ] Rollback notes if firmware/hardware pinouts change  

## Code style

- Python 3.10+, `pytest`, keep modules small and importable without ROS/hardware.
- Firmware: document serial commands next to the code that implements them.

## Security-sensitive changes

Contact maintainers privately for actuator control, auth, OTA, or data exfiltration paths — see `SECURITY.md`.
