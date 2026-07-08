
# SOTA 2026 repo comparison and design notes

This repository follows patterns from credible open robotics projects rather than treating Robotrola as a landing-page artifact.

## Repositories / projects reviewed

| Project | What it does well | Pattern copied into Robotrola Core |
|---|---|---|
| Hugging Face LeRobot | Models, datasets, policies, real-world robotics tooling, robot adapters, policy deployment docs. | `lerobot/` dataset schema, adapter scaffold, and data-first policy path. |
| Berkeley Humanoid Lite | Accessible 3D-printed humanoid, modular printed actuator/body strategy, documented sim-to-real path. | `cad/`, print manifest, actuator fixture, manufacturing checklist, sim-to-real roadmap. |
| ToddlerBot | Reproducible 3D-printed humanoid focused on policy learning, calibration, digital twin, teleop/data collection. | Calibration docs, teleop-first data collection plan, bench-to-upper-body-to-mobile roadmap. |
| Pollen Robotics / Reachy 2 | Open robotics platform with ROS ecosystem and real humanoid manipulation research. | ROS package separation: description, bringup, control, perception. |
| iCub / Robotology | Long-running open humanoid research platform with hardware + software + docs discipline. | Explicit safety, governance, and maintenance docs. |
| ROBOTIS / DYNAMIXEL ecosystem | Reusable networked smart actuator platform with docs/tools. | Prototype actuator buses and fixture-first validation. |
| Opulo LumenPnP | Open hardware manufacturing discipline: BOM, CAD, build guides, community mods. | BOM, print profile, manufacturing checklist, hardware license separation. |
| Gazebo / MoveIt / Isaac Sim | Simulation, ROS integration, manipulation planning and high-fidelity GPU digital twins. | `simulation/`, `ros2_ws/`, bridge configs, and digital-twin validation plan. |

## SOTA 2026 architecture conclusions

1. **Do not start from the full humanoid body.** Start from safety MCU + one actuator fixture, then upper-body stand, then full-body shell, then biped/mobile work in a cage.
2. **Keep AI above hard safety gates.** No VLA, LLM, or voice model should command motor current directly.
3. **Use LeRobot-style datasets early.** Even bench tests should generate synchronized camera/action/observation data with metadata.
4. **Make CAD reproducible.** Include parametric source, STL exports, print manifest, hardware inserts, and revision fields.
5. **Treat adult companion features as governance features.** Age-gating, consent UX, privacy, and interlocks belong in the repo, not as an afterthought.
6. **Use a serious compute split.** Jetson Thor/T5000-class edge AI can run perception/local models; safety MCU owns power gates.
7. **Avoid cloud dependency.** Local-first audio, vision, memory, and policy logs are easier to secure and audit.

## Primary references checked

- LeRobot docs: https://huggingface.co/docs/lerobot/index
- NVIDIA Jetson Thor: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/
- Intel RealSense D455: https://www.intel.com/content/www/us/en/products/sku/205847/intel-realsense-depth-camera-d455/specifications.html
- Orbbec SDK v2: https://github.com/orbbec/OrbbecSDK_v2
- ROBOTIS DYNAMIXEL X-Series: https://www.robotis.us/x-series/
- MoveIt 2 docs: https://moveit.picknik.ai/main/index.html
- Gazebo ROS 2 integration: https://gazebosim.org/docs/latest/ros2_integration/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- Berkeley Humanoid Lite paper/project: https://lite.berkeley-humanoid.org and arXiv 2504.17249
- ToddlerBot paper/project: arXiv 2502.00893
