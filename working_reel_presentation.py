"""Build catalogue sheets and the illustrated reel assembly books from exported geometry."""
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw
import trimesh

from working_gridfinity import BASE, CAP, DEPTHS, GEAR, ROOT, STEPS, core, mesh_path, parts_for, plate, WEB, STACK_SPACING, GEAR_THICKNESS
sys.path.insert(0, str(ROOT / "components"))
from reel_presentation import assembly_booklet, assembly_viewer

TOOLS = ROOT / "components/reel_presentation"
CACHE = ROOT / "build/reel_presentation"
URL = "https://github.com/oomlout/oomlout_oobb_part_organize_ribbon_reel_version_5"
NOTICE = "AI-generated CAD images and instructions. Errors possible."
LABELS = {CAP:"OOBB end cap", GEAR:"Four-peg drive gear"}
for d in DEPTHS:
    LABELS[core(d)] = f"{d} mm ribbon core"
for n in (2,3):
    for side in ("plug","socket"):
        LABELS[plate(n,side)] = f"Gridfinity {n} × {n} {side} plate"

HARDWARE = {
    "nut": ("M3 hex nut","hardware_nut_m3","3vb5b"),
    "screw": ("M3 × 12 countersunk","hardware_screw_countersunk_hex_head_black_m3_diameter_12_mm_length","1qf1u"),
}
EYE = (1.15,-1.55,1.35)


def version_folder(n):
    return ROOT/"parts"/(plate(n,"socket") if n else CAP)


def family(n):
    return f"Gridfinity {n} × {n}" if n else "Original OOBB"


def instance(path,role,pos=(0,0,0),rot=(0,0,0)):
    return [str(path),role,pos,rot]


def plan_views():
    jobs = []
    def view(path, objects, eye=EYE):
        path.parent.mkdir(parents=True,exist_ok=True)
        jobs.append(dict(target=str(path),objects=objects,eye=eye))
    cache_hardware()
    for part_id in LABELS:
        role = "black" if part_id==GEAR or "_core_" in part_id else "teal"
        item = instance(mesh_path(part_id),role)
        for name,eye in [("angle",EYE),("top",(0,0,1))]:
            view(CACHE/part_id/(name+".png"),[item],eye)
    for n in (0,2,3):
        folder = version_folder(n)/"assembly/render/raw"
        a,b,drum,gear = parts_for(n,25)
        screw_face = WEB if n else 3
        pieces = {
            "plug":instance(mesh_path(a),"teal",rot=(180,0,0)),
            "socket":instance(mesh_path(b),"teal",(0,0,25)),
            "core":instance(mesh_path(drum),"black"),
            "gear":instance(mesh_path(gear),"black",(0,0,25+screw_face+GEAR_THICKNESS),(180,0,0)),
        }
        for key, (label,identifier,code) in HARDWARE.items():
            pieces[key] = instance(CACHE/(key+".stl"),"steel")
        for key,item in pieces.items():
            view(folder/f"part_{key}.png",[instance(item[0],item[1])])
        nuts,loose,bottom,top = [],[],[],[]
        for x,y in [(15,7.5),(-7.5,15),(-15,-7.5),(7.5,-15)]:
            angle = math.degrees(math.atan2(y,x))+30
            ux,uy = math.cos(math.radians(angle)),math.sin(math.radians(angle))
            for z in (5.8,16.8):
                nuts.append(instance(pieces["nut"][0],"steel",(x,y,z),(0,0,angle)))
                loose.append(instance(pieces["nut"][0],"steel",(x+8*ux,y+8*uy,z),(0,0,angle)))
            bottom.append(instance(pieces["screw"][0],"steel",(x,y,-screw_face)))
            top.append(instance(pieces["screw"][0],"steel",(x,y,25+screw_face),(180,0,0)))
        stage2 = [pieces["core"],*nuts,pieces["plug"],*bottom]
        stage3 = [*stage2,pieces["socket"],*top]
        view(folder/"step_01.png",[pieces["core"],*loose])
        view(folder/"step_02.png",stage2,(1.1,-1.7,-1.2))
        view(folder/"step_03.png",stage3)
        view(folder/"step_04.png",[*stage3,pieces["gear"]])
        view(folder/"book_cover.png",[*stage3,pieces["gear"]],(1,-1.7,0.95))
        if n:
            fit = ROOT / "design_stages" / f"{n}x{n}"
            # Drives lift off the two faces that meet in a stack.
            lower = [instance(mesh_path(a),"teal",(0,0,-25),(180,0,0)),
                     instance(mesh_path(drum),"black",(0,0,-25)),instance(mesh_path(b),"teal")]
            upper = [instance(mesh_path(a),"teal",(0,0,STACK_SPACING),(180,0,0)),
                     instance(mesh_path(drum),"black",(0,0,STACK_SPACING)),
                     instance(mesh_path(b),"teal",(0,0,STACK_SPACING+25))]
            view(fit/"stacked_reels.png",lower+upper,(1,-1.7,0.8))
            view(fit/"corner_fit.png",[instance(fit/"corner_socket.stl","teal"),
                instance(fit/"corner_plug.stl","teal",(0,-(n-1)*42,STACK_SPACING),(180,0,0))])
    return jobs


def cache_hardware():
    CACHE.mkdir(parents=True,exist_ok=True)
    for key in HARDWARE:
        scad = CACHE/(key+".scad")
        scad.write_text('use <../../source_file/reel_hardware.scad>;\n'+key+'();\n')
        subprocess.run([shutil.which("openscad.com") or "openscad","-o",str(CACHE/(key+".stl")),str(scad)],
                       check=True,capture_output=True)


def render():
    jobs = plan_views()
    driver = TOOLS/"render.py"
    old = CACHE/"render_hashes.json"
    previous = json.loads(old.read_text()) if old.exists() else {}
    hashes, fingerprint, pending = {},{},[]
    for job in jobs:
        key = str(Path(job["target"]).relative_to(ROOT))
        inputs = []
        for path,*_ in job["objects"]:
            if path not in fingerprint:
                fingerprint[path] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            inputs.append(fingerprint[path])
        digest = hashlib.sha256(driver.read_bytes()+json.dumps([job,inputs]).encode()).hexdigest()
        hashes[key] = digest
        if previous.get(key) != digest or not Path(job["target"]).is_file():
            pending.append(job)
    if pending:
        task = CACHE/"jobs.json"
        task.write_text(json.dumps(pending))
        with (CACHE/"blender.log").open("w") as log:
            subprocess.run([shutil.which("blender") or "blender","-b","-t","8","--python-exit-code","1",
                            "-P",str(driver),"--",str(task)],stdout=log,stderr=subprocess.STDOUT,check=True)
        for job in pending:
            with Image.open(job["target"]) as im:
                im.verify()
        old.write_text(json.dumps(hashes,indent=2))
    sys.path.insert(0,str(BASE/"presentation/scripts"))
    from catalogue import sheet
    for part_id,label in LABELS.items():
        sheet(CACHE/part_id,mesh_path(part_id).with_name("3dpr_presentation.png"),label,
              trimesh.load_mesh(mesh_path(part_id)).extents)


def book(n):
    folder = version_folder(n)/"assembly"
    ids = parts_for(n,25)
    parts = {}
    for key,identifier in zip(("plug","socket","core","gear"),ids):
        parts[key] = dict(key=key,id=identifier,name=LABELS[identifier],quantity=1)
    if not n:
        parts["plug"]["name"] = "First OOBB cap"
        parts["socket"]["name"] = "Second OOBB cap"
    for key,(name,identifier,code) in HARDWARE.items():
        parts[key]=dict(key=key,id=identifier,name=name,quantity=8,md5_6_alpha=code,
                        short_url="https://oom.lt/a/"+code,short_label="oom.lt/a/"+code)
    groups = [dict(core=1,nut=8),dict(plug=1,screw=4),dict(socket=1,screw=4),dict(gear=1)]
    steps = [dict(key=f"step_{i:02d}",title=action,action=action,loose_parts=group)
             for i,(group,action) in enumerate(zip(groups,STEPS),1)]
    for key,item in parts.items():
        assert sum(group.get(key,0) for group in groups)==item["quantity"]
    details = ["The illustrations show the 25 mm core. The same assembly order applies to 50, 75 and 100 mm cores.",
               *STEPS, "Print the flat ribbon face on the bed. Use one drive per reel.", NOTICE]
    if n:
        details.insert(1,f"{n*42-.5:g} mm square, on the 42 mm Gridfinity pitch. Lift the drive off the mating faces and stack plug-side down. The 1 mm web has a 5 mm diamond lead-in at the ribbon slit.")
    data = dict(style=json.loads((TOOLS/"style.json").read_text()),parts=parts,
                printed_keys=list(parts)[:4], configuration_title=family(n)+" ribbon reel",steps=steps,
                physical_item_count=20,source_sha256={i:hashlib.sha256(mesh_path(i).read_bytes()).hexdigest() for i in ids},
                book=dict(cover_title="Ribbon reel",cover_subtitle=family(n)+" / 25–100 mm cores",
                    logo_svg="source_file/oomlout_logo_unshaded_original.svg",logo_symbol_subpaths=3,
                    project_url=URL,project_name=family(n)+" ribbon reel",details_title="Assembly and fit",
                    details=details,summary_title="Printed parts",hardware_title="Hardware",summary_step=True,
                    summary_view="book_cover",signature_pages=4,viewer_layout="a4-landscape-four-step",viewer_start="page-03"))
    with (folder/"parts.csv").open("w",encoding="utf-8",newline="") as file:
        writer=csv.writer(file)
        writer.writerow(["part","quantity","identity","hardware_url"])
        for item in parts.values():
            writer.writerow([item["name"],item["quantity"],item["id"],item.get("short_url","")])
    assembly_booklet.publish(output=folder,data=data)
    assembly_booklet.review_outputs(output=folder,data=data)
    assembly_viewer.publish(output=folder,data=data)


def listing_cover():
    sys.path.insert(0,str(BASE/"presentation/scripts"))
    from catalogue import font
    folder = ROOT/"output/project_summary"
    folder.mkdir(parents=True,exist_ok=True)
    page = Image.new("RGB",(1600,1200),"#f6f4ef")
    pen = ImageDraw.Draw(page)
    pen.text((72,48),"Stackable ribbon reels",font=font(60),fill="#243a3b")
    for n,box,label in [(3,(671,173,1540,860),"3 × 3"),(2,(60,405,627,958),"2 × 2")]:
        source = Image.open(version_folder(n)/"assembly/render/raw/book_cover.png").convert("RGBA")
        source = source.crop(source.getchannel("A").getbbox())
        scale = min((box[2]-box[0])/source.width,(box[3]-box[1])/source.height)
        source = source.resize((round(source.width*scale),round(source.height*scale)),Image.Resampling.LANCZOS)
        x = box[0]+(box[2]-box[0]-source.width)//2
        y = box[3]-source.height
        page.paste(source,(x,y),source)
        pen.text((x,box[3]+10),label,font=font(35),fill="#243a3b")
    pen.text((72,1118),"42 mm Gridfinity pitch   ·   25, 50, 75 and 100 mm winding widths",font=font(30),fill="#344b4b")
    pen.text((72,1163),NOTICE,font=font(20),fill="#536563")
    page.save(folder/"cover.png",optimize=True)


def main():
    render()
    for n in (0,2,3):
        book(n)
    listing_cover()


if __name__=="__main__":
    main()

