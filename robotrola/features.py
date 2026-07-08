
from __future__ import annotations
from pathlib import Path
import yaml

class FeatureFlags:
    def __init__(self, path: str | Path):
        data = yaml.safe_load(Path(path).read_text())
        self.flags = data["feature_flags"]
        self.required_interlocks = data.get("required_interlocks", {})

    def enabled(self, name: str) -> bool:
        return bool(self.flags.get(name, False))

    def can_enable(self, name: str, interlocks: set[str]) -> tuple[bool, list[str]]:
        missing = [x for x in self.required_interlocks.get(name, []) if x not in interlocks]
        return (not missing, missing)

    def enable_runtime(self, name: str, interlocks: set[str]) -> bool:
        ok, missing = self.can_enable(name, interlocks)
        if not ok:
            raise RuntimeError(f"Cannot enable {name}; missing interlocks: {missing}")
        self.flags[name] = True
        return True
