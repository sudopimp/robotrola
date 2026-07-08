
# CAD assets

## Directories

- `scad/`: parametric OpenSCAD source.
- `stl/`: generated STL reference parts, units in millimeters.
- `glb/`: generated GLB preview assets when export succeeds.
- `urdf/`: robot description references.
- `drawings/`: SVG blueprint-style diagrams.

## Important

The STLs are reference printable geometry for packaging and research. They are not final structural CAD. Use them to validate scale, ergonomics, sensor placement, cable channels, and manufacturing conversations.

Regenerate with:

```bash
python tools/generate_reference_stl.py
```
