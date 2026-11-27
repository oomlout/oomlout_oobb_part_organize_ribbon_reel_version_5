"""Exercise the production meshes and export small, printable interface trials."""
import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

import manifold3d as md
import numpy as np
import trimesh

from working_gridfinity import DEPTHS, GEAR, ROOT, core, mesh_path, plate, WEB, FOOT, RIM, STACK_SPACING, GEAR_FACE, GEAR_THICKNESS

SEATED = STACK_SPACING
ROOT_FIT = ROOT / "design_stages"
FLIP = (180, 0, 0)


def solid(path):
    mesh = trimesh.load_mesh(path)
    if not mesh.is_volume or mesh.body_count != 1:
        raise ValueError(f"Expected one watertight body in {path}")
    shape = md.Manifold(md.Mesh64(mesh.vertices.astype(float), mesh.faces.astype("uint64")))
    if shape.status() != md.Error.NoError:
        raise ValueError(f"Invalid solid in {path}: {shape.status()}")
    return shape


def export_scad(folder, name, contents, printable=False):
    scad = folder / (name + ".scad")
    scad.write_text(contents + "\n", encoding="utf-8")
    if printable:
        stl = scad.with_suffix(".stl")
        temp = stl.with_suffix(".tmp.stl")
        subprocess.run([shutil.which("openscad.com") or "openscad", "--export-format", "binstl",
                        "-o", str(temp), str(scad)], check=True, capture_output=True)
        solid(temp)
        temp.replace(stl)
    return scad


def run_size(n):
    folder = ROOT_FIT / f"{n}x{n}"
    folder.mkdir(parents=True, exist_ok=True)
    ids = {"plug": plate(n, "plug"), "socket": plate(n, "socket"), "gear": GEAR,
           **{f"core{d}": core(d) for d in DEPTHS}}
    shapes = {key: solid(mesh_path(identifier)) for key, identifier in ids.items()}
    modules = "\n".join(f'module {key}() {{ import("{Path(os.path.relpath(mesh_path(identifier), folder)).as_posix()}"); }}'
                        for key, identifier in ids.items())
    (folder / "models.scad").write_text(modules, encoding="utf-8")
    preamble = "use <models.scad>;\n"
    # Use the outer corner so the coupon captures both legs of the perimeter rim.
    c = -(n - 1) * 21
    for side in ("plug", "socket"):
        for name, crop in [("corner", f"translate([{c-21},{c-21},-1]) cube([42,42,17]);"),
                           ("gear_seat", "translate([-25,-25,-1]) cube([50,50,17]);")]:
            export_scad(folder, f"{name}_{side}", preamble +
                        f"intersection() {{ {side}(); {crop} }}", True)
    plug_gear_z = GEAR_FACE["plug"] + GEAR_THICKNESS
    export_scad(folder, "gear_seated", preamble +
                f'color("turquoise") plug(); color("dimgray") translate([0,0,{plug_gear_z}]) rotate([180,0,0]) gear();')
    stack = f'color("turquoise") socket(); color("gray") translate([0,0,{SEATED}]) rotate([180,0,0]) plug();'
    export_scad(folder, "stack_section", preamble + "difference() { union() { " + stack +
                " } translate([0,-100,-2]) cube([100,200,30]); }")
    export_scad(folder, "reel_exploded", preamble +
                'rotate([180,0,0]) plug(); translate([0,0,8]) core25(); '
                'translate([0,0,42]) socket(); translate([0,0,66]) rotate([180,0,0]) gear();')

    export_scad(folder, "stacked_reels", preamble + f"""
// Two 25 mm reels with the removable drives lifted off for stacking.
color("teal") {{
    translate([0,0,-25]) rotate([180,0,0]) plug();
    socket();
    translate([0,0,{SEATED}]) rotate([180,0,0]) plug();
    translate([0,0,{SEATED+25}]) socket();
}}
color("dimgray") {{
    translate([0,0,-25]) core25();
    translate([0,0,{SEATED}]) core25();
}}""")
    checks = {}
    def interference(name, first, second, required=False):
        volume = abs((first ^ second).volume())
        if (required and volume < 0.01) or (not required and volume > 0.0001):
            raise ValueError(f"{name}: unexpected overlap {volume:.6f} mm3")
        checks[name] = round(volume, 6)

    plug, socket = shapes["plug"], shapes["socket"]
    for side in ("plug", "socket"):
        body = shapes[side]
        face = GEAR_FACE[side]
        gear = shapes["gear"].rotate(FLIP).translate((0,0,face+GEAR_THICKNESS))
        expected_height = WEB + (FOOT if side=="plug" else RIM)
        if abs(body.bounding_box()[5]-expected_height)>1e-5:
            raise ValueError(f"Unexpected {side} plate height")
        # Measure the slit in the web at the edge and again past the diamond.
        edge = n*21-0.25
        for inset, width in [(0.05,4.9),(2.0,1.5)]:
            hits = body.ray_cast((edge-inset,-4,WEB/2),(edge-inset,4,WEB/2))
            ys = [hit.position[1] for hit in hits]
            if not np.allclose(ys,[-width/2,width/2],atol=0.002):
                raise ValueError(f"{side} ribbon guide at {inset} mm: {ys}")
        if side=="socket":
            # Across an interior cell boundary the socket has only its web.
            hits = body.ray_cast((c+21,c+7,-1),(c+21,c+7,8))
            if not np.allclose([h.position[2] for h in hits],[0,WEB]):
                raise ValueError("Unexpected interior socket rib")
        interference(side + "_gear_seated", body, gear)
        interference(side + "_gear_overtravel_0.1mm", body, gear.translate((0,0,-0.1)), True)
        interference(side + "_gear_rotated_12deg", body, gear.rotate((0,0,12)), True)
        for x in (-15,15):
            for y in (-15,15):
                # Each peg must engage the material below the operating face.
                length = min(3,face)
                bore = md.Manifold.cylinder(length, 3.25, circular_segments=64).translate((x,y,face-length))
                interference(f"{side}_open_bore_{x}_{y}", body, bore)
                interference(f"{side}_peg_engagement_{x}_{y}", gear, bore, True)
        hits = body.ray_cast((c+21,c-4,-1), (c+21,c-4,17))
        zs = [hit.position[2] for hit in hits]
        if not np.allclose(zs, [0,1], atol=1e-5):
            raise ValueError(f"{side} ribbon web at sample: {zs}")
        for depth in DEPTHS:
            # Core runs away from the seated drive, along negative Z.
            drum = shapes[f"core{depth}"].translate((0,0,-depth))
            opposite = shapes["socket" if side=="plug" else "plug"].rotate(FLIP).translate((0,0,-depth))
            interference(f"{side}_shaft_core_{depth}", gear, drum)
            interference(f"{side}_shaft_far_plate_{depth}", gear, opposite)
    rotated = plug.rotate(FLIP)
    for angle in (0,90,180,270):
        seated = rotated.rotate((0,0,angle)).translate((0,0,SEATED))
        interference(f"stack_at_{angle}deg", socket, seated)
        interference(f"stack_axial_stop_{angle}deg", socket, seated.translate((0,0,-0.1)), True)
        for axis, offset in [("x",(1,0,0)), ("y",(0,1,0))]:
            interference(f"stack_lateral_stop_{axis}_{angle}deg",socket,seated.translate(offset),True)
    # Independent full Gridfinity foot and baseplate from the reference dimensions.
    ref = (ROOT / "source_file/gridfinity_gauge.scad").read_text()
    ref_path = export_scad(folder, "reference_baseplate", ref + f"\nreference_plate({n});", True)
    interference("reference_baseplate", solid(ref_path.with_suffix(".stl")), rotated.translate((0,0,WEB+FOOT)))
    ref_path = export_scad(folder, "reference_bin_base", ref + f"\nreference_base({n});", True)
    interference("reference_bin_base", socket, solid(ref_path.with_suffix(".stl")).translate((0,0,WEB)))
    hardware = ROOT_FIT / "hardware"
    hardware.mkdir(exist_ok=True)
    for name in ("nut","screw"):
        source = (ROOT / "source_file/reel_hardware.scad").read_text()
        export_scad(hardware, name, source + f"\n{name}();", True)
    nut = solid(hardware/"nut.stl")
    screw = solid(hardware/"screw.stl")
    for x,y in [(15,7.5),(-7.5,15),(-15,-7.5),(7.5,-15)]:
        angle = math.degrees(math.atan2(y,x))+30
        axis = math.radians(angle)
        for depth in DEPTHS:
            drum = shapes[f"core{depth}"]
            for z in (5.8, depth-8.2):
                installed = nut.rotate((0,0,angle)).translate((x,y,z))
                start = installed.translate((12*math.cos(axis),12*math.sin(axis),0))
                # Convex external nut envelope swept over the entire insertion path.
                sweep = md.Manifold.batch_hull([installed,start])
                interference(f"nut_path_{depth}_{x}_{y}_{z:g}", drum, sweep)
            interference(f"screw_to_core_{depth}_{x}_{y}",drum,screw.translate((x,y,-WEB)))
        for side in ("plug","socket"):
            interference(f"countersink_{side}_{x}_{y}",shapes[side],
                         screw.rotate(FLIP).translate((x,y,WEB)))
            gear = shapes["gear"].rotate(FLIP).translate((0,0,GEAR_FACE[side]+GEAR_THICKNESS))
            interference(f"gear_hardware_{side}_{x}_{y}",gear,screw.rotate(FLIP).translate((x,y,WEB)))
    report = dict(size=n, footprints_mm=[n*42-.5]*2, measured_web_mm=1.0,
                  plug_total_mm=WEB+FOOT, socket_total_mm=WEB+RIM, diamond_mouth_mm=5, slit_mm=1.5,
                  seated_ribbon_plane_separation_mm=SEATED, intersection_volumes_mm3=checks,
                  sha256={key:hashlib.sha256(mesh_path(v).read_bytes()).hexdigest() for key,v in ids.items()})
    (folder / "fit_report.json").write_text(json.dumps(report,indent=2)+"\n")


def main():
    for n in (2,3):
        run_size(n)


if __name__ == "__main__":
    main()

