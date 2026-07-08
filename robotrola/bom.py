
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import csv

@dataclass(frozen=True)
class BomItem:
    category: str
    item: str
    candidate: str
    qty: str
    unit_est_usd: str
    risk: str
    notes: str
    source_url: str


def load_bom(path: str | Path) -> list[BomItem]:
    with open(path, newline='', encoding='utf-8') as f:
        return [BomItem(**row) for row in csv.DictReader(f)]


def risk_counts(items: list[BomItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.risk] = counts.get(item.risk, 0) + 1
    return counts
