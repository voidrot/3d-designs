"""Generate the corrected V2 first-fit ELCROW 10.1 frame and 20 degree cradle.

Run with FreeCADCmd or in FreeCAD. This revision never overwrites an existing V2
CAD document or export directory and never saves, closes, or modifies the source.
"""
import math
import os

import FreeCAD as App
import Mesh
import Part

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = "ELCROW_10_1_Dev_Frame_FirstFit_V2"
DOC_PATH = os.path.join(ROOT, NAME + ".FCStd")
OUT = os.path.join(ROOT, "exports", NAME)
SOURCE_NAME = "ELCROW_P4_10_1_STEP_REFERENCE_20251230"
SOURCE_PATH = os.path.join(ROOT, SOURCE_NAME + ".FCStd")

# Refuse to discard either generated files or an open document containing edits.
if os.path.exists(DOC_PATH):
    raise RuntimeError("Refusing to overwrite existing V2 document: " + DOC_PATH)
if os.path.exists(OUT):
    raise RuntimeError("Refusing to overwrite existing V2 export directory: " + OUT)
if NAME in App.listDocuments():
    raise RuntimeError("Refusing to replace open V2 document: " + NAME)

# Every value below is consumed by geometry or a generated check.
D = {
    "outer_x": 128.0, "outer_z": 82.0,
    "pcb_x": 123.5, "pcb_z": 73.5,
    "rear_cavity_x": 125.0, "rear_cavity_z": 75.0,
    "rear_y": -8.0, "front_y": 2.05, "lip_y": 5.05,
    "ap_w": 225.0, "ap_h": 129.0,
    "top_relief_x0": -30.0, "top_relief_w": 90.0, "top_relief_z": 68.0,
    "bottom_relief_half_w": 11.0, "bottom_relief_z": -64.0,
    "retainer_overlap": 1.5, "retainer_gap": 0.30,
    "retainer_z_low": -30.0, "retainer_z_high": 45.0,
    "m3_clear_d": 3.4, "m3_nut_af": 5.5, "m3_nut_t": 2.4,
    "m3_head_d": 5.5, "m3_head_h": 3.0,
    "retainer_screw_len": 12.0, "seam_screw_len": 8.0,
    "tilt_deg": 20.0, "base_depth": 125.0,
    "cradle_side_x0": 108.0, "cradle_outer_x": 142.0,
    "crossbar_half": 112.0,
}

os.makedirs(OUT)
doc = App.newDocument(NAME, "ELCROW 10.1 Dev Frame First Fit V2")
params = doc.addObject("App::FeaturePython", "Design_Parameters")
params.Label = "V2 driving dimensions (mm / degrees)"
for key, value in D.items():
    params.addProperty("App::PropertyFloat", key, "Driving dimensions")
    setattr(params, key, value)
params.addProperty("App::PropertyString", "Hardware", "Documentation")
params.Hardware = "M3x12 ISO 4762 + DIN 934 nuts (retainers); M3x8 ISO 4762 + DIN 934 nuts (seam)"
params.addProperty("App::PropertyString", "Purpose", "Documentation")
params.Purpose = "FIRST-FIT PROTOTYPE; no PCB holes used; physical fit and connector access remain required."

print_group = doc.addObject("App::DocumentObjectGroup", "Printable_Parts")
assembly = doc.addObject("App::DocumentObjectGroup", "Assembly")
checks_group = doc.addObject("App::DocumentObjectGroup", "Verification")
hardware_group = doc.addObject("App::DocumentObjectGroup", "Hardware_Envelopes")


def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))


def cylinder_axis(radius, length, origin, direction):
    return Part.makeCylinder(radius, length, App.Vector(*origin), App.Vector(*direction))


def hex_prism(axis, center, length, across_flats):
    """Regular hexagonal nut envelope, extruded along X or Y."""
    r = across_flats / math.sqrt(3.0)
    pts = []
    for i in range(6):
        a = math.radians(30.0 + i * 60.0)
        u, v = r * math.cos(a), r * math.sin(a)
        if axis == "x":
            pts.append(App.Vector(center[0] - length / 2.0, center[1] + u, center[2] + v))
        else:
            pts.append(App.Vector(center[0] + u, center[1] - length / 2.0, center[2] + v))
    face = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return face.extrude(App.Vector(length, 0, 0) if axis == "x" else App.Vector(0, length, 0))


def placed(shape, placement):
    result = shape.copy()
    result.Placement = placement
    return result


def add_part(name, label, shape, description, orientation, color):
    shape = shape.removeSplitter()
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    obj.addProperty("App::PropertyString", "Material", "Print")
    obj.Material = "PLA or PETG"
    obj.addProperty("App::PropertyString", "Print_Orientation", "Print")
    obj.Print_Orientation = orientation
    obj.addProperty("App::PropertyString", "Description", "Documentation")
    obj.Description = description
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = color
    print_group.addObject(obj)
    return obj


def add_hardware(name, label, shape):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape
    if obj.ViewObject:
        obj.ViewObject.ShapeColor = (0.72, 0.72, 0.76)
    hardware_group.addObject(obj)
    return obj

# Full source assembly includes LCD, touch, PCB, flexes, ports, switches and chips.
src = App.listDocuments().get(SOURCE_NAME)
if src is None:
    if not os.path.isfile(SOURCE_PATH):
        raise RuntimeError("Required source document not found: " + SOURCE_PATH)
    src = App.openDocument(SOURCE_PATH)
full_obj = src.getObject("_10_1CUN_ASM")
if not full_obj or full_obj.Shape.isNull() or len(full_obj.Shape.Solids) < 50:
    raise RuntimeError("Complete 10-1CUN assembly shape (>=50 solids) is unavailable")
full_reference = full_obj.Shape.copy()

# Frame: rear PCB-locating rail plus front aperture lip. Both cable corridors are real cuts.
rear = box(-D["outer_x"], D["rear_y"], -D["outer_z"],
           2 * D["outer_x"], D["front_y"] - D["rear_y"], 2 * D["outer_z"])
rear = rear.cut(box(-D["rear_cavity_x"], D["rear_y"] - 1, -D["rear_cavity_z"],
                    2 * D["rear_cavity_x"], D["lip_y"] - D["rear_y"] + 2,
                    2 * D["rear_cavity_z"]))
front = box(-D["outer_x"], D["front_y"], -D["outer_z"],
            2 * D["outer_x"], D["lip_y"] - D["front_y"], 2 * D["outer_z"])
front = front.cut(box(-D["ap_w"] / 2, D["front_y"] - 1, -D["ap_h"] / 2,
                      D["ap_w"], D["lip_y"] - D["front_y"] + 2, D["ap_h"]))
frame = rear.fuse(front)
frame = frame.cut(box(D["top_relief_x0"], D["rear_y"] - 5, D["top_relief_z"],
                      D["top_relief_w"], 25, 150))
frame = frame.cut(box(-D["bottom_relief_half_w"], D["rear_y"] - 5, -110,
                      2 * D["bottom_relief_half_w"], 25, 110 + D["bottom_relief_z"]))

# Retainer bosses are integral with the frame; each has a real clearance bore and rear-loaded nut slot.
retainer_centers = [(-1, D["retainer_z_low"]), (-1, D["retainer_z_high"]),
                    (1, D["retainer_z_low"]), (1, D["retainer_z_high"])]
for side, zc in retainer_centers:
    bx = -136.0 if side < 0 else 125.0
    boss = box(bx, D["rear_y"], zc - 7, 11, D["lip_y"] - D["rear_y"], 14)
    axis_origin = (-141.0, -1.5, zc) if side < 0 else (124.0, -1.5, zc)
    axis_dir = (1, 0, 0)
    hole = cylinder_axis(D["m3_clear_d"] / 2, 18, axis_origin, axis_dir)
    nut_x = -130.5 if side < 0 else 130.5
    nut = hex_prism("x", (nut_x, -1.5, zc), D["m3_nut_t"] + 0.25, D["m3_nut_af"] + 0.25)
    # Slot opens to the rear, allowing the nut to be loaded before the display.
    slot = box(nut_x - 1.4, D["rear_y"] - 0.1, zc - 2.95,
               2.8, 6.6, 5.9)
    frame = frame.fuse(boss).cut(hole.fuse(nut).fuse(slot))

# Front lower seam plate avoids the modeled bottom-center flex and cannot pierce a stand floor.
seam_xs = (-22.0, 22.0)
seam_z = -77.5
for sx in seam_xs:
    frame = frame.cut(cylinder_axis(D["m3_clear_d"] / 2, 9, (sx, 9, seam_z), (0, -1, 0)))
    frame = frame.cut(hex_prism("y", (sx, 3.45, seam_z), D["m3_nut_t"] + 0.25,
                               D["m3_nut_af"] + 0.25))
    # Front-open loading mouth; the seam plate captures the nut after assembly.
    frame = frame.cut(box(sx - 2.95, 3.3, seam_z - 2.95, 5.9, 1.85, 5.9))

left = frame.common(box(-145, -20, -110, 145, 45, 230))
right = frame.common(box(0, -20, -110, 145, 45, 230))
bez_l = add_part("PRINT_Bezel_Left", "PRINT Bezel - left half", left,
                 "Left frame half with two nut-loaded retainer bosses; no PCB holes.",
                 "Rear face on bed", (0.88, 0.55, 0.16))
bez_r = add_part("PRINT_Bezel_Right", "PRINT Bezel - right half", right,
                 "Right frame half with two nut-loaded retainer bosses; no PCB holes.",
                 "Rear face on bed", (0.88, 0.55, 0.16))

seam_plate = box(-29, D["lip_y"], -84, 58, 3.0, 13.0)
for sx in seam_xs:
    seam_plate = seam_plate.cut(cylinder_axis(D["m3_clear_d"] / 2, 5, (sx, 9, seam_z), (0, -1, 0)))
    seam_plate = seam_plate.cut(cylinder_axis(D["m3_head_d"] / 2 + 0.2, D["m3_head_h"] + 0.2,
                                              (sx, 8.2, seam_z), (0, -1, 0)))
seam = add_part("PRINT_Front_Seam_Lock", "PRINT Front lower seam lock", seam_plate,
                "Front-access seam bridge, clear of the bottom flex; two M3x8 screws and DIN 934 nuts.",
                "Large face on bed", (0.62, 0.64, 0.68))

# Retainers overlap the PCB edge by 1.5 mm while remaining 0.30 mm behind its rear face.
retainers = []
for side, zc in retainer_centers:
    suffix = ("L" if side < 0 else "R") + ("_lower" if zc < 0 else "_upper")
    mount_x = -140.0 if side < 0 else 136.0
    mount = box(mount_x, D["rear_y"], zc - 7, 4, D["lip_y"] - D["rear_y"], 14)
    hook_inner = D["pcb_x"] - D["retainer_overlap"]
    hook_x = -140.0 if side < 0 else hook_inner
    hook_dx = 140.0 - hook_inner
    hook = box(hook_x, -6.5 - D["retainer_gap"] - 3.2, zc - 6,
               hook_dx, 3.2, 12)
    shape = mount.fuse(hook)
    axis_origin = (-141.0, -1.5, zc) if side < 0 else (135.0, -1.5, zc)
    shape = shape.cut(cylinder_axis(D["m3_clear_d"] / 2, 6, axis_origin, (1, 0, 0)))
    r = add_part("PRINT_Retainer_" + suffix, "PRINT rear retainer " + suffix, shape,
                 "PCB-edge rear stop with 1.5 mm projected overlap and 0.30 mm nominal rear gap.",
                 "Outer side face on bed; PETG preferred", (0.35, 0.64, 0.84))
    retainers.append(r)

# The same rigid transform defines display visualization and every cradle contact plane.
pivot = App.Vector(0, 0, -D["outer_z"])
rot = App.Rotation(App.Vector(1, 0, 0), D["tilt_deg"])
assembly_place = App.Placement(App.Vector(0, 70, 94), rot, pivot)

# Cradle has hard bottom seats, rear support on the 3 mm outer rail, and front stops.
# A keyed crossbar ties both stands so they cannot spread; TPU is not in the load path.
def cradle(side):
    if side < 0:
        base = box(-D["cradle_outer_x"], 0, 0,
                   D["cradle_outer_x"] - D["cradle_side_x0"], D["base_depth"], 8)
        seat = box(-128, -8, -88, 20, 13.05, 6)
        rear_contact = box(-142, -13, -82, 17, 5, 142)
        outer_web = box(-142, -12.8, -82, 6, 23.25, 20)
        front_bridge = box(-142, 5.05, -82, 34, 0.6, 20)
        front_stop = box(-128, 5.45, -82, 20, 5, 20)
        pocket = box(-116, 95, 2, 8, 16, 6.2)
    else:
        base = box(D["cradle_side_x0"], 0, 0,
                   D["cradle_outer_x"] - D["cradle_side_x0"], D["base_depth"], 8)
        seat = box(108, -8, -88, 20, 13.05, 6)
        rear_contact = box(125, -13, -82, 17, 5, 142)
        outer_web = box(136, -12.8, -82, 6, 23.25, 20)
        front_bridge = box(108, 5.05, -82, 34, 0.6, 20)
        front_stop = box(108, 5.45, -82, 20, 5, 20)
        pocket = box(108, 95, 2, 8, 16, 6.2)
    contact_structure = placed(seat.fuse(rear_contact).fuse(outer_web).fuse(front_bridge).fuse(front_stop), assembly_place)
    return base.fuse(contact_structure).cut(pocket).removeSplitter()

stand_l = add_part("PRINT_Cradle_Left", "PRINT fixed 20 degree cradle - left", cradle(-1),
                   "Hard bottom seat and rear-rail support; keyed by the crossbar.",
                   "As modeled, base at Z=0", (0.25, 0.60, 0.35))
stand_r = add_part("PRINT_Cradle_Right", "PRINT fixed 20 degree cradle - right", cradle(1),
                   "Hard bottom seat and rear-rail support; keyed by the crossbar.",
                   "As modeled, base at Z=0", (0.25, 0.60, 0.35))

crossbar = box(-D["crossbar_half"], 96, 4, 2 * D["crossbar_half"], 14, 6)
crossbar = crossbar.fuse(box(-115.7, 96.3, 2.2, 7.4, 13.4, 6.0))
crossbar = crossbar.fuse(box(108.3, 96.3, 2.2, 7.4, 13.4, 6.0))
crossbar_part = add_part("PRINT_Cradle_Crossbar", "PRINT cradle keyed crossbar", crossbar,
                         "Drop-in keyed crossbar positively fixes stand spacing.",
                         "As modeled, lowest face at Z=0 after export", (0.25, 0.55, 0.32))

# Full, non-printable reference copy and assembly links.
ref = doc.addObject("PartDesign::Feature", "ASSEMBLY_REFERENCE_FULL_STEP_COPY")
ref.Label = "ASSEMBLY full STEP copy - 54 solids including components"
ref.Shape = full_reference
ref.Placement = assembly_place
ref.addProperty("App::PropertyString", "Source", "Documentation")
ref.Source = SOURCE_NAME + ".FCStd : _10_1CUN_ASM (read-only copy)"
if ref.ViewObject:
    ref.ViewObject.ShapeColor = (0.72, 0.78, 0.88)
    ref.ViewObject.Transparency = 68
assembly.addObject(ref)

for master in print_group.Group:
    link = doc.addObject("App::Link", "ASSEMBLY_" + master.Name[6:])
    link.Label = "ASSEMBLY " + master.Label.replace("PRINT ", "")
    link.LinkedObject = master
    link.LinkTransform = True
    if master.Name.startswith(("PRINT_Bezel", "PRINT_Retainer", "PRINT_Front")):
        link.Placement = assembly_place
    assembly.addObject(link)
    if master.ViewObject:
        master.ViewObject.Visibility = False

# Explicit screw/nut envelopes document axis, engagement and tip clearance.
hardware_shapes_source = []
for side, zc in retainer_centers:
    if side < 0:
        screw = cylinder_axis(1.5, D["retainer_screw_len"], (-140, -1.5, zc), (1, 0, 0))
        head = cylinder_axis(D["m3_head_d"] / 2, D["m3_head_h"], (-143, -1.5, zc), (1, 0, 0))
        nx = -130.5
    else:
        screw = cylinder_axis(1.5, D["retainer_screw_len"], (140, -1.5, zc), (-1, 0, 0))
        head = cylinder_axis(D["m3_head_d"] / 2, D["m3_head_h"], (143, -1.5, zc), (-1, 0, 0))
        nx = 130.5
    nut = hex_prism("x", (nx, -1.5, zc), D["m3_nut_t"], D["m3_nut_af"])
    hw = screw.fuse(head).fuse(nut)
    hardware_shapes_source.append(hw)
    add_hardware("HARDWARE_Retainer_%s_%s" % ("L" if side < 0 else "R", "low" if zc < 0 else "high"),
                 "M3x12 retainer screw and DIN 934 nut", placed(hw, assembly_place))
for sx in seam_xs:
    screw = cylinder_axis(1.5, D["seam_screw_len"], (sx, 8.05, seam_z), (0, -1, 0))
    head = cylinder_axis(D["m3_head_d"] / 2, D["m3_head_h"], (sx, 11.05, seam_z), (0, -1, 0))
    nut = hex_prism("y", (sx, 3.45, seam_z), D["m3_nut_t"], D["m3_nut_af"])
    hw = screw.fuse(head).fuse(nut)
    hardware_shapes_source.append(hw)
    add_hardware("HARDWARE_Seam_%s" % ("L" if sx < 0 else "R"),
                 "M3x8 seam screw and DIN 934 nut", placed(hw, assembly_place))

# Verification is executable and fatal: no collision waivers.
results = []
source_fixed = [bez_l, bez_r, seam] + retainers
for obj in source_fixed:
    vol = obj.Shape.common(full_reference).Volume
    results.append("COLLISION %s vs full 54-solid reference = %.6f mm^3" % (obj.Name, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])
transformed_reference = placed(full_reference, assembly_place)
for obj in (stand_l, stand_r, crossbar_part):
    vol = obj.Shape.common(transformed_reference).Volume
    results.append("COLLISION %s vs transformed full reference = %.6f mm^3" % (obj.Name, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])
for index, hw in enumerate(hardware_shapes_source, 1):
    vol = hw.common(full_reference).Volume
    results.append("COLLISION hardware envelope %d vs full reference = %.6f mm^3" % (index, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])

# Contact and capture invariants come directly from the same dimensions used above.
bezel_union_asm = placed(bez_l.Shape.fuse(bez_r.Shape), assembly_place)
for obj in (stand_l, stand_r):
    distance = obj.Shape.distToShape(bezel_union_asm)[0]
    penetration = obj.Shape.common(bezel_union_asm).Volume
    results.append("CONTACT %s to bezel distance %.6f mm, penetration %.6f mm^3" %
                   (obj.Name, distance, penetration))
    if distance > 0.001 or penetration > 0.001:
        raise RuntimeError("Cradle contact invariant failed: " + results[-1])

panel_half_w = 117.5
panel_half_h = 71.5
max_shift_x = D["rear_cavity_x"] - D["pcb_x"]
max_shift_z = D["rear_cavity_z"] - D["pcb_z"]
min_lip_x = panel_half_w - D["ap_w"] / 2 - max_shift_x
min_lip_z = panel_half_h - D["ap_h"] / 2 - max_shift_z
results += [
    "CAPTURE PCB lateral clearance each side = %.2f mm" % max_shift_x,
    "CAPTURE minimum panel/aperture overlap after worst lateral shift = %.2f mm X, %.2f mm Z" % (min_lip_x, min_lip_z),
    "RETAINER projected PCB overlap = %.2f mm; nominal rear gap = %.2f mm" %
    (D["retainer_overlap"], D["retainer_gap"]),
    "CRADLE hard bottom seat area per side = %.2f mm^2; rear rail contact area per side = %.2f mm^2" %
    (20.0 * 13.05, 3.0 * 142.0),
    "CRADLE source vertical transforms toward rear by %.2f mm over 164 mm rise (20 degrees)" %
    (164.0 * math.sin(math.radians(D["tilt_deg"]))),
    "FASTENER retainer: M3x12, 3.4 bore, 2.4 nut engagement, tip remains outside |X|=128",
    "FASTENER seam: M3x8 axis -Y from front, 3.4 bore, 2.4 nut engagement; no base/floor path",
    "LIGAMENT retainer boss around nut slot >= 4.05 mm Z; seam lower nut ligament = 1.31 mm",
]
if min_lip_x <= 0 or min_lip_z <= 0:
    raise RuntimeError("Panel aperture capture is not positive")

# Validate each printable as one valid solid, within practical build axes; export at Z=0.
for master in print_group.Group:
    if len(master.Shape.Solids) != 1 or not master.Shape.isValid():
        raise RuntimeError("Printable is not one valid solid: " + master.Name)
    bb = master.Shape.BoundBox
    if max(bb.XLength, bb.YLength, bb.ZLength) > 250.0 + 1e-6:
        raise RuntimeError("Printable exceeds 250 mm axis: " + master.Name)
    results.append("SOLID %s valid single; bbox %.2f x %.2f x %.2f mm" %
                   (master.Name, bb.XLength, bb.YLength, bb.ZLength))
    shp = master.Shape.copy()
    if master.Name.startswith("PRINT_Bezel"):
        shp.rotate(App.Vector(), App.Vector(1, 0, 0), -90)
    elif master.Name.startswith("PRINT_Retainer"):
        shp.rotate(App.Vector(), App.Vector(0, 1, 0), 90)
    elif master.Name == "PRINT_Front_Seam_Lock":
        shp.rotate(App.Vector(), App.Vector(1, 0, 0), 90)
    bb2 = shp.BoundBox
    shp.translate(App.Vector(-bb2.XMin + 3, -bb2.YMin + 3, -bb2.ZMin))
    if abs(shp.BoundBox.ZMin) > 1e-6:
        raise RuntimeError("Export orientation is not on Z=0: " + master.Name)
    temp = doc.addObject("Part::Feature", "EXPORT_TEMP")
    temp.Shape = shp
    Mesh.export([temp], os.path.join(OUT, master.Name.replace("PRINT_", "") + ".stl"))
    doc.removeObject(temp.Name)
    results.append("EXPORT %s base Z=0.000000 mm" % master.Name)

report = doc.addObject("App::FeaturePython", "Measured_Checks")
report.Label = "V2 measured checks - generated, fatal on failure"
report.addProperty("App::PropertyStringList", "Results", "Verification")
report.Results = results
report.addProperty("App::PropertyString", "Reference_Scope", "Verification")
report.Reference_Scope = "_10_1CUN_ASM: 54 solids, including LCD/touch/PCB/flex/ports/chips"
checks_group.addObject(report)

doc.recompute()
doc.saveAs(DOC_PATH)
print("\n".join(results))
print("SAVED " + DOC_PATH)
print("EXPORTED " + OUT)
