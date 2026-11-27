# Ribbon bobbin design notes

One bobbin uses **one core, two copies of the same end cap, eight M3 hex nuts and eight M3 countersunk screws**. Print the core upright and both caps flat with their countersinks facing up. In assembly, both countersunk faces point away from the ribbon.

## First two catalogue entries

| Part | Populate parameters | Physical dimensions |
| --- | --- | --- |
| Core | `diameter=3` in OOBB units, `depth=25` in mm | 44 mm winding diameter × 25 mm between cap mating faces |
| End cap | `width=7`, `height=7` in OOBB units, `depth=3` in mm | 104 × 104 × 3 mm, standard rounded OOBB plate |

The installed OOBB library uses a 15 mm pitch and a 1 mm overall size allowance. Its circle and plate convention gives a 44 mm diameter for three units and a 104 mm side for seven units. The assembled bobbin is 31 mm thick. The specified 25 mm is the nominal winding space. A ribbon measuring exactly 25 mm will have no designed axial running clearance. A later depth can provide extra room using the same caps. [OOBB circle](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/components/oobb_circle/working.py) · [OOBB plate](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/components/oobb_plate/working.py)

## Cap and screw positions

Use the plate centre as XY zero. I expanded the installed `oobb_holes` with `width=height=7`, `holes="all"` and `both_holes=True`. In the print mode it emits 218 cutters. The resulting cap has **169 distinct through-hole centres** on a 13 × 13 grid from −45 to +45 mm. The 49 full-grid positions have M6 clearance. The remaining 120 have M3 clearance. The centre stays M6. [OOBB hole arrays](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/components/oobb_holes/working.py)

Use the four combinations of **X = ±15 mm, Y = ±7.5 mm** for the core screws. All four are existing M3 holes. Countersink those four on the exterior face, leaving 116 plain M3 bores. The nearest M6 centre is 7.5 mm away. With the library's print radii of 3.6 mm for the head and 3.25 mm for the M6 bore, the narrowest ligament between them is 0.65 mm at the outer face. Inspect that ligament in the slicer. The hole pattern is mirror-symmetric, so the same printed cap fits both ends with its edges aligned. Orient the long axis of the four-screw rectangle the same way on both caps.

## Core cross-section

These are proposed first-print dimensions. Keep the 44 mm winding surface cylindrical so a ribbon can lie flat across the full 25 mm. Put the extra material and angled transitions **inside** the drum. The only interruptions on the outside are the eight short nut openings near the ends.

| Feature | First-print geometry |
| --- | --- |
| Main shell | Radius 22 mm, wall 1.6 mm, open through the centre |
| End lands | From each mating face to 5.8 mm inboard, use a continuous annular wall 2.6 mm thick. Taper its extra 1 mm of thickness back to the main wall over 1 mm of axial travel. |
| Nut bosses | Four integral cylindrical lands per end on the screw centres, each 5.2 mm in radius. The farthest point is 21.97 mm from the bobbin axis, inside the winding envelope. |
| Pocket | From 1.4 to 4.4 mm inboard in print mode. The 5.8 mm land leaves 1.4 mm of material behind the pocket before the taper begins. Mirror these distances at the other end. |
| Inward boss transition | Relieve the inside of each boss with a coaxial 45° taper. Start the relief at radius 11.6 mm at the back of each end land and grow toward the midplane. This keeps the upper lands printable from the wall below. |
| Screw pilot | Named M3 clearance from each mating face through the nut and at least 5.5 mm into the core. An M3×8 countersunk screw, measured including the head, projects about 5 mm past a flush 3 mm cap. Confirm engagement and tip clearance with the actual hardware. |

For the 25 mm core the boss relief reaches radius 18.3 mm at mid-height. This leaves a small continuous rib at each of the four stations and the 1.6 mm wall between them. For a deeper core, stop the relief at the shell's 20.4 mm inside radius. The two end lands and both nut positions stay fixed relative to their respective end faces.

## Which side of the nut is exposed

The nut lies flat, with its threaded axis parallel to the bobbin axis. Slide it sideways from the rim until it stops at the seated hexagon. Only the low rectangular end of the channel appears at the winding surface. Two mouths open toward +X and two toward −X at each end. The default hex has vertices along X and flats parallel to travel. The narrow mouth guides the nut on those flats and prevents it from spinning when the cap screw is tightened.

I expanded the local `oobb_nut` primitive. **`clearance="left"` extends 20 mm along local +X**. Its stock channel is twice the nut radius, which is wider than the distance across the flats. Rotating the primitive turns the slot and hex together and preserves that width. The local implementation permits narrowing the slot while retaining the requested literal. [OOBB nut implementation](https://github.com/oomlout/oomlout_oobb_version_5/blob/main/components/oobb_nut/working.py)

| Measured in the expanded primitive | 3dpr | true |
| --- | ---: | ---: |
| Hex circumradius | 3.462 mm | 3.1735 mm |
| Stock channel width | 6.924 mm | 6.347 mm |
| Channel width matched to flats | 5.996 mm | 5.497 mm |
| Pocket height | 3.0 mm | 2.5 mm |

For a single mode, set `r = oobb.gv("nut_radius_m3", mode)`, `extra_clearance = (sqrt(3) - 2) * r / 0.866`, and explicitly pass that mode's `nut_depth_m3`. The installed implementation applies a negative adjustment to width only. I checked that its generated print-mode slot is 20 × 5.996 × 3 mm. The hex pocket keeps its library radius. This calculation is specific to the installed primitive. Recheck the generated dimensions if the library changes. Screw fit, bridge sag across this roughly 6 mm mouth and winding behaviour still need a physical print.
