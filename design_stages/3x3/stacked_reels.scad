use <models.scad>;

// Two 25 mm reels with the removable drives lifted off for stacking.
color("teal") {
    translate([0,0,-25]) rotate([180,0,0]) plug();
    socket();
    translate([0,0,6.75]) rotate([180,0,0]) plug();
    translate([0,0,31.75]) socket();
}
color("dimgray") {
    translate([0,0,-25]) core25();
    translate([0,0,6.75]) core25();
}
