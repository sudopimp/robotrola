#!/usr/bin/env python3
"""ROS 2 joint command filter — delegates to robotrola.joint_filter.

Topics (JSON on std_msgs/String for zero-codegen dependency in pure Python CI;
when robotrola_msgs is built, the same payload fields match JointCommand.msg /
CommandResult.msg / SafetyState.msg):

  Sub: robotrola/joint_command_json   — JointCommand fields as JSON
  Sub: robotrola/safety_cmd          — ARM | ACTIVATE | FAULT | RESET
  Sub: robotrola/estop_ok, deadman_ok — Bool
  Pub: robotrola/command_result_json
  Pub: robotrola/safety_state_json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String

from robotrola.joint_filter import JointCommandFilter
from robotrola.msgs import JointCommandMsg
from robotrola.safety import SafetyInputs


class JointCommandFilterNode(Node):
    def __init__(self) -> None:
        super().__init__("robotrola_joint_command_filter")
        self.filt = JointCommandFilter()
        self.estop_ok = True
        self.deadman_ok = True

        self.create_subscription(String, "robotrola/joint_command_json", self._on_cmd, 10)
        self.create_subscription(String, "robotrola/safety_cmd", self._on_safety_cmd, 10)
        self.create_subscription(Bool, "robotrola/estop_ok", self._on_estop, 10)
        self.create_subscription(Bool, "robotrola/deadman_ok", self._on_deadman, 10)

        self.pub_result = self.create_publisher(String, "robotrola/command_result_json", 10)
        self.pub_state = self.create_publisher(String, "robotrola/safety_state_json", 10)
        self.create_timer(0.1, self._tick)
        self.get_logger().info(
            f"joint filter ready mode={self.filt.platform.supervisor.mode.value}"
        )

    def _inputs(self) -> SafetyInputs:
        return SafetyInputs(estop_ok=self.estop_ok, deadman_ok=self.deadman_ok)

    def _on_estop(self, msg: Bool) -> None:
        self.estop_ok = bool(msg.data)

    def _on_deadman(self, msg: Bool) -> None:
        self.deadman_ok = bool(msg.data)

    def _on_safety_cmd(self, msg: String) -> None:
        cmd = msg.data.strip().upper()
        inputs = self._inputs()
        if cmd == "ARM":
            self.filt.arm(inputs)
        elif cmd == "ACTIVATE":
            self.filt.activate(inputs)
        elif cmd == "FAULT":
            self.filt.fault_from_estop()
        elif cmd == "RESET":
            self.filt.reset_from_fault(inputs)
        else:
            self.get_logger().warn(f"unknown safety_cmd={cmd}")

    def _on_cmd(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
            jcmd = JointCommandMsg.from_dict(data)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            self.pub_result.publish(
                String(data=json.dumps({"ok": False, "reason": f"bad_json:{exc}", "mode": "", "joint": ""}))
            )
            return
        result = self.filt.filter_command(jcmd)
        self.pub_result.publish(String(data=json.dumps(result.to_dict())))

    def _tick(self) -> None:
        st = self.filt.safety_state(self._inputs())
        self.pub_state.publish(String(data=json.dumps(st.to_dict())))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = JointCommandFilterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
