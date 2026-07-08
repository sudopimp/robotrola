PYTHON ?= python3

.PHONY: test validate bom cad-catalog zip

test:
	$(PYTHON) -m pytest -q

validate:
	$(PYTHON) scripts/validate_repo.py

bom:
	$(PYTHON) scripts/bom_summary.py

cad-catalog:
	$(PYTHON) tools/render_cad_catalog.py

zip:
	cd .. && zip -r robotrola_core_sota2026_repo.zip robotrola_core_sota2026 -x "*.git*" "*/__pycache__/*"
