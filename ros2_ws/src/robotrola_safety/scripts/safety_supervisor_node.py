#!/usr/bin/env python3
"""Thin ROS 2 safety node — delegates to shipped robotrola.safety library."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow importing the monorepo Python package when sourced from workspace
_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

from robotrola.safety import SafetySupervisor, SafetyInputs, JointCommand, SafetyMode


class SafetySupervisorNode(Node):
    """Mirrors pure-Python SafetySupervisor for ROS bringup / teleop gates."""

    def __init__(self) -> None:
        super().__init__("robotrola_safety_supervisor")
        limits = self.declare_parameter(
            "limits_path",
            str(_REPO / "configs" / "safety_limits.yaml"),
        ).value
        self.sup = SafetySupervisor(limits)
        self.sup.self_test()

        self.estop_ok = True
        self.deadman_ok = True

        self.create_subscription(Bool, "robotrola/estop_ok", self._on_estop, 10)
        self.create_subscription(Bool, "robotrola/deadman_ok", self._on_deadman, 10)
        self.create_subscription(String, "robotrola/joint_command", self._on_cmd, 10)
        self.create_subscription(String, "robotrola/safety_cmd", self._on_safety_cmd, 10)

        self.pub_mode = self.create_publisher(String, "robotrola/safety_mode", 10)
        self.pub_result = self.create_publisher(String, "robotrola/command_result", 10)
        self.create_timer(0.1, self._tick)

        self.get_logger().info(
            f"safety supervisor ready mode={self.sup.mode.value} limits={limits}"
        )

    def _inputs(self) -> SafetyInputs:
        return SafetyInputs(estop_ok=self.estop_ok, deadman_ok=self.deadman_ok)

    def _on_estop(self, msg: Bool) -> None:
        self.estop_ok = bool(msg.data)
        self.sup.evaluate_inputs(self._inputs())

    def _on_deadman(self, msg: Bool) -> None:
        self.deadman_ok = bool(msg.data)
        self.sup.evaluate_inputs(self._inputs())

    def _on_safety_cmd(self, msg: String) -> None:
        cmd = msg.data.strip().upper()
        inputs = self._inputs()
        if cmd == "ARM":
            ok = self.sup.arm(inputs)
            self.get_logger().info(f"ARM -> {ok} mode={self.sup.mode.value}")
        elif cmd == "ACTIVATE":
            ok = self.sup.activate(inputs)
            self.get_logger().info(f"ACTIVATE -> {ok} mode={self.sup.mode.value}")
        elif cmd == "FAULT":
            self.sup.evaluate_inputs(SafetyInputs(estop_ok=False, deadman_ok=True))
        else:
            self.get_logger().warn(f"unknown safety_cmd={cmd}")

    def _on_cmd(self, msg: String) -> None:
        # format: name,pos,vel,effort
        parts = [p.strip() for p in msg.data.split(",")]
        if len(parts) != 4:
            self.pub_result.publish(String(data="reject:bad_format"))
            return
        name, pos, vel, eff = parts[0], float(parts[1]), float(parts[2]), float(parts[3])
        ok, reason = self.sup.approve_joint_command(
            JointCommand(name, pos, vel, eff)
        )
        self.pub_result.publish(String(data=f"{'ok' if ok else 'reject'}:{reason}"))

    def _tick(self) -> None:
        self.sup.evaluate_inputs(self._inputs())
        self.pub_mode.publish(String(data=self.sup.mode.value))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SafetySupervisorNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
