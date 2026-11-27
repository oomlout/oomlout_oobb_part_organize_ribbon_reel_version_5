import copy
import oobb
import yaml
import os
import scad_help

def main(**kwargs):
    make_scad(**kwargs)

def make_scad(**kwargs):
    typ = scad_help.get_typ(**kwargs)
    oomp_mode = "project"
    #oomp_mode = "oobb"
    filt = ""
    build_variables = scad_help.get_build_variables(typ, filter=filt)
    if True:
        kwargs.setdefault("filter", build_variables["filter"])
        kwargs.setdefault("save_type", build_variables["save_type"])
        kwargs.setdefault("navigation", build_variables["navigation"])
        kwargs.setdefault("overwrite", build_variables["overwrite"])
        kwargs.setdefault("modes", build_variables["modes"])
        kwargs["oomp_mode"] = oomp_mode
        kwargs["oomp_run"] = build_variables["oomp_run"]
    parts = get_parts(kwargs, oomp_mode)
    
    kwargs["parts"] = parts

    scad_help.make_parts(**kwargs)

    if kwargs["navigation"]:
        import working_navigation
        working_navigation.main()

def get_parts(kwargs, oomp_mode):
    import working_cad
    parts = []    

    #load parts from parts/folder/working.yaml
    parts_directory = os.path.join(os.path.dirname(__file__), "parts")
    if not os.path.isdir(parts_directory):
        return parts

    for folder in os.listdir(parts_directory):
        folder_path = os.path.join(parts_directory, folder)
        if not os.path.isdir(folder_path):
            continue

        working_yaml_path = os.path.join(folder_path, "working.yaml")
        if not os.path.isfile(working_yaml_path):
            continue

        with open(working_yaml_path, "r", encoding="utf-8") as infile:
            loaded_part = yaml.safe_load(infile)

        if not isinstance(loaded_part, dict):
            continue

        oobb_details = loaded_part.get("oobb_details")
        if not isinstance(oobb_details, dict):
            continue

        if not working_cad.enabled(oobb_details, "scad"):
            continue
        part = loaded_part

        part_kwargs = copy.deepcopy(kwargs)
        part_kwargs.update(copy.deepcopy(loaded_part.get("kwargs", {})))
        part_kwargs.update(copy.deepcopy(oobb_details))
        for key in ("modes", "save_type", "overwrite", "filter", "navigation", "oomp_run"):
            if key in kwargs:
                part_kwargs[key] = copy.deepcopy(kwargs[key])
        part["kwargs"] = working_cad.geometry_parameters(part_kwargs)
        part["oobb_name"] = part.get("oobb_name", oobb_details.get("oobb_name", oobb_details.get("oobb_type", "default")))

        if oomp_mode == "oobb":
            part["kwargs"]["oomp_size"] = part["oobb_name"]

        parts.append(part)


    return parts

def get_base(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    


    #add plate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "positive"
        p3["shape"] = f"oobb_plate"    
        p3["depth"] = depth
        #p3["holes"] = True         uncomment to include default holes
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        oobb.append_full(thing,**p3)
    
    #add holes seperate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"oobb_holes"
        p3["both_holes"] = True  
        p3["depth"] = depth
        p3["holes"] = "perimeter"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)         
        p3["pos"] = pos1
        oobb.append_full(thing,**p3)

    #add a test screw_countersunk
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"screw_countersunk"
        p3["depth"] = depth
        p3["radius_name"] = "m3"
        pos1 = copy.deepcopy(pos)         
        pos1[2] += depth
        p3["pos"] = pos1
        p3["m"] = "#"
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

def get_hole_cover(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)                    
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")
    
    diameter = kwargs.get("diameter", 10)
    clearance = kwargs.get("clearance", 0.5)
    thickness_wall = 2
    depth_taper = 3
    depth_top = 2
    diameter_top_extra = 10
    radius_gap=6
    diameter_top_taper = 5

    #add cylinder
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "positive"
    p3["shape"] = f"oobb_cylinder"    
    dep = depth - depth_taper 
    p3["depth"] = dep
    p3["radius"] = (diameter-clearance)/2
    #p3["m"] = "#"
    pos1 = copy.deepcopy(pos)         
    pos1[2] += depth_taper + dep/2
    p3["pos"] = pos1
    oobb.append_full(thing,**p3)
    
    #add cylinder taper using radius_1 and radius_2
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "positive"
    p3["shape"] = f"oobb_cylinder"
    p3["depth"] = depth_taper
    p3["radius_2"] = (diameter-clearance)/2
    p3["radius_1"] = (diameter+clearance-thickness_wall)/2    
    #p3["m"] = "#"
    pos1 = copy.deepcopy(pos)
    pos1[2] += depth_taper/2
    p3["pos"] = pos1
    oobb.append_full(thing,**p3)

    #add top cylinder
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "positive"
    p3["shape"] = f"oobb_cylinder"
    p3["depth"] = depth_top
    dia = diameter+diameter_top_extra
    p3["radius_2"] = (dia-diameter_top_taper)/2
    p3["radius_1"] = (dia)/2
    #p3["m"] = "#"
    pos1 = copy.deepcopy(pos)
    pos1[2] += depth-depth_top/2
    p3["pos"] = pos1
    oobb.append_full(thing,**p3)

    

    #add hole
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "negative"
    p3["shape"] = f"oobb_cylinder"
    p3["depth"] = depth - depth_top/2
    p3["radius"] = (diameter+clearance-thickness_wall)/2    

    pos1 = copy.deepcopy(pos)
    pos1[2] += depth/2 - depth_top/2
    p3["pos"] = pos1
    #p3["m"] = "#"
    oobb.append_full(thing,**p3)

    
    #diameter_top 30
    #add hole_top
    diameter_top_hole = 30
    p3 = copy.deepcopy(kwargs)
    p3["type"] = "negative"
    p3["shape"] = f"oobb_cylinder"
    p3["depth"] = depth_top
    p3["radius"] = (diameter_top_hole)/2
    pos1 = copy.deepcopy(pos)
    pos1[2] += depth - depth_top/2

    p3["pos"] = pos1
    p3["m"] = "#"
    oobb.append_full(thing,**p3)

    pos1 = copy.deepcopy(pos)
    pos1[1] += 100



    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)

    
def get_plate(thing, **kwargs):

    prepare_print = kwargs.get("prepare_print", False)
    width = kwargs.get("width", 1)
    height = kwargs.get("height", 1)
    depth = kwargs.get("depth", 3)
    rot = kwargs.get("rot", [0, 0, 0])
    pos = kwargs.get("pos", [0, 0, 0])
    extra = kwargs.get("extra", "")



    #add plate
    if True:
        if width == 1 and height == 1:
            p3 = copy.deepcopy(kwargs)
            p3["type"] = "positive"
            p3["shape"] = f"oobb_plate"
            p3["depth"] = depth
            #p3["holes"] = True         uncomment to include default holes
            #p3["m"] = "#"
            pos1 = copy.deepcopy(pos)
            p3["pos"] = pos1
            oobb.append_full(thing,**p3)
        else:
            p3 = copy.deepcopy(kwargs)
            p3["type"] = "positive"
            p3["shape"] = f"oobb_rounded_rectangle_rounded"
            wid = (width *15)-1
            hei = (height *15)-1
            dep = depth
            size = [wid, hei, dep]
            p3["radius_rounded"] = 1.5
            p3["size"] = size
            #p3["holes"] = True         uncomment to include default holes
            #p3["m"] = "#"
            pos1 = copy.deepcopy(pos)
            p3["pos"] = pos1
            oobb.append_full(thing,**p3)

    #add holes seperate
    if True:
        p3 = copy.deepcopy(kwargs)
        p3["type"] = "p"
        p3["shape"] = f"oobb_holes"
        p3["both_holes"] = True
        p3["depth"] = depth
        p3["holes"] = "all"
        #p3["m"] = "#"
        pos1 = copy.deepcopy(pos)
        p3["pos"] = pos1
        oobb.append_full(thing,**p3)

    if prepare_print:
        scad_help.prepare_base_for_print(thing, pos, **kwargs)


def _screw_stations():
    pitch = oobb.gv("osp")
    return [(pitch, pitch / 2), (-pitch / 2, pitch), (-pitch, -pitch / 2), (pitch / 2, -pitch)]


def get_core(thing, **kwargs):
    import math

    depth = float(kwargs["depth"])
    radius = (float(kwargs["diameter"]) * oobb.gv("osp") - oobb.gv("osp_minus")) / 2
    nut_offset = 5.5
    boss_land = 9.9
    if depth < 2 * boss_land:
        raise ValueError("Core depth must be at least 19.8 mm for the nut pockets")
    origin = kwargs.get("pos", [0, 0, 0])
    inner = radius - 1.6

    def cylinder(target, typ, z, height, r1, r2=None, x=0, y=0):
        params = dict(type=typ, shape="oobb_cylinder", pos=[origin[0]+x, origin[1]+y, origin[2]+z],
                      depth=height, zz="bottom")
        if r2 is None:
            params["radius"] = r1
        else:
            params.update(radius_1=r1, radius_2=r2)
        oobb.append_full(target, **params)

    # The shell and end lands have a separate bore from the local bosses.
    shell = {"components": [], "components_objects": [], "components_string": []}
    cylinder(shell, "positive", 0, depth, radius)
    cylinder(shell, "negative", -0.1, 5.91, inner - 1)
    cylinder(shell, "negative", 5.8, 1, inner - 1, inner)
    cylinder(shell, "negative", 6.79, depth - 13.58, inner)  # overlap both taper cuts
    cylinder(shell, "negative", depth - 6.8, 1, inner, inner - 1)
    cylinder(shell, "negative", depth - 5.81, 5.91, inner - 1)
    thing["components"].append({"type": "rotation", "typetype": "positive", "pos": [0, 0, 0],
                                "rot": [0, 0, 0], "objects": shell["components"]})

    body = {"components": [], "components_objects": [], "components_string": []}
    for x, y in _screw_stations():
        cylinder(body, "positive", 0, depth, 5.2, x=x, y=y)
    middle = depth / 2
    transition = min(middle - boss_land, inner - 11.8)
    relief = 11.6 + transition
    cylinder(body, "negative", -0.1, boss_land + 0.11, 11.6)
    cylinder(body, "negative", boss_land, transition, 11.6, relief)
    if depth - 2 * (boss_land + transition) > 0:
        cylinder(body, "negative", boss_land + transition, depth - 2 * (boss_land + transition), relief)
    cylinder(body, "negative", depth - boss_land - transition, transition, relief, 11.6)
    cylinder(body, "negative", depth - boss_land - 0.01, boss_land + 0.11, 11.6)
    thing["components"].append({"type": "rotation", "typetype": "positive", "pos": [0, 0, 0],
                                "rot": [0, 0, 0], "objects": body["components"]})

    # The 1 mm web leaves the final 2 mm of each drive peg inside the core.
    for x in (-15,15):
        for y in (-15,15):
            for z in (-0.1,depth-2.2):
                cylinder(thing, "negative", z, 2.3, 3.25, x=x, y=y)

    for x, y in _screw_stations():
        # The nose of a flush countersunk head reaches through the thin web.
        cylinder(thing, "negative", -0.1, 0.8, 2.3, 1.75, x=x, y=y)
        cylinder(thing, "negative", depth-0.7, 0.8, 1.75, 2.3, x=x, y=y)
        angle = math.degrees(math.atan2(y, x)) + 30
        for mode in ("3dpr", "true", "laser"):
            nut_depth = oobb.gv("nut_depth_m3", mode)
            for z in (nut_offset, depth - nut_offset - nut_depth):
                oobb.append_full(thing, type="negative", shape="oobb_nut",
                    pos=[origin[0] + x, origin[1] + y, origin[2] + z],
                    rot=[0, 0, angle], radius_name="m3", mode=mode,
                    depth=nut_depth, zz="bottom", clearance="",
                    hole=False, overhang=True)
                # A separate channel keeps the full hex seat. Adding 0.02 mm
                # per side prevents coincident channel and hex faces on export.
                half_width = math.sqrt(3) * oobb.gv("nut_radius_m3", mode) / 2 + 0.02
                oobb.append_full(thing, type="negative", shape="polygon", inclusion=mode,
                    pos=[origin[0]+x, origin[1]+y, origin[2]+z], rot=[0,0,angle],
                    points=[[0,-half_width],[20,-half_width],[20,half_width],[0,half_width]],
                    height=nut_depth)
        oobb.append_full(thing, type="negative", shape="oobb_hole",
            pos=[origin[0] + x, origin[1] + y, origin[2] - 0.1],
            radius_name="m3", depth=depth + 0.2)



def get_end_cap(thing, **kwargs):
    width, height, depth = kwargs["width"], kwargs["height"], kwargs["depth"]
    if width != height:
        raise ValueError("End caps must be square")
    origin = kwargs.get("pos", [0, 0, 0])
    oobb.append_full(thing, type="positive", shape="oobb_plate", pos=list(origin),
                     width=width, height=height, depth=depth)
    # Keep the normal grid, omitting holes on the ribbon entry line.
    holes = {"components": [], "components_objects": [], "components_string": []}
    oobb.append_full(holes, type="negative", shape="oobb_holes", pos=list(origin),
                     width=width, height=height, depth=depth, holes="all", both_holes=True, radius_name="m6")
    core_radius = (3 * oobb.gv("osp") - oobb.gv("osp_minus")) / 2
    edge = (width * oobb.gv("osp") - oobb.gv("osp_minus")) / 2
    junction_x = edge - 15
    branch_length = 30
    pitch = oobb.gv("osp")
    outer_grid = (width - 1) * pitch / 2
    pending = list(holes["components"])
    while pending:
        item = pending.pop()
        if isinstance(item, list):
            pending.extend(item)
        else:
            x = item["pos"][0] - origin[0]
            y = item["pos"][1] - origin[1]
            on_entry = abs(y) < 0.001 and x >= core_radius
            # Leave the branch and the two M3 positions beyond its end solid.
            radius = item.get("r", 0)
            nearest_y = min(max(y, 0), branch_length + 15)
            on_branch = (x - junction_x) ** 2 + (y - nearest_y) ** 2 <= (radius + 0.75) ** 2
            corner = abs(x - outer_grid) < 0.001 and abs(y - outer_grid) < 0.001
            clear_quadrant_hole = x >= outer_grid - pitch - 0.001 and y >= 0 and not corner
            overlaps_centre = x * x + y * y < (8.5 + radius) ** 2
            if not on_entry and not on_branch and not clear_quadrant_hole and not overlaps_centre:
                thing["components"].append(item)

    oobb.append_full(thing, type="negative", shape="oobb_cylinder",
                     pos=[origin[0], origin[1], origin[2] - 0.1],
                     zz="bottom", radius=8.5, depth=depth + 0.2)

    slot_length = edge - core_radius + 1
    oobb.append_full(thing, type="negative", shape="oobb_cube_center",
                     pos=[origin[0] + core_radius + slot_length / 2, origin[1], origin[2] - 0.1],
                     size=[slot_length, 1.5, depth + 0.2])
    # The diamond is an enlarged junction between the entry and the side branch.
    diamond_length = 5
    diamond_width = 5
    for diamond_middle in (junction_x, edge):
        oobb.append_full(thing, type="negative", shape="polygon",
                         pos=[origin[0] + diamond_middle, origin[1], origin[2] - 0.1],
                         points=[[-diamond_length / 2, 0], [0, -diamond_width / 2],
                                 [diamond_length / 2, 0], [0, diamond_width / 2]],
                         height=depth + 0.2)
    oobb.append_full(thing, type="negative", shape="oobb_cube_center",
                     pos=[origin[0] + junction_x, origin[1] + branch_length / 2, origin[2] - 0.1],
                     size=[1.5, branch_length, depth + 0.2])
    stations = _screw_stations()
    stations += [(x, -y) for x, y in stations]
    for x, y in stations:
        oobb.append_full(thing, type="negative", shape="oobb_screw_countersunk",
            pos=[origin[0]+x, origin[1]+y, origin[2]+depth], radius_name="m3",
            depth=depth, zz="top", hole=True, nut_include=False, overhang=False)



def get_gridfinity_end(thing, **kwargs):
    from working_gridfinity import ROOT
    oobb.append_full(thing, type="positive", shape="raw_scad",
                     source=(ROOT / "source_file/gridfinity_end.scad").read_text(encoding="utf-8"),
                     module="gridfinity_end", pos=kwargs.get("pos", [0, 0, 0]),
                     module_kwargs={"n": kwargs["cells"], "side": kwargs["side"], "web": kwargs["web"]})


def get_drive_gear(thing, **kwargs):
    origin = kwargs.get("pos", [0, 0, 0])
    shaft_length = kwargs.get("shaft_length", 30)
    plate_depth = kwargs.get("depth", 6)
    plate_z = origin[2]
    top_z = plate_z + plate_depth

    oobb.append_full(thing, type="positive", shape="oobb_cylinder",
                     pos=[origin[0], origin[1], top_z], zz="bottom", depth=shaft_length,
                     radius=kwargs.get("shaft_diameter", 15) / 2)
    oobb.append_full(thing, type="positive", shape="oobb_plate",
                     pos=[origin[0], origin[1], plate_z],
                     width=kwargs["width"], height=kwargs["height"], depth=plate_depth)

    spacing = oobb.gv("osp")
    for x in (-spacing, spacing):
        for y in (-spacing, spacing):
            peg_pos = [origin[0] + x, origin[1] + y, top_z]
            oobb.append_full(thing, type="positive", shape="oobb_cylinder",
                             pos=peg_pos, zz="bottom", depth=1.5, radius=2.75)
            oobb.append_full(thing, type="positive", shape="oobb_cylinder",
                             pos=[peg_pos[0], peg_pos[1], top_z + 1.5], zz="bottom",
                             depth=1.5, radius_1=2.75, radius_2=1.25)

    for x, y in ((spacing, 0), (-spacing, 0), (0, spacing), (0, -spacing)):
        oobb.append_full(thing, type="negative", shape="oobb_hole", radius_name="m6",
                         pos=[origin[0] + x, origin[1] + y, plate_z - 0.1],
                         depth=plate_depth + 0.2)

    half_pitch = spacing / 2
    for x in (-spacing, spacing):
        for y in (-half_pitch, half_pitch):
            for dx, dy in ((x, y), (y, x)):
                oobb.append_full(thing, type="negative", shape="oobb_screw_countersunk",
                                 radius_name="m3", depth=plate_depth, zz="top",
                                 pos=[origin[0] + dx, origin[1] + dy, top_z],
                                 hole=True, nut_include=False, overhang=False)

    oobb.append_full(thing, type="negative", shape="oobb_hole", radius_name="m6",
                     pos=[origin[0], origin[1], origin[2] - 0.1],
                     depth=shaft_length + plate_depth + 0.2)
    # Open the nut pocket at the end of the shaft.
    oobb.append_full(thing, type="negative", shape="oobb_nut", radius_name="m6",
                     pos=[origin[0], origin[1], top_z + shaft_length], zz="top", overhang=True)
    # A second nut can be inserted from the underside of the plate.
    for mode in ("3dpr", "true", "laser"):
        oobb.append_full(thing, type="negative", shape="oobb_nut", radius_name="m6",
                         pos=list(origin), zz="bottom", mode=mode,
                         depth=oobb.gv("nut_depth_m6", mode), overhang=True)



if __name__ == '__main__':
    main()



