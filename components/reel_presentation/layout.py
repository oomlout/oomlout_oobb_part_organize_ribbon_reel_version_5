def panel_geometry(style):
    return tuple((size - 2*style["margin_mm"] - (count-1)*style["gutter_mm"])/count
                 for size,count in zip(style["page_mm"], (style["columns"],style["rows"])))

