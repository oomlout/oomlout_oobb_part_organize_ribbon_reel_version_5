"""Catalogue definitions shared by population, fit fixtures and publication."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREFIX = "oobb_part_organize_ribbon_reel_"
DEPTHS = (25, 50, 75, 100)
WEB = 1.0
FOOT = 4.75
RIM = 1.6
STACK_SPACING = 2*WEB + FOOT
GEAR_FACE = {"plug": WEB+FOOT, "socket": WEB}
GEAR_THICKNESS = 6
GEAR = PREFIX + "drive_gear_3_width_3_height_6_depth"
CAP = PREFIX + "end_cap_7_width_7_height_3_depth"
BASE = ROOT.parent / "oomlout_oobb_version_5"
STEPS = (
    "Slide four M3 hex nuts into each end of the core.",
    "Seat the first plate against the core. Tighten four M3 × 12 countersunk screws in the matching holes.",
    "Turn the assembly over. Install the second plate with four screws. Keep both countersunk faces outward.",
    "Slide the gear shaft into the centre. Rotate to align its four pegs and press the gear face flat.",
)


def core(depth):
    return PREFIX + f"core_3_diameter_{depth}_depth"


def plate(n, side):
    return PREFIX + f"gridfinity_end_{n}x{n}_{side}"


def definitions():
    options = []
    for cells in (2, 3):
        for side in ("plug", "socket"):
            options.append({
                "oobb_type": "gridfinity_end",
                "cells": cells,
                "side": side,
                "web": WEB,
            })
    return options


def parts_for(n, depth):
    ends = [plate(n, "plug"), plate(n, "socket")] if n else [CAP, CAP]
    return [*ends, core(depth), GEAR]


def mesh_path(part_id):
    return ROOT / "parts" / part_id / "3dpr.stl"

