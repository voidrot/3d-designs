"""Generate the first-fit ELCROW 10.1 bezel and 20 degree cradle in FreeCAD.
Run inside FreeCAD's Python console or through the FreeCAD MCP server.
This script only creates ELCROW_10_1_Dev_Frame_FirstFit.FCStd and exports/ELCROW_10_1_Dev_Frame_FirstFit/*.stl.
"""
import FreeCAD as App, Part, Mesh, os, math

ROOT = "/home/buck/Projects/voidrot/3d-designs/ELCROW-10.1-Dev-Frame"
OUT = os.path.join(ROOT, "exports", "ELCROW_10_1_Dev_Frame_FirstFit")
DOC_PATH = os.path.join(ROOT, "ELCROW_10_1_Dev_Frame_FirstFit.FCStd")
os.makedirs(OUT, exist_ok=True)
NAME = "ELCROW_10_1_Dev_Frame_FirstFit"
old = App.listDocuments().get(NAME)
if old:
    App.closeDocument(NAME)
doc = App.newDocument(NAME, "ELCROW 10.1 Dev Frame First Fit")

# Fit dimensions in the vendor STEP coordinate system: X horizontal, Z vertical, front +Y.
D = {
    "panel_w": 235.0, "panel_h": 143.0, "pcb_w": 247.0, "pcb_h": 147.0,
    "clear_x": 125.0, "clear_z": 75.0, "outer_x": 128.0, "outer_z": 82.0,
    "ap_w": 225.0, "ap_h": 129.0, "front_gap": 0.05, "rear_gap": 0.30,
    "tilt": 20.0, "base_depth": 150.0,
}
params = doc.addObject("App::FeaturePython", "Design_Parameters")
params.Label = "Design Parameters (mm / degrees)"
for key, value in D.items():
    params.addProperty("App::PropertyFloat", key, "Fit dimensions")
    setattr(params, key, value)
params.addProperty("App::PropertyString", "Purpose", "Documentation")
params.Purpose = "FIRST-FIT ONLY: dimensions derive from supplied STEP; verify physical panel perimeter, visible aperture, connector and flex clearances before printing."

print_group = doc.addObject("App::DocumentObjectGroup", "Printable_Parts")
print_group.Label = "PRINTABLE PARTS (source-coordinate masters)"
assembly = doc.addObject("App::DocumentObjectGroup", "Assembled_20deg_Cradle")
assembly.Label = "ASSEMBLED 20 degree cradle (links/copy)"
checks = doc.addObject("App::DocumentObjectGroup", "Verification")

# Basic geometric helpers. Boxes use FreeCAD XYZ where Y is display depth.
def box(x, y, z, dx, dy, dz):
    return Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
def add_part(name, label, shape, group, color, desc):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Label = label
    obj.Shape = shape.removeSplitter()
    obj.addProperty("App::PropertyString", "Print_Material", "Print")
    obj.addProperty("App::PropertyString", "Print_Orientation", "Print")
    obj.addProperty("App::PropertyString", "Description", "Documentation")
    obj.Description = desc
    obj.ViewObject.ShapeColor = color
    group.addObject(obj)
    return obj

def xsplit(shape, left=True):
    # split at X=0; right includes no accidental overlap.
    return shape.common(box(-140 if left else 0, -30, -100, 140 if left else 140, 80, 220))

# Bezel: rear perimeter rail clears PCB (x +/-125, z +/-75), a 0.05 mm front gap,
# and a 225 x 129 aperture which stays outside the inferred 222.72 x 125.28 visible area.
rear = box(-128, -8, -82, 256, 10.05, 164).cut(box(-125, -9, -75, 250, 11.15, 150))
front = box(-128, 2.05, -82, 256, 3.0, 164).cut(box(-112.5, 1.5, -64.5, 225, 5.0, 129))
frame = rear.fuse(front)
# Open the central top flex corridor. This intentionally removes top retention only over the known tails.
flex_relief = box(-28, -10, 68, 86, 25, 30)
frame = frame.cut(flex_relief)
# The top seam remains an unencumbered butt seam: a tongue there would cross the known LCD flex corridor.
# A bottom tongue plus the removable lower seam lock provides the mechanical registration.
left = xsplit(frame, True).fuse(box(0, -8, -82, 12, 13.05, 7))
right = xsplit(frame, False).cut(box(0, -8.1, -82.1, 12.2, 13.3, 7.2))
bez_l = add_part("PRINT_Bezel_Left", "PRINT Bezel — left half", left, print_group, (0.85,0.55,0.15), "Left half of split front bezel; bottom tongue locates the seam while the top stays clear of flex.")
bez_r = add_part("PRINT_Bezel_Right", "PRINT Bezel — right half", right, print_group, (0.85,0.55,0.15), "Right half of split front bezel; bottom tongue pocket receives left-half tongue.")
for o in (bez_l, bez_r):
    o.Print_Material="PLA or PETG"; o.Print_Orientation="Lay rear face on build plate; no brim required by footprint." 

# Lower seam lock plate, below electronics perimeter. Two M3 x 10 screws into heat-set inserts in bottom rail.
join = box(-24, -8, -87, 48, 4, 5)
for x in (-14, 14):
    cyl = Part.makeCylinder(1.7, 8, App.Vector(x,-6,-89), App.Vector(0,0,1))
    join = join.cut(cyl)
joiner = add_part("PRINT_Lower_Seam_Lock", "PRINT Lower seam lock", join, print_group, (0.65,0.65,0.70), "Rear-bottom bridge locks split bezel; uses 2 M3 x 10 screws and two M3 heat-set inserts.")
joiner.Print_Material="PLA or PETG"; joiner.Print_Orientation="Flat, large face on build plate."

# Four non-compressive rear hooks; locations intentionally avoid the supplied connector zones.
def retainer(side, zc, name):
    # Exterior mount block and rear hook. Hook face stops 0.30 mm behind nominal PCB rear at Y=-6.5.
    if side < 0:
        mount = box(-132, -8, zc-6, 4, 13.05, 12)
        hook = box(-128, -10, zc-6, 4.2, 3.2, 12)
    else:
        mount = box(128, -8, zc-6, 4, 13.05, 12)
        hook = box(123.8, -10, zc-6, 4.2, 3.2, 12)
    return add_part(name, "PRINT rear retainer " + name.split('_')[-1], mount.fuse(hook), print_group, (0.40,0.65,0.85), "Non-compressive rear travel stop; nominal 0.30 mm rear clearance. Mount with one M3 x 6 thread-forming screw into exterior bezel rail.")
rets=[]
for side, zc, suffix in [(-1,-45,"L_lower"),(-1,48,"L_upper"),(1,-45,"R_lower"),(1,48,"R_upper")]:
    r=retainer(side,zc,"PRINT_Retainer_"+suffix); r.Print_Material="PETG preferred"; r.Print_Orientation="Mount face on build plate"; rets.append(r)

# Two fixed-angle side cradles. Their inner faces support bezel exterior only, never glass/PCB.
def stand_shape(x):
    # 11.4 mm wide: its inner hard face stops 0.6 mm from the bezel exterior;
    # optional 0.8 mm TPU pads bridge this deliberately small non-hard contact gap.
    base = box(x, 0, 0, 11.4, 150, 12)
    # Extruded Y/Z wedge; upper line is parallel to display back at 20 degrees from vertical.
    # Profile begins on the base top so the fused solid shares only a face with the base.
    pts=[App.Vector(x,0,12),App.Vector(x,150,12),App.Vector(x,72,20),App.Vector(x,22,168),App.Vector(x,12,168)]
    wire=Part.makePolygon(pts+[pts[0]])
    face=Part.Face(wire)
    wedge=face.extrude(App.Vector(11.4,0,0))
    # Front stop lies in front of the lower bezel exterior after assembly, with 0.6 mm nominal pad gap.
    stop=box(x, 75, 12, 11.4, 10, 18)
    return base.fuse(wedge).fuse(stop)
stand_l=add_part("PRINT_Cradle_Left", "PRINT fixed-angle cradle — left", stand_shape(-140), print_group, (0.25,0.60,0.35), "Left 20 degree fixed-angle side cradle; base footprint 150 mm deep.")
stand_r=add_part("PRINT_Cradle_Right", "PRINT fixed-angle cradle — right", stand_shape(128.6), print_group, (0.25,0.60,0.35), "Right 20 degree fixed-angle side cradle; base footprint 150 mm deep.")
for o in (stand_l,stand_r): o.Print_Material="PLA or PETG"; o.Print_Orientation="Print as modeled: base on build plate, vertical side wedge." 
# Optional adhesive TPU pads — no structural claim.
pad_shapes=[box(-128.6,75,12,0.8,10,18),box(127.8,75,12,0.8,10,18),box(-128.6,60,16,0.8,12,12),box(127.8,60,16,0.8,12,12)]
for i, shp in enumerate(pad_shapes,1):
    p=add_part("PRINT_TPU_Pad_%d"%i,"OPTIONAL TPU contact pad %d"%i,shp,print_group,(0.2,0.2,0.2),"Optional 1 mm TPU/foam pad, adhesive-backed; position only after physical fit check.")
    p.Print_Material="TPU or foam"; p.Print_Orientation="Flat"

# Import-copy compound remains non-printable and preserves the source geometry. No source object is modified.
src=App.getDocument("ELCROW_P4_10_1_STEP_REFERENCE_20251230")
if not src: raise RuntimeError("Required reference document is not open: ELCROW_P4_10_1_STEP_REFERENCE_20251230")
ref_shapes=[]
for n in ("Part__Feature","Part__Feature006","Part__Feature009"):
    obj=src.getObject(n)
    if not obj or obj.Shape.isNull(): raise RuntimeError("Reference shape missing or null: "+n)
    ref_shapes.append(obj.Shape.copy())
ref=doc.addObject("PartDesign::Feature","ASSEMBLY_REFERENCE_IMPORTED_COPY")
ref.Label="ASSEMBLY imported STEP copy (LCD/touch/PCB/flex)"
ref.Shape=Part.makeCompound(ref_shapes)
ref.addProperty("App::PropertyString","Source_Document","Documentation"); ref.Source_Document="ELCROW_P4_10_1_STEP_REFERENCE_20251230.FCStd (read-only source)"
ref.ViewObject.ShapeColor=(0.70,0.75,0.85); ref.ViewObject.Transparency=70
assembly.addObject(ref)

# Assembly links for printable masters, matching the reference rotation about bottom exterior center.
pivot=App.Vector(0,0,-82)
rot=App.Rotation(App.Vector(1,0,0),20)
place=App.Placement(App.Vector(0,70,94),rot,pivot) # transforms source bottom z=-82 to Z=12
# Equivalent expression confirms net translation, but Placement center keeps the source coordinate relationship explicit.
for master in print_group.Group:
    link=doc.addObject("App::Link","ASSEMBLY_"+master.Name[6:])
    link.Label="ASSEMBLY "+master.Label.replace("PRINT ","")
    link.LinkedObject=master
    link.LinkTransform=True
    # Cradles and optional pads are already laid out on the Z=0 assembly floor.
    link.Placement=App.Placement() if master.Name.startswith("PRINT_Cradle") or master.Name.startswith("PRINT_TPU") else place
    assembly.addObject(link)
ref.Placement=place
# Masters hidden: assembly links are the assembly view; masters still export separately.
for master in print_group.Group: master.ViewObject.Visibility=False

# Explicit collision and print-bound checks. Collision is measured in source coordinates because rigid assembly transform preserves it.
bezel_union=bez_l.Shape.fuse(bez_r.Shape)
pcb=src.getObject("Part__Feature009").Shape
touch=src.getObject("Part__Feature006").Shape
lcd=src.getObject("Part__Feature").Shape
results=[]
for nm, sh in [("PCB",pcb),("Touch",touch),("LCD_and_flex",lcd)]:
    vol=bezel_union.common(sh).Volume
    results.append("bezel vs %s = %.6f mm^3"%(nm,vol))
# Retainers deliberately have near-rail nominal gaps; report their nominal geometry separately, not as a waived collision.
for master in print_group.Group:
    bb=master.Shape.BoundBox
    ok=max(bb.XLength,bb.YLength,bb.ZLength) <= 250.0
    results.append("%s bbox %.2f x %.2f x %.2f mm : %s"%(master.Name,bb.XLength,bb.YLength,bb.ZLength,"PASS" if ok else "FAIL"))
report=doc.addObject("App::FeaturePython","Measured_Checks")
report.Label="Measured checks (generated)"
report.addProperty("App::PropertyStringList","Results","Verification")
report.Results=results
report.addProperty("App::PropertyString","Collision_Note","Verification")
report.Collision_Note="Zero-volume bezel checks are required. Flex relief is intentionally cut x=-28..58, z>=68 to keep both known flex tails open. Retainer nominal rear gap: 0.30 mm; not a measured physical fit."
checks.addObject(report)
print("\n".join(results))
if any("FAIL" in r for r in results): raise RuntimeError("A printable part exceeds the 250 mm practical build limit")
if any(float(r.rsplit("= ",1)[1].split()[0]) > 0.001 for r in results[:3]): raise RuntimeError("Unexpected bezel/reference collision; inspect before using design")

# STL exports: physically place each part's stated print face on Z=0 (not merely centered in the slicer).
for master in print_group.Group:
    shp=master.Shape.copy()
    if master.Name.startswith("PRINT_Bezel"):
        shp.rotate(App.Vector(), App.Vector(1,0,0), -90)  # rear Y face becomes the print face
    elif master.Name.startswith("PRINT_Retainer") or master.Name.startswith("PRINT_TPU"):
        shp.rotate(App.Vector(), App.Vector(0,1,0), 90)   # broad X-side face becomes the print face
    bb=shp.BoundBox
    shp.translate(App.Vector(-bb.XMin+5, -bb.YMin+5, -bb.ZMin))
    temp=doc.addObject("Part::Feature","EXPORT_TEMP")
    temp.Shape=shp
    path=os.path.join(OUT, master.Name.replace("PRINT_","")+".stl")
    Mesh.export([temp], path)
    doc.removeObject(temp.Name)

# Save only this new document; do not save or close the reference document.
doc.recompute()
doc.saveAs(DOC_PATH)
Gui.activeDocument().activeView().viewAxonometric()
Gui.activeDocument().activeView().fitAll()
print("SAVED "+DOC_PATH)
print("EXPORTED "+OUT)
