
from __future__ import annotations
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class PlanarArm:
    upper_m: float = 0.28
    forearm_m: float = 0.25

    def fk(self, shoulder_rad: float, elbow_rad: float) -> tuple[float, float]:
        x1 = self.upper_m * math.cos(shoulder_rad)
        z1 = self.upper_m * math.sin(shoulder_rad)
        x2 = x1 + self.forearm_m * math.cos(shoulder_rad + elbow_rad)
        z2 = z1 + self.forearm_m * math.sin(shoulder_rad + elbow_rad)
        return x2, z2
