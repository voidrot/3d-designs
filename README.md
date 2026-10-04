# 3d-designs

Parametric FreeCAD designs for 3D-printed parts. Each project lives in its own folder, and a Python generator script builds its geometry.

## Projects

| Project | Description | Status |
|---|---|---|
| [10.1-ESP-Touchscreen-Frame](10.1-ESP-Touchscreen-Frame/) | Desk case with a magnetic 30° cradle for the Elecrow CrowPanel Advanced 10.1" ESP32-P4 display | Prototype v2, not yet printed |

`Archive/` holds retired iterations kept for reference.

## Project layout

```
<Project>/
├── PLAN.md          decisions, reference dimensions, openings, print notes
├── *_proto.py       parametric generator (source of truth for geometry)
├── *.FCStd          FreeCAD document produced by the generator
├── *.stp            vendor reference model
├── exports/         print-ready STLs
└── *.png            renders
```

## Cloning

Binary files (`*.FCStd`, `*.stl`, `*.stp`/`*.step`, `*.3mf`, `*.png`) are stored with [Git LFS](https://git-lfs.com). Install it before cloning, or run `git lfs install && git lfs pull` afterward.

## Rebuilding a project

Requires FreeCAD 1.1 or later.

**Headless** (regenerates the checks and STLs):

```sh
cd 10.1-ESP-Touchscreen-Frame
freecadcmd -c "exec(open('crowpanel_case_proto.py').read())"
```

**In the FreeCAD GUI** (also updates the 3D model): run this in the Python console, then save the document.

```python
exec(open("/path/to/10.1-ESP-Touchscreen-Frame/crowpanel_case_proto.py").read())
```

Each run prints validity and collision checks, then writes STLs to `exports/`. Every STL is already in its print orientation, at z = 0.

## Printing

- Sized for a 256 × 256 mm bed (Bambu Lab).
- Every part prints without supports. Orientation and material notes are in each project's `PLAN.md`.
- Multi-color text ships as a separate STL aligned with its host part. In Bambu Studio, import both together as one object with multiple parts, then assign a filament to the text (requires an AMS).
