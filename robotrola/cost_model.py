"""Stage cost bands from hardware/BOM.csv unit_est_usd ranges."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from robotrola.bom import BomItem, load_bom

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOM = ROOT / "hardware" / "BOM.csv"

# Which BOM categories participate in each research build stage
STAGE_CATEGORIES: dict[str, set[str]] = {
    "bench": {
        "compute",  # budget path can still be listed; qty scaling below
        "mcu",
        "actuation",
        "power",
        "safety",
        "materials",
    },
    "upper_body": {
        "compute",
        "mcu",
        "actuation",
        "hands",
        "power",
        "safety",
        "vision",
        "audio",
        "sensing",
        "materials",
    },
    "full_body": {
        "compute",
        "mcu",
        "actuation",
        "hands",
        "power",
        "safety",
        "vision",
        "audio",
        "sensing",
        "docking",
        "service",
        "materials",
    },
}

# Multipliers for partial builds (bench does not buy full actuator set / Thor)
STAGE_QTY_SCALE: dict[str, dict[str, float]] = {
    "bench": {
        "compute": 0.15,  # Orin-class budget share of Thor line
        "actuation": 0.15,  # ~1–2 actuators of a 12-unit line
        "hands": 0.0,
        "docking": 0.0,
        "service": 0.0,
        "sensing": 0.25,
        "vision": 0.5,
        "audio": 0.5,
    },
    "upper_body": {
        "actuation": 0.7,
        "hands": 0.5,
        "docking": 0.0,
        "service": 0.0,
        "sensing": 0.5,
    },
    "full_body": {},
}

_RANGE_RE = re.compile(
    r"(?P<low>\d+(?:\.\d+)?)\s*-\s*(?P<high>\d+(?:\.\d+)?)"
)
_SINGLE_RE = re.compile(r"(?P<val>\d+(?:\.\d+)?)")


def parse_usd_range(text: str) -> tuple[float | None, float | None]:
    """Parse '80-800', '2999-3499', 'TBD', empty → (low, high) or (None, None)."""
    if not text:
        return None, None
    cleaned = text.strip().lower().replace(",", "").replace("$", "")
    if cleaned in {"tbd", "n/a", "na", "?", "-"}:
        return None, None
    m = _RANGE_RE.search(cleaned)
    if m:
        return float(m.group("low")), float(m.group("high"))
    m = _SINGLE_RE.search(cleaned)
    if m:
        v = float(m.group("val"))
        return v, v
    return None, None


def _qty(item: BomItem) -> float:
    try:
        return float(str(item.qty).strip() or "1")
    except ValueError:
        return 1.0


@dataclass(frozen=True)
class StageCost:
    stage: str
    low_usd: float
    high_usd: float
    line_count: int
    skipped_tbd: int
    categories: list[str]


def stage_cost(
    items: list[BomItem],
    stage: str,
) -> StageCost:
    if stage not in STAGE_CATEGORIES:
        raise ValueError(f"unknown stage: {stage}")
    cats = STAGE_CATEGORIES[stage]
    scales = STAGE_QTY_SCALE.get(stage, {})
    low = high = 0.0
    lines = 0
    skipped = 0
    for it in items:
        if it.category not in cats:
            continue
        lo, hi = parse_usd_range(it.unit_est_usd)
        if lo is None or hi is None:
            skipped += 1
            continue
        scale = scales.get(it.category, 1.0)
        if scale <= 0:
            continue
        q = _qty(it) * scale
        low += lo * q
        high += hi * q
        lines += 1
    return StageCost(
        stage=stage,
        low_usd=round(low, 2),
        high_usd=round(high, 2),
        line_count=lines,
        skipped_tbd=skipped,
        categories=sorted(cats),
    )


def full_cost_model(path: str | Path = DEFAULT_BOM) -> dict:
    items = load_bom(path)
    stages = {s: stage_cost(items, s) for s in ("bench", "upper_body", "full_body")}
    return {
        "currency": "USD",
        "disclaimer": (
            "Research BOM band estimates from unit_est_usd text ranges; "
            "not a quote, not including labor, tooling, certification, or facilities."
        ),
        "stages": {
            name: {
                "low_usd": sc.low_usd,
                "high_usd": sc.high_usd,
                "line_count": sc.line_count,
                "skipped_tbd": sc.skipped_tbd,
                "categories": sc.categories,
            }
            for name, sc in stages.items()
        },
        "risk_counts": _risk(items),
        "item_count": len(items),
    }


def _risk(items: list[BomItem]) -> dict[str, int]:
    out: dict[str, int] = {}
    for it in items:
        out[it.risk] = out.get(it.risk, 0) + 1
    return out
