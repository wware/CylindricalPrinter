sqrt2 = 1.41421356237;
s2 =  sqrt2 / 2;

module diamond(L, W) {
    translate([0, -sqrt2*L/2, -W/2])
        rotate([0, 0, 45])
            cube([L, W, W]);
    translate([-sqrt2*L/2 + W*s2, -W*s2, -W/2])
        rotate([0, 0, 45])
            cube([L, W, W]);
    translate([-sqrt2*L/2, 0, -W/2])
        rotate([0, 0, -45])
            cube([L, W, W]);
    translate([-W*s2, s2*L - W*s2, -W/2])
        rotate([0, 0, -45])
            cube([L, W, W]);
}

module octohedron(L, W) {
    diamond(L, W);
    rotate([90, 0, 0]) diamond(L, W);
    rotate([0, 90, 0]) diamond(L, W);
}

module support(x, y, H) {
    a = 0;
    b = 1;
    n = 6;
    dmin = 0.7;
    translate([x, y, 0]) {
        cylinder(d1=6, d2=2, h=2, $fn=n);
        cylinder(d=2, h=H+0.01-a-b, $fn=n);
        translate([0, 0, H-a-b])
            cylinder(d1=2, d2=0, h=b+0.01, $fn=n);
    }
}

W = 4;
L = 20;
H = 8;

translate([0, 0, (W-L)/2]) {
    support(-L/2 + s2*W/2, 0, H + 0.3);
    support(L/2 - s2*W/2, 0, H + 0.3);
}

translate([0, 0, H + W/2 + 0.7071*W/2])
    rotate([0, 45, 0]) {
        octohedron(L, W);
    }
