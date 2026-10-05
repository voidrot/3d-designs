"""CrowPanel Advanced 10.1" ESP32-P4 desk case — FreeCAD prototype generator.

Run inside the FreeCAD GUI:  exec(open(PATH).read())
Re-running rebuilds every Case_* object; the imported STEP reference is reused.

Display frame = STEP frame rotated 180° about X:  (x, y, z) = (X, -Y, -Z).
So +z is up, the screen faces -y (FreeCAD "Front" view), and +x is right.
"""
import os
import FreeCAD as App
import Part
from FreeCAD import Vector, Rotation, Placement

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else \
    "/home/buck/Projects/voidrot/3d-designs/10.1-ESP-Touchscreen-Frame"
STEP = os.path.join(HERE, "ESP32-P4-10_1-inch-20251230.stp")
DOC = "CrowPanelCase"

# ---------------------------------------------------------------- parameters
CLR = 0.4             # board-to-wall clearance
WALL = 2.4
R_OUT = 8.0           # plan-view corner radius
FILLET_FRONT = 1.5
FILLET_BACK = 4.0

PCB_X, PCB_Z = 123.5, 73.5
PCB_Y0, PCB_Y1 = 4.8, 6.5
GLASS_X, GLASS_Z = 117.5, 71.5
GLASS_Y0 = -2.0       # glass front face
LCD_Y1 = 4.3          # LCD back face

X_OUT = PCB_X + CLR + WALL
Z_TOP = 93.0          # keeps the camera reserve (z up to 90.25)
Z_BOT = -98.5         # speaker chin
Y_FRONT = GLASS_Y0 - 1.6   # lip thickness 1.6
Y_BACK = 14.6 + 2.0 + WALL # 2 mm behind the deepest connector
SEAM_Y = 12.0

LIP = 2.5             # lip overlap onto the glass
OPEN_R = 2.0
OPEN_CHAMFER = 1.0

SPK_W, SPK_H, SPK_D = 30.0, 20.0, 7.0
SPK_X = 75.0          # clears the microSD path (x 96..112) and the FPC fold
SPK_Z = -85.5
GASKET = 1.0

MAG_D, MAG_H = 6.0, 3.0
MAG_POS = [(-108, 85), (-45, 85), (45, 85), (108, 85),
           (-110, -91), (-40, -90), (40, -90), (110, -91)]
MAG_BOSS_R = 4.5

HOLES = [(sx * 120.5, sz * 70.5) for sx in (-1, 1) for sz in (-1, 1)]
PILOT_R = 1.3         # M3 thread-forming screw pilot
BOSS_TOP = PCB_Y0     # boss seat; tune with fit coupon (a) for glass/PCB stack slack

MIC = (120.4, 61.6)   # single bottom-port mic (V1.0/V1.2 brd U176), hole through the PCB

# Cradle magnet pairs (case frame x, z): shell back plate <-> dock face.
CRADLE_MAG_POS = [(sx * 61, z) for sx in (-1, 1) for z in (-60, -10)]
MAG_SKIN = 0.6        # plastic left over the shell-side magnet

TEXT = "MISSION\nCONTROL"   # "\n" stacks lines
TEXT_FONT = "/usr/share/fonts/noto/NotoSans-Bold.ttf"
TEXT_BLOCK_H = 14.4   # matches the grille slot field (6 slots, 2.6 pitch, 1.4 tall)
TEXT_LINE_GAP = 1.6
TEXT_TRACK = 1.2      # extra letter spacing
TEXT_DEPTH = 0.6      # inlay depth: 3 layers at 0.2 mm, printed face-down
TEXT_MAX_W = 112.0    # between the inner grille edges (x ±62) less 6 mm margins

TILT = 30.0
DOCK_X = 80.0         # dock half-width
DOCK_H = 90.0         # dock height above the base
DOCK_CREST = 14.0     # flat top depth behind the case
CAMERA_WINDOW = False


# ---------------------------------------------------------------- helpers
def rbox(x0, x1, y0, y1, z0, z1, r=0.0, axis="y"):
    """Box with edges parallel to `axis` rounded by r."""
    b = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, Vector(x0, y0, z0))
    if r > 0:
        idx = {"x": 0, "y": 1, "z": 2}[axis]
        edges = [e for e in b.Edges if abs(e.tangentAt(e.FirstParameter)[idx]) > 0.99]
        b = b.makeFillet(r, edges)
    return b


def rwire(x0, x1, z0, z1, r, y):
    b = rbox(x0, x1, y, y + 1, z0, z1, r)
    return [f for f in b.Faces if f.normalAt(0, 0).y < -0.99][0].OuterWire


def cyl_y(x, z, r, y0, y1):
    return Part.makeCylinder(r, y1 - y0, Vector(x, y0, z), Vector(0, 1, 0))


def fuse_all(shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = out.fuse(s)
    return out.removeSplitter()


def outline(inset, y0, y1, grow=0.0):
    """Case plan outline inset from the outer skin."""
    i = inset - grow
    return rbox(-X_OUT + i, X_OUT - i, y0, y1, Z_BOT + i, Z_TOP - i, max(R_OUT - i, 0.5))


def edges_on_y(shape, y):
    return [e for e in shape.Edges if abs(e.BoundBox.YMin - y) < 1e-6 and abs(e.BoundBox.YMax - y) < 1e-6]


# ---------------------------------------------------------------- document + reference
doc = App.getDocument(DOC) if DOC in App.listDocuments() else App.newDocument(DOC)
for o in [o for o in doc.Objects if o.Name.startswith("Case_")]:
    doc.removeObject(o.Name)

if not doc.getObject("Ref_Group"):
    import Import
    before = set(o.Name for o in doc.Objects)
    Import.insert(STEP, doc.Name)
    new = [doc.getObject(n) for n in set(o.Name for o in doc.Objects) - before]
    grp = doc.addObject("App::Part", "Ref_Group")
    flip = Placement(Vector(), Rotation(Vector(1, 0, 0), 180))
    for o in new:
        if not o.InList:
            o.Placement = flip.multiply(o.Placement)
            grp.addObject(o)
    # Flat FPC tails, misplaced socket headers, and the (unfitted) camera are hidden.
    for o in new:
        if o.TypeId == "Part::Feature" and o.Label in (
                "SOLID", "SOLID001", "SOLID003", "SOLID004", "SOLID005", "AS-AG638A32M1-25"):
            o.Visibility = False
    glass = doc.addObject("Part::Feature", "Ref_Glass")
    glass.Shape = rbox(-GLASS_X, GLASS_X, GLASS_Y0, 0.0, -GLASS_Z, GLASS_Z)
    lcd = doc.addObject("Part::Feature", "Ref_LCD")
    lcd.Shape = rbox(-GLASS_X, GLASS_X, 0.0, LCD_Y1, -GLASS_Z, GLASS_Z)
    act = doc.addObject("Part::Feature", "Ref_Active")
    act.Shape = rbox(-112.0, 110.72, GLASS_Y0 - 0.02, GLASS_Y0 - 0.01, -59.64, 65.64)
    for sx in (-1, 1):
        s = doc.addObject("Part::Feature", "Ref_Speaker%s" % ("L" if sx < 0 else "R"))
        s.Shape = rbox(sx * SPK_X - SPK_W / 2, sx * SPK_X + SPK_W / 2,
                       GLASS_Y0 + GASKET, GLASS_Y0 + GASKET + SPK_D,
                       SPK_Z - SPK_H / 2, SPK_Z + SPK_H / 2, 1.0)
        grp.addObject(s)
    for o in (glass, lcd, act):
        grp.addObject(o)
    if App.GuiUp:
        glass.ViewObject.ShapeColor = (0.02, 0.02, 0.03)
        lcd.ViewObject.ShapeColor = (0.3, 0.3, 0.3)
        act.ViewObject.ShapeColor = (0.15, 0.35, 0.75)

# ---------------------------------------------------------------- monolithic body
outer = outline(0, Y_FRONT, Y_BACK)
outer = outer.makeFillet(FILLET_FRONT, edges_on_y(outer, Y_FRONT))
outer = outer.makeFillet(FILLET_BACK, edges_on_y(outer, Y_BACK))
cavity = outline(WALL, GLASS_Y0, Y_BACK - WALL)
body = outer.cut(cavity)

# Screen opening with a front chamfer.
ox, oz = GLASS_X - LIP, GLASS_Z - LIP
body = body.cut(rbox(-ox, ox, Y_FRONT - 1, GLASS_Y0 + 0.1, -oz, oz, OPEN_R))
body = body.cut(Part.makeLoft([
    rwire(-ox - OPEN_CHAMFER, ox + OPEN_CHAMFER, -oz - OPEN_CHAMFER, oz + OPEN_CHAMFER,
          OPEN_R + OPEN_CHAMFER, Y_FRONT - 0.001),
    rwire(-ox, ox, -oz, oz, OPEN_R, Y_FRONT + OPEN_CHAMFER)], True, True))

# ---------------------------------------------------------------- bezel internals
glass_keepout = rbox(-GLASS_X - CLR, GLASS_X + CLR, GLASS_Y0 - 1, BOSS_TOP + 0.01,
                     -GLASS_Z - CLR, GLASS_Z + CLR)
bosses = []
for x, z in HOLES:
    sx = 1 if x > 0 else -1
    b = cyl_y(x, z, 3.0, GLASS_Y0, BOSS_TOP).fuse(
        rbox(min(x, sx * (X_OUT - WALL + 0.01)), max(x, sx * (X_OUT - WALL + 0.01)),
             GLASS_Y0, BOSS_TOP, z - 3.0, z + 3.0))
    bosses.append(b.cut(glass_keepout))
bezel_add = list(bosses)

# Speaker pockets: frame around speaker + gasket, open behind.
for sx in (-1, 1):
    cx = sx * SPK_X
    frame = rbox(cx - SPK_W / 2 - 1.5, cx + SPK_W / 2 + 1.5, GLASS_Y0, GLASS_Y0 + 4.0,
                 SPK_Z - SPK_H / 2 - 1.5, SPK_Z + SPK_H / 2 + 1.5, 2.0)
    frame = frame.cut(rbox(cx - SPK_W / 2 - 0.3, cx + SPK_W / 2 + 0.3, GLASS_Y0 - 1, GLASS_Y0 + 5,
                           SPK_Z - SPK_H / 2 - 0.3, SPK_Z + SPK_H / 2 + 0.3, 1.2))
    bezel_add.append(frame)

# Mic tube: seals the bezel pinhole to the PCB front face.
bezel_add.append(cyl_y(MIC[0], MIC[1], 2.0, GLASS_Y0, BOSS_TOP))

# Magnet bosses (bezel half).
for x, z in MAG_POS:
    bezel_add.append(cyl_y(x, z, MAG_BOSS_R, GLASS_Y0, SEAM_Y))

body = fuse_all([body] + bezel_add)

# ---------------------------------------------------------------- shell internals
shell_add = []
for x, z in MAG_POS:
    shell_add.append(cyl_y(x, z, MAG_BOSS_R, SEAM_Y, Y_BACK - WALL + 0.5))
for sx in (-1, 1):  # speaker hold-down ribs
    for dx in (-8, 8):
        shell_add.append(rbox(sx * SPK_X + dx - 1, sx * SPK_X + dx + 1,
                              GLASS_Y0 + GASKET + SPK_D + 0.3, Y_BACK - WALL + 0.5,
                              SPK_Z - 5, SPK_Z + 5))
BTN = [(119.25, -41.75), (119.25, -56.25)]  # BOOT, RESET
for x, z in BTN:  # pin guide tubes
    shell_add.append(cyl_y(x, z, 2.4, 11.6, Y_BACK - WALL + 0.5))
for x, z in CRADLE_MAG_POS:
    # Pocket opens toward the inside: glue the magnet in from inside the shell.
    shell_add.append(cyl_y(x, z, MAG_BOSS_R, Y_BACK - MAG_SKIN - MAG_H - 0.15, Y_BACK - WALL + 0.5))
# shell_add crosses the seam, so it joins the shell after the split.

# ---------------------------------------------------------------- openings (whole body)
cuts = []
# Left port bay recess.
cuts.append(rbox(-X_OUT - 1, -X_OUT + 1.4, -0.5, SEAM_Y, -20.0, 20.0, 3.0, axis="x"))
# Left edge ports: (z centre, y centre, z size, y size)
for zc, yc, zs, ys in [(10.47, 7.58, 12.5, 7.0),    # UART0 USB-C
                       (-10.47, 7.58, 12.5, 7.0)]:  # USB 2.0 USB-C
    cuts.append(rbox(-X_OUT - 1, -PCB_X + 0.2, yc - ys / 2, yc + ys / 2,
                     zc - zs / 2, zc + zs / 2, min(ys, zs) / 2 - 0.01, axis="x"))
# Back openings.
yb0, yb1 = Y_BACK - WALL - 1, Y_BACK + 1
cuts.append(rbox(-27.5, 27.5, yb0, yb1, -71.0, -61.0, 2.0))   # GPIO 2x12
cuts.append(rbox(76.0, 113.0, yb0, yb1, 64.0, 73.0, 2.0))     # UART1 + I2C
cuts.append(rbox(-122.6, -114.7, yb0, yb1, -39.5, -24.9, 2.0)) # UART3-IN (vertical XH, plug from back)
cuts.append(rbox(-122.6, -114.8, yb0, yb1, 22.4, 32.4, 2.0))   # power switch (handle points back)
cuts.append(rbox(95.0, 121.0, yb0, yb1, -86.0, -66.0, 3.0))    # microSD finger window
for x, z in BTN:
    cuts.append(cyl_y(x, z, 1.2, 11.0, yb1))
# Vents along the top and bottom of the back plate.
for zc in (77.75, -78.0):
    x = -90.0
    while x <= 90.0:
        cuts.append(rbox(x - 0.9, x + 0.9, yb0, yb1, zc - 2.25, zc + 2.25, 0.85))
        x += 4.5
# Speaker grilles.
for sx in (-1, 1):
    for i in range(6):
        z = SPK_Z - 6.5 + i * 2.6
        cuts.append(rbox(sx * SPK_X - 13, sx * SPK_X + 13, Y_FRONT - 1, GLASS_Y0 + 0.5,
                         z - 0.7, z + 0.7, 0.69))
# Mic pinhole.
cuts.append(cyl_y(MIC[0], MIC[1], 0.5, Y_FRONT - 1, BOSS_TOP + 0.1))
# Shell-side cradle magnet pockets (blind from inside).
for x, z in CRADLE_MAG_POS:
    cuts.append(cyl_y(x, z, MAG_D / 2 + 0.15, Y_BACK - MAG_SKIN - MAG_H - 0.15, Y_BACK - MAG_SKIN))
# Screw pilots.
for x, z in HOLES:
    cuts.append(cyl_y(x, z, PILOT_R, GLASS_Y0 + 1.2, BOSS_TOP + 0.1))
# Magnet pockets, both sides of the seam.
for x, z in MAG_POS:
    cuts.append(cyl_y(x, z, MAG_D / 2 + 0.15, SEAM_Y - MAG_H - 0.15, SEAM_Y + MAG_H + 0.15))
# Pry notch.
cuts.append(rbox(-6, 6, SEAM_Y, SEAM_Y + 1.5, Z_BOT - 1, Z_BOT + 1.2))
if CAMERA_WINDOW:
    cuts.append(cyl_y(0.0, 77.6, 3.5, Y_FRONT - 1, GLASS_Y0 + 0.5))

body = body.cut(Part.makeCompound(cuts))

# ---------------------------------------------------------------- split at the seam
big = 500
front_half = body.common(Part.makeBox(big, big, big, Vector(-big / 2, SEAM_Y - big, -big / 2)))
back_half = body.common(Part.makeBox(big, big, big, Vector(-big / 2, SEAM_Y, -big / 2)))

# Registration rim: bezel ring (inset 1.4..2.4) inside a shell relief (inset 1.2..2.4).
ring = outline(1.4, SEAM_Y, SEAM_Y + 3.0).cut(outline(WALL, SEAM_Y - 1, SEAM_Y + 4))
relief = outline(1.2, SEAM_Y - 1, SEAM_Y + 3.2).cut(outline(WALL, SEAM_Y - 2, SEAM_Y + 4))
ring = ring.cut(Part.makeCompound(cuts))
bezel = front_half.fuse(ring).removeSplitter()

# Inlaid text: a separate body that fills a matching recess in the chin face.
# Exported as its own part so the slicer can assign it a different filament.
lines = [Part.makeCompound([Part.makeFace(w, "Part::FaceMakerBullseye")
                             for w in Part.makeWireString(ln, TEXT_FONT, 10.0, TEXT_TRACK) if w])
         for ln in TEXT.split("\n")]  # spaces have no wires
n_lines = len(lines)
cap10 = max(c.BoundBox.YLength for c in lines)  # all caps: line height = cap height
scale = min((TEXT_BLOCK_H - TEXT_LINE_GAP * (n_lines - 1)) / n_lines / cap10,
            TEXT_MAX_W / max(c.BoundBox.XLength for c in lines))
pitch = cap10 * scale + TEXT_LINE_GAP
placed = []
for i, c in enumerate(lines):
    c = c.scaled(scale)
    bb = c.BoundBox
    c.translate(Vector(-bb.Center.x, (n_lines - 1) / 2 * pitch - i * pitch - bb.Center.y, 0))
    placed.append(c)
label = Part.makeCompound(placed)
label.rotate(Vector(), Vector(1, 0, 0), 90)       # XY glyphs -> front (XZ) plane
label.translate(Vector(0, Y_FRONT, SPK_Z))
text = label.extrude(Vector(0, TEXT_DEPTH, 0))       # flush with the front face
recess = label.copy()
recess.translate(Vector(0, -0.5, 0))
bezel = bezel.cut(recess.extrude(Vector(0, TEXT_DEPTH + 0.5, 0)))
shell = fuse_all([back_half.cut(relief)] + shell_add).cut(Part.makeCompound(cuts)).removeSplitter()

# ---------------------------------------------------------------- cradle
tilt = Placement(Vector(0, Y_FRONT, Z_BOT), Rotation(Vector(1, 0, 0), -TILT)).multiply(
    Placement(Vector(0, -Y_FRONT, -Z_BOT), Rotation()))
env = outline(0, Y_FRONT, Y_BACK, grow=0.3)
env = env.makeFillet(FILLET_FRONT, edges_on_y(env, Y_FRONT))
env = env.makeFillet(FILLET_BACK, edges_on_y(env, Y_BACK))
env.Placement = tilt
zmin = env.BoundBox.ZMin
base_top = zmin + 6.0
yf = env.BoundBox.YMin

# Case back plane in the desk frame, to size the dock's wedge profile.
back0 = tilt.multVec(Vector(0, Y_BACK + 0.3, Z_BOT))
back_dir = tilt.Rotation.multVec(Vector(0, 0, 1))
def back_y_at(h):
    return back0.y + (h - back0.z) / back_dir.z * back_dir.y
def back_h_at(z):
    return tilt.multVec(Vector(0, Y_BACK + 0.3, z)).z

h_top = base_top + DOCK_H
y_crest = back_y_at(h_top) + DOCK_CREST
y_rear = y_crest + DOCK_H * 0.8
base = rbox(-DOCK_X, DOCK_X, yf - 10, y_rear + 8, base_top - 10, base_top, 12.0, axis="z")
base = base.makeFillet(2.0, [e for e in base.Edges if abs(e.BoundBox.ZMax - base_top) < 1e-6])

# Solid wedge dock; its front face is the case back plane (+0.3 mm).
prof = Part.Face(Part.makePolygon([Vector(-DOCK_X, yf, base_top - 1), Vector(-DOCK_X, yf, h_top),
                                   Vector(-DOCK_X, y_crest, h_top), Vector(-DOCK_X, y_rear, base_top - 1),
                                   Vector(-DOCK_X, yf, base_top - 1)]))
dock = prof.extrude(Vector(2 * DOCK_X, 0, 0))
dock = dock.makeFillet(6.0, [e for e in dock.Edges if abs(e.BoundBox.YMin - y_crest) < 1e-6
                             and abs(e.BoundBox.ZMin - h_top) < 1e-6 and e.BoundBox.XLength > 1])
ahead = Part.makeBox(600, 600, 600, Vector(-300, Y_BACK + 0.3 - 600, -300))
ahead.Placement = tilt
dock = dock.cut(ahead)

# The cradle prints base-down; every cut below is shaped to print without supports.

# Centre tunnel (GPIO cable exit, vent outlet): 45° pitched roof with a 10 mm flat bridge.
h_wall = back_h_at(-60.0)
tunnel = Part.Face(Part.makePolygon([Vector(x, yf - 1, z) for x, z in (
    (-30, base_top - 3), (30, base_top - 3), (30, h_wall), (5, h_wall + 25),
    (-5, h_wall + 25), (-30, h_wall), (-30, base_top - 3))])).extrude(Vector(0, y_rear - yf + 12, 0))

# Vent groove across the dock face: flat floor + vertical back wall, so it has no ceiling.
h1, h2 = back_h_at(-82.0), back_h_at(-73.0)
groove = Part.Face(Part.makePolygon([Vector(-DOCK_X - 1, y, z) for y, z in (
    (back_y_at(h1) - 1, h1), (back_y_at(h2), h1), (back_y_at(h2), h2 + 1),
    (back_y_at(h2 + 1) - 1, h2 + 1), (back_y_at(h1) - 1, h1))])).extrude(Vector(2 * DOCK_X + 2, 0, 0))

# Gravity seats the case down the slope into the dock; magnets stop tipping and side slip.
dock_mags = []
for x, z in CRADLE_MAG_POS:
    m = cyl_y(x, z, MAG_D / 2 + 0.15, Y_BACK + 0.2, Y_BACK + 0.3 + MAG_H + 0.15)
    m.Placement = tilt
    dock_mags.append(m)
cradle = base.fuse(dock).removeSplitter().cut(env).cut(
    Part.makeCompound([tunnel, groove] + dock_mags))

# ---------------------------------------------------------------- publish
def add(name, shape, color, transp=0):
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    if App.GuiUp:
        o.ViewObject.ShapeColor = color
        o.ViewObject.Transparency = transp
    return o

# Case and reference ride in a tilted assembly; the cradle is built in the desk frame.
case_objs = [add("Case_Bezel", bezel, (0.16, 0.16, 0.17)),
             add("Case_Shell", shell, (0.24, 0.24, 0.26))]
case_objs.append(add("Case_Text", text, (0.95, 0.55, 0.10)))
cradle_obj = add("Case_Cradle", cradle, (0.72, 0.72, 0.70))
grp = doc.getObject("Ref_Group")
asm = doc.addObject("App::Part", "Case_Assembly")
asm.Placement = tilt
for o in case_objs + [grp]:
    asm.addObject(o)
doc.recompute()

# ---------------------------------------------------------------- checks
def ref_shapes():
    out = []
    for o in grp.Group:
        stack = [o]
        while stack:
            s = stack.pop()
            if s.TypeId == "Part::Feature" and s.Visibility and s.Shape.Solids:
                g = s.Shape.copy()
                g.Placement = s.getGlobalPlacement()
                out.append((s.Label, g))
            stack.extend(getattr(s, "Group", []) or [])
    return out

report = []
refs = ref_shapes()
for o in case_objs + [cradle_obj]:
    sh = o.Shape.copy()
    sh.Placement = o.getGlobalPlacement()
    for lbl, rs in refs:
        if sh.BoundBox.intersect(rs.BoundBox):
            v = sh.common(rs).Volume
            if v > 0.01:
                report.append("COLLISION %s vs %s: %.2f mm3" % (o.Label, lbl, v))
pairs = [("Case_Bezel", "Case_Shell"), ("Case_Bezel", "Case_Text"),
         ("Case_Bezel", "Case_Cradle"), ("Case_Shell", "Case_Cradle")]
for a, b in pairs:
    sa, sb = [doc.getObject(n).Shape.copy() for n in (a, b)]
    sa.Placement, sb.Placement = [doc.getObject(n).getGlobalPlacement() for n in (a, b)]
    v = sa.common(sb).Volume
    if v > 0.01:
        report.append("COLLISION %s vs %s: %.2f mm3" % (a, b, v))
for name, sh in [("Bezel", bezel), ("Shell", shell), ("Text", text), ("Cradle", cradle)]:
    bb = sh.BoundBox  # unplaced = print-frame size
    report.append("%-10s valid=%s solids=%d  %.1f x %.1f x %.1f" % (
        name, sh.isValid(), len(sh.Solids), bb.XLength, bb.YLength, bb.ZLength))
print("\n".join(report))

# ---------------------------------------------------------------- STL export (print orientation)
import MeshPart
EXPORT_DIR = os.path.join(HERE, "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def print_frame(shape, rot_x_deg):
    """Rotate about X into print orientation, then drop to z = 0 and centre on x/y."""
    pl = Placement(Vector(), Rotation(Vector(1, 0, 0), rot_x_deg))
    bb = shape.transformGeometry(pl.toMatrix()).BoundBox
    return Placement(Vector(-bb.Center.x, -bb.Center.y, -bb.ZMin), Rotation()).multiply(pl)

face_down = print_frame(bezel, 90)    # front face (-y) onto the bed
back_down = print_frame(shell, -90)   # back face (+y) onto the bed
desk = print_frame(cradle, 0)
# Text shares the bezel's transform so the two STLs import as aligned parts.
exports = [("bezel", bezel, face_down), ("bezel_text", text, face_down),
           ("back_shell", shell, back_down), ("cradle", cradle, desk)]
for name, shape, pl in exports:
    mesh = MeshPart.meshFromShape(Shape=shape.transformGeometry(pl.toMatrix()),
                                  LinearDeflection=0.02, AngularDeflection=0.15, Relative=False)
    path = os.path.join(EXPORT_DIR, "crowpanel_%s.stl" % name)
    mesh.write(path)
    bb = mesh.BoundBox
    print("STL %-11s %6d facets  %.1f x %.1f x %.1f  zmin=%.3f  solid=%s  nonmanifold=%s" % (
        name, mesh.CountFacets, bb.XLength, bb.YLength, bb.ZLength, bb.ZMin,
        mesh.isSolid(), mesh.hasNonManifolds()))
