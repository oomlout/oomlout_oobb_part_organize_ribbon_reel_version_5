// Independent, full (unrelieved) Gridfinity reference gauges.
// Source: willtree8's Gridfinity Design Reference, https://gridfinity.xyz/specification/
module ref_layer(w,r,z,h) {
    translate([0,0,z]) linear_extrude(h) offset(r=r,$fn=64)
        square([w-2*r,w-2*r],center=true);
}
module ref_band(w,r,z,delta) {
    hull() {
        ref_layer(w,r,z,0.001);
        ref_layer(w+2*delta,r+delta,z+delta-0.001,0.001);
    }
}
module ref_cells(n) {
    for(x=[0:n-1], y=[0:n-1])
        translate([42*(x-(n-1)/2),42*(y-(n-1)/2),0]) children();
}
module reference_base(n) {
    union() {
        ref_cells(n) union() {
            ref_band(35.6,0.8,0,0.8);
            ref_layer(37.2,1.6,0.8,1.8);
            ref_band(37.2,1.6,2.6,2.15);
        }
        ref_layer(n*42-0.5,3.75,4.75,1);
    }
}
module reference_plate(n) {
    difference() {
        ref_layer(n*42,4,-1,5.64);
        ref_cells(n) union() {
            ref_band(36.3,1.15,0,0.7);
            ref_layer(37.7,1.85,0.7,1.8);
            ref_band(37.7,1.85,2.5,2.15);
        }
    }
}

reference_base(3);
