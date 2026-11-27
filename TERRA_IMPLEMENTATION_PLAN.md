# Terra implementation plan

Build the two catalogue entries in [the design notes](BOBBIN_DESIGN_NOTES.md). The end cap is printed twice from one file. The only production code changes expected are in `working_oomp_populate.py` and `working_scad.py`. Run the existing OOMP stage to materialize the definitions.

## 1. Define the two parts

Replace the active wire-shortener option and its holder/electronic/wire taxonomy in `working_oomp_populate.py`. Use the common taxonomy fields 1–5 in this order: `oobb`, `part`, `organize`, `ribbon`, `reel`. Use these remaining fields and exact IDs.

| CAD selector and taxonomy field 6 | Subsequent taxonomy fields | Expected ID |
| --- | --- | --- |
| `core` | `3_diameter`, `25_depth` | `oobb_part_organize_ribbon_reel_core_3_diameter_25_depth` |
| `end_cap` | `7_width`, `7_height`, `3_depth` | `oobb_part_organize_ribbon_reel_end_cap_7_width_7_height_3_depth` |

Keep a core depth list starting with `[25]`. Generate the numeric `depth`, taxonomy segment and CAD details from the same value. Define the cap with independent numeric `width` and `height` fields and require them to match. Each option supplies its own `oobb_type`, with `oobb_details.run_scad=True` and `run_solidcraft=False`. Retain the existing extra-detail hook and `write_extras`. The OOMP helper builds IDs from numbered taxonomy fields, so a top-level numeric dimension alone cannot distinguish variants.

Run from the project root. These two commands let you check the definitions before adding either recipe.

```powershell
python working_oomp_populate.py
python -c "import working_oomp; working_oomp.main(wait_for_completion=True)"
```

Check both expected IDs in `parts_source/<id>/working.yaml` and `parts/<id>/working.yaml`. Confirm the dimensions and selector survived generation. The installed OOMP helper supports the completion flag. It waits for the files the SCAD runner reads. The existing checkout had neither generated directory at planning time. [Project loader](working_oomp.py) · [CAD dispatch](scad_help.py)

## 2. Establish the shared interface

In `working_scad.py` add `get_core(thing, **kwargs)` and `get_end_cap(thing, **kwargs)`. Define the four local XY stations once as the combinations of ±1 pitch in X and ±½ pitch in Y. Use that same definition for the pockets, pilots and head seats. Apply the supplied part origin to every feature. Set up both printable parts with their bottom faces at local Z = 0. Pass only the fields each primitive needs to `oobb.append_full`. In particular, a part's `depth`, `diameter` or `radius` must never accidentally size a nut, shaft, grid or taper.

## 3. Draw the core

1. Get the outside radius from `(diameter * oobb.gv("osp") - oobb.gv("osp_minus")) / 2`. Let `D` denote the populated depth in mm. Use the wall, land, pocket and pilot dimensions in the notes. Require enough depth to keep both 5.8 mm lands and their 1 mm band transitions distinct. Derive all far-end Z positions from `D`.
2. Build a hollow barrel of radius 22 and wall 1.6 using `oobb_cylinder_hollow`. Add the two end bands with a scoped outer cylinder minus an inner cylinder and frustum. For the lower band the inside radius is 19.4 at Z = 0 through 5.8 and grows to 20.4 at Z = 6.8. Mirror the profile at the upper end. Keep the outside radius constant. Scope bore cuts to their own solids so the barrel construction cannot erase the nut bosses.
3. Add four positive `oobb_cylinder`s, radius 5.2, centred at the screw stations over the length of the core. Shape their inner faces with a negative axial bore shared by all four. For distance `s = min(z, D-z)` from the nearest end, the relief radius is `min(R_inner, 11.6 + max(0, s - 5.8))`, where `R_inner` is the main shell inside radius. Implement its segments with straight and tapered `oobb_cylinder` cutters. Use `radius_1` at the bottom and `radius_2` at the top with explicit `zz="bottom"`. For D = 25, the axial profile breakpoints (Z, bore radius) are (0, 11.6), (5.8, 11.6), (12.5, 18.3), (19.2, 11.6), (25, 11.6). A longer core gets a straight central relief once the taper reaches the shell. Union the shaped bosses with the bands and barrel. Use volumetric overlap at adjoining positive solids and extend through-cutters slightly past open faces.
4. At each station subtract two `oobb_nut` primitives. Set `radius_name="m3"`, `type="negative"`, `clearance="left"`, `zz="bottom"`, `hole=False`, `overhang=False`. For each emitted mode explicitly pass its nut depth and the across-flats width adjustment from the notes. The near pocket starts at Z = 1.4. The far pocket starts at `D - 1.4 - pocket_depth`. Use 0° about Z for +X stations and 180° for −X at **both** ends. This lets the 20 mm clearance cutter exit the nearest side of the drum and keeps the closed hex seat on the inboard side. Group cuts after the union so they open through the outer shell as well as the boss.
5. Subtract eight coaxial `oobb_hole` pilots with `radius_name="m3"` and explicit finite depth. Cover the first and last 5.5 mm plus a small overrun at the mating face. A pilot must pass through the seated nut and provide space for the screw tip. Keep the core as one upright printable object.

## 4. Draw the end cap

1. Add a positive `oobb_plate` with the populated width, height and depth, bottom at Z = 0. Use its standard rounded corners.
2. Add `oobb_holes` with `holes="all"`, `both_holes=True`, `radius_name="m6"`, and the same width and height. Use the rectangular pattern at the plate centre. The template's `get_base` uses a perimeter pattern and a centre test screw, so build this recipe directly.
3. Subtract four `oobb_screw_countersunk` cutters at the shared stations. Use `radius_name="m3"`, `depth=3` from the cap parameter, `zz="top"`, `hole=True`, `nut_include=False`, `overhang=False` and place the anchor at Z = cap depth. In the installed screw primitive the cone extends down from the anchor. The print-mode cone spans Z = 1.1 to 3.0 mm with its wide end on the outside. The flat inner face bears on the core.

## 5. Build and check

Run these in sequence from the project root. The SCAD-only and STL actions both run populate → OOMP → SCAD. The completion flag keeps that ordering deterministic during a clean build.

```powershell
python -m unittest discover -s tests
python -c "import action_make_scad_no_stl as build; build.main(wait_for_completion=True)"
python -c "import action_make_scad as build; build.main(wait_for_completion=True)"
```

- **Catalogue and variants.** Require one core and one cap ID in a fresh build. Check `3dpr.scad` and a nonempty rendered STL in each part directory. Exercise a second depth, e.g. 40 mm, in a temporary population fixture. Verify a distinct `40_depth` ID, the same cap ID and screw coordinates, 40 mm between mating faces, and mirrored far-end features. Leave only the 25 mm core and 7×7 cap in the project population.
- **Mesh and assembly.** Render each part and check for one connected watertight solid per STL. Check bounds of 44 × 44 × 25 mm and 104 × 104 × 3 mm within mesh faceting tolerance. In a temporary assembly place the core at Z = 0…25, the caps at −3…0 and 25…28. Flip the lower cap about X so its countersinks face outward. Confirm all eight screw axes align, both caps seat flat and the tips clear the core.
- **Cap section.** Count 49 M6 and 120 M3 through-bores including the four joining holes. Compare the top and underside at a joining station. In print mode the head opening should be Ø7.2 mm and the shaft Ø3.6 mm. Check the 0.65 mm web to the adjacent M6 bore survives slicing.
- **Core sections.** Inspect horizontal slices at Z = 2.9 and 22.1 mm. Each should show four independent, one-sided entries that connect the rim to a seated hex, approximately 6.0 mm across the flats. Inspect an axial slice through Y = 7.5 mm for intact 1.4 mm pocket skins, screw-tip clearance, solid connections to the main shell and the 45° inner transitions. A mid-height slice away from a boss should show the 1.6 mm wall.
- **Print and fit.** Slice with supports off. Check that the upper bosses grow from supported material and that the short pocket roofs bridge between anchored edges. Print one core and two caps. Slide all eight nuts in sideways, tighten the countersunk screws, check that the nuts resist turning and the heads sit flush, then wind a ribbon and check for snagging. Record physical fit separately from CAD and slicer results if hardware is unavailable.

The research checks were in-memory expansions of the installed OOBB primitives and ID helper. The assembled model, slicer results and physical fit are the verification work for this implementation.
