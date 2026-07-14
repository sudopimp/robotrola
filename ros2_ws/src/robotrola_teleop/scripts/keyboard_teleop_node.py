#!/usr/bin/env python3
"""Guarded keyboard teleop stub — publishes joint commands through topics.

Does not bypass safety: publishes to ``robotrola/joint_command_json`` which the
control filter must approve. Default joint: neck_yaw small steps.
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
from std_msgs.msg import String


class KeyboardTeleopNode(Node):
    """Timer-based research teleop: cycles a small neck_yaw sinusoid.

    Real keyboard input is optional; this node is safe for headless CI and
    documents the teleop → filter contract.
    """

    def __init__(self) -> None:
        super().__init__("robotrola_keyboard_teleop")
        self.declare_parameter("joint", "neck_yaw")
        self.declare_parameter("amplitude", 0.15)
        self.declare_parameter("period_s", 4.0)
        self.declare_parameter("auto_arm", True)

        self.joint = self.get_parameter("joint").value
        self.amplitude = float(self.get_parameter("amplitude").value)
        self.period_s = float(self.get_parameter("period_s").value)
        self.t = 0.0

        self.pub_cmd = self.create_publisher(String, "robotrola/joint_command_json", 10)
        self.pub_safety = self.create_publisher(String, "robotrola/safety_cmd", 10)
        self.create_timer(0.1, self._tick)

        if bool(self.get_parameter("auto_arm").value):
            # Operator must still have estop/deadman healthy on filter side
            self.pub_safety.publish(String(data="ARM"))
            self.pub_safety.publish(String(data="ACTIVATE"))
            self.get_logger().info("published ARM+ACTIVATE (filter decides)")

        self.get_logger().info(
            f"teleop publishing joint={self.joint} amplitude={self.amplitude}"
        )

    def _tick(self) -> None:
        import math

        self.t += 0.1
        pos = self.amplitude * math.sin(2 * math.pi * self.t / max(self.period_s, 0.1))
        payload = {
            "name": self.joint,
            "position_rad": pos,
            "velocity_rad_s": 0.1,
            "effort_nm": 0.1,
        }
        self.pub_cmd.publish(String(data=json.dumps(payload)))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = KeyboardTeleopNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
