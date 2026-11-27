use <models.scad>;
difference() { union() { color("turquoise") socket(); color("gray") translate([0,0,6.75]) rotate([180,0,0]) plug(); } translate([0,-100,-2]) cube([100,200,30]); }
