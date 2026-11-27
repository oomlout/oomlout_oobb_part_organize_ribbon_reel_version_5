import copy

from oomp_populate_helper import build_oomp_id, write_extras


def main(**kwargs):
    options = [
        {"oobb_type": "core", "diameter": 3, "depth": depth}
        for depth in [25]
    ]
    options.append({"oobb_type": "end_cap", "width": 7, "height": 7, "depth": 3})
    for option in options:
        if option["oobb_type"] == "end_cap" and option["width"] != option["height"]:
            raise ValueError("End caps must be square")
        taxonomy = ["oobb", "part", "organize", "ribbon", "reel", option["oobb_type"]]
        if option["oobb_type"] == "core":
            taxonomy.extend([f'{option["diameter"]}_diameter', f'{option["depth"]}_depth'])
        else:
            taxonomy.extend([f'{option["width"]}_width', f'{option["height"]}_height', f'{option["depth"]}_depth'])
        for index, value in enumerate(taxonomy, 1):
            option[f"taxonomy_{index}"] = value
        option["oobb_details"] = copy.deepcopy(option)
        option["oobb_details"].update(run_scad=True, run_solidcraft=False)

    import working_oomp_populate_extra_detail
    working_oomp_populate_extra_detail.main(extras=options)
    write_extras(options)


if __name__ == "__main__":
    main()
