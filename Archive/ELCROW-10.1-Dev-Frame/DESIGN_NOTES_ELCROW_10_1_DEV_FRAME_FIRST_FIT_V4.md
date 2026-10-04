# V4 corrected-reference frame — published fit-test prototype

## Status

At the explicit user request, non-watertight/nonmanifold meshes are warnings, not export blockers. All remaining geometric checks passed during generation in the existing FreeCAD GUI session. The reference and existing user documents were preserved.

Published native CAD: `ELCROW_10_1_Dev_Frame_FirstFit_V4_PUBLISHED_20260920_0240.FCStd`.
Screenshot: `ELCROW_10_1_Dev_Frame_FirstFit_V4_PUBLISHED_20260920_0240_assembled.png`.
Eleven STLs and complete `validation.txt`: `exports/ELCROW_10_1_Dev_Frame_FirstFit_V4_PUBLISHED_20260920_0240/`.
Generator: `generate_elcrow_10_1_dev_frame_v4.py`.

Both cradle meshes report `isSolid=False`; all other exported meshes report `isSolid=True`. All eleven CAD parts are valid single BRep solids. Independent STL reload verified nonempty facets, finite bounds, dimensions no greater than 250 mm, and base Z=0. CAD validity does not establish slicer reliability; slicing and physical fit remain unverified.

## Reference and proposed changes

The live `_10_1CUN_ASM` in `ELCROW_P4_10_1_STEP_REFERENCE_20251230` was copied read-only: 52 solids, 66473.589978 mm³. All remaining real components, including LCD_10_1CUN, TP_10_1CUN, PCB and antenna, remain in the collision reference. The original STEP was not reimported.

Only the new design adds explicitly labeled bounding proxies, not exact vendor geometry:

- LCD: X ±117.5, Z ±71.5, Y -4.3..0 mm.
- Glass: X ±117.5, Z ±71.5, Y 0.5..2 mm.

The obsolete top cable notch is removed. The bottom opening narrows to X ±7.5 mm for the retained lower-center antenna; it is not a large flex-cable assumption. Rear side-rail and support openings provide modeled plug/tool corridors. The left upper retainer moves to Z=52 mm to avoid the left connector corridor. No guessed mounting holes are used.

Two front seam bridges register the upper and lower split. Rear-loaded full hex pockets replace the clipped square mouths. Their nuts seat against a 3 mm front shoulder, so screws clamp the bridges to the frame rather than clamping only the bridges to their own nuts. Minimum measured seam-edge ligament is 2.180 mm.

## Checks reached

All listed zero-penetration checks use a 0.001 mm³ numerical tolerance, not an overlap waiver:

- All 11 assembled printable parts versus the complete current reference plus both envelopes; all 55 printable pairs.
- Eight screw/nut assemblies versus every printable, the reference and each other. Bolt/nut envelopes have an idealized matching bore; thread geometry is not simulated.
- All eight head-bearing areas: 14.679 mm². All eight nut-bearing areas: 17.118 mm². Zero seating distance; full 2.400 mm axial engagement.
- Eight tool corridors and eight continuous rear nut-loading sweeps: zero obstruction.
- Continuous framed-display removal/insertion sweeps, including hardware: 25 mm up along the tilted display, then 15 mm forward; zero stand obstruction.
- Separate bottom and rear support witnesses on both stands: respectively 30.150 and 30.000 mm², with no penetration. Support and display share the same 20° transform.
- Four modeled side-access corridors: zero printed obstruction. Actual plug shells and bend radii remain unverified.
- All four retainers: measured 1.500 mm overlap at worst permitted lateral shift. Aperture capture remains positive.
- Bezel halves, two seam bridges and four retainers: valid single solids and watertight, within-limit, base-Z-zero candidate meshes.
- Completed export: both cradles are valid single BRep solids, approximately 40 × 125 × 141.948 mm, with non-watertight meshes accepted as requested. All eleven exports passed bounds and base-Z checks; the largest part is the 231.40 mm crossbar.

An earlier support-witness failure was traced to the placement helper discarding an existing probe translation. Composition of placements corrected that test boundary; subsequent support witnesses passed. No acceptance assertion was relaxed.

## Proposed BOM and rear assembly — NOT physically validated

Eight M3×12 ISO 4762 socket-head screws, eight DIN 934 M3 nuts (5.5 mm AF × 2.4 mm), and a 2.5 mm hex key. Four screws retain the rear hooks; four fasten the two front seam bridges. PLA/PETG structural parts; PETG preferred for retainers. No structural TPU.

If publication completes after the explicit mesh-warning waiver: load all nuts from the rear into the empty bezel; join both halves with the two front bridges; place the frame face-down on a protected surface; insert the display from the open rear without pinching the antenna; fit the four rear retainers and side screws without clamping the PCB. Fit the keyed crossbar into both stands, then lower the framed display onto its actual bottom and rear contacts. Seam screws are front-access; retainer screws are side-access. This sequence still requires physical trial fitting and does not establish slicer success.

## Required next decision and remaining risks

The mesh topology is intentionally not repaired or redesigned. Publication is currently blocked by the FreeCADCmd repeated-execution/open-document behavior described above, not by the waived mesh condition. Use a controlled FreeCAD GUI/MCP session that executes the generator once, while preserving user documents, before retrying. Do not silently repair mesh holes.

Deferred: completed STL round-trip inspection, screenshot and visual inspection, independent acceptance, completed final-solid/export gates under the revised mesh-warning policy, quantitative keyed-crossbar spreading limits, and any further assembly-path checks. Strength, torque, nut-fit tolerances, creep, thermal behavior, stand tipping, active-pixel clearance, antenna/RF behavior, actual connector use and real-panel dimensional accuracy remain physical tests, not established by collision checks.

Original STEP, updated reference, V1/V2/V3 files and existing open documents were not closed, reloaded or overwritten.
