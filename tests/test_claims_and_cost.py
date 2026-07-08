from pathlib import Path
import json
import re

from robotrola.cost_model import full_cost_model, parse_usd_range

ROOT = Path(__file__).resolve().parents[1]


def test_claims_matrix_sections():
    text = (ROOT / "docs/CLAIMS_MATRIX.md").read_text(encoding="utf-8")
    for h in ("## Proven today", "## Lab next", "## Not claimed"):
        assert h in text
    assert "42" in text
    assert "certified" in text.lower() or "Not claimed" in text


def test_investor_brief_exists():
    text = (ROOT / "docs/INVESTOR_TECH_BRIEF.md").read_text(encoding="utf-8")
    assert "42" in text
    assert "not" in text.lower() and "certified" in text.lower()
    assert "demo_investor" in text or "demo_investor.py" in text
    assert "BOM" in text or "bom" in text


def test_spec_has_verify_hints():
    text = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    assert "verifyHint" in text
    assert "C1" in text and "C10" in text


def test_parse_usd_range():
    assert parse_usd_range("80-800") == (80.0, 800.0)
    assert parse_usd_range("TBD") == (None, None)
    assert parse_usd_range("100") == (100.0, 100.0)


def test_stage_cost_model_bands():
    model = full_cost_model(ROOT / "hardware/BOM.csv")
    assert model["currency"] == "USD"
    for name in ("bench", "upper_body", "full_body"):
        s = model["stages"][name]
        assert s["low_usd"] > 0
        assert s["high_usd"] >= s["low_usd"]
        assert s["line_count"] >= 3
    # full body should be >= upper body high band typically
    assert model["stages"]["full_body"]["high_usd"] >= model["stages"]["bench"]["high_usd"]


def test_readme_points_to_claims_and_demo():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "CLAIMS_MATRIX" in readme
    assert "demo_investor" in readme
