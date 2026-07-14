# Simulation

## Hardware-free sim smoke (shipped)

```bash
python scripts/sim_smoke.py
# → SIM_SMOKE_OK
```

Runs a small joint-space trajectory through `robotrola.joint_filter` using the
shipped 42-DOF description. **Not** a physics engine.

## Gazebo

Use Gazebo for open simulation, ROS 2 bridges, sensors, and controller smoke
tests. Config notes live under `simulation/gazebo/`. Full plant correlation is
**lab next**.

## Isaac Sim / Isaac Lab

Optional high-fidelity digital twin and synthetic data. See `simulation/isaac/`.

## MuJoCo

Research MJCF export ships under `simulation/mujoco/robotrola_r01_research.xml`.

```bash
python scripts/sim_mujoco_smoke.py   # MUJOCO_SMOKE_OK (export; load if mujoco installed)
```

## Digital twin checklist (lab)

- match mesh scale
- measure mass/inertia (replace URDF estimates)
- measure joint limits
- measure actuator delay
- model foot contact/friction
- compare simulated and real sensor timings
