from __future__ import annotations

from pathlib import Path
import csv
import re
import yaml

from robotrola.description import (
    assert_full_humanoid,
    mesh_filenames,
    DEFAULT_URDF,
    TARGET_DOF,
    MIN_HUMANOID_DOF,
)

REQUIRED_PATHS = [
    "README.md",
    "SAFETY.md",
    "SPEC.md",
    "docs/CLAIMS_MATRIX.md",
    "docs/INVESTOR_TECH_BRIEF.md",
    "hardware/BOM.csv",
    "configs/feature_flags.yaml",
    "configs/safety_limits.yaml",
    "configs/robot_description/joints.yaml",
    "cad/print_manifest.csv",
    "cad/urdf/robotrola_r01_reference.urdf.xacro",
    "ros2_ws/src/robotrola_description/package.xml",
    "ros2_ws/src/robotrola_description/urdf/robotrola_r01_reference.urdf.xacro",
    "firmware/esp32_safety_mcu/src/main.cpp",
    "firmware/esp32_safety_mcu/include/config.h",
    "firmware/stm32_dynamixel_bridge/src/main.cpp",
    "firmware/stm32_dynamixel_bridge/include/protocol.h",
    "robotrola/safety.py",
    "robotrola/command_path.py",
    "robotrola/description.py",
    "robotrola/protocol_sim.py",
    "robotrola/cost_model.py",
    "robotrola/joint_filter.py",
    "robotrola/sim_core.py",
    "robotrola/msgs.py",
    "robotrola/host_serial.py",
    "lerobot/v3_layout.py",
    "scripts/demo_investor.py",
    "scripts/bom_cost_model.py",
    "scripts/run_safety_path.py",
    "scripts/sim_smoke.py",
    "scripts/check_firmware.py",
    "scripts/host_serial_demo.py",
    "scripts/sim_mujoco_smoke.py",
    "scripts/export_mujoco_model.py",
    "robotrola/host_client.py",
    "ros2_ws/src/robotrola_control/scripts/joint_command_filter_node.py",
    "ros2_ws/src/robotrola_teleop/scripts/keyboard_teleop_node.py",
    "ros2_ws/src/robotrola_perception/scripts/camera_config_node.py",
    "ros2_ws/src/robotrola_msgs/msg/JointCommand.msg",
    "ros2_ws/src/robotrola_msgs/msg/CommandResult.msg",
    ".github/workflows/firmware-optional.yml",
    ".github/workflows/ros-optional.yml",
]


def validate_repo(root: str | Path = ".") -> list[str]:
    root = Path(root)
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing:{rel}")

    flags_path = root / "configs/feature_flags.yaml"
    if flags_path.exists():
        flags = yaml.safe_load(flags_path.read_text()).get("feature_flags", {})
        for dangerous in ["autonomous_locomotion", "human_contact_mode", "cloud_connectivity"]:
            if flags.get(dangerous) is True:
                errors.append(f"dangerous_feature_enabled_by_default:{dangerous}")

    bom_path = root / "hardware/BOM.csv"
    if bom_path.exists():
        rows = list(csv.DictReader(open(bom_path, encoding="utf-8")))
        if len(rows) < 15:
            errors.append("bom_too_small")
        cats = {r.get("category", "") for r in rows}
        for need in ["compute", "mcu", "actuation", "power", "safety", "vision", "docking", "service"]:
            if need not in cats:
                errors.append(f"bom_missing_category:{need}")
        if not any(r.get("risk") == "critical" for r in rows):
            errors.append("bom_missing_critical_risk_items")

    # Full humanoid description gate
    urdf = root / "cad/urdf/robotrola_r01_reference.urdf.xacro"
    if urdf.exists():
        from robotrola.description import inertial_coverage, urdf_limits_align_with_safety

        info = assert_full_humanoid(urdf)
        if info["revolute_count"] < MIN_HUMANOID_DOF:
            errors.append(f"urdf_dof_too_low:{info['revolute_count']}<{MIN_HUMANOID_DOF}")
        if info["revolute_count"] != TARGET_DOF:
            errors.append(f"urdf_dof_not_target:{info['revolute_count']}!={TARGET_DOF}")
        if info["missing_regions"]:
            errors.append("urdf_missing_regions:" + ",".join(info["missing_regions"]))
        # mesh files must exist under description package
        mesh_dir = root / "ros2_ws/src/robotrola_description/meshes"
        for mesh in mesh_filenames(urdf):
            if not (mesh_dir / mesh).exists() and not (root / "cad/stl" / mesh).exists():
                errors.append(f"mesh_missing:{mesh}")
        cov = inertial_coverage(urdf)
        if not cov["ok"]:
            errors.append(
                f"urdf_inertial_incomplete:links={cov['link_count']}"
                f",inertial={cov['inertial_count']},mass={cov['mass_count']}"
            )
        align = urdf_limits_align_with_safety(
            urdf, root / "configs/safety_limits.yaml"
        )
        if not align["ok"]:
            errors.append("urdf_safety_limits_mismatch:" + ",".join(align["mismatches"]))

    # joint limits cover neck + a leg + a hand joint
    limits_path = root / "configs/safety_limits.yaml"
    if limits_path.exists():
        limits = yaml.safe_load(limits_path.read_text()).get("joint_limits", {})
        for need in ["neck_yaw", "left_knee", "right_index_curl", "waist_yaw"]:
            if need not in limits:
                errors.append(f"limits_missing_joint:{need}")

    # firmware protocol markers (serial safety MCU — not micro-ROS)
    mcu = root / "firmware/esp32_safety_mcu/src/main.cpp"
    if mcu.exists():
        src = mcu.read_text(encoding="utf-8")
        for token in ["HEARTBEAT", "RESET", "FAULT", "STATUS", "PIN_ESTOP"]:
            if token not in src:
                errors.append(f"firmware_missing_token:{token}")
        if len(src.splitlines()) < 80:
            errors.append("firmware_too_thin")
        # Real micro-ROS / rclc stack would pull these APIs — must not appear here
        for bad in ("#include <micro_ros", "rclc_support", "rmw_microxrcedds", "rcl_init"):
            if bad in src:
                errors.append(f"firmware_unexpected_ros_client_api:{bad}")
    # Forbid legacy misleading package path
    if (root / "firmware/micro_ros_safety_esp32").exists():
        errors.append("legacy_micro_ros_package_path_present")

    # Phase-0+ ROS packages must ship nodes (not empty shells)
    for rel, needle in [
        (
            "ros2_ws/src/robotrola_control/scripts/joint_command_filter_node.py",
            "JointCommandFilter",
        ),
        (
            "ros2_ws/src/robotrola_teleop/scripts/keyboard_teleop_node.py",
            "joint_command_json",
        ),
    ]:
        p = root / rel
        if p.is_file():
            txt = p.read_text(encoding="utf-8", errors="replace")
            if needle not in txt:
                errors.append(f"ros_node_thin:{rel}")
            if len(txt.splitlines()) < 30:
                errors.append(f"ros_node_too_short:{rel}")

    for pkg_xml in [
        "ros2_ws/src/robotrola_control/package.xml",
        "ros2_ws/src/robotrola_teleop/package.xml",
    ]:
        px = root / pkg_xml
        if px.is_file() and "stub" in px.read_text(encoding="utf-8").lower():
            errors.append(f"ros_package_still_stub:{pkg_xml}")

    bridge = root / "firmware/stm32_dynamixel_bridge/src/main.cpp"
    if bridge.exists():
        bsrc = bridge.read_text(encoding="utf-8")
        if "dynamixel" not in bsrc.lower() and "DXL" not in bsrc:
            errors.append("bridge_missing_dynamixel_refs")
        if len(bsrc.splitlines()) < 40:
            errors.append("bridge_too_thin")

    # print manifest maps assembly stages
    man = root / "cad/print_manifest.csv"
    if man.exists():
        rows = list(csv.DictReader(open(man, encoding="utf-8")))
        if len(rows) < 15:
            errors.append("print_manifest_too_small")
        if "stage" in (rows[0] if rows else {}):
            stages = {r.get("stage", "") for r in rows}
            for s in ["bench", "upper_body", "full_body"]:
                if s not in stages:
                    errors.append(f"print_manifest_missing_stage:{s}")

    # diligence docs must separate proven vs not claimed
    claims = root / "docs/CLAIMS_MATRIX.md"
    if claims.exists():
        ct = claims.read_text(encoding="utf-8")
        for heading in ["## Proven today", "## Lab next", "## Not claimed"]:
            if heading not in ct:
                errors.append(f"claims_missing_section:{heading}")

    return errors
