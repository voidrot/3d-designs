# CrowPanel Advanced 10.1" ESP32-P4 — Desk Case Plan

Board: Elecrow CrowPanel Advanced 10.1" ESP32-P4 (DHE04310D). Reference: `ESP32-P4-10_1-inch-20251230.stp`.

## Decisions

| Item | Choice |
|---|---|
| Use | Desk, resting in a separate cradle stand at 30° |
| Printer | 256 × 256 bed (one-piece bezel and shell) |
| Front | Thin lip over glass, ≤ 3 mm |
| Speakers | Moved to a chin below the screen, facing forward |
| Camera | No cutout yet; the top band is kept at full camera height, and the window is a parameter |
| Ports | Straight USB-C now; a recessed bay so right-angle plugs also fit |
| Power | USB-C powers and flashes for now. A 5 V supply can be added later on a pigtail plugged into UART3-IN through its back opening |
| Expansion | GPIO, UART1, and I2C openings |
| Closure | Board screwed to the bezel; back shell held on by magnets |
| Not included | Battery bay, wireless-module clearance |

## Datum (STEP coordinates, mm)

The axes are X = width, Z = height with **+Z down**, and Y = depth with the front at +Y. Seen from the front, +X is right.

| Feature | Value |
|---|---|
| PCB | X ±123.5, Z ±73.5, Y −4.9 to −6.5 (247 × 147 × 1.7) |
| Glass and LCD | X ±117.5, Z ±71.5, glass front Y +2.0 |
| Visible screen area | X −112 to 110.72, Z −65.64 to 59.64 |
| Black border (L / R / top / bottom) | 5.5 / 6.78 / 5.86 / 11.86 |
| Mounting holes | (±120.5, ±70.5), Ø3.2 hole, Ø6 pad; the pad reaches the glass edge |
| Deepest part in the STEP | Y −14.6 (UART1/I2C connectors) |
| Camera module (reserved space) | X ±6.25, Z −90.25 to −65, Y −8.1 to +2.9 |
| Speakers (2) | 30 × 20 face, 7 mm deep, 60 mm leads |

### Missing from or wrong in the STEP

- **Ribbon cables.** The LCD and touch cables are modeled flat out to Z 126 and Z 205. On the real board they fold behind it at bottom center, so the shell needs a pocket there.
- **Wireless-module socket.** The headers are misplaced at the origin. The real socket is at the top-left.
- **Speakers** aren't modeled at all. They're relocated to the chin anyway (see below).

## Envelope

| Dimension | Value | What drives it |
|---|---|---|
| Width | ~252 | PCB 247 + 0.4 clearance + 2.0 wall per side |
| Height | ~192 | Top band to Z −93 (camera reserve) + PCB + chin to Z +99 |
| Depth | ~22 | Lip front Y +3.5 to back outer Y −18.6 (2 mm clearance behind −14.6, 2 mm wall) |

The bezel lies flat on the bed at 252 × 192, which fits 256 × 256.

## Architecture

### 1. Front bezel

- One piece, printed face-down.
- The lip over the glass is ≤ 3 mm, so it stays inside the black border on every side.
- **Top band** (~19 mm) stays solid for now. A `camera_window` parameter cuts the window later at X 0, Z −90 to −65.
- **Chin** (~25 mm below the PCB edge) holds two forward-facing speakers.
  - The speaker pockets sit at about X ±90. They're short wire runs from SPK-L (X −107) and SPK-R (X +88).
  - Each pocket has a foam gasket ring between the speaker face and the grille.
  - Crush ribs hold the speaker laterally, and a rib on the back shell holds it in depth.
  - The grille is a fine slot or hole pattern in the chin's front face.
- **Label:** "MISSION" over "CONTROL", inlaid in the chin between the grilles.
  - Noto Sans Bold, 6.4 mm caps with a 1.6 mm line gap. The block is 44 × 14.4 mm, matching the grille height.
  - It's 0.6 mm deep (3 layers at 0.2 mm) and flush with the face.
  - The text is a separate body (`Case_Text`) filling a matching recess in the bezel.
  - The bezel prints face-down, so the text sits in the first 3 layers.
  - **Bambu Studio:** export the bezel and text as two STLs in the same frame and import both at once. Answer **yes** to loading them as one object with multiple parts, then assign a filament to the text part.
  - This needs an AMS, since both colors share the same layers.
- **Board bosses:** 4 D-shaped bosses with M3 heat-set inserts. The bosses widen toward the PCB edge so they clear the glass.
  - The board is screwed to the bezel from inside (4 × M3).
  - These screws are hidden under the back shell and stay put when the shell comes off.

### 2. Back shell, held by magnets

- It carries no load. It only closes the case, so magnets are enough.
- **Magnets:** about 8 pairs of 6 × 3 mm N52 discs, at the corners and mid-sides.
  - They're glued into pockets with 0.15 mm clearance.
  - Each pocket's floor is marked with the polarity.
- A **registration rim** runs between bezel and shell. It takes side loads, since magnets are weak in shear.
- A small **pry notch** at the bottom edge lets you pull the shell off.
- **Vents** run along the top and bottom back edges, out of sight. The board draws 8–10 W.
- There's a pocket for the folded ribbon cables at bottom center.
- **5 V provision:** none needed in the case. A 5 V supply cable ending in an XH2.54-4P plug fits UART3-IN through its back-plate opening.

### 3. Left-side port bay (both USB-Cs)

- The side wall steps inward over Z −20 to +20, so the outer surface sits flush with the USB-C receptacle mouths (X −124.5).
- **Straight plugs:** each USB-C cutout is a 12.5 × 7 mm rounded slot that passes the plug's molded body.
- **Right-angle plugs:** the bay brings the outer surface flush with the receptacle mouths. Common L-plugs bend along z, and the ports are 21 mm apart (a board constraint). So USB 2.0 takes a down-bent L cable for power, and UART0 takes a straight cable for flashing.
- The cradle stays clear of the left-side zone.

### 4. Cradle stand

- The case sits in a 6 mm pocket that matches its tilted bottom. Gravity pushes it down the 30° slope into a solid wedge dock (160 wide, 90 tall), which also takes the push from touch presses. There's no front lip.
- 4 magnet pairs (6 × 3 mm) hold the back plate to the dock face, so the case can't tip forward or slip sideways.
  - The shell-side magnets sit behind 0.6 mm of plastic. The dock-side magnets are glued into open pockets.
  - Lifting the case shears these magnets, which are weak in shear, so the shell's own 8 seam pairs keep it on the bezel.
- The base extends behind the case so it doesn't tip.
- A center tunnel (60 wide) runs through the dock for the GPIO cable and the vent outlet. A groove across the dock face keeps the bottom vent row breathing.
- **Prints base-down without supports:**
  - The tunnel has a 45° pitched roof with a 10 mm flat bridge.
  - The vent groove is a triangle with a flat floor and a vertical back wall, so it has no ceiling.
  - The dock face overhangs 30° from vertical.
  - Solid geometry; low infill keeps print time down.

## Openings (seen from the front)

| Edge | Feature | Location | Treatment |
|---|---|---|---|
| Back | Power switch (handle points back) | Z −32 to −23 | Toggle slot in the back plate |
| Left | UART0 USB-C (flashing) | Z −15 to −6 | Plug-body slot in the port bay |
| Left | PWR/CHG LEDs | Z ≈ 0 | Light slot |
| Left | USB 2.0 USB-C | Z 6 to 15 | Plug-body slot in the port bay |
| Back | UART3-IN (vertical XH, plug enters from the back) | Z 26 to 38 | Back plate opening |
| Right | BOOT, RESET | Z 38 to 60 | Pin-press holes in the back shell |
| Top | UART1, I2C HY2.0-4P | X 78 to 111 | Back opening with cable exit |
| Front | Mic (single bottom-port, U176) | X +120.4, Z −61.6 | Ø1 pinhole in the bezel, with a tube sealing to the PCB front |
| Bottom | GPIO 2×12 female header | X ±25.6, Z −71 to −61 | Back opening with cable exit |
| Bottom | microSD (flat socket on the back; card slides out downward) | X 96 to 112 | Finger window in the back plate below the slot; right speaker at X +75 keeps the withdrawal path clear |
| Front | Speakers | Chin, X ±90 | Grilles |

### Keep-outs

- **Wi-Fi antenna corner** (X 107 to 123.5, Z −53 to −40): no magnets, inserts, or screws nearby.
- **Folded ribbon cables** at bottom center.
- **Camera reserve** in the top band: keep it free of magnets and ribs so the window can be cut later.

## Confirmed inputs

- **Speakers:** 30 × 20 × 7 mm, no tabs. Each has a 60 mm lead to its connector (SPK-L at X −107, SPK-R at X +88, both at Z 63 to 71). The pockets must stay within about 45 mm of their connector to leave slack.
- **Magnets:** 6 × 3 mm discs; about 24 total (8 seam pairs + 4 cradle pairs).

## 5 V inlet — verified from the schematic

Sources: Elecrow's schematics `Eagle_SCH&PCB/1.0` and `1.2/...sch` (same power path in both); Vishay and MDD SS34 datasheets (DSS34 is an SS34-class part); JST XH datasheet.

- **Connector:** UART3-IN is J10, an XH2.54-4P.
  - Pin 1 = TXD3, pin 2 = RXD3, pin 3 = +5V_IN, pin 4 = GND.
  - A power pigtail uses only pins 3 and 4. Leave pins 1 and 2 unconnected.
- **Inputs are diode-ORed.** +5V_IN, USB-C J1 (VBUS1), and USB-C J16 (VBUS2) each reach VCC5V through their own DSS34 Schottky diode.
  - USB and the 5 V inlet can be connected at the same time safely. The higher supply carries the load.
  - The diodes block backfeed into the USB host.
- **The power switch still works.** VCC5V passes through P-FET Q5, and slide switch SW1 drives its gate, before reaching the load rail VDD5V.
- **Current:**
  - The DSS34 is rated 3 A, with about 0.45–0.5 V drop at 2–3 A.
  - The XH contact is rated 3 A with AWG 22 wire.
  - Elecrow's 2 A rating is conservative against both parts. A draw of 8–10 W is about 1.6–2.0 A.
- **Supply recommendation:** a 5.1 V, ≥ 3 A supply with an AWG 22 pigtail. The extra 0.1 V offsets the diode and wire drop. USB has the same diode, so the inlet is no worse than USB power.
- **Supply cable (when added):** an XH2.54-4P plug wired to pins 3 (+5 V) and 4 (GND) only. If the far end is a USB-C power-only breakout, it must have 5.1 kΩ CC pull-downs, or a USB-C charger won't output 5 V. A barrel jack avoids that issue.

## Phases

| # | Work | Done when |
|---|---|---|
| 1 | Write a generator script (FreeCAD Python, pattern: `Archive/ELCROW-10.1-Dev-Frame/generate_elcrow_10_1_dev_frame_v6.py`). It holds the parameter block, loads the STEP reference, and builds stand-in volumes for the speakers, folded ribbon cables, camera reserve, and plug bodies (straight and right-angle) | Everything loads and sits in its measured place |
| 2 | Front bezel: lip, top band, chin with speaker pockets and grille, bosses, magnet pockets | The lip stays inside the black border; the speakers seat |
| 3 | Back shell: rim, magnet pockets, vents, port bay, openings | Every plug body and opening's access path is clear |
| 4 | Cradle stand | Tip-over check at 30° passes; nothing collides with the port bay or cable exits |
| 5 | Checks (reuse the archive's collision and access-path checks), renders, STL export | Zero collisions; every part ≤ 256 mm and correctly oriented |
| 6 | Fit-test coupons: (a) a bezel corner with its boss and a magnet pair; (b) a slice of the left port bay; (c) one speaker pocket | They fit the real board, plugs, and speaker; tolerances are tuned before the full print |

## Exports

Every generator run writes `exports/crowpanel_*.stl`. Each part is already in print orientation, sitting at z = 0 and centered on x/y.

| File | Orientation | Size (mm) |
|---|---|---|
| `crowpanel_bezel.stl` | Face-down | 252.6 × 191.5 × 18.6 |
| `crowpanel_bezel_text.stl` | Bezel's transform (aligned part) | 44.1 × 14.4 × 0.6 |
| `crowpanel_back_shell.stl` | Back-down | 252.6 × 191.5 × 12.7 |
| `crowpanel_cradle.stl` | Base-down | 160 × 179.7 × 100 |

All meshes are closed solids with no non-manifold edges. On reload, the text and bezel overlap by 0.015 mm³, which is just mesh rounding.

## Print notes

- **Bezel:** print face-down, so the front face takes the bed's texture. No supports needed. The only flat bridges are the 5.5 mm tops of the USB slots; every other overhang is 45° or steeper.
- **Back shell:** print back-down. No overhangs. All magnet pockets open toward the inside, so the magnets glue in after printing (no pause needed).
- **Cradle:** print base-down, no supports (see Cradle stand).
- **Material:** PETG is preferred because of the 8–10 W heat. Matte PLA works for prototypes.
- **Hardware:**
  - 4 × M3 heat-set inserts plus 4 × M3×6 screws for the board.
  - About 24 × 6 × 3 mm N52 magnets (8 seam pairs + 4 cradle pairs).
  - Foam gasket tape for the speakers.
