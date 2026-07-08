
# Mechanical architecture

## Body strategy

Robotrola Core uses a two-layer mechanical model:

1. **Internal frame:** aluminum/CNC or high-strength printed fixtures for load paths.
2. **External shell:** printable non-load-bearing shells for appearance, covers, airflow, sensor placement, and cable routing.

The included STLs are reference shells and fixtures. Do not treat them as final load-bearing parts.

## Subassemblies

| Subassembly | Files | Purpose |
|---|---|---|
| Head/neck | `head_shell_front`, `head_shell_back`, `neck_gimbal_mount`, `camera_bar_mount` | Camera, mic, expression, sensor packaging. |
| Torso | `torso_front_shell`, `torso_back_shell`, `electronics_tray` | Compute, power distribution, cable channels, service panels. |
| Arms/hands | `upper_arm_shell`, `forearm_shell`, `hand_palm`, `finger_phalanx_*` | Shell and tactile/dexterity test packaging. |
| Pelvis/legs | `pelvis_frame`, `thigh_shell`, `shin_shell`, `foot_sole_force_sensor_mount` | Lower-body packaging and force-sensor placement. |
| Safety/service | `e_stop_button_plate`, `battery_cradle`, `docking_alignment_target`, `peristaltic_pump_mount`, `hygiene_dock_nozzle_mount` | Safety, power, docking, and non-explicit service modules. |

## Materials

- PLA/PLA+: fit and visual prototypes only.
- PETG: moderate temperature covers and non-load fixtures.
- PA-CF / nylon carbon fiber: stronger prototypes, requires dry filament and enclosure.
- Aluminum / steel: final load path, actuator plates, high-stress joints.
- Medical-grade silicone: soft exterior skin research; use vendor material safety data sheets.

## Fasteners

Default hardware pattern:

- M3 heat-set inserts for shells.
- M4/M5 for actuator brackets.
- Threadlocker only where service schedule allows.
- Locknuts or captive nuts for vibration zones.
