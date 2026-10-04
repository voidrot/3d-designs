"""Generate the V5 integrated-joint ELCROW 10.1 frame and 20 degree cradle.

Run once via runpy in the existing FreeCAD GUI. This revision never overwrites an
existing V5 CAD document or populated export directory and never saves, closes,
hides, or modifies the source reference document.
"""
import math
import os
from types import SimpleNamespace

import FreeCAD as App
import Mesh
import Part

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = "ELCROW_10_1_Dev_Frame_FirstFit_V5"
DOC_PATH = os.path.join(ROOT, NAME + ".FCStd")
OUT = os.path.join(ROOT, "exports", NAME)
SOURCE_NAME = "ELCROW_P4_10_1_STEP_REFERENCE_20251230"
SOURCE_PATH = os.path.join(ROOT, SOURCE_NAME + ".FCStd")

# Refuse to discard either generated files or an open document containing edits.
if os.path.exists(os.path.join(ROOT, NAME + "_assembled.png")):
    raise RuntimeError("Refusing to overwrite existing V5 screenshot")
if os.path.exists(DOC_PATH):
    raise RuntimeError("Refusing to overwrite existing V5 document: " + DOC_PATH)
if os.path.exists(OUT) and os.listdir(OUT):
    raise RuntimeError("Refusing to overwrite existing V5 export directory: " + OUT)
if NAME in App.listDocuments():
    raise RuntimeError("Refusing to replace open V5 document: " + NAME)

# Every value below is consumed by geometry or a generated check.
D = {
    "outer_x": 128.0, "outer_z": 82.0,
    "pcb_x": 123.5, "pcb_z": 73.5,
    "rear_cavity_x": 125.0, "rear_cavity_z": 75.0,
    "rear_y": -8.0, "front_y": 2.05, "lip_y": 5.05,
    "ap_w": 225.0, "ap_h": 129.0,
    "retainer_overlap": 3.0, "retainer_gap": 0.30,
    "retainer_l_low_z": -45.0, "retainer_l_high_z": 52.0,
    "retainer_r_low_z": -20.0, "retainer_r_high_z": 20.0,
    "m3_clear_d": 3.4, "m3_nut_af": 5.5, "m3_nut_t": 2.4,
    "m3_head_d": 5.5, "m3_head_h": 3.0,
    "retainer_screw_len": 12.0, "joint_screw_len": 8.0,
    "joint_tongue_len": 20.0, "joint_clearance": 0.30,
    "tilt_deg": 20.0, "base_depth": 125.0,
    "cradle_side_x0": 108.0, "cradle_outer_x": 148.0,
    "crossbar_half": 112.0,
}

# Geometry and all checks are computed before creating any document or output.
print_group = SimpleNamespace(Group=[])
hardware_items = []


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
    result.Placement = placement.multiply(result.Placement)
    return result


def add_part(name, label, shape, description, orientation, color):
    shape = shape.removeSplitter()
    obj = SimpleNamespace(Name=name, Label=label, Shape=shape,
                          Description=description, Print_Orientation=orientation, Color=color)
    print_group.Group.append(obj)
    return obj


def add_hardware(name, label, shape):
    hardware_items.append((name, label, shape))

# Recheck the current live source. V5 excludes exactly the user-authorized camera
# object from fit checks without changing its source visibility or shape.
src = App.listDocuments().get(SOURCE_NAME)
if src is None:
    raise RuntimeError("Required source must already be open in the FreeCAD GUI: " + SOURCE_NAME)
full_obj = src.getObject("_10_1CUN_ASM")
camera_obj = src.getObject("Part__Feature065")
if (not full_obj or full_obj.Shape.isNull() or len(full_obj.Shape.Solids) != 52 or
        abs(full_obj.Shape.Volume - 66473.58997830914) > 0.01):
    raise RuntimeError("Live corrected 52-solid reference differs from the verified source")
if (not camera_obj or camera_obj.Label != "AS-AG638A32M1-25" or
        len(camera_obj.Shape.Solids) != 1):
    raise RuntimeError("Authorized camera exclusion object is unavailable or relabeled")
expected_camera_bounds = (-6.25, -8.1, -90.25, 6.25, 2.9, -65.0)
def bounds_tuple(shape):
    bb = shape.BoundBox
    return (bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax)
if (abs(camera_obj.Shape.Volume - 910.7150495454664) > 0.001 or
        max(abs(a-b) for a,b in zip(bounds_tuple(camera_obj.Shape), expected_camera_bounds)) > 0.001):
    raise RuntimeError("Authorized camera exclusion geometry changed")
matching_camera_solids = [s for s in full_obj.Shape.Solids
    if abs(s.Volume-camera_obj.Shape.Volume) < 0.001 and
    max(abs(a-b) for a,b in zip(bounds_tuple(s), expected_camera_bounds)) < 0.001]
if len(matching_camera_solids) != 1:
    raise RuntimeError("Could not identify exactly one camera solid in live assembly")
excluded_camera = matching_camera_solids[0].copy()
# Python shape wrappers are not identity-stable, so remove by the verified signature.
effective_solids = [s.copy() for s in full_obj.Shape.Solids
    if not (abs(s.Volume-camera_obj.Shape.Volume) < 0.001 and
            max(abs(a-b) for a,b in zip(bounds_tuple(s), expected_camera_bounds)) < 0.001)]
if len(effective_solids) != 51:
    raise RuntimeError("Effective reference must contain exactly 51 retained solids")
current_reference = Part.makeCompound(effective_solids)
lcd_envelope = box(-117.5, -4.3, -71.5, 235, 4.3, 143)
glass_envelope = box(-117.5, 0.5, -71.5, 235, 1.5, 143)
full_reference = Part.makeCompound([current_reference, lcd_envelope, glass_envelope])

# Frame: rear PCB-locating rail plus continuous top/front aperture lip. The
# lower camera/antenna relief is closed in V5; all functional side access remains.
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
# Continuous top lip: no obsolete flex/cable notch.
# Local rear side-rail openings clear the modeled ports and switches.
port_windows = [(-1, -18, 19), (-1, 23, 41), (-1, -35, -20), (1, 36, 63)]
for side, z0, z1 in port_windows:
    frame = frame.cut(box(-145 if side < 0 else 124.9, -9, z0, 20.1, 11.05, z1-z0))

# Retainer bosses are integral with the frame; each has a real clearance bore and rear-loaded nut slot.
retainer_centers = [(-1, D["retainer_l_low_z"]), (-1, D["retainer_l_high_z"]),
                    (1, D["retainer_r_low_z"]), (1, D["retainer_r_high_z"])]
for side, zc in retainer_centers:
    bx = -136.0 if side < 0 else 125.0
    boss = box(bx, D["rear_y"], zc - 7, 11, D["lip_y"] - D["rear_y"], 14)
    axis_origin = (-141.0, -1.5, zc) if side < 0 else (124.0, -1.5, zc)
    axis_dir = (1, 0, 0)
    hole = cylinder_axis(D["m3_clear_d"] / 2, 18, axis_origin, axis_dir)
    nut_x = -130.5 if side < 0 else 130.5
    nut = hex_prism("x", (nut_x, -1.5, zc), D["m3_nut_t"] + 0.25, D["m3_nut_af"] + 0.25)
    # Slot opens to the rear, allowing the nut to be loaded before the display.
    slot = box(nut_x - 1.325, D["rear_y"] - 0.1, zc - 3.4,
               2.65, 6.6, 6.8)
    frame = frame.fuse(boss).cut(hole.fuse(nut).fuse(slot))

# Hook channels remove only the rear 1.4 mm of each local rail/boss. The screw
# center remains 5.1 mm forward of the channel, preserving the nut-slot ligaments.
for side, zc in retainer_centers:
    clear_x = -140.2 if side < 0 else 120.3
    frame = frame.cut(box(clear_x, -10.2, zc - 6.2, 19.9, 3.6, 12.4))

# Two hidden rear-access lap joints replace the separate external seam plates.
# Both right-half tongues enter left-half receiver housings in one lateral
# assembly motion. They sit behind Y=-8, outside the retained electronics and
# panel envelopes, leaving the top/front skins uninterrupted except at X=0.
# The socket has 0.30 mm lateral/tip clearance; its front face is a clamp bearing.
joint_zs = (-78.4, 78.4)
tongues = []
for joint_z in joint_zs:
    tongues.append(box(-D["joint_tongue_len"], -14.0, joint_z-4.0,
                       D["joint_tongue_len"], 6.0, 8.0))

left = frame.common(box(-145, -20, -110, 145, 45, 230))
right = frame.common(box(0, -20, -110, 145, 45, 230))
for joint_z, tongue in zip(joint_zs, tongues):
    housing = box(-D["joint_tongue_len"]-1.0, -14.3, joint_z-5.8,
                  D["joint_tongue_len"]+1.0, 7.6, 11.6)
    # Localized front shoulder gives the nut 0.8 mm of bearing material while
    # remaining beyond the verified Z=+/-73.5 retained-reference envelope.
    shoulder = box(-13.6, -6.7, joint_z-3.35, 7.2, 1.0, 6.7)
    socket = box(-D["joint_tongue_len"]-D["joint_clearance"], -14.3,
                 joint_z-4.0-D["joint_clearance"],
                 D["joint_tongue_len"]+D["joint_clearance"],
                 6.3, 8.0+2*D["joint_clearance"])
    bore = cylinder_axis(D["m3_clear_d"]/2, 14, (-10.0, -15.0, joint_z), (0, 1, 0))
    head_recess = cylinder_axis(D["m3_head_d"]/2+0.20, D["m3_head_h"]+0.10,
                               (-10.0, -14.1, joint_z), (0, 1, 0))
    # Rear-loaded full-hex tunnel terminates at the bearing face Y=-6.5.
    nut_tunnel = hex_prism("y", (-10.0, -9.45, joint_z), 5.9,
                           D["m3_nut_af"]+0.25)
    nut_clearance = hex_prism("y", (-10.0, -7.7, joint_z),
                              D["m3_nut_t"]+0.25, D["m3_nut_af"]+0.25)
    left = left.fuse(housing).fuse(shoulder).cut(socket).cut(bore.fuse(nut_tunnel))
    # Preloaded receiver nuts need a lateral entry channel in the tongue.
    # The rear 1.975 mm head-bearing web remains continuous below this channel.
    nut_entry = box(-20.0, -9.025, joint_z-3.32, 12.875, 2.65, 6.64)
    # A four-millimetre root crosses the rear-face plane with finite area;
    # a tongue ending at X=0/Y=-8 only edge-touches the right bezel.
    root = box(0, -14.0, joint_z-4.0, 4.0, 7.3, 8.0)
    right = right.fuse(tongue).fuse(root).cut(bore).cut(head_recess.fuse(nut_clearance).fuse(nut_entry))
bez_l = add_part("PRINT_Bezel_Left", "PRINT Bezel - left half", left,
                 "Left frame half with two internal tongue receivers and captured joint nuts.",
                 "Rear face on bed", (0.88, 0.55, 0.16))
bez_r = add_part("PRINT_Bezel_Right", "PRINT Bezel - right half", right,
                 "Right frame half with two integrated clearance-fit tongues; no external seam plates.",
                 "Rear face on bed", (0.88, 0.55, 0.16))

# Retainers overlap the nominal PCB edge by 3.0 mm, retaining 1.5 mm at worst
# permitted lateral shift, while remaining 0.30 mm behind its rear face.
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
                 "PCB-edge rear stop with 3.0 mm nominal / 1.5 mm worst-shift overlap and 0.30 mm rear gap.",
                 "Outer side face on bed; PETG preferred", (0.35, 0.64, 0.84))
    retainers.append(r)

# The same rigid transform defines display visualization and every cradle contact plane.
pivot = App.Vector(0, 0, -D["outer_z"])
rot = App.Rotation(App.Vector(1, 0, 0), D["tilt_deg"])
assembly_place = App.Placement(App.Vector(0, 70, 94), rot, pivot)

# Cradle has hard bottom seats, rear support on the 3 mm outer rail, and front stops.
# A keyed crossbar ties both stands so they cannot spread; TPU is not in the load path.
def cradle(side):
    side_centers = [zc for ret_side, zc in retainer_centers if ret_side == side]
    if side < 0:
        base = box(-D["cradle_outer_x"], 0, 0,
                   D["cradle_outer_x"] - D["cradle_side_x0"], D["base_depth"], 8)
        seat = box(-128, -8, -88, 20, 13.05, 6)
        # Back plate stops 0.3 mm behind the hooks. A narrow contact strip reaches
        # the bezel rear plane, with local hook slots, while the back plate stays continuous.
        rear_back = box(-148, -13, -82, 23, 2.8, 142)
        rear_contact = box(-128, -10.3, -82, 3, 2.3, 142)
        for zc in side_centers:
            channel = box(-140.2, -13.2, zc - 6.2, 15.4, 5.5, 37.2)
            rear_back = rear_back.cut(channel)
            rear_contact = rear_contact.cut(channel)
        outer_web = box(-148, -12.8, -82, 6, 23.25, 20)
        front_bridge = box(-148, 5.05, -82, 40, 0.6, 20)
        front_stop = box(-128, 5.45, -82, 20, 5, 20)
        pocket = box(-116, 95, 2, 8, 16, 6.2)
    else:
        base = box(D["cradle_side_x0"], 0, 0,
                   D["cradle_outer_x"] - D["cradle_side_x0"], D["base_depth"], 8)
        seat = box(108, -8, -88, 20, 13.05, 6)
        rear_back = box(125, -13, -82, 23, 2.8, 142)
        rear_contact = box(125, -10.3, -82, 3, 2.3, 142)
        for zc in side_centers:
            channel = box(124.8, -13.2, zc - 6.2, 15.4, 5.5, 37.2)
            rear_back = rear_back.cut(channel)
            rear_contact = rear_contact.cut(channel)
        outer_web = box(142, -12.8, -82, 6, 23.25, 20)
        front_bridge = box(108, 5.05, -82, 40, 0.6, 20)
        front_stop = box(108, 5.45, -82, 20, 5, 20)
        pocket = box(108, 95, 2, 8, 16, 6.2)
    for window_side, z0, z1 in port_windows:
        if window_side == side:
            rear_contact = rear_contact.cut(box(-149, -14, z0, 298, 7, z1-z0))
    contact_structure = placed(
        seat.fuse(rear_back).fuse(rear_contact).fuse(outer_web).fuse(front_bridge).fuse(front_stop),
        assembly_place)
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

# Explicit screw/nut envelopes document axis, engagement, bearing and tip clearance.
hardware_shapes_source = []
hardware_shapes_asm = []
hardware_records = []
for (side, zc), retainer in zip(retainer_centers, retainers):
    if side < 0:
        screw = cylinder_axis(1.5, D["retainer_screw_len"], (-140, -1.5, zc), (1, 0, 0))
        head = cylinder_axis(D["m3_head_d"] / 2, D["m3_head_h"], (-143, -1.5, zc), (1, 0, 0))
        nut_center = (-130.625, -1.5, zc)  # seated on the outer-X pocket shoulder
        bearing_origin, bearing_dir = (-140, -1.5, zc), (1, 0, 0)
        nut_target = bez_l.Shape
    else:
        screw = cylinder_axis(1.5, D["retainer_screw_len"], (140, -1.5, zc), (-1, 0, 0))
        head = cylinder_axis(D["m3_head_d"] / 2, D["m3_head_h"], (143, -1.5, zc), (-1, 0, 0))
        nut_center = (130.625, -1.5, zc)
        bearing_origin, bearing_dir = (140, -1.5, zc), (-1, 0, 0)
        nut_target = bez_r.Shape
    nut = hex_prism("x", nut_center, D["m3_nut_t"], D["m3_nut_af"])
    # Nuts have an idealized minor-thread envelope equal to the screw shank;
    # mating threads are not meshed. Bolt and nut must not penetrate each other.
    bolt = screw.fuse(head)
    nut = nut.cut(screw)
    if bolt.common(nut).Volume > 0.001:
        raise RuntimeError("Bolt/nut envelope penetration")
    hw = bolt.fuse(nut)
    hardware_shapes_source.append(hw)
    hardware_shapes_asm.append(placed(hw, assembly_place))
    hardware_records.append(("retainer %s %s" % ("L" if side < 0 else "R", "low" if zc < 0 else "high"),
                             head, nut, retainer.Shape, nut_target, bearing_origin, bearing_dir))
    add_hardware("HARDWARE_Retainer_%s_%s" % ("L" if side < 0 else "R", "low" if zc < 0 else "high"),
                 "M3x12 retainer screw and DIN 934 nut", placed(hw, assembly_place))
for joint_z in joint_zs:
    screw = cylinder_axis(1.5, D["joint_screw_len"], (-10.0, -11.0, joint_z), (0, 1, 0))
    head = cylinder_axis(D["m3_head_d"]/2, D["m3_head_h"],
                         (-10.0, -14.0, joint_z), (0, 1, 0))
    nut = hex_prism("y", (-10.0, -7.7, joint_z), D["m3_nut_t"], D["m3_nut_af"])
    bolt = screw.fuse(head)
    nut = nut.cut(screw)
    if bolt.common(nut).Volume > 0.001:
        raise RuntimeError("Joint bolt/nut envelope penetration")
    hw = bolt.fuse(nut)
    hardware_shapes_source.append(hw)
    hardware_shapes_asm.append(placed(hw, assembly_place))
    hardware_records.append(("integrated joint %s" % ("lower" if joint_z < 0 else "upper"),
                             head, nut, bez_r.Shape, bez_l.Shape,
                             (-10.0, -11.0, joint_z), (0, 1, 0)))
    add_hardware("HARDWARE_Joint_%s" % ("Lower" if joint_z < 0 else "Upper"),
                 "M3x8 recessed integrated-joint screw and DIN 934 nut",
                 placed(hw, assembly_place))

# Verification is executable and fatal: reference, every printable pair, every
# hardware/printable pair, hardware pairs, seating, tool access and insertion path.
results = [
    "REFERENCE live _10_1CUN_ASM = 52 solids, %.6f mm^3" % full_obj.Shape.Volume,
    "REFERENCE excluded Part__Feature065 / AS-AG638A32M1-25 = 1 solid, %.6f mm^3, bounds %s" % (excluded_camera.Volume, expected_camera_bounds),
    "REFERENCE effective fit set = 51 solids, %.6f mm^3 plus LCD/glass envelopes" % current_reference.Volume,
]
source_fixed = [bez_l, bez_r] + retainers
for obj in source_fixed:
    vol = obj.Shape.common(full_reference).Volume
    results.append("REFERENCE %s = %.6f mm^3" % (obj.Name, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])
transformed_reference = placed(full_reference, assembly_place)
for obj in (stand_l, stand_r, crossbar_part):
    vol = obj.Shape.common(transformed_reference).Volume
    results.append("REFERENCE %s = %.6f mm^3" % (obj.Name, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])

assembly_print = []
for master in print_group.Group:
    shape = placed(master.Shape, assembly_place) if master.Name.startswith(("PRINT_Bezel", "PRINT_Retainer")) else master.Shape
    assembly_print.append((master.Name, shape))
for i, (name_a, shape_a) in enumerate(assembly_print):
    for name_b, shape_b in assembly_print[i + 1:]:
        vol = shape_a.common(shape_b).Volume
        results.append("PAIR %s vs %s = %.6f mm^3" % (name_a, name_b, vol))
        if vol > 0.001:
            raise RuntimeError(results[-1])

for hi, hw in enumerate(hardware_shapes_asm, 1):
    ref_vol = hw.common(transformed_reference).Volume
    results.append("HARDWARE %d vs reference = %.6f mm^3" % (hi, ref_vol))
    if ref_vol > 0.001:
        raise RuntimeError(results[-1])
    for part_name, part_shape in assembly_print:
        vol = hw.common(part_shape).Volume
        results.append("HARDWARE %d vs %s = %.6f mm^3" % (hi, part_name, vol))
        if vol > 0.001:
            raise RuntimeError(results[-1])
    for hj in range(hi, len(hardware_shapes_asm)):
        vol = hw.common(hardware_shapes_asm[hj]).Volume
        results.append("HARDWARE %d vs hardware %d = %.6f mm^3" % (hi, hj + 1, vol))
        if vol > 0.001:
            raise RuntimeError(results[-1])

# Measure intact annular head bearing and nut seating against their intended solids.
expected_bearing = math.pi * ((D["m3_head_d"] / 2) ** 2 - (D["m3_clear_d"] / 2) ** 2)
for label, head, nut, head_target, nut_target, origin, direction in hardware_records:
    outer = cylinder_axis(D["m3_head_d"] / 2, 0.02, origin, direction)
    inner = cylinder_axis(D["m3_clear_d"] / 2, 0.02, origin, direction)
    measured_area = outer.cut(inner).common(head_target).Volume / 0.02
    head_distance = head.distToShape(head_target)[0]
    nut_distance = nut.distToShape(nut_target)[0]
    seat_probe = nut.copy()
    axis = App.Vector(*direction)
    seat_probe.translate(axis.multiply(0.02 if label.startswith("integrated joint") else -0.02))
    nut_area = seat_probe.common(nut_target).Volume / 0.02
    # Full nut face minus the clearance bore must bear on the intended shoulder.
    expected_nut_area = math.sqrt(3)/2*D["m3_nut_af"]**2 - math.pi*(D["m3_clear_d"]/2)**2
    results.append("NUT BEARING %s %.3f / %.3f mm^2" % (label, nut_area, expected_nut_area))
    if nut_area < expected_nut_area - 0.05:
        raise RuntimeError(results[-1])
    results.append("SEATING %s head area %.3f/%.3f mm^2 distance %.6f mm; nut distance %.6f mm" %
                   (label, measured_area, expected_bearing, head_distance, nut_distance))
    if measured_area < expected_bearing - 0.05 or head_distance > 0.001 or nut_distance > 0.001:
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

# 3 mm-radius tool approach corridors are clear of all printables and reference.
tool_shapes = []
for side, zc in retainer_centers:
    tool = cylinder_axis(3.0, 20, (-163, -1.5, zc), (1, 0, 0)) if side < 0 else cylinder_axis(3.0, 20, (143, -1.5, zc), (1, 0, 0))
    tool_shapes.append(placed(tool, assembly_place))
for joint_z in joint_zs:
    tool_shapes.append(placed(cylinder_axis(3.0, 16, (-10.0, -30.0, joint_z), (0, 1, 0)), assembly_place))
for ti, tool in enumerate(tool_shapes, 1):
    obstruction = tool.common(transformed_reference).Volume
    for _, part_shape in assembly_print:
        obstruction += tool.common(part_shape).Volume
    for hw in hardware_shapes_asm:
        obstruction += tool.common(hw).Volume
    results.append("TOOL corridor %d obstruction = %.6f mm^3" % (ti, obstruction))
    if obstruction > 0.001:
        raise RuntimeError(results[-1])

# Exact linear swept-volume check. Cradle faces are planar: extruding every
# boundary face plus its initial solid covers the complete translational sweep.
framed_display = Part.makeCompound([transformed_reference] + hardware_shapes_asm +
    [shape for name, shape in assembly_print if name.startswith(("PRINT_Bezel", "PRINT_Retainer"))])
cradle_union = stand_l.Shape.fuse(stand_r.Shape).fuse(crossbar_part.Shape)
up = rot.multVec(App.Vector(0, 0, 25))
forward = rot.multVec(App.Vector(0, 15, 0))
for stage, start, vector in [("up25", App.Vector(), up), ("then_forward15", up, forward)]:
    moving = framed_display.copy()
    moving.translate(start)
    backwards = App.Vector(-vector.x, -vector.y, -vector.z)
    swept_cradle = Part.makeCompound([cradle_union] + [face.extrude(backwards) for face in cradle_union.Faces
                  if abs(face.normalAt(0, 0).dot(backwards)) > 1e-8])
    vol = moving.common(swept_cradle).Volume
    results.append("INSERTION continuous sweep %s obstruction = %.6f mm^3" % (stage, vol))
    if vol > 0.001:
        raise RuntimeError(results[-1])

panel_half_w = 117.5
panel_half_h = 71.5
max_shift_x = D["rear_cavity_x"] - D["pcb_x"]
max_shift_z = D["rear_cavity_z"] - D["pcb_z"]
min_lip_x = panel_half_w - D["ap_w"] / 2 - max_shift_x
min_lip_z = panel_half_h - D["ap_h"] / 2 - max_shift_z
worst_retainer_overlap = D["retainer_overlap"] - max_shift_x
results += [
    "CAPTURE PCB lateral clearance each side = %.2f mm" % max_shift_x,
    "CAPTURE minimum panel/aperture overlap after worst lateral shift = %.2f mm X, %.2f mm Z" % (min_lip_x, min_lip_z),
    "RETAINER nominal overlap = %.2f mm; worst-shift overlap = %.2f mm; rear gap = %.2f mm" %
    (D["retainer_overlap"], worst_retainer_overlap, D["retainer_gap"]),
    "CRADLE seat envelope per side = %.2f mm^2; actual bearing checked separately" % (20.0 * 13.05),
    "CRADLE source vertical transforms toward rear by %.2f mm over 164 mm rise (20 degrees)" %
    (164.0 * math.sin(math.radians(D["tilt_deg"]))),
    "FASTENER retainer: M3x12, 3.4 bore, 2.4 nut engagement, tip remains outside |X|=128",
    "JOINT two integrated 20 mm tongues; 0.30 mm non-bearing clearance; single lateral assembly path",
    "FASTENER joint: two M3x8 rear-access recessed screws with captured DIN 934 nuts",

]
if min_lip_x <= 0 or min_lip_z <= 0 or worst_retainer_overlap <= 0:
    raise RuntimeError("Capture is not positive at worst permitted shift")

# Separate bottom AND rear bearing witnesses, not merely minimum distance.
for side, stand in [(-1, stand_l), (1, stand_r)]:
    x0 = -128 if side < 0 else 125
    bottom = box(x0, -8, -82, 3, 10.05, 0.02)
    rear_witness = box(x0, -8, -70, 3, 0.02, 10)
    bezel = bez_l.Shape if side < 0 else bez_r.Shape
    for kind, witness in [("bottom", bottom), ("rear", rear_witness)]:
        area = witness.common(bezel).Volume / 0.02
        if area < 29.9:
            raise RuntimeError("Missing bezel bearing " + kind)
        w = witness.copy()
        w.translate(App.Vector(0, 0, -0.02) if kind == "bottom" else App.Vector(0, -0.02, 0))
        support_area = placed(w, assembly_place).common(stand.Shape).Volume / 0.02
        results.append("BEARING %s %s bezel %.3f / support %.3f mm^2" % (side, kind, area, support_area))
        if support_area < area-0.05:
            raise RuntimeError(results[-1])

# Joint geometry: quantify tongue section, receiver shell, clearance and single
# lateral assembly path. The 8 mm tongue has a deliberate nut-clearance pocket;
# the surrounding 11.6 mm receiver has over 2.4 mm Z ligament at the nut corners.
for joint_z, tongue in zip(joint_zs, tongues):
    z_ligament = 5.8 - (D["m3_nut_af"]+0.25)/math.sqrt(3)
    actual_tongue = tongue.common(bez_r.Shape)
    web = cylinder_axis(D["m3_head_d"]/2, 1.975, (-10, -11, joint_z), (0,1,0)).cut(
        cylinder_axis(D["m3_clear_d"]/2, 1.975, (-10, -11, joint_z), (0,1,0)))
    web_volume = web.common(bez_r.Shape).Volume
    root_witness = box(0, -8, joint_z-3.0, 4, 1.3, 6)
    root_volume = root_witness.common(bez_r.Shape).Volume
    results.append("JOINT %.1f head web 1.975 mm intact %.6f/%.6f mm^3; root %.6f/%.6f mm^3" %
                   (joint_z, web_volume, web.Volume, root_volume, root_witness.Volume))
    if web_volume < web.Volume-0.001 or root_volume < root_witness.Volume-0.001:
        raise RuntimeError(results[-1])
    results.append("JOINT %.1f tongue volume %.3f mm^3; Z ligament %.3f mm; clearance %.2f mm" %
                   (joint_z, actual_tongue.Volume, z_ligament, D["joint_clearance"]))
    if actual_tongue.Volume < tongue.Volume*0.55 or z_ligament < 2.4:
        raise RuntimeError(results[-1])
    # Exact swept volume from +X through final seating, including both preloaded
    # receiver nuts. Intended final face contact has zero intersection volume.
    moving = bez_r.Shape.copy()
    moving.translate(App.Vector(25,0,0))
    backwards = App.Vector(-25.0,0,0)
    swept = Part.makeCompound([moving] + [face.extrude(backwards) for face in moving.Faces
        if abs(face.normalAt(0,0).dot(backwards)) > 1e-8])
    joint_nuts = Part.makeCompound([record[2] for record in hardware_records[4:]])
    obstruction = swept.common(bez_l.Shape).Volume + swept.common(joint_nuts).Volume
    results.append("JOINT %.1f lateral pre-seat sweep obstruction %.6f mm^3" % (joint_z, obstruction))
    if obstruction > 0.001:
        raise RuntimeError(results[-1])
for i, (_, _, nut, _, _, _, direction) in enumerate(hardware_records):
    axis = "X" if i < 4 else "Y"
    bb = nut.BoundBox
    low, high = (bb.XMin, bb.XMax) if axis == "X" else (bb.YMin, bb.YMax)
    if i < 4:
        screw_low, screw_high = (-140, -140+D["retainer_screw_len"]) if i < 2 else (140-D["retainer_screw_len"],140)
    else:
        screw_low, screw_high = -11.0, -11.0+D["joint_screw_len"]
    engagement = min(high,screw_high)-max(low,screw_low)
    results.append("ENGAGEMENT hardware %d %.3f mm" % (i+1, engagement))
    if engagement < D["m3_nut_t"]-0.001:
        raise RuntimeError(results[-1])

# Side corridors from connector/switch faces to outside the assembly; conservative
# 6 mm rearward tool/plug envelope. Real plug shells/bend radii remain physical checks.
for side, z0, z1 in port_windows:
    corridor = box(-164.5 if side < 0 else 123.5, -10, z0+1, 40 if side < 0 else 41, 6, z1-z0-2)
    obstacle = sum(corridor.common(obj.Shape).Volume for obj in source_fixed)
    world = placed(corridor, assembly_place)
    obstacle += sum(world.common(obj.Shape).Volume for obj in (stand_l, stand_r, crossbar_part))
    results.append("PORT corridor side %d Z %.1f..%.1f obstruction %.6f mm^3" % (side,z0+1,z1-1,obstacle))
    if obstacle > 0.001:
        raise RuntimeError(results[-1])

# Actual retainer solids must overlap the worst-shift PCB edge projection.
for (side, zc), retainer in zip(retainer_centers, retainers):
    shift = -side * max_shift_x
    projection = box(-D["pcb_x"]+shift, -10, zc-6, 2*D["pcb_x"], 3.2, 12)
    overlap = retainer.Shape.common(projection).Volume / (3.2*12)
    results.append("MEASURED RETENTION side %d Z %.1f worst shift overlap %.3f mm" % (side,zc,overlap))
    if overlap < 1.5-0.001:
        raise RuntimeError(results[-1])

# Nuts are loaded before the display/screws. Check their complete linear paths
# through the rear openings, including hex corners, against the empty bezel.
for i, (_, _, nut, _, _, _, _) in enumerate(hardware_records):
    bb=nut.BoundBox
    center=((bb.XMin+bb.XMax)/2, (bb.YMin+bb.YMax)/2, (bb.ZMin+bb.ZMax)/2)
    envelope=hex_prism("x" if i<4 else "y", center, D["m3_nut_t"], D["m3_nut_af"])
    back=App.Vector(0,-20,0)
    sweep=Part.makeCompound([envelope]+[face.extrude(back) for face in envelope.Faces
              if abs(face.normalAt(0,0).dot(back))>1e-8])
    loading_target = frame if i < 4 else bez_l.Shape
    obstruction=sweep.common(loading_target).Volume
    results.append("NUT LOADING %d swept obstruction %.6f mm^3" % (i+1,obstruction))
    if obstruction>0.001:
        raise RuntimeError(results[-1])

# Validate each printable as one valid solid, within practical build axes; export at Z=0.
export_shapes = []
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
    bb2 = shp.BoundBox
    shp.translate(App.Vector(-bb2.XMin + 3, -bb2.YMin + 3, -bb2.ZMin))
    if abs(shp.BoundBox.ZMin) > 1e-6:
        raise RuntimeError("Export orientation is not on Z=0: " + master.Name)
    mesh = Mesh.Mesh(shp.tessellate(0.08))
    mb = mesh.BoundBox
    if (mesh.CountFacets == 0 or
            not all(math.isfinite(v) for v in bounds_tuple(mesh)) or
            abs(mb.ZMin)>1e-5 or max(mb.XLength,mb.YLength,mb.ZLength)>250.00001):
        raise RuntimeError("Invalid or oversized export mesh: " + master.Name)
    if not mesh.isSolid() or mesh.hasNonManifolds():
        results.append("WARNING MESH %s isSolid=%s; hasNonManifolds=%s; watertight/nonmanifold gate waived at explicit user request" %
                       (master.Name, mesh.isSolid(), mesh.hasNonManifolds()))
    export_shapes.append((master.Name, shp))
    results.append("EXPORT %s base Z=0.000000 mm" % master.Name)

# Publish only after every fatal check has passed.
# FreeCADCmd can leave the selected output directory empty before this script is
# evaluated. An empty directory contains no artifact to overwrite; populated
# destinations remain rejected above.
os.makedirs(OUT, exist_ok=True)
doc = App.newDocument(NAME, "ELCROW 10.1 V5 integrated-joint first fit")
params = doc.addObject("App::FeaturePython", "Design_Parameters")
params.addProperty("App::PropertyString", "Parameter_Status", "Documentation")
params.Parameter_Status = "Generation inputs, not live parametric drivers; rerun generator to rebuild"
for key, value in D.items():
    params.addProperty("App::PropertyFloat", key, "Generation inputs")
    setattr(params, key, value)
assembly = doc.addObject("App::DocumentObjectGroup", "Assembly")
prints = doc.addObject("App::DocumentObjectGroup", "Printable_Parts")
for item in print_group.Group:
    obj = doc.addObject("PartDesign::Feature", item.Name)
    obj.Label, obj.Shape = item.Label, item.Shape
    for key in ("Description", "Print_Orientation"):
        obj.addProperty("App::PropertyString", key, "Documentation")
        setattr(obj, key, getattr(item, key))
    prints.addObject(obj)
    obj.ViewObject.ShapeColor = item.Color
    link = doc.addObject("App::Link", "ASSEMBLY_" + item.Name[6:])
    link.LinkedObject, link.LinkTransform = obj, True
    if item in source_fixed:
        link.Placement = assembly_place
    assembly.addObject(link)
    obj.ViewObject.Visibility = False
for name, label, shape in hardware_items:
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label, obj.Shape = label, shape
    obj.ViewObject.ShapeColor = (0.72, 0.72, 0.76)
    assembly.addObject(obj)
for name, label, shape in [
    ("REFERENCE_Effective_51_Solids", "Effective fit reference: 51 retained real solids (camera excluded)", current_reference),
    ("REFERENCE_EXCLUDED_CAMERA", "EXCLUDED FROM FIT ONLY: Part__Feature065 / AS-AG638A32M1-25", excluded_camera),
    ("REFERENCE_LCD_ENVELOPE", "RECONSTRUCTED LCD envelope 235x143: NOT exact vendor geometry", lcd_envelope),
    ("REFERENCE_GLASS_ENVELOPE", "RECONSTRUCTED glass envelope 235x143: NOT exact vendor geometry", glass_envelope)]:
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label, obj.Shape = label, placed(shape, assembly_place)
    obj.ViewObject.ShapeColor = (0.20, 0.28, 0.36)
    obj.ViewObject.Transparency = 45 if "ENVELOPE" in name else 0
    obj.ViewObject.Visibility = name != "REFERENCE_EXCLUDED_CAMERA"
    assembly.addObject(obj)
report = doc.addObject("App::FeaturePython", "Measured_Checks")
report.addProperty("App::PropertyStringList", "Results", "Verification")
report.Results = results
for name, shape in export_shapes:
    mesh = Mesh.Mesh(shape.tessellate(0.08))
    mesh.write(os.path.join(OUT, name.replace("PRINT_", "") + ".stl"))
with open(os.path.join(OUT, "validation.txt"), "x") as f:
    f.write("\n".join(results) + "\n")
doc.recompute()
doc.saveAs(DOC_PATH)
import FreeCADGui as Gui
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
Gui.activeDocument().activeView().saveImage(os.path.join(ROOT, NAME + "_assembled.png"), 1600, 1200, "White")
print("\n".join(results))
print("SAVED " + DOC_PATH)
