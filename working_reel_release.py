"""Publish reel instructions, fit trials, catalogue pages and MakerWorld project files."""
import yaml

from working_gridfinity import CAP, GEAR, ROOT, STEPS, plate
from working_navigation import leaf_for, main as navigation, relative
from working_reel_presentation import LABELS, NOTICE, family, version_folder


def write_generated(path, body):
    start,end = "<!-- reel-catalogue:start -->","<!-- reel-catalogue:end -->"
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    block = start+"\n"+body.strip()+"\n"+end
    if start in old and end in old:
        old = old[:old.index(start)]+block+old[old.index(end)+len(end):]
    else:
        old = old.rstrip()+"\n\n"+block
    path.write_text(old.strip()+"\n",encoding="utf-8")


def readmes():
    discovery = navigation()
    rows = []
    index = {}
    hardware = "Eight [M3 hex nuts](https://oom.lt/a/3vb5b) and eight [M3 × 12 countersunk screws](https://oom.lt/a/1qf1u) per reel."
    for n in (0,2,3):
        folder = version_folder(n)
        link = relative(ROOT,folder)
        name = family(n)
        guide = "assembly/assembly_instructions"
        rows.append(f"| [![{name} reel]({link}/assembly/thumbnail.png)]({link}/) | [{name}]({link}/) | {n*42-.5 if n else 104:g} mm square | [Offline HTML]({link}/{guide}.html) | [PDF]({link}/{guide}.pdf) |")
        from PIL import Image
        im = Image.open(folder/"assembly/render/raw/book_cover.png").convert("RGBA")
        im.thumbnail((240,240))
        canvas = Image.new("RGB",im.size,"#f6f4ef")
        canvas.paste(im,mask=im.getchannel("A"))
        canvas.save(folder/"assembly/thumbnail.png")
        sequence = []
        for i,action in enumerate(STEPS,1):
            sequence.append(f"{i}. {action}\n\n   [![Assembly step {i}](assembly/cards/step_{i:02d}.png)](assembly/cards/step_{i:02d}.png)")
        fit = ""
        if n:
            other = ROOT/"parts"/plate(n,"plug")
            fit = (f"Use one [plug plate]({relative(folder,other)}/) and this socket plate. "
                   f"The ribbon web is 1 mm thick. The bottom feet add 4.75 mm and the top perimeter rim rises 1.6 mm. The edge diamond funnels ribbon from a 5 mm mouth into the 1.5 mm slit. "
                   f"The four 6.5 mm bores sit on 30 mm centres. Remove the drive from the mating faces and align the feet with the top rim. "
                   f"[Fit trials and measured checks](../../design_stages/{n}x{n}/)")
        index[folder.name] = (fit+"\n\n"+hardware+"\n\n"
            +f"[Offline page viewer]({guide}.html) · [Printable booklet]({guide}.pdf)\n\n"+"\n\n".join(sequence))
    for identifier,label in LABELS.items():
        folder = ROOT/"parts"/identifier
        data = yaml.safe_load((folder/"working.yaml").read_text(encoding="utf-8"))
        cfg = data.get("oobb_details",{})
        n = cfg.get("cells")
        if n:
            description = f"{label} for a {n*42-.5:g} mm square ribbon reel on a 42 mm pitch. Print ribbon face down."
        elif identifier == GEAR:
            description = "A removable drive with a 44 mm face, a 15 mm shaft and four tapered locating pegs."
        elif identifier == CAP:
            description = "The original 104 mm square OOBB end plate. Two identical prints close a reel."
        else:
            description = f"A 44 mm diameter winding drum with {cfg['depth']} mm between end plates. Print upright."
        assembly = index.get(identifier)
        if not assembly:
            guide = version_folder(n or 0)
            assembly = f"[Open the reel assembly guide]({relative(folder,guide)}/#assembly)."
        text = f"""# {label}

> {NOTICE}

## Summary

{description}

[![Generated studio views](3dpr_presentation.png)](./)

## Details

[Printable STL](3dpr.stl) · [OpenSCAD source](3dpr.scad) · [Part folder](./) · [OOBB navigation]({relative(folder,leaf_for(data))}/)

## Parts

`{identifier}`

<details><summary>Catalogue metadata</summary>

```yaml
{yaml.safe_dump(data,sort_keys=False,allow_unicode=True).strip()}
```

</details>

## Assembly

{assembly}
"""
        write_generated(folder/"README.md",text)
    title = """# OOBB ribbon reels

Print a reel for ribbon up to 25, 50, 75 or 100 mm wide. The original end plates use the OOBB hole grid. The two Gridfinity versions sit in a baseplate and let one reel stack on another. All three use the same winding cores and removable four-peg drive.

Based on [oomlout’s OOBB system](https://github.com/oomlout/oomlout_oobb_version_5) and [Zack Freedman’s Gridfinity](https://www.youtube.com/watch?v=ra_9zU-mnl8), using [willtree8’s dimension reference](https://gridfinity.xyz/specification/).

> This is an entirely AI-generated coding project. The source code is largely unreadable by humans, but usable generated files are included. It is published so others can use their own AI tools to understand, modify and regenerate the design.

AI-generated CAD images and instructions. Errors possible. Physical fit has yet to be confirmed on a print.

## Print and fit

[Download the named Bambu Studio plates](output/project_summary/) or [print a small interface trial](design_stages/). Each build plate contains a complete reel and one drive. The core length is the distance between the two ribbon faces. Allow winding clearance when choosing a core for ribbon of exactly that width. On the Gridfinity versions a 1 mm backing carries the feet or shallow perimeter rim. Remove the drive from the mating faces before stacking.

"""
    write_generated(ROOT/"README.md",title+f"[Browse printable parts]({relative(ROOT,discovery)}/) · [Regenerate the files](CAD_BUILDING.md#ribbon-reel-release)\n\n## Assembly\n\nEach guide illustrates the 25 mm core and covers all four winding widths.\n\n| Reel | Version | Footprint | Assembly viewer | Booklet |\n| --- | --- | --- | --- | --- |\n"+"\n".join(rows))


def main():
    import working_fit
    import working_reel_presentation
    import working_project_summary
    working_fit.main()
    working_reel_presentation.main()
    readmes()
    working_project_summary.build()
    working_project_summary.slice_profiles()


if __name__ == "__main__":
    main()

