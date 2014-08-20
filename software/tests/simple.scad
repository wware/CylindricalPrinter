module pyramid() {
    polyhedron(
        points=[ [1,1,0],[1,-1,0],[-1,-1,0],[-1,1,0],[0,0,1]  ],
        faces=[ [0,1,4],[1,2,4],[2,3,4],[3,0,4],[1,0,3],[2,1,3] ]
    );
}

union() {
    translate([0,0,1.65])
        difference() {
            scale(1.2) pyramid();
            pyramid();
        }
    translate([0,0,-0.3])
        difference() {
            intersection() {
                translate([-1.15,-1.15,-2])
                    cube([2.3,2.3,5], $fn=40);
                difference() {
                    translate([0,0,-.3])
                        cylinder(h=2.3, r1=1, r2=2, $fn=40);
                    translate([-1,-1,0])
                        cube([2,2,2], $fn=40);
                }
            }
            union() {
                translate([0,2.5,1.5])
                    rotate(90, [1,0,0])
                        cylinder(h=5, r1=0.9, r2=0.9, $fn=40);
                translate([-2.5,0,1.5])
                    rotate(90, [0,1,0])
                        cylinder(h=5, r1=0.9, r2=0.9, $fn=40);
            }
        }
    for (i = [0:2]) {
        rotate(i*120, [0,0,1])
            translate([0.8,0,-1.6])
                cylinder(h=1, r1=0.1, r2=0.04, $fn=12);
    }
}
