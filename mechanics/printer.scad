use <sprockets.scad>;

/*
 * Let's keep life simple by establishing the top surface of the bucket
 * as z = 0.
 */
module home_depot_bucket() {
    translate([0, 0, -14.5])
        difference() {
            cylinder(h=14.5, d1=10.25, d2=12, $fn=60);
            translate([0,0,1/4])
                cylinder(h=14.5, d1=10, d2=11.75, $fn=60);
        }
}

module ThreadedRod(length) {
    // Home Depot 1/4"-20 threaded rod
    cylinder(d=1/4, h=length, $fn=12);
}


module CrudeNEMA23() {
    translate([0, 0, -0.01])
        cylinder(d=0.26, h=1.1, $fn=12);
    translate([-1.15, -1.15, -1/4])
        cube([2.3, 2.3, 1/4]);
    translate([0, 0, -2.75])
        cylinder(h=2.5, d=2.3, $fn=30);
}


module Prism45() {
    translate([-1/2, -1/2, 0]) {
        difference() {
            cube([1, 1, 1]);
            rotate([0, -45, 0])
                translate(-1, 0, 0)
                cube([2, 2, 2]);
        }
    }
}


teeth = 8;
wrench_size = 0.43;

/* STL files are dimensionless and I usually like to use inches,
 * but the Formlabs machine prefers millimeters, and OpenSCAD
 * seems to want them also.
 */

scale([25.4, 25.4, 25.4]) {
    home_depot_bucket();

    /* mirror and supports */
    translate([1, 6.5, 0])
        ThreadedRod(6);
    translate([1, -6.5, 0])
        ThreadedRod(6);
    translate([-1, 6.5, 0])
        ThreadedRod(6);
    translate([-1, -6.5, 0])
        ThreadedRod(6);
    translate([-1.5, -7, 5])
        cube([3, 14, 1/4]);
    translate([0, 0, 3.25])
        rotate([0, 45, 0])
            translate([-3, -3, 0])
                cube([6, 6, 1/4]);
    translate([1.5, 0, 3.5])
        scale([3, 3, 3])
        rotate([0, -90, 0])
        Prism45();

    /* lower support */
    difference() {
        union() {
            translate([0, 0, 0])
                    cylinder(d=15, h=1/4, $fn=60);
            rotate([0, 0, 60])
                translate([7, -2.5, 0])
                    cube([2.5, 1, 1/4]);
            rotate([0, 0, 60])
                translate([7, 1.5, 0])
                    cube([2.5, 1, 1/4]);
        }
        translate([0, 0, -1/2])
            cylinder(h=2, d=8, $fn=60);
    }
    for (i = [0 : 2])
        rotate([0, 0, 120*i])
            translate([6, -1.5, -1])
                cube([1, 3, 1]);

    /* stepper and stepper sprocket */
    rotate([0, 0, 60]) {
        translate([8, 0, 7/16])
            StepperSprocket(teeth, 1/4);
        translate([8, 0, -1/4])
            CrudeNEMA23();
        translate([6.5, -2.5, -1/4])
            cube([3, 5, 1/4]);
    }

    /* hex nut sprockets */
    for (i = [0 : 2])
        rotate([0, 0, 120*i])
            translate([4.5, 0, 7/16])
                HexNutSprocket(teeth, wrench_size);

    /* build platform with threaded rods */
    translate([0, 0, -10])
        cylinder(d=10, h=1/4, $fn=30);
    for (i = [0 : 2])
        rotate([0, 0, 120*i])
            translate([4.5, 0, -10])
                ThreadedRod(16);
    for (i = [0 : 2])
        rotate([0, 0, 120*i])
            translate([4.5, 0, 7/16])
                HexNutSprocket(teeth, wrench_size);
}
