$fn = 50;

// Print with the ribbon face on Z=0. All dimensions in millimetres.
module square_section(w, r) {
    offset(r=r, $fn=48) square([w-2*r,w-2*r],center=true);
}
module slab(w,r,z,h) {
    translate([0,0,z]) linear_extrude(h) square_section(w,r);
}
// Constant corner centres give true 45-degree flanks.
module taper(w1,r1,w2,r2,z,h) {
    hull() {
        slab(w1,r1,z,0.001);
        slab(w2,r2,z+h-0.001,0.001);
    }
}
// The feet are the standard three-stage male profile, measured from the web.
module plug_foot(web) {
    taper(41.5,3.75,37.2,1.6,web,2.15);
    slab(37.2,1.6,web+2.15,1.8);
    taper(37.2,1.6,35.6,0.8,web+3.95,0.8);
}
// A single perimeter lip captures only the tip of the mating feet.
module top_rim(n,web) {
    w=n*42-0.5;
    difference() {
        slab(w,3.75,web,1.6);
        taper(n*42-5.7,1.15,n*42-4.3,1.85,web,0.7);
        slab(n*42-4.3,1.85,web+0.7,1);
    }
}
module gridfinity_end(n=2,side="plug",web=1) {
    assert(n==2 || n==3);
    assert(side=="plug" || side=="socket");
    w=n*42-0.5;
    cut=web+5;
    difference() {
        union() {
            slab(w,3.75,0,web);
            if (side=="plug")
                for (i=[0:n-1],j=[0:n-1])
                    translate([42*(i-(n-1)/2),42*(j-(n-1)/2),0]) plug_foot(web);
            else top_rim(n,web);
        }
        translate([0,0,-0.1]) cylinder(d=17,h=cut+0.2,$fn=80);
        for(x=[-15,15],y=[-15,15]) translate([x,y,-0.1])
            cylinder(d=6.5,h=cut+0.2,$fn=64);
        // Seat screws flush with the web on either face of the core.
        for(a=[0:90:270],s=[-1,1]) rotate([0,0,a]) translate([15,s*7.5,0]) {
            translate([0,0,-0.1]) cylinder(d=3.4,h=cut+0.2,$fn=48);
            translate([0,0,web-1.6]) cylinder(d1=3.2,d2=6.4,h=1.6,$fn=48);
            translate([0,0,web]) cylinder(d=6.4,h=5,$fn=48);
        }
        j=w/2-12;
        translate([22,-0.75,-0.1]) cube([w/2-21,1.5,cut+0.2]);
        // Half of this diamond opens to the edge, making a 5 mm lead-in.
        for(x=[j,w/2]) translate([x,0,-0.1]) linear_extrude(cut+0.2)
            polygon([[-2.5,0],[0,-2.5],[2.5,0],[0,2.5]]);
        translate([j-0.75,0,-0.1]) cube([1.5,min(30,w/2-12),cut+0.2]);
    }
}


difference() {
	union() {
		gridfinity_end(n = 2, side = "plug", web = 1.0);
	}
	union();
}
