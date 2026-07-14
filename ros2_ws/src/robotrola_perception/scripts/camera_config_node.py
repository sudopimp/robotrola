#!/usr/bin/env python3
"""Perception config node — loads cameras.yaml and publishes status.

Not a full RGB-D pipeline. Proves the package is more than an empty shell and
exposes configured camera names for bringup checks.
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
import yaml


class CameraConfigNode(Node):
    def __init__(self) -> None:
        super().__init__("robotrola_camera_config")
        default_cfg = str(
            _REPO / "ros2_ws/src/robotrola_perception/config/cameras.yaml"
        )
        cfg_path = self.declare_parameter("config_path", default_cfg).value
        self.cfg = {}
        p = Path(cfg_path)
        if p.is_file():
            self.cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        self.pub = self.create_publisher(String, "robotrola/perception_status", 10)
        self.create_timer(1.0, self._tick)
        self.get_logger().info(f"perception config loaded keys={list(self.cfg.keys())}")

    def _tick(self) -> None:
        status = {
            "ok": bool(self.cfg),
            "cameras": list(self.cfg.keys()) if isinstance(self.cfg, dict) else [],
            "note": "config-only; no RGB-D driver attached",
        }
        self.pub.publish(String(data=json.dumps(status)))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CameraConfigNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
