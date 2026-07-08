
# SOTA 2026 stack decisions

## Baseline

- ROS 2 Jazzy for stable middleware.
- Gazebo Jetty/Harmonic-compatible simulation configs.
- Isaac Sim / Isaac Lab optional for GPU-based digital twin and synthetic data.
- LeRobot-compatible datasets for demonstrations and policies.
- MoveIt 2 for manipulation planning.
- Jetson AGX Thor/T5000-class compute for humanoid/physical-AI experiments; Orin Nano/Orin NX as lower-cost dev alternatives.
- RealSense D455 + Orbbec RGB-D support to avoid single-vendor perception lock-in.
- ROBOTIS DYNAMIXEL X-series for early prototype actuators; custom cycloidal printable actuator experiments quarantined to fixtures.

## Why this stack

Robotrola is sensor-heavy and human-adjacent. The stack prioritizes:

1. Reproducibility.
2. Local-first privacy.
3. Safety isolation.
4. Simulation before human-contact tests.
5. Modular hardware replacement.
6. Data capture compatibility with modern robot-learning workflows.
