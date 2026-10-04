# ELCROW 10.1 development frame — first-fit prototype V2

## Status and scope

V2 is a corrected, mechanically coherent **first-fit prototype**, not a certified enclosure or stand. It preserves the supplied STEP, the V1 generator, V1 CAD document, V1 exports, V1 notes, and V1 screenshot. `generate_elcrow_10_1_dev_frame_v2.py` refuses to run if its V2 CAD path, export directory, or open V2 document already exists.

The design uses only the supplied STEP geometry. It does not invent PCB mounting holes. PLA or PETG may be used for rigid parts; PETG is preferred for retainers. TPU is not required and is not in the structural load path.

## Reference and coordinates

* Source coordinates: X horizontal, Z vertical, front +Y.
* The copied reference is source object `_10_1CUN_ASM`, containing 54 solids: LCD, touch, PCB, flexes, ports, switches, headers, and other modeled components. The complete shape, not the V1 three-object subset, is copied into the V2 assembly and used for every collision check.
* PCB envelope is X=±123.5, Z=±73.5, with its nominal rear face at Y=-6.5.
* Rigid panel envelope is X=±117.5, Z=±71.5. The modeled front aperture remains 225 × 129 mm.
* Top flex relief is X=-30..60 from Z=68 upward. A bottom-center relief X=±11 through Z=-64 and below clears the modeled lower flex/antenna object.

## Corrected retention and capture

The rear frame cavity is X=±125 and Z=±75, giving the PCB 1.50 mm nominal lateral travel per side. The panel overlaps the aperture by 5.0 mm per side in X and 7.0 mm per side in Z when centered. At the worst permitted PCB shift, the remaining panel/aperture overlap is still **3.50 mm in X and 5.50 mm in Z**, so the panel cannot shift out through the front aperture.

Four removable rear stops are located at Z=-30 and +45. Their hooks project to X=±122.0, producing **1.50 mm positive overlap** onto the modeled bare PCB edge strip. Their nearest rear face is Y=-6.8, leaving a **0.30 mm non-compressive nominal gap** behind the PCB. V2 checks each complete retainer against all 54 reference solids; every common volume is 0.000000 mm³. The side rails provide lateral location; the hooks provide rear travel stops; the front lip provides front capture.

## Modeled fasteners

No heat-set insert and no self-tapping assumption remains.

### Retainers

* Hardware: four M3 × 12 ISO 4762 socket-head cap screws and four M3 DIN 934 full nuts.
* Axis: X. Screw heads remain outside the side retainers; a 2.5 mm hex key approaches from each outer side.
* Modeled clearance bore: 3.40 mm through each retainer and integral frame boss.
* Nut: 5.50 mm across flats, 2.40 mm thick; each nut loads through a rear-open boss slot before the display is installed.
* Engagement: the screw crosses the 4 mm retainer and reaches through the complete 2.40 mm nut thickness. Its modeled tip ends at |X|=128, outside the PCB edge at |X|=123.5.
* Minimum boss ligament around the nut slot in Z is 4.05 mm.

### Split-frame seam

* Hardware: two M3 × 8 ISO 4762 socket-head cap screws and two M3 DIN 934 full nuts.
* Axis: -Y from the front. A 2.5 mm hex key approaches from the front below the aperture.
* The 3.40 mm passages and 5.90 mm nut-loading mouths are modeled in the lower front rail. The seam plate includes 5.90 mm head recesses.
* Each screw engages the full 2.40 mm nut and ends near Y=0.05 at X=±22, away from the modeled center flex.
* The seam is in front of the frame at Y=5.05..8.05. It does not pass through a cradle base or floor. Minimum lower nut-pocket ligament is 1.31 mm.
* The former bottom tongue is omitted because the complete STEP shows a bottom-center flex/antenna where V1 placed it. The screw-fastened front plate supplies seam registration and locking without crossing that component.

## Corrected 20° cradle and load path

The assembly transform and all cradle contact solids use the same +20° rotation about X. A 164 mm source-vertical rise moves 56.09 mm toward the rear (negative assembly Y), so the support slope and display lean agree.

Each stand is a valid single solid with:

1. a hard lower seat built from the transformed bezel lower plane, with 261.00 mm² nominal seat area per side;
2. a hard rear support built from the transformed rear-rail plane, with 426.00 mm² nominal bezel-contact area per side (the remainder of the wider plate is structural);
3. a front stop 0.40 mm ahead of the front bezel face; and
4. an outer web that connects the seat, back, and stop to the base without touching glass, PCB, or modeled components.

CAD reports 0.000000 mm distance from each cradle to the bezel at the intended hard contacts and 0.000000 mm³ penetration. The load path is bezel lower rail → hard seat/rear support → stand base → floor. No foam, TPU, adhesive, or friction-only support is required.

A 231.40 mm keyed crossbar drops into top-open pockets in both bases. The key shoulders positively limit stand spreading while remaining below the display. It is a separate printable part because the complete stand width would exceed the practical 250 mm part limit.

## BOM

| Item | Qty | Specification and use |
|---|---:|---|
| M3 × 12 socket-head cap screw | 4 | ISO 4762; retainer axes X; outer-side tool access |
| M3 full hex nut | 4 | DIN 934, 5.5 mm AF × 2.4 mm; rear-loaded retainer boss slots |
| M3 × 8 socket-head cap screw | 2 | ISO 4762; seam axes -Y; front tool access |
| M3 full hex nut | 2 | DIN 934, 5.5 mm AF × 2.4 mm; front-loaded seam pockets |
| 2.5 mm hex key | 1 | Retainer and seam screw access |

## Print and rear assembly sequence

1. Print all ten STLs in their exported orientations. Every export is translated to base Z=0. Use PLA or PETG, 0.4 mm nozzle, 0.2 mm layers, four perimeters, and 20–30% infill as initial prototype settings, not qualification values.
2. Trial-fit the keyed crossbar into both cradle base pockets. Do not force a warped part.
3. Load the four retainer nuts into the rear-open side-boss slots. Load the two seam nuts into the front-open lower-rail pockets.
4. Join the empty left and right bezel halves and fasten the front seam plate with the two M3 × 8 screws. The screw heads and tool remain on the front below the aperture.
5. Place the joined bezel face-down on a clean non-scratching surface. With power disconnected, lower the complete display into the bezel **from the rear**, routing the upper and lower flex features through their modeled reliefs. The display is not inserted through the smaller front opening.
6. Fit each rear retainer from the rear/outer side and install its M3 × 12 screw from the outer side. Tighten only to retain the screw and nut; the 0.30 mm gap is deliberate and the PCB must not be clamped.
7. Drop the crossbar keys into the two cradle pockets to fix stand spacing. Lower the framed display into the hard lower seats, against the hard rear supports, and behind the front stops.
8. Confirm the full bezel rail—not glass or PCB—bears on both lower seats and rear supports before applying power.

## Generated CAD validation

`ELCROW_10_1_Dev_Frame_FirstFit_V2.FCStd` stores the following fatal generated checks in `Measured_Checks.Results`:

* every bezel half, seam lock, retainer, cradle, crossbar, and modeled hardware envelope has 0.000000 mm³ common volume with the complete reference in its applicable coordinate system;
* both cradle-to-bezel contact distances are 0.000000 mm with 0.000000 mm³ penetration;
* positive aperture capture, retainer overlap, rear gap, contact areas, lean direction, screw engagement, and minimum ligaments are reported;
* each of the ten printable parts is one valid solid and every bounding-box axis is ≤250 mm;
* each exported orientation has base Z=0.000000 mm.

Largest printable dimensions are the crossbar at 231.40 × 14.00 × 7.80 mm and each cradle at 34.00 × 125.00 × 142.70 mm.

## Remaining physical tests — UNCONFIRMED

Before relying on the prototype, physically verify:

* actual print shrinkage and fit at the 1.50 mm PCB clearances, 0.30 mm rear gap, nut slots, and crossbar keys;
* active-pixel clearance behind the inferred 225 × 129 mm aperture;
* all cable plug insertion/removal paths, bend radii, and strain relief with the frame and cradle assembled;
* that no unmodeled adhesive, coating, solder protrusion, or cable occupies a contact/retainer region;
* screw torque, nut retention, layer-direction strength, long-term creep, stand tip resistance, and response to tapping or cable loads;
* thermal suitability of the chosen PLA/PETG and surface protection for the panel.

Stop and revise rather than forcing assembly if any retainer touches a component, the rear gap closes, a flex is pinched, or a load reaches glass/PCB.

## Revision artifacts

* `generate_elcrow_10_1_dev_frame_v2.py`
* `ELCROW_10_1_Dev_Frame_FirstFit_V2.FCStd`
* `ELCROW_10_1_Dev_Frame_FirstFit_V2_assembled.png`
* `DESIGN_NOTES_ELCROW_10_1_DEV_FRAME_FIRST_FIT_V2.md`
* `exports/ELCROW_10_1_Dev_Frame_FirstFit_V2/` containing ten STL files
