#!/usr/bin/env python3
"""Generate full R-01 humanoid URDF + joint limits from the joint map (single source)."""
from __future__ import annotations

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]

# 42 DOF humanoid map: (name, parent, child, origin_xyz, axis, lower, upper, effort, velocity, mesh)
# mesh may be None for pure kinematic links
def joint_map() -> list[dict]:
    m = []

    def j(name, parent, child, xyz, axis, lo, hi, effort, vel, mesh=None, jtype="revolute"):
        m.append(dict(name=name, parent=parent, child=child, xyz=xyz, axis=axis,
                      lo=lo, hi=hi, effort=effort, vel=vel, mesh=mesh, jtype=jtype))

    # torso chain
    j("waist_yaw", "pelvis_link", "waist_link", "0 0 0.08", "0 0 1", -0.6, 0.6, 2.0, 0.2, "pelvis_frame.stl")
    j("waist_pitch", "waist_link", "torso_link", "0 0 0.12", "0 1 0", -0.35, 0.45, 2.5, 0.2, "torso_front_shell.stl")
    j("waist_roll", "torso_link", "torso_roll_link", "0 0 0.05", "1 0 0", -0.3, 0.3, 1.5, 0.2, "torso_back_shell.stl")

    # neck/head 3
    j("neck_yaw", "torso_roll_link", "neck_yaw_link", "0 0 0.28", "0 0 1", -0.9, 0.9, 0.5, 0.25, "neck_gimbal_mount.stl")
    j("neck_pitch", "neck_yaw_link", "neck_pitch_link", "0 0 0.04", "0 1 0", -0.5, 0.6, 0.5, 0.25, None)
    j("neck_roll", "neck_pitch_link", "head_link", "0 0 0.06", "1 0 0", -0.35, 0.35, 0.4, 0.2, "head_shell_front.stl")

    # arms 7 each
    for side, sx in (("left", 0.18), ("right", -0.18)):
        pre = f"{side}_"
        j(f"{pre}shoulder_pitch", "torso_roll_link", f"{pre}shoulder_pitch_link",
          f"{sx} 0 0.22", "0 1 0", -1.4, 1.4, 1.5, 0.25, "upper_arm_shell.stl")
        j(f"{pre}shoulder_roll", f"{pre}shoulder_pitch_link", f"{pre}shoulder_roll_link",
          "0 0 0", "1 0 0", -0.3 if side == "left" else -1.5, 1.5 if side == "left" else 0.3, 1.2, 0.25, None)
        j(f"{pre}shoulder_yaw", f"{pre}shoulder_roll_link", f"{pre}upper_arm_link",
          "0 0 -0.05", "0 0 1", -1.2, 1.2, 1.0, 0.3, None)
        j(f"{pre}elbow", f"{pre}upper_arm_link", f"{pre}forearm_link",
          "0 0 -0.22", "0 1 0", 0.0, 2.2, 1.0, 0.3, "forearm_shell.stl")
        j(f"{pre}wrist_yaw", f"{pre}forearm_link", f"{pre}wrist_yaw_link",
          "0 0 -0.2", "0 0 1", -1.4, 1.4, 0.4, 0.4, None)
        j(f"{pre}wrist_pitch", f"{pre}wrist_yaw_link", f"{pre}wrist_pitch_link",
          "0 0 0", "0 1 0", -0.9, 0.9, 0.4, 0.4, None)
        j(f"{pre}wrist_roll", f"{pre}wrist_pitch_link", f"{pre}hand_link",
          "0 0 0", "1 0 0", -0.9, 0.9, 0.3, 0.4, "hand_palm.stl")
        # hand 5 fingers * 1 DOF (curl) = 10
        for fi, fname in enumerate(["thumb", "index", "middle", "ring", "pinky"]):
            mesh = "finger_phalanx_proximal.stl" if fi < 2 else "finger_phalanx_distal.stl"
            j(f"{pre}{fname}_curl", f"{pre}hand_link", f"{pre}{fname}_link",
              f"{0.02*(fi-2)} 0.03 0.02", "0 1 0", 0.0, 1.4, 0.15, 0.5, mesh)

    # legs 6 each
    for side, sy in (("left", 0.1), ("right", -0.1)):
        pre = f"{side}_"
        j(f"{pre}hip_yaw", "pelvis_link", f"{pre}hip_yaw_link",
          f"0 {sy} -0.05", "0 0 1", -0.6, 0.6, 2.0, 0.25, None)
        j(f"{pre}hip_roll", f"{pre}hip_yaw_link", f"{pre}hip_roll_link",
          "0 0 0", "1 0 0", -0.4, 0.4, 2.0, 0.25, None)
        j(f"{pre}hip_pitch", f"{pre}hip_roll_link", f"{pre}thigh_link",
          "0 0 0", "0 1 0", -1.4, 0.8, 3.0, 0.25, "thigh_shell.stl")
        j(f"{pre}knee", f"{pre}thigh_link", f"{pre}shin_link",
          "0 0 -0.35", "0 1 0", 0.0, 2.2, 3.0, 0.3, "shin_shell.stl")
        j(f"{pre}ankle_pitch", f"{pre}shin_link", f"{pre}ankle_pitch_link",
          "0 0 -0.35", "0 1 0", -0.7, 0.7, 1.5, 0.3, None)
        j(f"{pre}ankle_roll", f"{pre}ankle_pitch_link", f"{pre}foot_link",
          "0 0 0", "1 0 0", -0.4, 0.4, 1.0, 0.3, "foot_sole_force_sensor_mount.stl")

    return m


def write_urdf(path: Path, package_meshes: bool) -> int:
    joints = joint_map()
    if package_meshes:
        mesh_prefix = "package://robotrola_description/meshes"
    else:
        mesh_prefix = "package://robotrola_description/meshes"

    lines = [
        '<?xml version="1.0"?>',
        '<robot name="robotrola_r01" xmlns:xacro="http://www.ros.org/wiki/xacro">',
        f'  <xacro:property name="mesh_prefix" value="{mesh_prefix}" />',
        '  <!-- Robotrola R-01 full-body research description: 42 revolute DOF -->',
        '  <link name="base_link"/>',
        '  <link name="pelvis_link">',
        '    <visual><geometry><mesh filename="${mesh_prefix}/pelvis_frame.stl" scale="0.001 0.001 0.001"/></geometry></visual>',
        '    <collision><geometry><box size="0.25 0.2 0.12"/></geometry></collision>',
        '  </link>',
        '  <joint name="base_to_pelvis" type="fixed">',
        '    <parent link="base_link"/><child link="pelvis_link"/>',
        '    <origin xyz="0 0 0.95" rpy="0 0 0"/>',
        '  </joint>',
    ]

    created_links = {"base_link", "pelvis_link"}

    def ensure_link(name: str, mesh: str | None):
        if name in created_links:
            return
        created_links.add(name)
        if mesh:
            lines.append(f'  <link name="{name}">')
            lines.append(
                f'    <visual><geometry><mesh filename="${{mesh_prefix}}/{mesh}" '
                f'scale="0.001 0.001 0.001"/></geometry></visual>'
            )
            lines.append('    <collision><geometry><cylinder radius="0.04" length="0.08"/></geometry></collision>')
            lines.append('  </link>')
        else:
            lines.append(f'  <link name="{name}"/>')

    for jd in joints:
        ensure_link(jd["parent"], None if jd["parent"] == "pelvis_link" else None)
        # parents may not exist yet except pelvis
        if jd["parent"] not in created_links:
            ensure_link(jd["parent"], None)
        ensure_link(jd["child"], jd["mesh"])
        lines.append(f'  <joint name="{jd["name"]}" type="{jd["jtype"]}">')
        lines.append(f'    <parent link="{jd["parent"]}"/><child link="{jd["child"]}"/>')
        lines.append(f'    <origin xyz="{jd["xyz"]}" rpy="0 0 0"/>')
        lines.append(f'    <axis xyz="{jd["axis"]}"/>')
        lines.append(
            f'    <limit lower="{jd["lo"]}" upper="{jd["hi"]}" '
            f'effort="{jd["effort"]}" velocity="{jd["vel"]}"/>'
        )
        lines.append('  </joint>')

    # fixed accessories on torso
    for name, mesh, xyz in [
        ("camera_bar_link", "camera_bar_mount.stl", "0 0.05 0.3"),
        ("electronics_tray_link", "electronics_tray.stl", "0 -0.05 0.15"),
        ("battery_cradle_link", "battery_cradle.stl", "0 0 -0.02"),
        ("estop_plate_link", "e_stop_button_plate.stl", "0.12 0 0.2"),
        ("hygiene_dock_link", "hygiene_dock_nozzle_mount.stl", "0 -0.15 0.0"),
        ("beverage_mount_link", "peristaltic_pump_mount.stl", "0.1 -0.1 0.1"),
    ]:
        parent = "torso_roll_link" if "torso_roll_link" in created_links else "torso_link"
        ensure_link(name, mesh)
        lines.append(f'  <joint name="fixed_{name}" type="fixed">')
        lines.append(f'    <parent link="{parent}"/><child link="{name}"/>')
        lines.append(f'    <origin xyz="{xyz}" rpy="0 0 0"/>')
        lines.append('  </joint>')

    lines.append("</robot>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    return len(joints)


def write_limits_yaml(path: Path) -> int:
    joints = joint_map()
    lines = ["# Auto-generated joint limits for R-01 (42 DOF) — source: scripts/generate_robot_description.py",
             "joint_limits:"]
    lines.append("  default:")
    lines.append("    position_min_rad: -1.57")
    lines.append("    position_max_rad: 1.57")
    lines.append("    velocity_max_rad_s: 0.25")
    lines.append("    effort_max_nm: 1.0")
    for jd in joints:
        lines.append(f"  {jd['name']}:")
        lines.append(f"    position_min_rad: {jd['lo']}")
        lines.append(f"    position_max_rad: {jd['hi']}")
        lines.append(f"    velocity_max_rad_s: {jd['vel']}")
        lines.append(f"    effort_max_nm: {jd['effort']}")
    lines += [
        "thermal:",
        "  compute_max_c: 75",
        "  actuator_max_c: 65",
        "  battery_max_c: 45",
        "power:",
        "  battery_nominal_v: 48",
        "  actuator_bus_max_a: 40",
        "  logic_bus_max_a: 8",
        "watchdog:",
        "  main_heartbeat_timeout_ms: 250",
        "  mcu_loop_period_ms: 10",
        "protocol:",
        "  serial_baud: 115200",
        "  heartbeat_cmd: HEARTBEAT",
        "  reset_cmd: RESET",
        "  fault_cmd: FAULT",
        "  status_cmd: STATUS",
    ]
    path.write_text("\n".join(lines) + "\n")
    return len(joints)


def write_joint_map_yaml(path: Path) -> None:
    joints = joint_map()
    lines = [
        "# R-01 joint map (42 revolute DOF)",
        f"dof_total: {len(joints)}",
        "groups:",
        "  torso: [waist_yaw, waist_pitch, waist_roll]",
        "  head: [neck_yaw, neck_pitch, neck_roll]",
        "  left_arm: [left_shoulder_pitch, left_shoulder_roll, left_shoulder_yaw, left_elbow, left_wrist_yaw, left_wrist_pitch, left_wrist_roll]",
        "  right_arm: [right_shoulder_pitch, right_shoulder_roll, right_shoulder_yaw, right_elbow, right_wrist_yaw, right_wrist_pitch, right_wrist_roll]",
        "  left_hand: [left_thumb_curl, left_index_curl, left_middle_curl, left_ring_curl, left_pinky_curl]",
        "  right_hand: [right_thumb_curl, right_index_curl, right_middle_curl, right_ring_curl, right_pinky_curl]",
        "  left_leg: [left_hip_yaw, left_hip_roll, left_hip_pitch, left_knee, left_ankle_pitch, left_ankle_roll]",
        "  right_leg: [right_hip_yaw, right_hip_roll, right_hip_pitch, right_knee, right_ankle_pitch, right_ankle_roll]",
        "joints:",
    ]
    for jd in joints:
        lines.append(f"  - name: {jd['name']}")
        lines.append(f"    parent: {jd['parent']}")
        lines.append(f"    child: {jd['child']}")
        lines.append(f"    type: {jd['jtype']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    n1 = write_urdf(ROOT / "cad/urdf/robotrola_r01_reference.urdf.xacro", True)
    n2 = write_urdf(
        ROOT / "ros2_ws/src/robotrola_description/urdf/robotrola_r01_reference.urdf.xacro", True
    )
    n3 = write_limits_yaml(ROOT / "configs/safety_limits.yaml")
    write_limits_yaml(ROOT / "ros2_ws/src/robotrola_safety/config/safety_limits.yaml")
    write_joint_map_yaml(ROOT / "configs/robot_description/joints.yaml")
    assert n1 == n2 == n3 == 42, (n1, n2, n3)
    print(f"Generated full R-01 description: {n1} revolute DOF")


if __name__ == "__main__":
    main()
