# Security Policy

## Supported versions

The `main` branch of this repository is the supported research surface.

## Reporting a vulnerability

**Do not open a public issue for security-sensitive reports.**

Email or private channel preferred for:

- local audio/video pipeline abuse
- actuator / safety-gate bypasses
- feature-flag or config default regressions that enable remote/cloud control
- log retention / privacy leaks
- supply-chain issues in published packages or CI

Include: affected path, reproduction steps, impact, and whether a fix is proposed.

## Hardening posture (defaults)

- Local-first processing; cloud connectivity **off** by default
- No remote actuation path in the pure-Python command stack
- Safety MCU contactor path independent of application Linux
- High-risk modules feature-flagged and interlocked

We treat “safety bypass for convenience” as a security bug.
