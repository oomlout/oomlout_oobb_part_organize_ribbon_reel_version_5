// Nominal, thread-free purchased hardware envelopes for fit and instruction views.
module nut() {
    difference() {
        cylinder(h=2.4,r=5.5/sqrt(3),$fn=6);
        translate([0,0,-0.1]) cylinder(h=2.6,d=2.5,$fn=48);
    }
}
module screw() {
    difference() {
        union() {
            cylinder(h=1.5,d1=6,d2=3,$fn=48);
            translate([0,0,1.49]) cylinder(h=10.51,d=3,$fn=48);
        }
        translate([0,0,-0.01]) cylinder(h=1.1,d=2*2/sqrt(3),$fn=6);
    }
}

nut();
