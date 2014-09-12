sqrt2 = 1.41421;
W = 4;
L = 20;

module diamond() {
    translate([0, -sqrt2*L/2, -W/2])
        rotate([0, 0, 45])
            cube([L, W, W]);
    translate([-sqrt2*L/2 + W*sqrt2/2, -W*sqrt2/2, -W/2])
        rotate([0, 0, 45])
            cube([L, W, W]);
    translate([-sqrt2*L/2, 0, -W/2])
        rotate([0, 0, -45])
            cube([L, W, W]);
    translate([-W*sqrt2/2, sqrt2*L/2 - W*sqrt2/2, -W/2])
        rotate([0, 0, -45])
            cube([L, W, W]);
}

diamond();
rotate([90, 0, 0]) diamond();
rotate([0, 90, 0]) diamond();

// pedestal height and diameter
Ph = 10;
Pd = 5;

translate([0, 0, -Ph - L*sqrt2/2 + W*sqrt2/2])
    cylinder(h=Ph, d=Pd, $fn=20);