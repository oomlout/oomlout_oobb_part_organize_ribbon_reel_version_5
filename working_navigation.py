"""Write taxonomy guides and byte-identical production STLs at their leaves."""
import os
import re
import shutil
from pathlib import Path

import yaml

from working_gridfinity import ROOT


def relative(source, target):
    return Path(os.path.relpath(target,source)).as_posix()


def leaf_for(data):
    fields = [data.get(f"taxonomy_{i}") for i in range(1,16)]
    return ROOT.joinpath("navigation_oobb",*(str(f) for f in fields if f))


def main():
    nav = ROOT/"navigation_oobb"
    branches = {}
    leaves = {}
    for metadata in sorted((ROOT/"parts").glob("*/working.yaml")):
        data = yaml.safe_load(metadata.read_text(encoding="utf-8"))
        if not data.get("oobb_details"):
            continue
        part = metadata.parent
        leaf = leaf_for(data)
        leaf.mkdir(parents=True,exist_ok=True)
        leaves[leaf] = part
        node = leaf
        while node != nav:
            branches.setdefault(node.parent,set()).add(node)
            node = node.parent
        source = part/"3dpr.stl"
        if source.is_file():
            dest = leaf/source.name
            shutil.copyfile(source,dest)
            if dest.read_bytes() != source.read_bytes():
                raise IOError(f"Navigation STL mismatch: {dest}")
        # Older leaves also carry CAD and metadata. Refresh the files present there.
        for old in leaf.iterdir():
            original = part/old.name
            if old.suffix in {".scad",".yaml",".svg",".png"} and original.is_file():
                shutil.copyfile(original,old)
        (leaf/"oomp_id.txt").write_text(part.name+"\n")
        where = relative(leaf,part)
        name = part.name.removeprefix("oobb_part_organize_ribbon_reel_").replace("_"," ")
        (leaf/"README.md").write_text(f"# {name}\n\n[Part folder and instructions]({where}/) · [Printable STL](3dpr.stl)\n\n`{part.name}`\n",encoding="utf-8")
    for branch,children in branches.items():
        lines = []
        for child in sorted(children,key=lambda p:[int(v) if v.isdigit() else v for v in re.split(r"(\d+)",p.name)]):
            target = leaves.get(child,child)
            lines.append(f"- [{child.name.replace('_',' ')}]({relative(branch,target)}/)")
        (branch/"README.md").write_text(f"# {branch.name.replace('_',' ')}\n\n"+"\n".join(lines)+"\n",encoding="utf-8")
    node = nav
    while len(branches.get(node,())) == 1:
        node = next(iter(branches[node]))
    return node

