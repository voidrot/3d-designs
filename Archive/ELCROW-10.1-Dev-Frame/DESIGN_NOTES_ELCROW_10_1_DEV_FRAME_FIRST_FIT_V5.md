# V5 integrated-joint fit-test prototype

## Published files

- Native CAD, open in FreeCAD: `ELCROW_10_1_Dev_Frame_FirstFit_V5.FCStd`
- Visually inspected screenshot: `ELCROW_10_1_Dev_Frame_FirstFit_V5_assembled.png`
- Nine individually oriented STLs: `exports/ELCROW_10_1_Dev_Frame_FirstFit_V5/`
- Evidence in that directory: `validation.txt`, `post_validation.txt`, `artifact_verification.json`.
- Generator: `generate_elcrow_10_1_dev_frame_v5.py` (generation inputs are not live parametric drivers).

Both separate joining plates are removed. Two rear integrated tongue/receiver joints connect the bezel halves. The top/front edge is solid apart from the assembly seam; the lower camera opening is closed. The back remains open, with four retainers, modeled side-port corridors, and the removable 20-degree cradle.

Only `Part__Feature065 / AS-AG638A32M1-25` is excluded from fit. Its hidden copy is labeled in V5; the source remains unchanged. Fit uses 51 retained source solids plus explicitly reconstructed 235 × 143 mm LCD/glass envelopes. These envelopes are not vendor-exact geometry. Source and earlier artifacts were not overwritten or closed.

## Blocker diagnosis and correction

The original receiver collided with `Part__Feature040 / H1_HDR-SMD_40P-P2_54-V-F-R2-C20`: 6.929999 mm³, common bounds X −21..0, Y −10..−6.7, Z 71.4..71.5 mm. Moving joint centers from Z ±77.2 to ±78.4 clears it; measured final header/receiver distance is 0.460977 mm.

The tongue was deepened rearward to Y −14 to preserve a 1.975 mm head-bearing web. A lateral nut-entry channel admits preloaded receiver nuts. Four-millimetre-wide integral roots correct the original edge-only tongue attachment (three disconnected right-half solids). Final bezel halves are each one valid solid. No reference-shaped subtraction was used.

## Validation

All fatal generation checks passed in the existing GUI via `runpy`: effective-reference/envelope collisions; all 36 printable pairs; six fastener assemblies versus printables/reference/each other; six tool corridors and nut-loading sweeps; full 25 mm lateral joining sweep with both receiver nuts preloaded; stand insertion/removal sweeps; positive bottom/rear support contacts; connector corridors; and worst-shift retention.

Measured head bearing: 14.679 mm²; nut bearing: 17.118 mm²; seating distance zero; engagement 2.400 mm. Each joint retains its complete 1.975 mm head web, 0.800 mm nut shoulder and 2.480 mm nut-corner Z ligament; receiver socket side walls are 1.5 mm. Actual strength is untested. Retention at worst lateral shift is 1.500 mm. Stand support areas are 30.150 mm² bottom and 30.000 mm² rear per side.

All nine native parts are valid single solids. Independent binary-STL reload checked every vertex for finite coordinates, nonempty facets, dimensions ≤250 mm and base Z=0. Largest dimension: 231.40 mm. Native archive integrity passed. Both cradle meshes report `isSolid=False`; these are accepted warnings, not repaired or concealed.

## BOM and assembly

Print two bezel halves, four labeled retainers, two cradles and one crossbar in PLA/PETG; PETG preferred for retainers. Hardware: four M3×12 and two M3×8 ISO 4762 socket-head screws, six DIN 934 M3 nuts (5.5 mm AF × 2.4 mm), 2.5 mm hex key. No separate joining plates or glue required.

Load nuts into the empty bezel halves from the rear. Slide both right tongues into the left receivers simultaneously, then install the two rear-access M3×8 screws. Insert the display from the open rear on a protected face-down surface; fit retainers using M3×12 screws. Do not clamp the PCB or overtorque the thin nut shoulders. Key the cradles together with the crossbar and lower the framed display onto both seats.

## Physical limits

Not sliced or printed. Rear-down bezel exports have stepped undersides: assess supports, bridging and bed adhesion in the slicer. Watertightness warnings may affect slicing. Printed clearance, nut loading, layer strength, shoulder strength, torque, creep, heat, tipping stability, actual plug shells/bend radii, active-pixel clearance and RF performance remain unverified. This is a fit-test prototype, not a strength-qualified production design.
