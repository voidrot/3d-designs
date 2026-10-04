# ELCROW 10.1 development frame — first-fit prototype

## Scope and assumptions

This is a **first-fit, non-certified prototype**, generated from the supplied STEP reference. It deliberately uses perimeter retention, not electronics mounting holes.

* Coordinate basis from the source: X horizontal, Z vertical, display front +Y.
* Rigid touch-panel envelope used for fit: 235 × 143 mm, Y=0.5..2.0. PCB envelope: 247 × 147 × 1.7 mm, Y=-6.5..-4.8.
* The 222.72 × 125.28 mm apparent area is **UNCONFIRMED**. The bezel aperture is 225 × 129 mm, leaving 1.14 mm horizontal and 1.86 mm vertical margin to that inferred area; it must be checked powered before a final print.
* Material: PLA is acceptable for indoor prototype use; PETG is preferred for the four retainers and for warm environments. TPU/foam pads are optional and non-structural.
* Bambu X1-Carbon usable volume is treated as 256 mm cubed. A practical per-part maximum of 250 mm was checked. The 256 mm-wide bezel is split to avoid a marginal full-width print.

## Design decisions

* **Open back / landscape:** 225 × 129 mm front aperture; rear PCB, USB-C, side and lower connectors stay open. The top center has an 86 mm-wide relief (`X=-28..58`, `Z>=68`) for the known LCD and touch flex tails.
* **Bezel:** outer source envelope X=±128, Z=±82. Its rear rail clears the PCB envelope by 1.5 mm per side and 1.5 mm at top/bottom. Its front lip starts 0.05 mm in front of the modeled touch surface: it is a locating lip, not a clamp.
* **Split seam:** left half has a lower tongue; right half receives it. A removable lower seam lock bridges the split below the electronics with two M3×10 screws into two M3 heat-set inserts in the bottom rail. Top seam is intentionally a butt seam, because a tongue would cross the known LCD flex route.
* **Rear retention:** four separate rear-travel stops at left Z=-45/+48 and right Z=-45/+48. Their hook faces are nominally 0.30 mm behind the STEP PCB rear face; they must not be tightened to compress the assembly. They use M3×6 thread-forming screws into the bezel exterior side rail. Their local component clearance is **UNCONFIRMED** physically.
* **Cradle:** two 11.4 mm side wedges, 150 mm deep, hold the bezel exterior at a fixed 20° back from vertical. Hard cradle faces stop 0.6 mm short of the bezel; four optional 0.8 mm TPU/foam pads bridge that gap. The front stops and back wedge contact only bezel exterior, never glass or PCB.

## BOM

| Item | Qty | Notes |
|---|---:|---|
| M3 × 10 mm machine screw | 2 | lower seam lock |
| M3 heat-set insert | 2 | insert into lower bezel rail after test fit |
| M3 × 6 mm thread-forming plastic screw | 4 | rear retainer mounting only |
| 0.8–1 mm TPU/foam adhesive pad | 4 | optional, trim from exported pads |

Do **not** use screws through the display/PCB: no verified electronics mounting holes exist.

## Print and assembly

1. Print `Bezel_Left` and `Bezel_Right` in PLA/PETG, rear face down. Print the seam lock flat. Print each cradle with its base on the build plate. The exported STLs are placed in those orientations at Z=0.
2. Start with 0.4 mm nozzle, 0.2 mm layers, 4 perimeters, 20–30% infill; PETG retainers benefit from 4 perimeters. These are process suggestions, not qualification data.
3. Without electronics installed, test the lower tongue and seam lock. Heat-set inserts only after it seats flat.
4. With power disconnected, trial-fit display from the front. Confirm aperture does not cover active pixels, top flex exits freely, USB-C and every connector remain accessible, and the rear stops have a visible non-compressive gap. Stop if any condition fails.
5. Add optional pads to the cradle inner faces; set their thickness only after the bezel is physically fitted. Place the display in the cradle so the lower bezel rests behind the front stops and the outer side bezel bears on the padded back support.

## Measured CAD checks

Generated document property `Measured_Checks.Results` records:

* bezel common volume with PCB: 0.000000 mm³;
* bezel common volume with touch: 0.000000 mm³;
* bezel common volume with LCD plus flex: 0.000000 mm³;
* all individual printable bounding-box axes are no greater than 250 mm.

The test is a geometric STEP check only. It does **not** verify physical production tolerances, unmodeled adhesive/foam, true visible aperture, connector insertion clearance, flex bend radius, screw retention, print shrinkage, or strength.

## Simple static support estimate (not engineering certification)

Using the modeled display center at approximately Z=0 in source coordinates, the 20° rotation about the lower bezel puts its vertical load line at roughly Y=42 mm in a 0..150 mm base footprint. That leaves about 42 mm toward the front and 108 mm toward the rear of the base polygon. This is a geometry-only static margin estimate; it excludes cable forces, tapping, vibration, print anisotropy, friction and display mass uncertainty. Keep cables strain-relieved and do not treat it as a tip-over or structural certification.

## Reproduction

Run `generate_elcrow_10_1_dev_frame.py` with the reference document `ELCROW_P4_10_1_STEP_REFERENCE_20251230` open in FreeCAD. It creates only `ELCROW_10_1_Dev_Frame_FirstFit.FCStd` and `exports/ELCROW_10_1_Dev_Frame_FirstFit/`; it does not modify, save, close, or hide source objects.
