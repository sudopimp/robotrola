#!/usr/bin/env python3
"""Export a minimal MuJoCo MJCF from the R-01 joint map (research scaffold).

Does not require MuJoCo installed to *write* the file. Optional load smoke
runs only when ``mujoco`` is importable.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _joint_map():
    import importlib.util

    path = ROOT / "scripts" / "generate_robot_description.py"
    spec = importlib.util.spec_from_file_location("robotrola_gen_desc", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generate_robot_description")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.joint_map()


def build_mjcf() -> ET.Element:
    """Build a simplified chain MJCF: free base + revolute joints as hinges."""
    mujoco = ET.Element("mujoco", model="robotrola_r01_research")
    ET.SubElement(mujoco, "compiler", angle="radian", autolimits="true")
    ET.SubElement(mujoco, "option", timestep="0.002", gravity="0 0 -9.81")
    default = ET.SubElement(mujoco, "default")
    ET.SubElement(
        default,
        "joint",
        damping="0.5",
        armature="0.01",
        limited="true",
    )
    ET.SubElement(default, "geom", type="capsule", size="0.03", rgba="0.8 0.7 0.5 1")

    world = ET.SubElement(mujoco, "worldbody")
    # Fixed pedestal
    ET.SubElement(
        world,
        "geom",
        name="floor",
        type="plane",
        size="2 2 0.1",
        rgba="0.2 0.2 0.2 1",
    )
    pelvis = ET.SubElement(
        world,
        "body",
        name="pelvis_link",
        pos="0 0 0.95",
    )
    ET.SubElement(pelvis, "geom", name="pelvis_geom", type="box", size="0.12 0.1 0.06")
    ET.SubElement(pelvis, "inertial", mass="8", pos="0 0 0", diaginertia="0.08 0.06 0.05")

    # Track bodies we've created
    bodies: dict[str, ET.Element] = {"pelvis_link": pelvis, "world": world}

    def ensure_body(name: str, parent_name: str, xyz: str) -> ET.Element:
        if name in bodies:
            return bodies[name]
        parent = bodies.get(parent_name)
        if parent is None:
            parent = ensure_body(parent_name, "pelvis_link", "0 0 0")
        body = ET.SubElement(parent, "body", name=name, pos=xyz)
        ET.SubElement(
            body,
            "geom",
            name=f"{name}_geom",
            type="capsule",
            fromto="0 0 0 0 0 -0.08",
            size="0.025",
        )
        ET.SubElement(
            body,
            "inertial",
            mass="0.5",
            pos="0 0 -0.04",
            diaginertia="0.002 0.002 0.001",
        )
        bodies[name] = body
        return body

    joints = _joint_map()
    for jd in joints:
        if jd["jtype"] != "revolute":
            continue
        parent = jd["parent"]
        child = jd["child"]
        if parent not in bodies:
            ensure_body(parent, "pelvis_link", "0 0 0")
        body = ensure_body(child, parent, jd["xyz"])
        ax_s = " ".join(jd["axis"].split())
        # Avoid duplicate joint tags if ensure_body re-entered
        if body.find(f"joint[@name='{jd['name']}']") is None:
            ET.SubElement(
                body,
                "joint",
                name=jd["name"],
                type="hinge",
                axis=ax_s,
                range=f'{jd["lo"]} {jd["hi"]}',
            )

    actuator = ET.SubElement(mujoco, "actuator")
    for jd in joints[:12]:  # first 12 for light research control
        if jd["jtype"] != "revolute":
            continue
        ET.SubElement(
            actuator,
            "position",
            name=f'act_{jd["name"]}',
            joint=jd["name"],
            kp="20",
            ctrlrange=f'{jd["lo"]} {jd["hi"]}',
        )

    # comment note as element text via XML comment is awkward; use sensor size 0
    ET.SubElement(mujoco, "size", nconmax="200", njmax="500")
    return mujoco


def write_mjcf(path: Path) -> Path:
    root = build_mjcf()
    # Pretty-ish write
    try:
        ET.indent(root, space="  ")
    except AttributeError:
        pass
    tree = ET.ElementTree(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    # Prepend honesty comment
    text = path.read_text(encoding="utf-8")
    note = (
        "<!-- Robotrola R-01 research MJCF scaffold. "
        "Inertias/estimated; not measured hardware. Not a validated digital twin. -->\n"
    )
    if "xml" in text[:50]:
        parts = text.split("\n", 1)
        text = parts[0] + "\n" + note + (parts[1] if len(parts) > 1 else "")
    else:
        text = note + text
    path.write_text(text, encoding="utf-8")
    return path


def try_load(path: Path) -> dict:
    try:
        import mujoco  # type: ignore
    except ImportError:
        return {"loaded": False, "reason": "mujoco_not_installed"}
    model = mujoco.MjModel.from_xml_path(str(path))
    data = mujoco.MjData(model)
    # one step
    mujoco.mj_step(model, data)
    return {
        "loaded": True,
        "nq": int(model.nq),
        "nv": int(model.nv),
        "nu": int(model.nu),
        "nbody": int(model.nbody),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "simulation/mujoco/robotrola_r01_research.xml"),
    )
    ap.add_argument("--load", action="store_true", help="try mujoco load if installed")
    args = ap.parse_args(argv)
    out = write_mjcf(Path(args.output))
    print(f"wrote {out.relative_to(ROOT)}")
    if args.load:
        info = try_load(out)
        print(info)
        if info.get("loaded"):
            print("MUJOCO_LOAD_OK")
            return 0
        print("MUJOCO_LOAD_SKIP", info.get("reason"))
        return 0  # skip is not failure
    print("MUJOCO_EXPORT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
