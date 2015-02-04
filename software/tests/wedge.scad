intersection() {
    cube([10,10,10]);
    rotate([-45,0,0])
        cube([40,40,40]);
    rotate([0,0,-45])
        cube([40,40,40]);
}
