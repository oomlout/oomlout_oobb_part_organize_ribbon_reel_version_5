"""Publish complete, editable P1S print plates using the OOBB summary writer."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

import trimesh
import yaml

from working_gridfinity import DEPTHS, ROOT, mesh_path, parts_for

sys.path.insert(0, str(ROOT / "components/print_profiles"))
from project_summary import SummaryPlate, publish_summary

OUTPUT = ROOT / "output/project_summary"


def build():
    plates = []
    for size in (0, 2, 3):
        family = f"Gridfinity {size}x{size}" if size else "OOBB 7x7"
        for depth in DEPTHS:
            ids = parts_for(size,depth)
            names = ["Plug plate","Socket plate"] if size else ["End cap A","End cap B"]
            names.extend([f"{depth} mm winding core", "Drive gear"])
            paths = [mesh_path(i) for i in ids]
            plates.append(SummaryPlate(
                part_id=f"reel_{size or 7}x{size or 7}_{depth}mm",
                name=f"{family} - {depth} mm ribbon space",
                pieces=[(name,trimesh.load_mesh(path)) for name,path in zip(names,paths)],
                source_stls=[path.relative_to(ROOT).as_posix() for path in paths],
                notes="Print flat ribbon faces down, core and drive shaft upright. Add eight M3 nuts and eight M3 x 12 countersunk screws.",
            ))
    with tempfile.TemporaryDirectory() as tmp:
        template = Path(tmp) / "settings.3mf"
        with ZipFile(template,"w") as archive:
            archive.write(ROOT / "source_file/p1s_profile.json","Metadata/project_settings.config")
        publish_summary(plates=plates, template=template, folder=OUTPUT,
                        title="OOBB ribbon reels and Gridfinity stacking plates", repo_root=ROOT)


def slice_profiles():
    exe = os.environ.get("BAMBU_STUDIO") or shutil.which("bambu-studio") or r"C:\Program Files\Bambu Studio\bambu-studio.exe"
    manifest = yaml.safe_load((OUTPUT/"plates.yaml").read_text(encoding="utf-8"))
    results = {}
    for entry in manifest["files"]:
        profile = OUTPUT / entry["file"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            result = subprocess.run([exe, "--slice", "0", "--outputdir", str(tmp), str(profile)],
                                    capture_output=True, text=True, errors="replace")
            files = sorted(tmp.rglob("*.gcode"))
            if result.returncode or len(files) != len(entry["plates"]):
                raise RuntimeError(f"{profile.name}: expected {len(entry['plates'])} slices, got {len(files)}. {result.stdout[-3500:]} {result.stderr[-2500:]}")
            results[profile.name] = dict(sha256=hashlib.sha256(profile.read_bytes()).hexdigest(),
                slicer=Path(exe).name, plates={f.name:f.stat().st_size for f in files},
                warnings=sorted(set(line.strip() for line in (result.stdout+result.stderr).splitlines()
                                    if "warning" in line.lower())))
    (OUTPUT/"slice_report.json").write_text(json.dumps(results,indent=2)+"\n", encoding="utf-8")

    write_upload_readme(manifest)


def write_upload_readme(manifest):
    lines = ["# Ribbon reel print profiles", "",
             "Each named P1S plate contains two end plates, a winding core and one removable drive. Select the reel and winding width in Bambu Studio.", "",
             "| 3MF | Local plate | Reel and winding width |", "| --- | ---: | --- |"]
    for volume in manifest["files"]:
        filename = volume["file"]
        for row in volume["plates"]:
            lines.append(f"| [{filename}]({filename}) | {row['plate']} | {row['name']} |")
    lines.extend(["", "## MakerWorld listing", "",
                  "Use [the cover image](cover.png) and the draft description, hardware list, additional images and profile settings in [plates.yaml](plates.yaml). Image and guide paths in the YAML are relative to the repository root. Select the publication licence and live category when uploading.",
                  "", "[Assembly guides](../../README.md#assembly) · [Printable fit trials](../../design_stages/) · [Slice verification](slice_report.json)"])
    (OUTPUT/"README.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


if __name__ == "__main__":
    build()
    slice_profiles()

