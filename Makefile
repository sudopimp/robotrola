PYTHON ?= python3

.PHONY: test validate bom bom-cost safety-path demo description cad-catalog diligence zip

test:
	$(PYTHON) -m pytest -q

validate:
	$(PYTHON) scripts/validate_repo.py

bom:
	$(PYTHON) scripts/bom_summary.py

bom-cost:
	$(PYTHON) scripts/bom_cost_model.py

safety-path:
	$(PYTHON) scripts/run_safety_path.py

demo:
	$(PYTHON) scripts/demo_investor.py

diligence: test validate bom-cost safety-path demo

description:
	$(PYTHON) scripts/generate_robot_description.py

cad-catalog:
	$(PYTHON) tools/render_cad_catalog.py

zip:
	cd .. && zip -r robotrola_core_sota2026_repo.zip robotrola_core_sota2026 -x "*.git*" "*/__pycache__/*"
