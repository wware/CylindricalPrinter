/* http://www.thingiverse.com/thing:426854 */

module sprocket_tooth() {
    difference() {
        union() {
            translate([-1/4,0,-1/16])
                cube([1/2,3/8,1/8]);
            intersection() {
                translate([1/4, 0, -1/16])
                    cylinder(h=1/8, d=1-5/16, $fn=30);
                translate([-1/4, 0, -1/16])
                    cylinder(h=1/8, d=1-5/16, $fn=30);
            }
        }
    translate([1/4, 0, -1/8])
        cylinder(h=1/4, d=5/16, $fn=30);
    translate([-1/4, 0, -1/8])
        cylinder(h=1/4, d=5/16, $fn=30);
    multmatrix(m = [
        [1, 0, 0, -0.5],
        [0, 1, 4, -1.3],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
        cube([1, 1, 1]);
    multmatrix(m = [
        [1, 0, 0, -0.5],
        [0, 1, -4, 2.7],
        [0, 0, 1, -1],
        [0, 0, 0, 1]
    ])
        cube([1, 1, 1]);
    }
}

module sprocket(teeth, hub_diameter) {
    pitch = 1/2;   // bicycle chain, 1/2 - 1/8
    theta = 360.0 / teeth;
    r = (pitch / 2) / tan(theta / 2);
    for (i = [0 : teeth-1])
        rotate(theta*i, [0, 0, 1])
            translate([0, -r, 0]) sprocket_tooth();
    translate([0,0,-1/16])
        cylinder(h=1/8, d=2*r-0.5, $fn=20);
    translate([0,0,-3/16])
        cylinder(h=3/8, d=hub_diameter, $fn=20);
}

module StepperSprocket(teeth, axle_diameter) {
    dcut = 0.5 * (0.22/0.250) * axle_diameter;
    difference() {
        sprocket(teeth, 0.5);
        difference() {
            translate([0,0,-0.5])
                cylinder(h=1, r=axle_diameter/2, $fn=40);
            translate([dcut, -0.5, -0.5])
                cube([1, 1, 1]);
        }
    }
}

module HexNutSprocket(teeth, wrench_size) {
    difference() {
        sprocket(teeth, 0.75);
        intersection_for(n = [1 : 3])
            rotate(60 * n, [0, 0, 1])
                translate([-0.5 * wrench_size, -0.5, -0.5])
                    cube([wrench_size, 1, 1]);
    }
}

teeth = 8;
wrench_size = 0.43;

/* STL files are dimensionless and I usually like to use inches,
 * but the Formlabs machine prefers millimeters, and OpenSCAD
 * seems to want them also.
 */

scale([25.4, 25.4, 25.4]) {
    // StepperSprocket(teeth, 1/4);

    HexNutSprocket(teeth, wrench_size);
}
