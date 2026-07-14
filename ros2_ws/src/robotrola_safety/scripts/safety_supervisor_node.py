#!/usr/bin/env python3
"""Thin ROS 2 safety node — delegates to shipped robotrola.safety / joint_filter."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow importing the monorepo Python package when sourced from workspace
_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool

from robotrola.joint_filter import JointCommandFilter
from robotrola.msgs import JointCommandMsg
from robotrola.safety import SafetyInputs


class SafetySupervisorNode(Node):
    """Mirrors pure-Python SafetySupervisor for ROS bringup / teleop gates."""

    def __init__(self) -> None:
        super().__init__("robotrola_safety_supervisor")
        limits = self.declare_parameter(
            "limits_path",
            str(_REPO / "configs" / "safety_limits.yaml"),
        ).value
        # JointCommandFilter owns Platform + SafetySupervisor
        self.filt = JointCommandFilter()
        # Allow override limits path by reconstructing if needed
        if limits:
            from robotrola.safety import SafetySupervisor

            self.filt.platform.supervisor = SafetySupervisor(limits)
            self.filt.platform.boot()

        self.estop_ok = True
        self.deadman_ok = True

        self.create_subscription(Bool, "robotrola/estop_ok", self._on_estop, 10)
        self.create_subscription(Bool, "robotrola/deadman_ok", self._on_deadman, 10)
        # Legacy CSV wire format
        self.create_subscription(String, "robotrola/joint_command", self._on_cmd_csv, 10)
        # Typed JSON (matches robotrola_msgs/JointCommand fields)
        self.create_subscription(
            String, "robotrola/joint_command_json", self._on_cmd_json, 10
        )
        self.create_subscription(String, "robotrola/safety_cmd", self._on_safety_cmd, 10)

        self.pub_mode = self.create_publisher(String, "robotrola/safety_mode", 10)
        self.pub_result = self.create_publisher(String, "robotrola/command_result", 10)
        self.pub_result_json = self.create_publisher(
            String, "robotrola/command_result_json", 10
        )
        self.pub_state_json = self.create_publisher(
            String, "robotrola/safety_state_json", 10
        )
        self.create_timer(0.1, self._tick)

        self.get_logger().info(
            f"safety supervisor ready mode={self.filt.platform.supervisor.mode.value} limits={limits}"
        )

    def _inputs(self) -> SafetyInputs:
        return SafetyInputs(estop_ok=self.estop_ok, deadman_ok=self.deadman_ok)

    def _on_estop(self, msg: Bool) -> None:
        self.estop_ok = bool(msg.data)
        self.filt.platform.supervisor.evaluate_inputs(self._inputs())

    def _on_deadman(self, msg: Bool) -> None:
        self.deadman_ok = bool(msg.data)
        self.filt.platform.supervisor.evaluate_inputs(self._inputs())

    def _on_safety_cmd(self, msg: String) -> None:
        cmd = msg.data.strip().upper()
        inputs = self._inputs()
        if cmd == "ARM":
            ok = self.filt.arm(inputs)
            self.get_logger().info(f"ARM -> {ok} mode={self.filt.platform.supervisor.mode.value}")
        elif cmd == "ACTIVATE":
            ok = self.filt.activate(inputs)
            self.get_logger().info(
                f"ACTIVATE -> {ok} mode={self.filt.platform.supervisor.mode.value}"
            )
        elif cmd == "FAULT":
            self.filt.fault_from_estop()
        elif cmd == "RESET":
            self.filt.reset_from_fault(inputs)
        else:
            self.get_logger().warn(f"unknown safety_cmd={cmd}")

    def _publish_result(self, result) -> None:
        self.pub_result.publish(String(data=result.wire()))
        self.pub_result_json.publish(String(data=json.dumps(result.to_dict())))

    def _on_cmd_csv(self, msg: String) -> None:
        try:
            jcmd = JointCommandMsg.from_csv(msg.data)
        except ValueError:
            self.pub_result.publish(String(data="reject:bad_format"))
            return
        self._publish_result(self.filt.filter_command(jcmd))

    def _on_cmd_json(self, msg: String) -> None:
        try:
            jcmd = JointCommandMsg.from_dict(json.loads(msg.data))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            self.pub_result.publish(String(data=f"reject:bad_json:{exc}"))
            return
        self._publish_result(self.filt.filter_command(jcmd))

    def _tick(self) -> None:
        st = self.filt.safety_state(self._inputs())
        self.pub_mode.publish(String(data=st.mode))
        self.pub_state_json.publish(String(data=json.dumps(st.to_dict())))


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
