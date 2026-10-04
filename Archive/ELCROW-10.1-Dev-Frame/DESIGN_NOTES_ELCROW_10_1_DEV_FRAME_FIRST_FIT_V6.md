# V6 protective rear-rest rails

## Published files

- Native CAD, open in FreeCAD: `ELCROW_10_1_Dev_Frame_FirstFit_V6.FCStd`
- Assembly screenshot: `ELCROW_10_1_Dev_Frame_FirstFit_V6_assembled.png`
- Explanatory back-down/desk-plane screenshot: `ELCROW_10_1_Dev_Frame_FirstFit_V6_rear_rest.png`
- Nine individually oriented STLs: `exports/ELCROW_10_1_Dev_Frame_FirstFit_V6/`
- Evidence: `validation.txt`, `post_validation.txt`, and `artifact_verification.json` in that directory
- Generator: `generate_elcrow_10_1_dev_frame_v6.py` (inputs are not live parametric drivers)

The V5 source, native document, exports, screenshots, and notes remain unchanged. The source reference also remains open and unchanged.

## Revision and rear-rest datum

V6 extends only the integral 3 mm-wide left and right structural side rails rearward. Their source-Y bearing plane moves from the original frame rear at Y = -8.0 mm to Y = -16.6 mm: an **8.6 mm rail-depth increase**. Total side depth from the new rear plane to the front lip is 21.65 mm. The open back, closed lower camera cutout, solid top, split halves, integrated joints, retainers, and front geometry remain as in V5.

The live effective fit reference was remeasured rather than assumed. Its rear extremum is Y = -14.600 mm after excluding exactly `Part__Feature065 / AS-AG638A32M1-25` and retaining the other 51 source solids plus the reconstructed 235 × 143 mm LCD/glass envelopes. The desk support plane at Y = -16.600 mm therefore gives **2.000 mm worst-case electronics clearance**.

The nearest nonbearing frame feature is an integrated joint housing at 2.300 mm above the plane. The nearest hardware is a joint screw head at 2.600 mm. Retainers clear by 6.600 mm; retainer hardware clears by 12.350 mm. Thus rear-down load is carried by the rails, not electronics, glass, retainers, or fasteners.

Four explicit 36.000 mm² bearing witnesses passed at both sides and Z = ±70 mm. Their support polygon spans X = -126.5..126.5 mm and Z = -70..70 mm and contains the nominal device centroid (0,0), providing widely separated coplanar contacts against rocking. Purposeful rail windows preserve all four modeled connector/switch paths through the full added depth.

## Cradle changes

The removable 20-degree cradle remains two side pieces plus the keyed crossbar. Its rear contacts were moved to the new rail plane, and local base notches clear the tilted deeper rails. A rear spine behind the validated plug corridors keeps each cradle a connected single solid without entering those corridors. The base footprint, bottom seats, front stops, keyed spacing, and 20-degree transform are unchanged. TPU remains optional and nonstructural.

## Validation

Fatal generation checks passed in the existing FreeCAD GUI:

- live 52-solid source signature and sole authorized camera exclusion;
- 51 retained solids plus LCD/glass envelopes versus every printable;
- independent flat-back checks for every retained solid/envelope, all frame hardware, retainers, and nonbearing bezel geometry;
- coplanar side faces, four bearing patches, and centroid-containing support polygon;
- all 36 assembled printable pairs with zero collision;
- all six hardware assemblies versus reference, printables, and each other;
- head/nut bearing, seating, 2.4 mm engagement, tool access, and nut-loading sweeps;
- 25 mm joint joining sweep with receiver nuts preloaded;
- stand contacts and two-stage insertion/removal sweeps;
- four full-depth USB/switch/header corridors;
- worst-shift panel and PCB retention;
- nine valid native single solids, each within the 250 mm build-axis limit;
- finite, nonempty, base-Z-zero STL exports.

Measured V5 invariants remain: 14.679 mm² screw-head bearing, 17.118 mm² nut bearing, 1.500 mm worst-shift retainer overlap, 30.150/30.000 mm² cradle bottom/rear support per side, 1.975 mm joint head web, 0.800 mm nut shoulder, and 2.480 mm nut-corner Z ligament.

Independent reload with FreeCAD 1.1.3 confirmed all nine STLs are finite, nonempty, base Z = 0, and no axis exceeds 250 mm. The largest dimension is 231.400 mm. Native archive integrity passed. Both cradle meshes report `isSolid=False` and `hasNonManifolds=False`; this is the accepted nonwatertight warning, not concealed or repaired.

## BOM, printing, and assembly

BOM quantity is unchanged: two bezel halves, four labeled retainers, two cradles, and one keyed crossbar; four M3×12 screws, two M3×8 screws, six DIN 934 M3 nuts, and a 2.5 mm hex key. PLA/PETG remain suitable prototype materials; PETG is preferred for retainers. No separate feet, joining plates, glue, or structural TPU are added.

Print orientation remains as exported: bezel halves rear-face-down, retainers outer-side-down, and cradle/crossbar as modeled at base Z = 0. The deeper bezel rails increase rear-face print depth; inspect supports, bridging, and bed adhesion in the slicer. Assembly order is unchanged from V5.

## Physical limits

Not sliced or printed. Desk flatness, physical rocking, impact strength, creep, rail strength, nut-shoulder strength, plug-shell fit, attached cable bend radius, and real connector insertion remain unverified. The 2 mm protection margin applies to the modeled device components and installed frame hardware, not attached plugs or cables; those may require additional clearance. Reconstructed LCD/glass envelopes remain approximations. This is a fit-test prototype, not a strength-qualified production enclosure.
