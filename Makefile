PYTHON ?= python3

.PHONY: test validate bom bom-cost safety-path demo description cad-catalog \
	diligence zip sim-smoke firmware firmware-build phase0

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

sim-smoke:
	$(PYTHON) scripts/sim_smoke.py

firmware:
	$(PYTHON) scripts/check_firmware.py

firmware-build:
	$(PYTHON) scripts/check_firmware.py --build

# Phase-0+ software bar (no hardware, no ROS install required)
phase0: test validate sim-smoke firmware demo

diligence: test validate bom-cost safety-path demo sim-smoke firmware

description:
	$(PYTHON) scripts/generate_robot_description.py

cad-catalog:
	$(PYTHON) tools/render_cad_catalog.py

zip:
	cd .. && zip -r robotrola_core_sota2026_repo.zip robotrola_core_sota2026 -x "*.git*" "*/__pycache__/*"
