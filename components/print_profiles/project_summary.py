"""Write editable Bambu project summaries from ordered (plate name, printable pieces) pairs."""
import io
import json
import math
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
import yaml
from PIL import Image, ImageDraw
from p1s_print_kit import CORE, add_printable_copy, validate_kit_archive

ET.register_namespace("", CORE)
PLATES_PER_FILE = 9


@dataclass
class SummaryPlate:
    part_id: str
    name: str
    pieces: list
    source_stls: list[str]
    notes: str


def core(tag):
    return f"{{{CORE}}}{tag}"


def geometry(mesh):
    node = ET.Element(core("mesh"))
    vertices = ET.SubElement(node, core("vertices"))
    for x, y, z in mesh.vertices:
        ET.SubElement(vertices, core("vertex"), x=f"{x:.8f}", y=f"{y:.8f}", z=f"{z:.8f}")
    faces = ET.SubElement(node, core("triangles"))
    for a, b, c in mesh.faces:
        ET.SubElement(faces, core("triangle"), v1=str(a), v2=str(b), v3=str(c))
    return node


def arrange(pieces, bed, excluded, height):
    """Centre one row or column on a rectangular bed; keep 6 mm between parts."""
    extents = np.array([mesh.extents for _, mesh in pieces])
    if (extents[:, 2] > height).any():
        raise ValueError("Object exceeds printable height")
    for axis in (0, 1):
        span = extents[:, axis].sum() + 6 * (len(pieces) - 1)
        cursor = (bed[axis] - span) / 2
        positions = []
        for size in extents[:, :2]:
            low = (bed - size) / 2
            low[axis] = cursor
            high = low + size
            if (low < 3).any() or (high > bed - 3).any():
                break
            if any(np.all(high > a) and np.all(low < b) for a, b in excluded):
                break
            positions.append(low)
            cursor += size[axis] + 6
        if len(positions) == len(pieces):
            return positions
    # Reel kits place the two end plates in opposite corners. The core and
    # removable drive occupy the free space across the diagonal.
    if len(pieces) == 4:
        anchors = [(0.005, 0.995), (0.995, 0.005), (0.76, 0.76), (0.25, 0.25)]
        lows = [(bed - size[:2]) * anchor for size, anchor in zip(extents, anchors)]
        boxes = [(low, low + size[:2]) for low, size in zip(lows, extents)]
        for i, (low, high) in enumerate(boxes):
            if (low < 0.6).any() or (high > bed - 0.6).any():
                break
            obstacles = list(excluded) + boxes[:i]
            if any(np.all(high + 2 > a) and np.all(low - 2 < b) for a, b in obstacles):
                break
        else:
            return lows
    raise ValueError("The complete kit does not fit this bed")


def xy(points):
    return np.array([list(map(float, point.split("x"))) for point in points])


def makerworld_listing(root, template, title, volumes):
    source = root / "working_makerworld.yaml"
    listing = dict(category=None, license=None, design_type="Original", design_credits=None,
                   original_model_url=None, assembly=None, hardware=None)
    if source.is_file():
        listing.update(yaml.safe_load(source.read_text(encoding="utf-8")) or {})
    listing["category_browser_url"] = "https://makerworld.com/en/3d-models"
    listing["category_list_url"] = "https://github.com/iamdjem/modelprep/blob/main/deploy/src/data/makerworld-categories.json"
    listing["field_inputs"] = dict(
        category="single_category_choice", license="license_permission_choices",
        design_type="upload_type_choice", design_credits="description_text",
        original_model_url="source_link_for_remix",
        printer="3mf_profile", nozzle_diameter_mm="3mf_profile", material="3mf_profile",
        print_settings="3mf_profile", profile_name="text", profile_description="text",
        assembly="description_text", hardware="description_text",
    )
    listing["model_name"] = title
    # write_summary copies these settings verbatim and assigns every printable to slot 1.
    with ZipFile(template) as archive:
        settings = json.loads(archive.read("Metadata/project_settings.config"))
    listing["printer"] = settings["printer_model"]
    listing["nozzle_diameter_mm"] = float(settings["nozzle_diameter"][0])
    listing["material"] = settings["filament_type"][0]
    listing["filament_preset"] = settings["filament_settings_id"][0]
    listing["filament_colour"] = settings["filament_colour"][0]
    listing["print_settings"] = dict(
        process=settings["print_settings_id"], build_plate=settings["curr_bed_type"],
        layer_height_mm=float(settings["layer_height"]), wall_loops=int(settings["wall_loops"]),
        infill_density=settings["sparse_infill_density"], infill_pattern=settings["sparse_infill_pattern"],
        supports_enabled=str(settings["enable_support"]) == "1", support_type=settings.get("support_type"),
    )
    listing["print_profiles"] = []
    for volume in volumes:
        rows = volume["plates"]
        first, last = rows[0]["catalogue_plate"], rows[-1]["catalogue_plate"]
        span = str(first) if first == last else f"{first}–{last}"
        listing["print_profiles"].append(dict(
            file=volume["file"], name=f"{title} · {span}",
            description=f"Catalogue plate{'s' if len(rows) > 1 else ''} {span}. "
                        f"{listing['material']}, {settings['layer_height']} mm layers, "
                        f"{settings['wall_loops']} walls and {settings['sparse_infill_density']} "
                        f"{settings['sparse_infill_pattern']} infill.",
        ))
    return listing


def write_summary(*, plates, template, output, title):
    """Each piece is a (name, oriented single-body trimesh in millimetres) pair."""
    names = [name for name, _ in plates]
    if not names or len(set(names)) != len(names):
        raise ValueError("Expected distinct, nonempty plate inventory")
    with ZipFile(template) as source:
        profile = source.read("Metadata/project_settings.config")
    printer = json.loads(profile)
    corners = xy(printer["printable_area"])
    bed = corners.max(axis=0)
    if set(map(tuple, corners)) != {(0, 0), (bed[0], 0), (0, bed[1]), tuple(bed)}:
        raise ValueError("Expected an axis-aligned rectangular bed starting at (0, 0)")
    excluded = [(p.min(axis=0), p.max(axis=0)) for p in xy(printer.get("bed_exclude_area", [])).reshape(-1, 4, 2)]
    height = float(printer["printable_height"])
    columns = math.ceil(math.sqrt(len(plates)))
    model = ET.Element(core("model"), unit="millimeter", attrib={"xml:lang": "en-US", "xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    for key, value in [("Application", "BambuStudio-02.07.01.57"), ("BambuStudio:3mfVersion", "1"), ("Title", title)]:
        ET.SubElement(model, core("metadata"), name=key).text = value
    resources = ET.SubElement(model, core("resources"))
    build = ET.SubElement(model, core("build"))
    config = ET.Element("config")
    serial = 0
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as tmp:
        archive = Path(tmp) / "working.3mf"
        with ZipFile(archive, "w", ZIP_DEFLATED) as destination:
            destination.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/><Default Extension="png" ContentType="image/png"/></Types>')
            destination.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="model" Target="/3D/3dmodel.model" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/><Relationship Id="thumb" Target="/Metadata/plate_1.png" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/></Relationships>')
            destination.writestr("Metadata/project_settings.config", profile)
            for i, (name, pieces) in enumerate(plates):
                if not pieces:
                    raise ValueError(f"Empty plate: {name}")
                plate = ET.SubElement(config, "plate")
                thumbnail = f"Metadata/plate_{i + 1}.png"
                for key, value in [("plater_id", str(i + 1)), ("plater_name", name), ("locked", "false"), ("thumbnail_file", thumbnail)]:
                    ET.SubElement(plate, "metadata", key=key, value=value)
                image = Image.new("RGB", (400, 400), "#f1f1ed")
                draw = ImageDraw.Draw(image)
                origin = bed * 1.2 * np.array([i % columns, -(i // columns)])
                for (label, mesh), low in zip(pieces, arrange(pieces, bed, excluded, height)):
                    if not mesh.is_volume:
                        raise ValueError(f"Expected closed production mesh: {label}")
                    mesh = mesh.copy()
                    mesh.apply_translation(-mesh.bounds[0])
                    serial += 1
                    x, y = origin + low
                    add_printable_copy(serial=serial, name=label, mesh=geometry(mesh), resources=resources,
                                       build=build, settings=config, plate=plate,
                                       transform=f"1 0 0 0 1 0 0 0 1 {x:.8f} {y:.8f} 0")
                    points = (mesh.triangles[mesh.face_normals[:, 2] > 0.001, :, :2] + low) * (400 / bed)
                    points[:, :, 1] = 400 - points[:, :, 1]
                    for triangle in points:
                        draw.polygon(triangle.flatten().tolist(), fill=printer["filament_colour"][0][:7])
                buffer = io.BytesIO()
                image.save(buffer, "PNG")
                destination.writestr(thumbnail, buffer.getvalue())
            with destination.open("3D/3dmodel.model", "w") as stream:
                ET.ElementTree(model).write(stream, encoding="utf-8", xml_declaration=True)
            destination.writestr("Metadata/model_settings.config", ET.tostring(config, encoding="utf-8"))
        resources.clear()
        validate_kit_archive(archive, count=serial)
        with ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError("Archive CRC mismatch")
            actual = ET.fromstring(z.read("Metadata/model_settings.config"))
            inventory = [(p.find("metadata[@key='plater_name']").get("value"), len(p.findall("model_instance"))) for p in actual.findall("plate")]
            if inventory != [(name, len(pieces)) for name, pieces in plates]:
                raise ValueError("Plate inventory differs from source")
        archive.replace(output)
    print(f"{output}: {len(plates)} plates, {serial} editable pieces", flush=True)


def publish_summary(*, plates, template, folder, title, repo_root):
    """Write numbered nine-plate projects and their source inventory."""
    folder = Path(folder)
    root = Path(repo_root).resolve()
    if not plates or len({p.name for p in plates}) != len(plates):
        raise ValueError("Supply a nonempty catalogue with unique plate names")
    folder.mkdir(parents=True, exist_ok=True)
    volumes = []
    with tempfile.TemporaryDirectory(dir=folder) as tmp:
        stage = Path(tmp)
        for start in range(0, len(plates), PLATES_PER_FILE):
            number = len(volumes) + 1
            filename = "working.3mf" if number == 1 else f"working_{number}.3mf"
            batch = plates[start:start + PLATES_PER_FILE]
            rows = []
            for local, plate in enumerate(batch, 1):
                paths = []
                for source in plate.source_stls:
                    stl = (root / source).resolve()
                    if not stl.is_file() or stl.suffix.lower() != ".stl":
                        raise ValueError(f"Missing source STL for {plate.name}: {source}")
                    paths.append(stl.relative_to(root).as_posix())
                if not paths:
                    raise ValueError(f"No source STLs for {plate.name}")
                rows.append(dict(plate=local, catalogue_plate=start + local,
                                 part_id=plate.part_id, name=plate.name, source_stls=paths,
                                 printed_pieces=len(plate.pieces), notes=plate.notes))
            write_summary(plates=[(p.name, p.pieces) for p in batch], template=template,
                          title=f"{title} ({number} of {math.ceil(len(plates) / PLATES_PER_FILE)})",
                          output=stage / filename)
            volumes.append(dict(file=filename, plates=rows))
        index = dict(project=title, source_paths_relative_to="repository root",
                     max_plates_per_file=PLATES_PER_FILE, total_plates=len(plates), files=volumes)
        index["makerworld"] = makerworld_listing(root, template, title, volumes)
        index_file = stage / "plates.yaml"
        index_file.write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")
        expected = {volume["file"] for volume in volumes}
        for name in sorted(expected):
            (stage / name).replace(folder / name)
        index_file.replace(folder / index_file.name)
        for old in folder.glob("*.3mf"):
            if old.name not in expected and re.fullmatch(r"working_[1-9]\d*\.3mf|plates_\d+-\d+\.3mf", old.name):
                old.unlink()
